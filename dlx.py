#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Datapath
"""

from myhdl import Signal, delay, always, always_comb, now, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL, traceSignals

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

#hazard controls

from forwarding import forwarding
from hazard_detector import hazard_detector




DEBUG = True  #set to false to convert 


import random

MIN = -(2**31)
MAX = 2**31 - 1

MIN_16 = -(2**15)
MAX_16 = 2**15 - 1



def dlx(clk_period=1, Reset=Signal(intbv(0)[1:]), Zero=Signal(intbv(0)[1:])):

    """
    A DLX processor with 5 pipeline stages. 
    =======================================

    Stages
    ------
     +------------------+
     |        +------- Hazard
     |        |    +-> Detect <-----+
     |        |    |   |            |
     |        |    |   |            |
     v        v    |   v            |
     [IF] -> IF/ID -> [ID] -> ID/EX -> [EX] -> EX/MEM -> [MEM] -> MEM/WB __
                   ^                |  ^                |               |  |
                   |                |  |  <_____________|               |  |
                   |                +> FORW <___________________________|  |
                   |                                                       | 
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
    MuxMemO_wb = Signal(intbv(0, min=MIN, max=MAX))    #data output from WB mux connected as Write Data input on Register File (ID stage)

    RegWrite_wb = Signal(intbv(0)[1:])

    ForwardA, ForwardB = [ Signal(intbv(0)[2:]) for i in range(2) ]     #Signals Generated in Forwarding units to control ALU's input muxers 
            
    AluResult_mem = Signal(intbv(0, min=MIN, max=MAX))

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
    INCREMENT = 1   #it's 4 in the book, but my instruction memory is organized in 32bits words, not in bytes
    PcAdderOut_if =  Signal(intbv(0)[32:] )   #output of pc_adder - input0 branch_adder and mux_branch

    pc_adder = ALU(Signal(0b0010), Ip, Signal(INCREMENT), PcAdderOut_if, Signal(0))    #hardwiring an ALU to works as an adder
    
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

    NopSignal = Signal(intbv(0)[1:])

    instruction_decoder_ = instruction_dec(Instruction_id, Opcode_id, Rs_id, Rt_id, Rd_id, Shamt_id, Func_id, Address16_id, NopSignal)

    #sign extend
    Address32_id = Signal(intbv(0, min=MIN, max=MAX)) 

    sign_extend_ = sign_extend(Address16_id, Address32_id)

    #CONTROL 
    signals_1bit = [Signal(intbv(0)[1:]) for i in range(7)]
    RegDst_id, ALUSrc_id, MemtoReg_id, RegWrite_id, MemRead_id, MemWrite_id, Branch_id = signals_1bit     
    
    ALUop_id = Signal(intbv(0)[2:])  
    
    control_ = control(Opcode_id, RegDst_id, Branch_id, MemRead_id, 
                        MemtoReg_id, ALUop_id, MemWrite_id, ALUSrc_id, RegWrite_id, NopSignal)
    

    #REGISTER FILE
    Data1_id =  Signal(intbv(0, min=MIN, max=MAX))
    Data2_id =  Signal(intbv(0, min=MIN, max=MAX))

    register_file_i = register_file(Clk, Rs_id, Rt_id, WrRegDest_wb, MuxMemO_wb, RegWrite_wb, Data1_id, Data2_id, depth=32)
    
    
    
    ##############################
    # ID/EX
    ##############################
    
    PcAdderOut_ex =  Signal(intbv(0)[32:])
    
    signals_1bit = [Signal(intbv(0)[1:]) for i in range(7)]
    RegDst_ex, ALUSrc_ex, MemtoReg_ex, RegWrite_ex, MemRead_ex, MemWrite_ex, Branch_ex = signals_1bit

    ALUop_ex = Signal(intbv(0)[2:])  
    
    Data1_ex =  Signal(intbv(0, min=MIN, max=MAX))
    Data2_ex =  Signal(intbv(0, min=MIN, max=MAX))
    

    Rs_ex = Signal(intbv(0)[5:])       #instruction 25:21  - to read_reg_1
    Rt_ex = Signal(intbv(0)[5:])       #instruction 20:16  - to read_reg_2 and mux controlled by RegDst
    Rd_ex = Signal(intbv(0)[5:])       #instruction 15:11  - to the mux controlled by RegDst
    #Shamt_ex = Signal(intbv(0)[5:])    #instruction 10:6   - 
    Func_ex = Signal(intbv(0)[6:])     #instruction 5:0    - to ALUCtrl
    
    Address32_ex = Signal(intbv(0, min=MIN, max=MAX)) 

    
    latch_id_ex_ = latch_id_ex(Clk, Reset, 
                                PcAdderOut_id, 
                                Data1_id, Data2_id, Address32_id,
                                Rs_id, Rt_id, Rd_id, Func_id, 
                                
                                RegDst_id, ALUop_id, ALUSrc_id,     #signals to EX pipeline stage
                                Branch_id, MemRead_id, MemWrite_id, #signals to MEM pipeline stage
                                RegWrite_id, MemtoReg_id,           #signals to WB pipeline stage
                                
                                PcAdderOut_ex, 
                                Data1_ex, Data2_ex, Address32_ex,
                                Rs_ex, Rt_ex, Rd_ex, Func_ex, 

                                RegDst_ex, ALUop_ex, ALUSrc_ex,     #signals to EX pipeline stage
                                Branch_ex, MemRead_ex, MemWrite_ex, #signals to MEM pipeline stage
                                RegWrite_ex, MemtoReg_ex            #signals to WB pipeline stage
                               )


    ##############################
    # EX
    ##############################

    BranchAdderO_ex = Signal(intbv(0, min=MIN, max=MAX)[32:])

    Zero_ex = Signal(intbv(0)[1:])
    AluResult_ex = Signal(intbv(0, min=MIN, max=MAX))

    ForwMux1Out, ForwMux2Out = [ Signal(intbv(0, min=MIN, max=MAX)) for i in range(2) ]  #Output of forw_mux1 and forw_mux2

    MuxAluDataSrc_ex = Signal(intbv(0, min=MIN, max=MAX))

    WrRegDest_ex = Signal(intbv(0)[32:])
    
    
    
    forw_mux1_ = mux4(ForwardA, ForwMux1Out, Data1_ex, MuxMemO_wb, AluResult_mem)

    forw_mux2_ = mux4(ForwardB, ForwMux2Out, Data2_ex, MuxMemO_wb, AluResult_mem)


    #2nd muxer of 2nd operand in ALU
    mux_alu_src = mux2(ALUSrc_ex, MuxAluDataSrc_ex, ForwMux2Out, Address32_ex)

    #Branch adder
    branch_adder_ = ALU(Signal(0b0010), PcAdderOut_ex, Address32_ex, BranchAdderO_ex, Signal(0))

    #ALU Control
    AluControl = Signal(intbv('1111')[4:])  #control signal to alu
    alu_control_ = alu_control(ALUop_ex, Func_ex, AluControl)

    #ALU
    alu_ = ALU(AluControl, ForwMux1Out, MuxAluDataSrc_ex, AluResult_ex, Zero_ex)

    #Mux RegDestiny Control Write register between rt and rd. 
    mux_wreg = mux2(RegDst_ex, WrRegDest_ex, Rt_ex, Rd_ex)

    
    ##############################
    # EX/MEM
    ##############################

    BranchAdderO_mem = Signal(intbv(0, min=MIN, max=MAX))

    Zero_mem = Signal(intbv(0)[1:])
    

    Data2_mem =  Signal(intbv(0, min=MIN, max=MAX))

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

    DataMemOut_mem = Signal(intbv(0, min=MIN, max=MAX))
    
    #branch AND gate
    branch_and_gate = and_gate(Branch_mem, Zero_mem, PCSrc_mem)  
    
    #data memory
    data_memory_ = data_memory(Clk, AluResult_mem, Data2_mem, DataMemOut_mem, MemRead_mem, MemWrite_mem)

    
    ##############################
    # EX/WB
    ##############################
    
    #RegWrite_wb, on feedback signals section
    MemtoReg_wb = Signal(intbv(0)[1:])
    
    DataMemOut_wb = Signal(intbv(0, min=MIN, max=MAX))
    AluResult_wb = Signal(intbv(0, min=MIN, max=MAX))


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
    
    #mux2(sel, mux_out, chan1, chan2):

    mux_mem2reg_ = mux2(MemtoReg_wb, MuxMemO_wb, AluResult_wb, DataMemOut_wb)


    ##############################
    # Forwarding unit
    ##############################



    forwarding_ = forwarding(RegWrite_mem, WrRegDest_mem, Rs_ex, Rt_ex,     #inputs of EX hazards
                             RegWrite_wb, WrRegDest_wb,   #left inputs of MEM hazards
                             ForwardA, ForwardB
                            )
    
    
    ##############################
    # hazard detection unit
    ##############################
    


    if DEBUG:
        @always(Clk.posedge)
        def debug_internals():
            sep =  "\n" + "=" * 34 + " time %s " + "=" * 34 
            print sep % now()
            #IF
            print "\n" +  "." * 35 + " IF " + "." * 35 + "\n"
            print "PcAdderOut_if %i | BranchAdderO_mem %i | PCSrc_mem %i | NextIp %i | Ip %i"  % (PcAdderOut_if, BranchAdderO_mem, PCSrc_mem, NextIp, Ip)
            print 'Instruction_if %s (%i)' %  (bin(Instruction_if, 32), Instruction_if)

            if True: # now () > 2:

                #ID
                print "\n" + "." * 35 + " ID " + "." * 35 + "\n"
                print "PcAdderO_id %i | Instruction_id %s (%i) | Nop %i"  % (PcAdderOut_id, bin(Instruction_id, 32), Instruction_id, NopSignal )
                print 'Op %s | Rs %i | Rt %i | Rd %i | Func %i | Addr16 %i | Addr32 %i' % \
                        (bin(Opcode_id, 6), Rs_id, Rt_id, Rd_id, Func_id, Address16_id, Address32_id )
                
                print 'Data1 %i | Data2 %i' % (Data1_id, Data2_id)
                print '-->CONTROL'
                print 'RegDst %i  ALUop %s  ALUSrc %i | Branch %i  MemR %i  MemW %i |  RegW %i Mem2Reg %i ' % \
                        ( RegDst_id , bin(ALUop_id, 2), ALUSrc_id, Branch_id, MemRead_id, MemWrite_id, RegWrite_id, MemtoReg_id)

            if True: #if now () > 4:

                #EX
                print "\n" + "." * 35 + " EX " + "." * 35 + "\n"

                print "PcAdderO_ex %i | BranchAdderO_ex %i "  % (PcAdderOut_ex, BranchAdderO_ex)
                print "Rs %i | Rt %i | Rd %i | Func %i | Addr32 %i" % (Rs_ex, Rt_ex, Rd_ex, Func_ex, Address32_ex )
                
                print 'Data1_ex %i | Data2_ex %i' % (Data1_ex, Data2_ex)
                
                print 'ForwardA %i | ForwardB %i' % (ForwardA, ForwardB)
                print 'ForwMux1Out %i | ForwMux2Out %i' % (ForwMux1Out, ForwMux2Out)
                

                print '-->CONTROL'
                print 'RegDst %i  ALUop %s  ALUSrc %i | Branch %i  MemR %i  MemW %i |  RegW %i Mem2Reg %i ' % \
                        ( RegDst_ex , bin(ALUop_ex, 2), ALUSrc_ex, Branch_ex, MemRead_ex, MemWrite_ex, RegWrite_ex, MemtoReg_ex)
                
                print '--> ALU'
                print 'MuxAluDataSrc %i  | AluCtrl %s | AluResult_ex %i | Zero_ex %i'   % (MuxAluDataSrc_ex, bin(AluControl, 4), AluResult_ex, Zero_ex)
                print 'WrRegDest_ex %i' % WrRegDest_ex

            if True: #if now () > 6:
    
                #MEM
                print "\n" + "." * 35 + "MEM " + "." * 35 + "\n"
                print "BranchAdderO_mem %i "  % (BranchAdderO_mem)
                
                print '-->CONTROL'
                print 'Branch %i  MemR %i  MemW %i |  RegW %i Mem2Reg %i ' % \
                         ( Branch_mem, MemRead_mem, MemWrite_mem, RegWrite_mem, MemtoReg_mem)

                print '--> Branch'
                print 'Branch_mem %i Zero %i | PCSrc_mem %i' % (Branch_mem, Zero_mem, PCSrc_mem)

                print '--> Data mem'
                print 'AluResult_mem %i | Data2_mem %i | DataMemOut_mem %i | MemW %i MemR %i' \
                        % (AluResult_mem, Data2_mem, DataMemOut_mem, MemWrite_mem, MemRead_mem)

                print 'WrRegDest_mem %i' % WrRegDest_mem
            
            if True: #if now() > 8: 
                #WB
                print "\n" + "." * 35 + "WB" + "." * 35 + "\n"
                print 'CONTROL --> RegW %i Mem2Reg %i ' %  ( RegWrite_mem, MemtoReg_mem)
                
                print 'DataMemOut_wb %i | AluResult_wb %i | MuxMemO_wb %i ' % (DataMemOut_wb, AluResult_wb, MuxMemO_wb)
                print 'WrRegDest_wb %i | MuxMemO_wb %i' % (WrRegDest_wb, MuxMemO_wb)
            
            
                  

    return instances()



def testBench():


    if not DEBUG:
        datapath_i = traceSignals(dlx)  #() #toVHDL(datapath)
    else:
        datapath_i = dlx()

    

    return instances()



def main():
    sim = Simulation(testBench())
    sim.run(19)


if __name__ == '__main__':


    main()



