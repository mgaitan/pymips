#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Describe a digital system with 4 inputs (E3, E2, E1 y E0 --E0 is LSB --) 
and an output (S). S is ‘1’ when the BCD input corresponds to a prime number
"""

from myhdl import Signal, delay, always_comb, now, Simulation, \
                  intbv, bin, instance, toVHDL, toVerilog


def is_prime(n):
    """checks if n is a prime between 0 - 15 (4bits)"""

    return n in (2, 3, 5, 7, 11, 13) 
    #return False


def prime_detector(E, S):

    """ Prime detector. 

    E -- input intbv signal, binary encoded
    S -- output signal 
    
    S is '1' when B is a prime number
    """

    @always_comb
    def logic():
        if is_prime(E):
            S.next = 1
        else:
            S.next = 0
    return logic



def testBench():

    E = Signal(intbv(0, min=0, max=16))
    S = Signal(intbv(0, min=0, max=2))

    #pd_instance = prime_detector(E, S)
    pd_instance = toVHDL(prime_detector, E, S)

    @instance
    def stimulus():
        for i in range(16):
            E.next = intbv(i)
            yield delay(10)
            print "E: " + bin(E, 4) + " (" + str(E) + ") | S: " + bin(S, 1)

    return pd_instance, stimulus



def main():
    sim = Simulation(testBench())
    sim.run()


if __name__ == '__main__':
    main()
