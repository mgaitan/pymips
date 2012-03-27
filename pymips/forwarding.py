#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Forwarding Unit
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def forwarding(RegWrite_mem, Rd_mem, Rs_ex, Rt_ex,     #inputs of EX hazards
                RegWrite_wb, Rd_wb,   #left inputs of MEM hazards
                ForwardA, ForwardB
                ):
    """
    Detects and controls forwarding for 2 pairs of data hazard conditions:

        1a. Rd_mem = Rs_ex
        1b. Rd_mem = Rt_ex

        1a. Rd_wb = Rs_ex
        2b. Rd_wb = Rt_ex
    """

    @always_comb
    def hazards_control():

        #1a
        if RegWrite_mem == 1 and Rd_mem != 0 and Rd_mem == Rs_ex:
            ForwardA.next = 2  #int('10', 2)

        #2a
        elif RegWrite_wb == 1 and Rd_wb != 0 and Rd_mem != Rs_ex and Rd_wb == Rs_ex:
            ForwardA.next = 1 #int('01', 2)
        
        else:
            ForwardA.next = 0
            

        #1b
        if RegWrite_mem == 1 and Rd_mem != 0 and Rd_mem == Rt_ex:
            ForwardB.next = 2 #int('10', 2)

        #2b
        elif RegWrite_wb == 1 and Rd_wb != 0 and Rd_mem != Rt_ex and Rd_wb == Rt_ex:
            ForwardB.next = 1 #int('01', 2)
        
        else:
            ForwardB.next = 0

    return hazards_control



import unittest

class testBench(unittest.TestCase):



    def setUp(self):
        self.Rd_mem, self.Rs_ex, self.Rt_ex, self.Rd_wb = [ Signal(intbv(0)[5:]) for i in range(4) ] 

        self.RegWrite_mem, self.RegWrite_wb = [ Signal(intbv(0)[1:]) for i in range(2) ] 

        self.ForwardA, self.ForwardB = [ Signal(intbv(0)[2:]) for i in range(2) ] 

        self.forwarding_ = toVHDL(forwarding, self.RegWrite_mem, self.Rd_mem, self.Rs_ex, self.Rt_ex,   #inputs of EX hazards
                    self.RegWrite_wb, self.Rd_wb,   #left inputs of MEM hazards
                    self.ForwardA, self.ForwardB
                    )
    

    def test_not_regwrite_mem(self):
        @instance
        def test():
            self.RegWrite_mem.next = 0
            yield delay(1)
            self.assertEqual(int(self.ForwardA), 0)
            self.assertEqual(int(self.ForwardB), 0)

        
        sim = Simulation(self.forwarding_, test)
        sim.run()

    def test_not_regwrite_wb(self):
        @instance
        def test():
            self.RegWrite_wb.next = 0
            yield delay(1)
            self.assertEqual(int(self.ForwardA), 0)
            self.assertEqual(int(self.ForwardB), 0)

        sim = Simulation(self.forwarding_, test)
        sim.run()


    def test_1a(self):
        @instance
        def test():
        
            self.RegWrite_mem.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_mem.next = intbv(val)
            self.Rs_ex.next = intbv(val)

            yield delay(2)

            self.assertEqual(int(self.ForwardA), int('10',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()
        
    def test_1b(self):
        @instance
        def test():
        
            self.RegWrite_mem.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_mem.next = intbv(val)
            self.Rt_ex.next = intbv(val)

            yield delay(2)

            self.assertEqual(int(self.ForwardB), int('10',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()
        
    def test_2a(self):
        """RegWrite_wb == 1 and Rd_wb != 0 and Rd_mem != Rs_ex and Rd_wb == Rs_ex"""

        @instance
        def test():
        
            self.RegWrite_wb.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_wb.next = intbv(val)
            self.Rs_ex.next = intbv(val)

            self.Rd_mem.next = intbv(val + 1)

            yield delay(2)

            self.assertEqual(int(self.ForwardA), int('01',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()

    def test_2b(self):
        """elif RegWrite_wb == 1 and Rd_wb != 0 and Rd_mem != Rt_ex and Rd_wb == Rt_ex"""

        @instance
        def test():
        
            self.RegWrite_wb.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_wb.next = intbv(val)
            self.Rt_ex.next = intbv(val)

            self.Rd_mem.next = intbv(val + 1)

            yield delay(2)

            self.assertEqual(int(self.ForwardB), int('01',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()

            

def main():
    unittest.main()

if __name__ == '__main__':
    main()
    
