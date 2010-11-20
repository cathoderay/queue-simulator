#!/usr/bin/python
# -*- coding:utf-8 -*-


from obj.simulator import *


if __name__ == "__main__":
    print "Starting simulation..."
    simulator = Simulator( entry_rate=0.45, warm_up=10000, sample_limit=100000, samples=5, service_policy=LCFS)
    simulator.start()
    simulator.report()
