#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Data Memory
"""

import random 

from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL



def data_memory(clk, address, write_data, read_data, memread, memwrite ):
    """
    Ports:

    clk -- trigger
    read_data -- data out
    write_data -- data in
    address -- address bus
    memwrite -- write enable: write if 1
    memread -- interface enable: read address if 1
    """    

    mem = [Signal(intbv(0, min=-(2**31), max=2**31-1)) for i in range(1024)]

    #mem[7] = Signal(intbv(51, min=-(2**31), max=2**31-1))      #usefull to test load instruction directly
    
    @always(clk.negedge)
    def logic():
        if memwrite == 1:
            mem[int(address)].next = write_data.val
    
        elif memread == 1:
            read_data.next = mem[int(address)]

        #print 'mem:', [int(i) for i in mem][0:20]

    return logic



def testBench():

    depth = 5

    address = Signal(intbv(0)[32:]) 

    data_in, data_out = [Signal( intbv(0, min=-(2**31),max=2**31-1)) for i in range(2)]

    clk = Signal(intbv(1)[1:])
    write_control = Signal(intbv(0)[1:])
    read_control = Signal(intbv(0)[1:])

    memory_i = data_memory(clk, address, data_in, data_out, read_control, write_control)

    addresses = [random.randint(0, 1024) for i in range(depth)]
    values = [random.randint(-(2**31), 2**31-1) for i in range(depth)]

    @instance
    def stimulus():

        #write
        for addr, val in zip(addresses, values):
            
            address.next = intbv( addr)[32:]
            data_in.next = intbv( val, min=-(2**31), max=2**31-1)
            
            write_control.next = 1
            clk.next = 0

            print "Write: addr %i = %d" % ( addr, val)
            yield delay(5)
            write_control.next = 0
            clk.next = 1
            yield delay(5)
        
        #read
        for addr in addresses:
            address.next = intbv( addr)[32:]
            read_control.next = 1
            clk.next = 0
            yield delay(5)
            print "Read: addr %i = %d" % (addr, data_out)
            clk.next = 1
            read_control.next = 0
            yield delay(5)
            
    return instances()


def main():
    sim = Simulation(testBench())
    sim.run()

if __name__ == '__main__':
    main()
