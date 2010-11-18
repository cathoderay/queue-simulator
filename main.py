#!/usr/bin/python
# -*- coding:utf-8 -*-


from obj.simulator import *


if __name__ == "__main__":
    print "Starting simulation..."
    simulator = Simulator(sample_seed=20, entry_rate=0.1, samples=10, service_policy=LCFS, T=2880)
    simulator.start()
    simulator.report()
