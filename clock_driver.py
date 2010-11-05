#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
a generic clock driver
"""


from myhdl import Signal, delay, always_comb, always, Simulation, \
                  intbv, bin, instance, instances, now, toVHDL




def clock_driver(clk, period=1):

    halfPeriod = delay(period)

    @always(halfPeriod)
    def drive_clock():
        clk.next = not clk

    return drive_clock
