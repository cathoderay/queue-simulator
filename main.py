#!/usr/bin/python
# -*- coding:utf-8 -*-

from obj.simulator import *
from obj.analytic import *


if __name__ == "__main__":
    print "Starting simulation..."
    simulator = Simulator(entry_rate=0.1, warm_up=50000, clients=50000, samples=50, service_policy=FCFS)
    simulator.start()    
    simulator.report()
    print "Starting analytic calculations..."
    analytic = Analytic(entry_rate=0.1, service_policy=FCFS)    
    analytic.start()
    analytic.report()