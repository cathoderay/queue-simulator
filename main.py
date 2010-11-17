#!/usr/bin/python
# -*- coding:utf-8 -*-


from obj.simulator import *


if __name__ == "__main__":
    print "Starting simulation..."
    simulator = Simulator(sample_seed=1, entry_rate=0.45, samples=100, service_policy=FCFS, T=100000)
    simulator.start()
    simulator.report()
