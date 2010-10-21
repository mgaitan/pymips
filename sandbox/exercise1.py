#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Describe a digital system with 4 inputs (E3, E2, E1 y E0 --E0 is LSB --) 
and an output (S). S is ‘1’ when the BCD input corresponds to a prime number
"""

from myhdl import Signal, delay, always_comb, now, Simulation, \
                  intbv, bin, instance, toVHDL, toVerilog



import re

pattern = r'^1?$|^(11+?)\1+$'
PRIME_ROM = tuple([0 if re.match(pattern, '1'*i) else 1 for i in range(16)])

#PRIME_ROM = (0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0)

def prime_detector(I, O):
    """ 
    Prime detector

    I -- input intbv signal, binary encoded
    O -- output signal 
    
    O is '1' when I is a prime number
    """

    @always_comb
    def logic():
            O.next = PRIME_ROM[int(I)]
    return logic



def testBench():

    I = Signal(intbv(0, min=0, max=16))
    O = Signal(intbv(0, min=0, max=2))
    

    #pd_instance = prime_detector(E, S)
    pd_instance = toVHDL(prime_detector, I, O)

    @instance
    def stimulus():
        for i in range(16):
            I.next = intbv(i)
            yield delay(10)
            print "I: " + bin(I, 4) + " (" + str(I) + ") | O: " + bin(O, 1)

    return pd_instance, stimulus



def main():
    sim = Simulation(testBench())
    sim.run()


if __name__ == '__main__':
    main()
