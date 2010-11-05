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
    A program counter that works as a latch. 

    clk : clock signal   . On posedge it refresh the output with it's internal state
    input: the input count
    output: address output
    """

    state = Signal(intbv(0)[32:])

    @always(clk.posedge)
    def up_out():        
        output.next = state.val

    @always(clk.negedge)
    def up_state():        
        state.next = input.val      #this should be done in a separate instance

    return up_out, up_state


def testBench():

    clk = Signal(intbv(0)[1:])
    i = Signal(intbv(0, min=0, max=32))
    o = Signal(intbv(0, min=0, max=32))

    clkdriver_inst = clock_driver(clk)
    pc_inst = program_counter( clk, i, o)

    alu_i = ALU( Signal('0010'), o, Signal(1), i, Signal(0))


    @instance
    def stimulus():
        while True:
            i.next = i + 1
            yield delay(1)
            print "time: %s | Clock: %i | in: %i | out: %i" % (now(), clk, i, o)

    return instances()


def main():
    tc = traceSignals(testBench)
    sim = Simulation(tc)
    sim.run(20)

if __name__ == '__main__':
    main()
    
