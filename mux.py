#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
2-channel of Generic-bits multiplexor
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, now, toVHDL




def mux2(sel, mux_out, chan1, chan2):
    """
    2-channels m-bits multiplexor

    channels: generic bits input vectors
    mux_out: is the output vector
    sel: is the channel selector
    """

    @always_comb
    def route_channel():
        if sel == 0:
            mux_out.next = chan1
        else:
            mux_out.next = chan2

    return route_channel


def mux4(sel, mux_out, chan1, chan2, chan3, chan4):
    """
    4-channels m-bits multiplexor

    channels: generic bits input vectors
    mux_out: is the output vector
    sel: is the channel selector
    """

    @always_comb
    def route_channel():
        if sel == 0:
            mux_out.next = chan1
        elif sel == 1:
            mux_out.next = chan2
        elif sel == 2:
            mux_out.next = chan3
        elif sel == 3:
            mux_out.next = chan4

    return route_channel



def testBench():

    I0, I1, I2, I3 = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(4)]
    O = Signal(intbv(0)[32:])
    S = Signal(intbv(0, min=0, max=4))
   
    mux_inst = toVHDL(mux2, S, O, I2, I3)
    #mux_inst = toVHDL(mux4, S, O, I0, I1, I2, I3)

    @instance
    def stimulus():
        while True:
            S.next = Signal(intbv(random.randint(0, 4))[2:])
            #I0.next , I1.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]
            I2.next, I3.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]
            #print "Inputs: %i %i %i %i | S: %i | Output: %i" % (I0, I1, I2, I3, S, O)
            print "Inputs: %i %i | S: %i | Output: %i" % (I2, I3, S, O)
            yield delay(5)

    return mux_inst, stimulus


def main():
    sim = Simulation(testBench())
    sim.run(100)



if __name__ == '__main__':
    main()
    
