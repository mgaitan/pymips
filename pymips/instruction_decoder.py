#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Instruction decoder
"""

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, now, toVHDL




def instruction_dec(instruction, opcode, rs, rt, rd, shamt, func, address, NopSignal=Signal(intbv(0)[1:]) ):
    """

    Decode segments of 32bits encoded instruction

    instruction: 32 bits 
    rs = Signal(intbv(0)[5:])       #instruction 25:21  - to read_reg_1
    rt = Signal(intbv(0)[5:])       #instruction 20:16  - to read_reg_2 and mux controlled by RegDst
    rd = Signal(intbv(0)[5:])       #instruction 15:11  - to the mux controlled by RegDst
    shamt = Signal(intbv(0)[5:])    #instruction 10:6   - 
    func = Signal(intbv(0)[6:])     #instruction 5:0    - to ALUCtrl
    address = Signal(intbv(0)[16:]) #instruction 15:0   - to Sign Extend
    
    """

    @always_comb
    def decode():
        opcode.next = instruction[32:26]
        rs.next = instruction[26:21]         #- to read_reg_1
        rt.next = instruction[21:16]         #- to read_reg_2 and mux controlled by RegDst
        rd.next = instruction[16:11]         #- to the mux controlled by RegDst
        shamt.next = instruction[11:6]   
        func.next = instruction[6:0]         #- to ALUCtrl
        address.next = instruction[16:0].signed()     #- to Sign Extend


        if instruction == 0:
            NopSignal.next = 1
        else: 
            NopSignal.next = 0

    return decode


def testBench():
    pass
    


def main():
    sim = Simulation(testBench())
    sim.run()



if __name__ == '__main__':
    main()
    
