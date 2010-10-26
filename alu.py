#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


"""
ALU
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
        else:
            control_out.next = intbv(0)


    return logic


def alu(control, op1, op2, out_, zero):
    """
    control : 4 bit control vector.
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
    def logic():
        aux = intbv(0)[32:].signed()
    
        if control == int('0000',2):
            aux =  op1 & op2

        elif control == int('0001',2):
            aux =  op1 | op2

        elif control == int('0010',2):
            aux =  op1 + op2           #what happend if there is overflow ?
       
        elif control == int('0110',2):
            aux =  op1 - op2
            

        elif control == int('0111',2):
            #TODO: set on less than
            pass
        elif bin(control, 4) == '1100':
            aux =  ~ (op1 | op2)   #TODO check this
           

        if aux == 0:
            zero.next = 1
        else:
            zero.next = 0

        out_.next = aux

    return logic




def testBench_alu():

    control_i = Signal(intbv(0)[4:])

    op1_i = Signal(intbv(0)[32:])
    op2_i = Signal(intbv(0)[32:])
    
    out_i = Signal(intbv(0)[32:].signed()) 

    zero_i = Signal(bool(False))
    
    alu_i = alu(control_i, op1_i, op2_i, out_i, zero_i)

    control_func = (('0000', 'AND'), ('0001', 'OR'),  ('0010', 'add'), ('0110', 'substract'), ('0111', 'set on <'), ('1100', 'NOR') )

    @instance
    def stimulus():
        for control_val, func in [(int(b, 2), func) for (b,func) in control_func]:
            control_i.next = Signal(intbv(control_val))

            op1_i.next, op2_i.next = [Signal(intbv(random.randint(0, 255))[32:]) for i in range(2)]
            
            yield delay(10)
            print "Control: %s | %i %s %i | %i | z=%i" % (bin(control_i, 4), op1_i, func, op2_i, out_i, zero_i) 
        
    return instances()
        
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
    sim = Simulation(testBench_alu())
    sim.run()

if __name__ == '__main__':
    main()
