#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Program counter
"""


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL, traceSignals

from clock_driver import clock_driver

from alu import ALU

def program_counter(clk, input, output):
    """

    clk : clock signal   . On posedge it refresh the output with it's internal state
    input: the input count
    output: address output
    """

    @always(clk.posedge)
    def update():        
        output.next = input

    return update


def pc_testbench():

    clk = Signal(intbv(0)[1:])
    i = Signal(intbv(0, min=0, max=32))
    o = Signal(intbv(0, min=0, max=32))

    clkdriver_inst = clock_driver(clk)
    pc_inst = program_counter( clk, i, o)
    
    
    
    c = Signal(0b0010)
    alu_i = ALU( c, o, Signal(1), i, Signal(0))


    @instance
    def stimulus():
        while True:
            yield delay(1)
            print "time: %s | Clock: %i | in: %i | out: %i" % (now(), clk, i, o)

    return instances()


def main():
    tc =  traceSignals(pc_testbench)
    sim = Simulation(tc)
    sim.run(20)

if __name__ == '__main__':
    main()
    
