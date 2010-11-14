# -*- coding:utf-8 -*-
# Main code
from obj.simulator import *

if __name__ == "__main__":
    simulator = Simulator(sample_seed=10, entry_rate=0.1, service_policy=FCFS, T=28800)
    import time
    before = time.time()
    simulator.start()
    after = time.time()
    print after - before
    simulator.report()
