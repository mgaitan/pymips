#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Latch between MEM and Write-Back stage 
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def latch_mem_wb(clk, rst, 
                 ram_in, 
                 alu_result_in, 
                 wr_reg_in, 
                 RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                 ram_out, 
                 alu_result_out, 
                 wr_reg_out, 
                 RegWrite_out, MemtoReg_out,     #signals to WB pipeline stage
                ):
    """
    Latch to control state between Execution and MEM pipeline stages

    """

    @always(clk.posedge, rst.posedge)

    def latch():
        if rst == 1:
            ram_out.next = 0
            alu_result_out.next = 0
            wr_reg_out.next = 0
            RegWrite_out.next = 0
            MemtoReg_out.next = 0
        else:
            ram_out.next = ram_in #.signed()
            alu_result_out.next = alu_result_in #.signed()
            wr_reg_out.next = wr_reg_in #.signed()
            RegWrite_out.next = RegWrite_in
            MemtoReg_out.next = MemtoReg_in

    return latch


def testBench():

    ram_in, alu_result_in, wr_reg_in = [Signal(intbv(random.randint(-255, 255), min=-(2**31), max=2**31-1)) for i in range(3)]
    ram_out, alu_result_out, wr_reg_out = [Signal(intbv(0, min=-(2**31), max=2**31-1)) for i in range(3)]

    RegWrite_in, MemtoReg_in = [Signal(intbv(0)[1:]) for i in range(2)]
    RegWrite_out, MemtoReg_out = [Signal(intbv(0)[1:]) for i in range(2)]

    clk = Signal(intbv(0)[1:])
    rst = Signal(intbv(0)[1:])
   
    latch_inst = toVHDL(latch_mem_wb, clk, rst,
                             ram_in, 
                             alu_result_in, 
                             wr_reg_in, 
                             RegWrite_in, MemtoReg_in,     #signals to WB pipeline stage
                             ram_out, 
                             alu_result_out, 
                             wr_reg_out, 
                             RegWrite_out, MemtoReg_out,     #signals to WB pipeline stage
                            )
    @instance
    def stimulus():
        for i in range(5):            

            if random.random() > 0.25:
                clk.next = 1
            if random.random() > 0.75:
                rst.next = 1
            
            ram_in.next, alu_result_in.next, wr_reg_in.next = [intbv(random.randint(-255, 255)) for i in range(3)]

            RegWrite_in.next , MemtoReg_in.next = [random.randint(0,1) for i in range(2)]

            yield delay(1)
            print "-" * 79
            print "%i %i %i |  %i  %i " % ( ram_in, alu_result_in, wr_reg_in,
                                            RegWrite_in, MemtoReg_in)
            print "clk: %i  rst: %i " % (clk, rst)

            print "%i %i %i |  %i  %i " % ( ram_out, alu_result_out, wr_reg_out,
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
    
