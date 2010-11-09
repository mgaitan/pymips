#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Datapath
"""

from myhdl import Signal, delay, always, always_comb, now, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL

from clock_driver import clock_driver
from program_counter import program_counter
from instruction_memory import instruction_memory
from instruction_decoder import instruction_dec
from alu import ALU
from alu_control import alu_control
from and_gate import and_gate
from control import control
from register_file import register_file
from sign_extender import sign_extend
from mux import mux2, mux4
from data_memory import data_memory

from latch_if_id import latch_if_id
from latch_id_ex import latch_id_ex
from latch_ex_mem import latch_ex_mem
from latch_mem_wb import latch_mem_wb

DEBUG = False #True  #set to false to convert 



MIN = -(2**31)
MAX = 2**31 - 1

MIN_16 = -(2**15)
MAX_16 = 2**15 - 1

def pipeline(clk_period=1, Reset=Signal(intbv(0)[1:]), Zero=Signal(intbv(0)[1:])):

    """
    A DLX processor with 5 pipeline stages. 
    =======================================

    Stages
    ------
    
     [IF] -> IF/ID -> [ID] -> ID/EX -> [EX] -> EX/MEM -> [MEM] -> MEM/WB __
                   ^                                                       |
                   |_______________________________________________________|

    Conventions:
    ------------

    * Signals are in ``CamelCase``

    * Instances are with ``under_score``

    * The signals shared two or more stage are suffixed with the pipeline stage to which it belongs.
      For example: ``PcAdderO_if``  before IF/ID latch is the same signal than 
      ``PcAdderO_id`` after it. 

    """

    ##############################
    # clock settings
    ##############################

    Clk = Signal(intbv(0)[1:])     #internal clock
    ClkPc = Signal(intbv(0)[1:])   #frec should be almost 1/4 clk internal

    clk_driver = clock_driver(Clk, clk_period)
    clk_driver_pc = clock_driver(ClkPc, clk_period * 4)

    ####################
    #feedback Signals 
    ######################
    
    # signals from and advanced stage which feeds a previous component

    BranchAdderO_mem = Signal(intbv(0, min=MIN, max=MAX)[32:])
    PCSrc_mem   = Signal(intbv(0)[1:]) #control of mux for program_counter on IF stage - (branch or inmediante_next)    

    WrRegDest_wb = Signal(intbv(0)[32:])        #register pointer where MuxMemO_wb data will be stored.
    MuxMemO_wb = Signal(intbv(0, min=MIN, max=MAX)[32:])    #data output from WB mux connected as Write Data input on Register File (ID stage)

    RegWrite_wb = Signal(intbv(0)[1:])

    ##############################
    # IF
    ##############################

    #instruction memory

    Ip = Signal(intbv(0)[32:] ) #connect PC with intruction_memory
    Instruction_if = Signal(intbv(0)[32:])   #32 bits instruction line.
    im = instruction_memory (Ip, Instruction_if)

    #PC
    NextIp =  Signal(intbv(0)[32:] )   #output of mux_branch - input of pc
    pc = program_counter(Clk, NextIp, Ip)

    #pc_adder
    INCREMENT = 1   #it's 4 in the book, but my memory it's organized in 32bits words, not bytes
    PcAdderOut_if =  Signal(intbv(0)[32:] )   #output of pc_adder - input0 branch_adder and mux_branch

    pc_adder = ALU(Signal(0b0010), Ip, Signal(INCREMENT), PcAdderOut_if, Signal(0))    #hardwire an ALU to works as an adder
    
    #mux controlling next ip branches. 

    mux_pc_source = mux2(PCSrc_mem, NextIp, PcAdderOut_if, BranchAdderO_mem)

    ##############################
    # IF/ID
    ##############################

    PcAdderOut_id =  Signal(intbv(0)[32:])
    Instruction_id = Signal(intbv(0)[32:])   
    
    latch_if_id_ = latch_if_id(Clk, Reset, Instruction_if, PcAdderOut_if, Instruction_id, PcAdderOut_id)


    ##############################
    # ID
    ##############################

    #DECODER
    Opcode_id = Signal(intbv(0)[6:])   #instruction 31:26  - to Control
    Rs_id = Signal(intbv(0)[5:])       #instruction 25:21  - to read_reg_1
    Rt_id = Signal(intbv(0)[5:])       #instruction 20:16  - to read_reg_2 and mux controlled by RegDst
    Rd_id = Signal(intbv(0)[5:])       #instruction 15:11  - to the mux controlled by RegDst
    Shamt_id = Signal(intbv(0)[5:])    #instruction 10:6   - 
    Func_id = Signal(intbv(0)[6:])     #instruction 5:0    - to ALUCtrl
    Address16_id = Signal(intbv(0, min=-(2**15), max=2**15 - 1))   #instruction 15:0   - to Sign Extend

    instruction_decoder_ = instruction_dec(Instruction_id, Opcode_id, Rs_id, Rt_id, Rd_id, Shamt_id, Func_id, Address16_id)

    #sign extend
    Address32_id = Signal(intbv(0, min=MIN, max=MAX)[32:]) 

    sign_extend_ = sign_extend(Address16_id, Address32_id)

    #CONTROL 
    signals_1bit = [Signal(intbv(0)[1:]) for i in range(7)]
    RegDst_id, ALUSrc_id, MemtoReg_id, RegWrite_id, MemRead_id, MemWrite_id, Branch_id = signals_1bit     
    
    ALUop_id = Signal(intbv(0)[2:])  
    
    control_ = control(Opcode_id, RegDst_id, Branch_id, MemRead_id, 
                        MemtoReg_id, ALUop_id, MemWrite_id, ALUSrc_id, RegWrite_id)
    

    #REGISTER FILE
    Data1_id =  Signal(intbv(0, min=MIN, max=MAX)[32:])
    Data2_id =  Signal(intbv(0, min=MIN, max=MAX)[32:])

    register_file_i = register_file(Clk, Rs_id, Rt_id, WrRegDest_wb, MuxMemO_wb, RegWrite_wb, Data1_id, Data2_id, depth=32)
    
    
    
    ##############################
    # ID/EX
    ##############################
    
    PcAdderOut_ex =  Signal(intbv(0)[32:])
    
    signals_1bit = [Signal(intbv(0)[1:]) for i in range(7)]
    RegDst_ex, ALUSrc_ex, MemtoReg_ex, RegWrite_ex, MemRead_ex, MemWrite_ex, Branch_ex = signals_1bit

    ALUop_ex = Signal(intbv(0)[2:])  
    
    Data1_ex =  Signal(intbv(0, min=MIN, max=MAX)[32:])
    Data2_ex =  Signal(intbv(0, min=MIN, max=MAX)[32:])
    

    Rs_ex = Signal(intbv(0)[5:])       #instruction 25:21  - to read_reg_1
    Rt_ex = Signal(intbv(0)[5:])       #instruction 20:16  - to read_reg_2 and mux controlled by RegDst
    Rd_ex = Signal(intbv(0)[5:])       #instruction 15:11  - to the mux controlled by RegDst
    #Shamt_ex = Signal(intbv(0)[5:])    #instruction 10:6   - 
    Func_ex = Signal(intbv(0)[6:])     #instruction 5:0    - to ALUCtrl
    
    Address32_ex = Signal(intbv(0, min=MIN, max=MAX)[32:]) 

    
    latch_id_ex_ = latch_id_ex(Clk, Reset, 
                                PcAdderOut_id, 
                                Data1_id, Data2_id, Address32_id,
                                Rd_id, Rt_id, Func_id, 
                                
                                RegDst_id, ALUop_id, ALUSrc_id,     #signals to EX pipeline stage
                                Branch_id, MemRead_id, MemWrite_id, #signals to MEM pipeline stage
                                RegWrite_id, MemtoReg_id,           #signals to WB pipeline stage
                                
                                PcAdderOut_ex, 
                                Data1_ex, Data2_ex, Address32_ex,
                                Rd_ex, Rt_ex, Func_ex, 

                                RegDst_ex, ALUop_ex, ALUSrc_ex,     #signals to EX pipeline stage
                                Branch_ex, MemRead_ex, MemWrite_ex, #signals to MEM pipeline stage
                                RegWrite_ex, MemtoReg_ex            #signals to WB pipeline stage
                               )


    ##############################
    # EX
    ##############################

    BranchAdderO_ex = Signal(intbv(0, min=MIN, max=MAX)[32:])

    Zero_ex = Signal(intbv(0)[1:])
    AluResult_ex = Signal(intbv(0, min=MIN, max=MAX)[32:])


    MuxAluDataSrc_ex = Signal(intbv(0, min=MIN, max=MAX)[32:])

    WrRegDest_ex = Signal(intbv(0)[32:])
    
    #muxer 2nd operand in ALU
    mux_alu_src = mux2(ALUSrc_ex, MuxAluDataSrc_ex, Data2_ex, Address32_ex)

    #Branch adder
    branch_adder_ = ALU(Signal(0b0010), PcAdderOut_ex, Address32_ex, BranchAdderO_ex, Signal(0))

    #ALU Control
    AluControl = Signal(intbv('1111')[4:])  #control signal to alu
    alu_control_ = alu_control(ALUop_ex, Func_ex, AluControl)

    #ALU
    alu_ = ALU(AluControl, Data1_ex, MuxAluDataSrc_ex, AluResult_ex, Zero_ex)

    #Mux RegDestiny Control Write register between rt and rd. 
    mux_wreg = mux2(RegDst_ex, WrRegDest_wb, Rt_ex, Rd_ex)

    
    ##############################
    # EX/MEM
    ##############################

    BranchAdderO_mem = Signal(intbv(0, min=MIN, max=MAX)[32:])

    Zero_mem = Signal(intbv(0)[1:])
    AluResult_mem = Signal(intbv(0, min=MIN, max=MAX)[32:])

    Data2_mem =  Signal(intbv(0, min=MIN, max=MAX)[32:])

    WrRegDest_mem = Signal(intbv(0)[32:])

    #control signals
    signals_1bit = [Signal(intbv(0)[1:]) for i in range(5)]
    MemtoReg_mem, RegWrite_mem, MemRead_mem, MemWrite_mem, Branch_mem = signals_1bit

    
    latch_ex_mem_ = latch_ex_mem(Clk, Reset, 
                                BranchAdderO_ex,
                                AluResult_ex, Zero_ex, 
                                Data2_ex, WrRegDest_ex, 
                                Branch_ex, MemRead_ex, MemWrite_ex,  #signals to MEM pipeline stage
                                RegWrite_ex, MemtoReg_ex,     #signals to WB pipeline stage
                                
                                BranchAdderO_mem,
                                AluResult_mem, Zero_mem, 
                                Data2_mem, WrRegDest_mem, 
                                Branch_mem, MemRead_mem, MemWrite_mem,  #signals to MEM pipeline stage
                                RegWrite_mem, MemtoReg_mem,     #signals to WB pipeline stage
                                
                            )
    
    ##############################
    # MEM
    ##############################

    DataMemOut_mem = Signal(intbv(0, min=MIN, max=MAX)[32:])
    AluResult_ = Signal(intbv(0, min=MIN, max=MAX)[32:])
    
    #branch AND gate
    branch_and_gate = and_gate(Branch_mem, Zero_mem, PCSrc_mem)  
    
    #data memory
    data_memory_ = data_memory(Clk, AluResult_mem, Data2_mem, DataMemOut_mem, MemRead_mem, MemWrite_mem)

    
    ##############################
    # EX/WB
    ##############################
    
    #RegWrite_wb, on feedback signals section
    MemtoReg_wb = Signal(intbv(0)[1:])
    
    DataMemOut_wb = Signal(intbv(0, min=MIN, max=MAX)[32:])
    AluResult_wb = Signal(intbv(0, min=MIN, max=MAX)[32:])


    #WrRegDest_wb on feedback signals sections. 

    latch_mem_wb_ = latch_mem_wb(Clk, Reset, 
                                 DataMemOut_mem, 
                                 AluResult_mem, 
                                 WrRegDest_mem, 
                                 RegWrite_mem, MemtoReg_mem,     #signals to WB pipeline stage
                                 
                                 DataMemOut_wb, 
                                 AluResult_wb, 
                                 WrRegDest_wb, 
                                 RegWrite_wb, MemtoReg_wb,     #signals to WB pipeline stage
                                 )

    ##############################
    # WB
    ##############################
    

    mux_mem2reg_ = mux2(MemtoReg_wb, MuxMemO_wb, DataMemOut_wb, AluResult_wb)


                    

    if DEBUG:
        @always(clk.posedge)
        def debug_internals():
            print "-" * 78
            print "time %s | clk %i | clk_pc %i | ip %i " % (now(), clk, clk_pc, ip)

            print 'pc_add_o %i | branch_add_o %i | BranchZ %i | next_ip %i' % (pc_adder_out, branch_adder_out, branchZ, next_ip)
            print 'instruction', bin(instruction, 32) 

            print 'opcode %s | rs %i | rt %i | rd %i | shamt %i | func %i | address %i' % \
                 (bin(opcode, 6), rs, rt, rd, shamt, func, address )

            print 'wr_reg_in %i | dat1 %i | dat2 %i | muxALUo %i ' % \
                  (wr_reg_in, data1, data2, mux_alu_out)

            print 'RegDst %i | ALUSrc %i | Mem2Reg %i | RegW %i | MemR %i | MemW %i | Branch %i | ALUop %s' % ( RegDst, ALUSrc, MemtoReg, RegWrite, MemRead, MemWrite, Branch, bin(ALUop, 2))
        
            print 'func: %s | aluop: %s | alu_c_out: %s' % ( bin(func, 5), 
                                                            bin(ALUop, 2), 
                                                            bin(alu_control_out, 4) )

            print 'ALU_out: %i | Zero: %i' % (alu_out, zero)


            print 'ram_out %i | mux_ram_out %i ' % (ram_out, mux_ram_out)
            
            

    return instances()



def testBench():


    if not DEBUG:
        datapath_i = pipeline() #toVHDL(datapath)
    else:
        datapath_i = pipeline()

    

    return instances()



def main():
    sim = Simulation(testBench())
    sim.run(10)


if __name__ == '__main__':


    main()



