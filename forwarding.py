#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Forwarding Unit
"""

import random


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def forwarding(RegWrite_ex, Rd_ex, Rs_id, Rt_id,     #inputs of EX hazards
                RegWrite_mem, Rd_mem,   #left inputs of MEM hazards
                ForwardA, ForwardB
                ):
    """
    Detects and controls forwarding for 2 pairs of hazard conditions:

        1a. EX/MEM.RegisterRd = ID/EX.RegisterRs 
        1b. EX/MEM.RegisterRd = ID/EX.RegisterRt

        2a. MEM/WB.RegisterRd = ID/EX.RegisterRs
        2b. MEM/WB.RegisterRd = ID/EX.RegisterRt
    """

    @always_comb
    def hazards_control():

        #1a
        if RegWrite_ex == 1 and Rd_ex != 0 and Rd_ex == Rs_id:
            ForwardA.next = 2  #int('10', 2)

        #2a
        elif RegWrite_mem == 1 and Rd_mem != 0 and Rd_ex != Rs_id and Rd_mem == Rs_id:
            ForwardA.next = 1 #int('01', 2)
        
        else:
            ForwardA.next = 0
            

        #1b
        if RegWrite_ex == 1 and Rd_ex != 0 and Rd_ex == Rt_id:
            ForwardB.next = 2 #int('10', 2)

        #2b
        elif RegWrite_mem == 1 and Rd_mem != 0 and Rd_ex != Rt_id and Rd_mem == Rt_id:
            ForwardB.next = 1 #int('01', 2)
        
        else:
            ForwardB.next = 0

    return hazards_control



import unittest

class testBench(unittest.TestCase):

    def setUp(self):
        self.Rd_ex, self.Rs_id, self.Rt_id, self.Rd_mem = [ Signal(intbv(0)[5:]) for i in range(4) ] 

        self.RegWrite_ex, self.RegWrite_mem = [ Signal(intbv(0)[1:]) for i in range(2) ] 

        self.ForwardA, self.ForwardB = [ Signal(intbv(0)[2:]) for i in range(2) ] 

        self.forwarding_ = toVHDL(forwarding, self.RegWrite_ex, self.Rd_ex, self.Rs_id, self.Rt_id,   #inputs of EX hazards
                    self.RegWrite_mem, self.Rd_mem,   #left inputs of MEM hazards
                    self.ForwardA, self.ForwardB
                    )
    

    def test_not_regwrite_ex(self):
        @instance
        def test():
            self.RegWrite_ex.next = 0
            yield delay(1)
            self.assertEqual(int(self.ForwardA), 0)
            self.assertEqual(int(self.ForwardB), 0)

        
        sim = Simulation(self.forwarding_, test)
        sim.run()

    def test_not_regwrite_mem(self):
        @instance
        def test():
            self.RegWrite_mem.next = 0
            yield delay(1)
            self.assertEqual(int(self.ForwardA), 0)
            self.assertEqual(int(self.ForwardB), 0)

        sim = Simulation(self.forwarding_, test)
        sim.run()


    def test_1a(self):
        @instance
        def test():
        
            self.RegWrite_ex.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_ex.next = intbv(val)
            self.Rs_id.next = intbv(val)

            yield delay(2)

            self.assertEqual(int(self.ForwardA), int('10',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()
        
    def test_1b(self):
        @instance
        def test():
        
            self.RegWrite_ex.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_ex.next = intbv(val)
            self.Rt_id.next = intbv(val)

            yield delay(2)

            self.assertEqual(int(self.ForwardB), int('10',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()
        
    def test_2a(self):
        """RegWrite_mem == 1 and Rd_mem != 0 and Rd_ex != Rs_id and Rd_mem == Rs_id"""

        @instance
        def test():
        
            self.RegWrite_mem.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_mem.next = intbv(val)
            self.Rs_id.next = intbv(val)

            self.Rd_ex.next = intbv(val + 1)

            yield delay(2)

            self.assertEqual(int(self.ForwardA), int('01',2))
            

        sim = Simulation(self.forwarding_, test)
        sim.run()

    def test_2b(self):
        """elif RegWrite_mem == 1 and Rd_mem != 0 and Rd_ex != Rt_id and Rd_mem == Rt_id"""

        @instance
        def test():
        
            self.RegWrite_mem.next = 1 

            val = random.randint(1, 2**5)

            self.Rd_mem.next = intbv(val)
            self.Rt_id.next = intbv(val)

            self.Rd_ex.next = intbv(val + 1)

            yield delay(2)

            self.assertEqual(int(self.ForwardB), int('01',2))
            

        sim = Simulation(self.forwarding_, test)
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
    
