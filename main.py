# -*- coding:utf-8 -*-
# Main code
from obj.simulator import *

if __name__ == "__main__":
    simulator = Simulator(sample_seed=1230, entry_rate=0.45, service_policy=1, T=288000)
    import time
    before = time.time()
    simulator.start()
    after = time.time()
    print after - before
    simulator.report()
