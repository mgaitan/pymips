#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Hazard detection Unit
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def hazard_detector(MemRead_ex, Rt_ex, 
                          Rs_id, Rt_id, 
                          Stall
                        ):
    """
    Stalls the pipeline when a instruction try to read a register 
    following a load instruction that writes the same register. 
    (raw data hazard)

    it controls the writing of PC and IF/ID registers plus a multiplexor
    that choose between the real control values or all 0s

    """

    @always_comb
    def logic():
        if MemRead_ex == 1  and (Rt_ex == Rs_id or Rt_ex == Rt_id):
            #stall the pipeline
            Stall.next = 1
        else: 
            #no hazard
            Stall.next = 0
            
        
    return logic



import unittest

class testBench(unittest.TestCase):

    def setUp(self):
        self.Rt_ex, self.Rs_id, self.Rt_id = [ Signal(intbv(0)[5:]) for i in range(3) ] 

        self.MemRead_ex, self.Stall = [ Signal(intbv(0)[1:]) for i in range(2) ] 

        
        self.detector_ = toVHDL( hazard_detector, self.MemRead_ex, self.Rt_ex, 
                                            self.Rs_id, self.Rt_id, 
                                            self.Stall
                                           )
    
    def test_not_mem_read(self):
        @instance
        def test():
            self.MemRead_ex.next = 0
            yield delay(1)
            self.assertEqual(int(self.Stall), 0)

        
        sim = Simulation(self.detector_, test)
        sim.run()

    def test_condition2(self):
        @instance
        def test():
            valueA, valueB = random.sample(range(32), 2)
        
            self.Rt_ex.next = valueA
            self.Rs_id.next = valueA

                    
            self.Rt_id.next = valueB     #rt_ex != rt_id


            self.MemRead_ex.next = 1

            yield delay(1)
            self.assertEqual(int(self.Stall), 1)
            

        sim = Simulation(self.detector_, test)
        sim.run()

    def test_condition2b(self):
        @instance
        def test():
            valueA, valueB = random.sample(range(32), 2)
        
            self.Rt_ex.next = valueA

            self.Rs_id.next = valueB
            self.Rt_id.next = valueB     #rt_ex != rt_id

            self.MemRead_ex.next = 1
            yield delay(1)
            self.assertEqual(int(self.Stall), 0)
            

        sim = Simulation(self.detector_, test)
        sim.run()



    def test_condition3(self):
        @instance
        def test():
            valueA, valueB = random.sample(range(32), 2)
        
            self.Rt_ex.next = valueA
        
            self.Rs_id.next = valueB     #rt_ex != rs_id

            self.Rt_id.next = valueA

            self.MemRead_ex.next = 1

            yield delay(1)
            self.assertEqual(int(self.Stall), 1)
            

        sim = Simulation(self.detector_, test)
        sim.run()



    def test_condition2_3(self):
        @instance
        def test():
            valueA, valueB = random.sample(range(32), 2)
        
            self.Rt_ex.next = valueA
        
            self.Rs_id.next = valueA

            self.Rt_id.next = valueA

            self.MemRead_ex.next = 1

            yield delay(1)
            self.assertEqual(int(self.Stall), 1)
            

        sim = Simulation(self.detector_, test)
        sim.run()


    def test_condition_not_2_nor_3(self):
        @instance
        def test():
            valueA, valueB, valueC = random.sample(range(32), 3)
        
            self.Rt_ex.next = valueA
        
            self.Rs_id.next = valueB

            self.Rt_id.next = valueC

            self.MemRead_ex.next = 1

            yield delay(1)
            self.assertEqual(int(self.Stall), 0)
            

        sim = Simulation(self.detector_, test)
        sim.run()



    
    def tearDown(self):
        #~ print "RegW_ex %i | Rd_ex %i | Rs_id %i | Rt_id %i" % (self.RegWrite_ex, self.Rd_ex, self.Rs_id, self.Rt_id)
        #~ print "RegW_mem %i | Rd_mem %i  " % (self.RegWrite_mem, self.Rd_mem)
        #~ print ""
        #~ print "ForwardA  %s | ForwardB  %s " % (bin(self.ForwardA, 2), bin(self.ForwardB, 2))
        pass

            

def main():
    unittest.main()

if __name__ == '__main__':
    main()
    
