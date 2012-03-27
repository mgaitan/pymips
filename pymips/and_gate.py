#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
AND gate
"""

import random

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL

from myhdl.conversion import analyze


def and_gate(op1, op2, out):
    """
    op1: operator 1. 
    op2: operator 2. 
    out: and
    """

    @always_comb
    def logic():
        out.next = op1 & op2

    return logic


### TESTBENCHS

def testBench_gate():


    op1_i = Signal(intbv(0)[1:])
    op2_i = Signal(intbv(0)[1:])
    
    out_i = Signal(intbv(0)[1:])

    and_gate_i = toVHDL(and_gate, op1_i, op2_i, out_i)


    @instance
    def stimulus():
        for a in range(2):
            op1_i.next = a

            for b in range(2):
                op2_i.next = b

                yield delay(2)

                print "%i %i | %i " % (op1_i, op2_i, out_i) 
        
    return instances()


def main():
    #sim = Simulation(testBench_alu_control())
    sim = Simulation(testBench_gate())
    sim.run()

if __name__ == '__main__':
    main()
