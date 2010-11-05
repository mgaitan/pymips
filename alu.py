#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
ALU
"""

import random

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL

from myhdl.conversion import analyze


def ALU(control, op1, op2, out_, zero):
    """
    control : 4 bit control/selector vector.
    op1: operator 1. 32bits
    op2: operator 2. 32bits
    out: ALU result. 32bits
    zero: zero detector. ``1`` when out is 0. 

    =============  =======================
     ALU control    Function
    =============  =======================
     0000           AND
     0001           OR
     0010           add
     0110           substract
     0111           set on less than
     1100           NOR
    =============  =======================

    """

    

    @always_comb
    def logic_alu():
        if control == 0: #int('0000',2):
            out_.next =  op1 & op2

        elif control == 1 : #int('0001',2):
            out_.next =  op1 | op2

        elif control == 2 : #int('0010',2):
            out_.next =  op1 + op2           #what happend if there is overflow ?
       
        elif control == 6 : # int('0110',2):
            out_.next =  op1 - op2
            

        elif control == 0b0111 : #int('0111',2):
            
            out_.next = op1 < op2

        elif control == 12 : #int('1100', 2):
            out_.next =  ~ (op1 | op2)   #TODO check this
    

    @always_comb
    def zero_detector():
        if out_ == 0:
            zero.next = 1
        else:
            zero.next = 0

    return logic_alu, zero_detector


### TESTBENCHS

def testBench_alu():

    control_i = Signal(intbv(0)[4:])

    op1_i = Signal(intbv(0)[32:])
    op2_i = Signal(intbv(0)[32:])
    
    out_i = Signal(intbv(0,  min=-(2**31), max=2**31-1)) 

    zero_i = Signal(bool(False))
    
    #alu_i = alu(control_i, op1_i, op2_i, out_i, zero_i)
    alu_i = toVHDL(ALU, control_i, op1_i, op2_i, out_i, zero_i)
    #alu_i = analyze(alu, control_i, op1_i, op2_i, out_i, zero_i)

    control_func = (('0000', 'AND'), ('0001', 'OR'),  ('0010', 'add'), ('0110', 'substract'), ('0111', '<'), ('1100', 'NOR') )

    @instance
    def stimulus():
        for control_val, func in [(int(b, 2), func) for (b,func) in control_func]:
            control_i.next = Signal(intbv(control_val))

            op1_i.next, op2_i.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]
            
            yield delay(10)
            print "Control: %s | %i %s %i | %i | z=%i" % (bin(control_i, 4), op1_i, func, op2_i, out_i, zero_i) 
        
    return instances()


def main():
    #sim = Simulation(testBench_alu_control())
    sim = Simulation(testBench_alu())
    sim.run()

if __name__ == '__main__':
    main()
