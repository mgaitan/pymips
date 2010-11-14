#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
ALU
"""

import unittest
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
            print 'and'
            out_.next =  op1 & op2

        elif control == 1 : #int('0001',2):
            print 'or'
            out_.next =  op1 | op2

        elif control == 3 : #int('0010',2):
            print 'add'
            out_.next =  op1 + op2           #what happend if there is overflow ?
       
        elif control == 6 : # int('0110',2):
            'print sub'
            out_.next =  op1 - op2
            

        elif control == 7 : #int('0111',2):
            #TODO: set on less than
            'print <'
            out_.next = 0

        elif control == 12 : #int('1100', 2):
            'print nor'
            out_.next =  ~ (op1 | op2)   #TODO check this
    
        

    @always_comb
    def zero_detector():
        if out_ == 0:
            zero.next = 1
        else:
            zero.next = 0

    return logic_alu, zero_detector


### test

class TestALU(unittest.TestCase):

    def setUp(self):
        self.control_i = Signal(intbv(0)[4:])
        self.op1_i = Signal(intbv(0)[32:])
        self.op2_i = Signal(intbv(0)[32:])
        self.out_i = Signal(intbv(0,  min=-(2**31), max=2**31-1)) 
        self.zero_i = Signal(bool(False))

        self.alu_i = ALU(self.control_i, self.op1_i, self.op2_i, self.out_i, self.zero_i)

        #control_func = (('0000', 'AND'), ('0001', 'OR'),  ('0010', 'add'), ('0110', 'substract'), ('0111', 'set on <'), ('1100', 'NOR') )

    def testBench_add(self):

        def stimulus():
            
            a, b = self.op1_i.next, self.op2_i.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]

            self.control_i.next = intbv('0010')[4:] #add function
            expected = a + b
            yield delay(1)

            print self.out_i, self.op1_i, self.op2_i,  expected
            self.assertEqual(int(self.out_i), expected)
        
        sim = Simulation(self.alu_i, stimulus())
        sim.run()


def main():
    unittest.main()

if __name__ == '__main__':
    main()
