#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
4-channel of 32 bits multiplexor
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, now


def ClkDriver(clk):

    halfPeriod = delay(10)

    @always(halfPeriod)
    def driveClk():
        clk.next = not clk

    return driveClk



def mux_4x32(clk, I0, I1, I2, I3, O, S):
    """
    clk : clock signal
    I0 - I3: 32 bits input vectors
    O: is the output vector
    S: is the channel selector
    """

    @always(clk.posedge)
    def route_channel():
        O.next = [I0, I1, I2, I3][int(S.val)]

    return route_channel


def testBench():

    clk = Signal(0)
    I0, I1, I2, I3 = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(4)]
    O = Signal(intbv(0)[32:])
    S = Signal(intbv(0, min=0, max=4))

    clkdriver_inst = ClkDriver(clk)
    mux_inst = mux_4x32(clk, I0, I1, I2, I3, O, S)

    @instance
    def stimulus():
        while True:
            S.next = Signal(intbv(random.randint(0, 4))[2:])
            I0.next, I1.next, I2.next, I3.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(4)]
            yield delay(5)

            print "time: %s | Clock: %i | Inputs: %i %i %i %i | S: %i | Output: %i" % (now(), clk, I0, I1, I2, I3, S, O)

    return clkdriver_inst, mux_inst, stimulus


def main():
    sim = Simulation(testBench())
    sim.run(100)



if __name__ == '__main__':
    main()
    
