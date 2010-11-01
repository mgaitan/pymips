#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Sign Extender
"""

import random

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL


def sign_extend(input16, output32):
    
    @always_comb
    def logic():
        output32.next = input16.val

    return logic


def testBench():

   
    data_in = Signal( intbv(0, min=-(2**15),max=2**15-1))

    data_out = Signal( intbv(0, min=-(2**31),max=2**31-1))

    sign_extend_i = toVHDL(sign_extend, data_in, data_out)
    
    @instance
    def stimulus():
        for i in range(32):
            value = random.randint(-(2**15), 2**15-1)
            data_in.next = intbv( value, min=-(2**15), max=2**15-1)
            
            print "In: %s (%i) | Out: %s (%i)" % (bin(data_in, 16), data_in, bin(data_out, 32), data_out)
            yield delay(5)
        
    return instances()


def main():
    #sim = Simulation(testBench_alu_control())
    sim = Simulation(testBench())
    sim.run()

if __name__ == '__main__':
    main()
