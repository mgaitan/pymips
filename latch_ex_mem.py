#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Latch between EX and MEM stage 
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def latch_ex_mem(clk, rst, 
                branch_adder_in, 
                alu_result_in, zero_in, 
                data2_in, wr_reg_in, 
                Branch_in, MemRead_in, MemWrite_in,  #signals to MEM pipeline stage
                RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                branch_adder_out, 
                alu_result_out, zero_out, 
                data2_out, wr_reg_out, 
                Branch_out, MemRead_out, MemWrite_out, 
                RegWrite_out, MemtoReg_out,     
                ):
    """
    Latch to control state between Execution and MEM pipeline stages

    """

    @always(clk.posedge, rst.posedge)

    def latch():
        if rst == 1:
            branch_adder_out.next = 0 
            alu_result_out.next = 0
            zero_out.next = 0
            data2_out.next = 0
            wr_reg_out.next = 0
            Branch_out.next = 0
            MemRead_out.next = 0
            MemWrite_out.next = 0
            RegWrite_out.next = 0
            MemtoReg_out.next = 0
        else:
            branch_adder_out.next = branch_adder_in.signed()
            alu_result_out.next = alu_result_in.signed()
            zero_out.next = zero_in
            data2_out.next = data2_in
            wr_reg_out.next = wr_reg_in.signed()

            Branch_out.next = Branch_in
            MemRead_out.next = MemRead_in
            MemWrite_out.next = MemWrite_in
            RegWrite_out.next = RegWrite_in
            MemtoReg_out.next = MemtoReg_in


    return latch


def testBench():

    branch_adder_in, alu_result_in, data2_in, wr_reg_in = [Signal(intbv(random.randint(-255, 255), min=-(2**31), max=2**31-1)) for i in range(4)]
    branch_adder_out, alu_result_out, data2_out, wr_reg_out = [Signal(intbv(0, min=-(2**31), max=2**31-1)) for i in range(4)]

    zero_in, zero_out = [Signal(intbv(0)[1:]) for i in range(2)]   
    
    Branch_in, MemRead_in, MemWrite_in = [Signal(intbv(0)[1:]) for i in range(3)] 
    RegWrite_in, MemtoReg_in = [Signal(intbv(0)[1:]) for i in range(2)]
    
    Branch_out, MemRead_out, MemWrite_out = [Signal(intbv(0)[1:]) for i in range(3)] 
    RegWrite_out, MemtoReg_out = [Signal(intbv(0)[1:]) for i in range(2)]

    clk = Signal(intbv(0)[1:])
    rst = Signal(intbv(0)[1:])
   
    latch_inst = toVHDL(latch_ex_mem, clk, rst, 
                                branch_adder_in, 
                                alu_result_in, zero_in, 
                                data2_in, wr_reg_in, 
                                Branch_in, MemRead_in, MemWrite_in,  #signals to MEM pipeline stage
                                RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                                branch_adder_out, 
                                alu_result_out, zero_out, 
                                data2_out, wr_reg_out, 
                                Branch_out, MemRead_out, MemWrite_out, 
                                RegWrite_out, MemtoReg_out,     
                                )

    @instance
    def stimulus():
        for i in range(5):            

            if random.random() > 0.25:
                clk.next = 1
            if random.random() > 0.75:
                rst.next = 1
            
            branch_adder_in.next, alu_result_in.next, data2_in.next, wr_reg_in.next = [intbv(random.randint(-255, 255)) for i in range(4)]

            Branch_in.next , MemRead_in.next , MemWrite_in.next, zero_in.next  = [random.randint(0,1) for i in range(4)]
            RegWrite_in.next , MemtoReg_in.next = [random.randint(0,1) for i in range(2)]

            yield delay(1)
            print "-" * 79
            print "%i %i %i %i | %i | %i  %i  %i  %i  %i " % ( branch_adder_in, alu_result_in, data2_in, wr_reg_in, zero_in, 
                                                                                                Branch_in, MemRead_in, MemWrite_in, 
                                                                                                RegWrite_in, MemtoReg_in)
            print "clk: %i  rst: %i " % (clk, rst)

            print "%i %i %i %i | %i | %i  %i  %i  %i  %i " % ( branch_adder_out, alu_result_out, data2_out, wr_reg_out, zero_out,   
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
    
