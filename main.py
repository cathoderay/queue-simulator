#!/usr/bin/python
# -*- coding:utf-8 -*-


from obj.simulator import *


if __name__ == "__main__":
    print "Starting simulation..."
    simulator = Simulator( entry_rate=0.1, warm_up=10000, sample_limit=100000, samples=4, service_policy=FCFS)
    simulator.start()
    simulator.report()
