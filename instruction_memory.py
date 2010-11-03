#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Instruction memory
"""

from myhdl import Signal, delay, always_comb, now, Simulation, \
                  intbv, bin, instance, instances, toVHDL, toVerilog



ROM = [0] * 32
ROM[0:3] = [ int("01000000001000010000000000000001", 2),        #R1 = R1 + b'0001'
             int("01000000010000100000000000000011", 2),        #R2 = R2 + b'0011'
             int("00000000001000100100000000100000", 2),        #R3 = R1 + R2
              ]

ROM = tuple(ROM)

def instruction_memory(address, instruction):
    """ 
    address -- the pointer defined by PC 
    instruction -- 32 bit encoded instruction
    """
    
    @always_comb
    def logic():
            instruction.next = ROM[int(address)]
    return logic




def testBench():

    I = Signal(intbv(0, min=0, max=16))
    O = Signal(intbv(0)[32:])
    

    #pd_instance = prime_detector(E, S)
    im_instance = toVHDL(instruction_memory, I, O)

    @instance
    def stimulus():
        for i in range(8):
            I.next = intbv(i)
            yield delay(10)
            print "address: " + bin(I, 4) + " (" + str(I) + ") | instruction: " + bin(O, 32)

    return instances()



def main():
    sim = Simulation(testBench())
    sim.run()


if __name__ == '__main__':
    main()
