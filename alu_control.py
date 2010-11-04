#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
ALU CONTROL
"""

import random

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def alu_control(aluop, funct_field, control_out):
    

    @always_comb
    def logic():
        if not aluop[0] and not aluop[1]:
            control_out.next = intbv('0010')

        elif aluop[0]:
            control_out.next = intbv('0110')

        elif aluop[1]:
           
            if bin(funct_field[3:], 4) == '0000':
                control_out.next = intbv('0010')
            
            elif bin(funct_field[3:], 4) == '0010':
                control_out.next = intbv('0110')
                
            elif bin(funct_field[3:], 4) == '0100':
                control_out.next = intbv('0000')
        
            elif bin(funct_field[3:], 4) == '0101':
                control_out.next = intbv('0001')
        
            elif bin(funct_field[3:], 4) == '1010':
                control_out.next = intbv('0111')

            else:
                control_out.next = intbv(0)
        #else:
        #    control_out.next = intbv(0)


    return logic


        
def testBench_alu_control():

    aluop_i = Signal(intbv(0)[2:])
    funct_field_i = Signal(intbv(0)[6:])
    alu_control_lines = Signal(intbv(0)[4:])

    alu_control_i = toVHDL(alu_control, aluop_i, funct_field_i, alu_control_lines)

    @instance
    def stimulus():
        for i in range(4):
            aluop_i.next = intbv(i)

            for j in range(2**6):

                funct_field_i.next = intbv(j)

                yield delay(10)
                print "aluop: %s | funct field: %s | alu_control_lines: %s" % (bin(aluop_i, 2), bin(funct_field_i, 6 ), bin(alu_control_lines, 4)) 
            
    return instances()



def main():
    #sim = Simulation(testBench_alu_control())
    sim = Simulation(testBench_alu_control())
    sim.run()

if __name__ == '__main__':
    main()
