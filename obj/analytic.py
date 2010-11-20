# Helper module to calculate analytic results
from util.constants import *


class Analytic:

    def __init__(self, entry_rate, service_policy, service_rate=1.0):
        self.entry_rate = entry_rate
        self.service_policy = service_policy
        self.service_rate = service_rate
        self.utilization = 2.0*(entry_rate/service_rate)
        self.X = 1.0/self.service_rate
        self.W_1 = 0.0
        self.W_2 = 0.0
        self.T_1 = 0.0
        self.T_2 = 0.0
        self.Nq_1 = 0.0
        self.Nq_2 = 0.0      
        self.N_1 = 0.0
        self.N_2 = 0.0
        self.V_1 = 0.0
    
    def start(self):
        self.W_1 = (self.utilization*self.X)/(1.0 - self.entry_rate*self.X)
        self.W_2 = (self.utilization*self.W_1 + 2.0*self.entry_rate*(self.service_rate**2))/(1.0 - self.utilization)
        self.T_1 = self.W_1 + self.X
        self.T_2 = self.W_2 + self.X
        self.Nq_1 = self.entry_rate*self.W_1
        self.Nq_2 = self.entry_rate*self.W_2
        self.N_1 = self.entry_rate*self.T_1
        self.N_2 = self.entry_rate*self.T_2
        if self.service_policy == FCFS:
            self.V_1 = (4.0*self.utilization)/(2.0 - self.utilization)
        elif self.service_policy == LCFS:
            self.V_1 = (4.0*self.entry_rate)*(self.entry_rate**2 - self.entry_rate + 1)/((1.0 - self.entry_rate)**3)
    
    def report(self):
        print "E[N1] analitico: ", self.N_1
        print "E[N2] analitico: ", self.N_2
        print "E[T1] analitico: ", self.T_1
        print "E[T2] analitico: ", self.T_2
        print "E[Nq1] analitico: ", self.Nq_1
        print "E[Nq2] analitico: ", self.Nq_2
        print "E[W1] analitico: ", self.W_1
        print "E[W2] analitico: ", self.W_2
        print "V[W1] analitico: ", self.V_1
    