#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Datapath
"""

from myhdl import Signal, delay, always, always_comb, now, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL


from program_counter import ClkDriver, program_counter
from instruction_memory import instruction_memory
from alu import ALU
from alu_control import alu_control
from control import control
from register_file import register_file
from sign_extender import sign_extend


DEBUG = True  #set to false to convert 


def datapath(clk, reset=Signal(intbv(0)[1:]), zero=Signal(intbv(0)[1:])):


    #
    #   internal signals
    #

    ip = Signal(intbv(0)[16:] ) #connect PC with intruction_memory
    instruction = Signal(intbv(0)[32:])   #32 bits instruction line.

    #control signals
    signal_1bit = [Signal(intbv(0)[1:]) for i in range(7)]
    RegDst, ALUSrc, MemtoReg, RegWrite, MemRead, MemWrite, Branch = signal_1bit     
    
    #ALUop connect Control with ALUcontrol
    ALUop = Signal(intbv(0)[2:])  

    #intruction memory output connectors
    opcode = Signal(intbv(0)[6:])   #instruction 31:26  - to Control
    rs = Signal(intbv(0)[4:])       #instruction 25:21  - to read_reg_1
    rt = Signal(intbv(0)[4:])       #instruction 20:16  - to read_reg_2 and mux controlled by RegDst
    rd = Signal(intbv(0)[4:])       #instruction 15:11  - to the mux controlled by RegDst
    shamt = Signal(intbv(0)[4:])    #instruction 10:6   - 
    func = Signal(intbv(0)[6:])     #instruction 5:0    - to ALUCtrl
    address = Signal(intbv(0)[16:]) #instruction 15:0   - to Sign Extend

    address32 = Signal(intbv(0)[32:]) #output of signextend

    #register file data vectors (input and outputs)
    data_in, data1, data2 = [Signal( intbv(0, min=-(2**31),max=2**31-1)) for i in range(3)]

    #ALU
    alu_control_out = Signal(intbv(0)[4:])
    alu_out = Signal(intbv(0,  min=-(2**31), max=2**31-1)) 
    zero = Signal(bool(False))

    #

    #
    # component instances
    #
    pc = program_counter(clk, ip)
    im = instruction_memory (ip, instruction)
    register_file_i = register_file(rs, rt, rd, data_in, RegWrite, data1, data2, depth=8)
    
    sign_extend_i = sign_extend(address, address32)

    alu_control_i = alu_control(ALUop, func, alu_control_out)

    alu_i = ALU(alu_control_out, data1, data2, alu_out, zero)


    control_i = control(opcode, RegDst, Branch, MemRead, MemtoReg, ALUop, MemWrite, ALUSrc, RegWrite)

    
    


    @always_comb
    def instruction_change():
        opcode.next = instruction[32:26]
        rs.next = instruction[26:21]    #- to read_reg_1
        rt.next = instruction[21:16]         #- to read_reg_2 and mux controlled by RegDst
        rd.next = instruction[16:11]         #- to the mux controlled by RegDst
        shamt.next = instruction[11:6]   
        func.next = instruction[6:0]         #- to ALUCtrl
        address.next = instruction[16:0]     #- to Sign Extend


    if DEBUG:
        @always(clk.posedge)
        def debug_internals():
            print "-" * 78
            print "time: %s | Clock: %i | ip: %i" % (now(), clk, ip)
            print 'instruction', bin(instruction, 32) 

            print 'opcode: %s | rs: %i | rt: %i | rd: %i | data1: %i | data2: %i' % \
                  (bin(opcode, 6), rs, rt, rd, data1, data2)

            print 'Control lines:', RegDst, ALUSrc, MemtoReg, RegWrite, MemRead, MemWrite, Branch, bin(ALUop, 2)
        
            print 'func: %s | aluop: %s | alu_c_out: %s' % ( bin(func, 5), 
                                                            bin(ALUop, 2), 
                                                            bin(alu_control_out, 4) )

            print 'ALU_out: %i | Zero: %i' % (alu_out, zero)

            
            

    return instances()



def testBench():

    clk = Signal(intbv(0)[1:])
    clkdriver_inst = ClkDriver(clk)


    if not DEBUG:
        datapath_i = toVHDL(datapath, clk)
    else:
        datapath_i = datapath(clk)

    

    return instances()



def main():
    sim = Simulation(testBench())
    sim.run(50)


if __name__ == '__main__':
    main()
