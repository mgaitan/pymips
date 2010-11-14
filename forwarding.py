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



def testBench():

    
    Rd_ex, Rs_id, Rt_id, Rd_mem = [ Signal(intbv(0)[5:]) for i in range(4) ] 

    RegWrite_ex, RegWrite_mem = [ Signal(intbv(0)[1:]) for i in range(2) ] 

    ForwardA, ForwardB = [ Signal(intbv(0)[2:]) for i in range(2) ] 

    forwarding_ = toVHDL(forwarding, RegWrite_ex, Rd_ex, Rs_id, Rt_id,   #inputs of EX hazards
                RegWrite_mem, Rd_mem,   #left inputs of MEM hazards
                ForwardA, ForwardB
                )

    @instance
    def stimulus():
            print "RegW_ex %i | Rd_ex %i | Rs_id %i | Rt_id %i" % (RegWrite_ex, Rd_ex, Rs_id, Rt_id)
            print "RegW_mem %i | Rd_mem %i  %s " % (RegWrite_mem, Rd_mem, bin(ForwardA, 2))
            

            yield delay(1)

    return instances()


def main():
    sim = Simulation(testBench())
    sim.run()



if __name__ == '__main__':
    main()
    
