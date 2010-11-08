#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Latch between ID and EX stage 
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def latch_id_ex(clk, rst, 
                pc_adder_in, 
                data1_in, data2_in, address32_in, 
                RegDst_in, ALUop_in, ALUSrc_in,     #signals to EX pipeline stage
                Branch_in, MemRead_in, MemWrite_in,  #signals to MEM pipeline stage
                RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                pc_adder_out, 
                data1_out, data2_out, address32_out,
                RegDst_out, ALUop_out, ALUSrc_out,     
                Branch_out, MemRead_out, MemWrite_out, 
                RegWrite_out, MemtoReg_out,     
                ):
    """
    Latch to control state between Instruction Decoding and Execution

    """

    @always(clk.posedge, rst.posedge)

    def latch():
        if rst == 1:
            pc_adder_out.next = 0
            data1_out.next = 0
            data2_out.next = 0
            address32_out.next = 0
            RegDst_out.next = 0
            ALUop_out.next = 0
            ALUSrc_out.next = 0
            Branch_out.next = 0
            MemRead_out.next = 0
            MemWrite_out.next = 0
            RegWrite_out.next = 0
            MemtoReg_out.next = 0
        else:
            pc_adder_out.next = pc_adder_in.signed()
            data1_out.next = data1_in.signed()
            data2_out.next = data2_in.signed()
            address32_out.next = address32_in.signed()
            RegDst_out.next = RegDst_in
            ALUop_out.next = ALUop_in
            ALUSrc_out.next = ALUSrc_in
            Branch_out.next = Branch_in
            MemRead_out.next = MemRead_in
            MemWrite_out.next = MemWrite_in
            RegWrite_out.next = RegWrite_in
            MemtoReg_out.next = MemtoReg_in

    return latch


def testBench():

    pc_adder_in, data1_in, data2_in, address32_in = [Signal(intbv(random.randint(-255, 255), min=-(2**31), max=2**31-1)) for i in range(4)]
    pc_adder_out, data1_out, data2_out, address32_out = [Signal(intbv(0, min=-(2**31), max=2**31-1)) for i in range(4)]

    RegDst_in, ALUop_in, ALUSrc_in = [Signal(intbv(0)[1:]) for i in range(3)]   
    Branch_in, MemRead_in, MemWrite_in = [Signal(intbv(0)[1:]) for i in range(3)] 
    RegWrite_in, MemtoReg_in = [Signal(intbv(0)[1:]) for i in range(2)]

    RegDst_out, ALUop_out, ALUSrc_out = [Signal(intbv(0)[1:]) for i in range(3)]   
    Branch_out, MemRead_out, MemWrite_out = [Signal(intbv(0)[1:]) for i in range(3)] 
    RegWrite_out, MemtoReg_out = [Signal(intbv(0)[1:]) for i in range(2)]

    clk = Signal(intbv(0)[1:])
    rst = Signal(intbv(0)[1:])
   
    latch_inst = toVHDL(latch_id_ex, clk, rst,
                                pc_adder_in, 
                                data1_in, data2_in, address32_in,
                                RegDst_in, ALUop_in, ALUSrc_in,     #signals to EX pipeline stage
                                Branch_in, MemRead_in, MemWrite_in,  #signals to MEM pipeline stage
                                RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                                pc_adder_out, 
                                data1_out, data2_out, address32_out,
                                RegDst_out, ALUop_out, ALUSrc_out,     
                                Branch_out, MemRead_out, MemWrite_out, 
                                RegWrite_out, MemtoReg_out)    

    @instance
    def stimulus():
        for i in range(5):            
            if random.random() > 0.25:
                clk.next = 1
            if random.random() > 0.75:
                rst.next = 1
            
            pc_adder_in.next, data1_in.next, data2_in.next, address32_in.next = [Signal(intbv(random.randint(-255, 255), min=-(2**31), max=2**31-1)) for i in range(4)]

            RegDst_in.next, ALUop_in.next, ALUSrc_in.next = [random.randint(0,1) for i in range(3)]
            Branch_in.next , MemRead_in.next , MemWrite_in.next  = [random.randint(0,1) for i in range(3)]
            RegWrite_in.next , MemtoReg_in.next = [random.randint(0,1) for i in range(2)]

            yield delay(1)
            print "-" * 79
            print "32bits  in  %i %i %i | 1bit inputs  %i  %i  %i  %i  %i  %i  %i  %i " % ( data1_in, data2_in, address32_in, RegDst_in, ALUop_in, ALUSrc_in,     
                                                                                                Branch_in, MemRead_in, MemWrite_in, 
                                                                                                RegWrite_in, MemtoReg_in)
            print "clk: %i  rst: %i " % (clk, rst)

            print "32bits out  %i %i %i | 1bit outputs  %i  %i  %i  %i  %i  %i  %i  %i " % ( data1_out, data2_out, address32_out, RegDst_out, ALUop_out, ALUSrc_out,     
                                                                                                Branch_out, MemRead_out, MemWrite_out, 
                                                                                                RegWrite_out, MemtoReg_out)

            clk.next = 0
            rst.next = 0
            yield delay(1)

    return instances()


def main():
    sim = Simulation(testBench())
    sim.run()



if __name__ == '__main__':
    main()
    
