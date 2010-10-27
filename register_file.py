#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Register file
"""

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, now


def register_file (read_reg1, read_reg2, write_reg, data_in, write_control, out_data1, out_data2, depth=16):

    mem = [Signal(intbv(0)[32:]) for i in range(depth)]
   
    @always_comb
    def logic():
        if write_control:
            mem[int(write_reg)].next = data_in
        else:
            out_data1.next = mem[int(read_reg1)]
            out_data2.next = mem[int(read_reg2)]

    return logic




def main():
    
    return 0

if __name__ == '__main__':
    main()
