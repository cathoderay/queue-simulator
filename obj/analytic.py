# -*- coding:utf-8 -*-
# Classe que realiza os cálculos analíticos dos valores a serem estimados, para comparação.


from util.constants import *


class Analytic:

    def __init__(self, entry_rate, service_policy, service_rate=1.0):
        self.entry_rate = entry_rate
        self.service_policy = service_policy
        self.service_rate = service_rate
        self.utilization = 2.0*(entry_rate/service_rate)
        self.X = 1.0/self.service_rate
        self.results = { 'E[W1]'  : 0.0, 'E[W2]'  : 0.0, 'E[T1]'  : 0.0, 'E[T2]'  : 0.0,
                         'E[Nq1]' : 0.0, 'E[Nq2]' : 0.0, 'E[N1]'  : 0.0, 'E[N2]'  : 0.0,
                         'V(W1)'  : 0.0, 'V(W2)'  : 'X' }
    
    # Método que define os valores de forma analítica.
    def start(self):
        self.results['E[W1]']  = (self.utilization*self.X)/(1.0 - self.entry_rate*self.X)
        self.results['E[W2]']  = (self.utilization*self.results['E[W1]'] + 2.0*self.entry_rate*(self.service_rate**2))/(1.0 - self.utilization)
        self.results['E[T1]']  = self.results['E[W1]'] + self.X
        self.results['E[T2]']  = self.results['E[W2]'] + self.X
        self.results['E[Nq1]'] = self.entry_rate*self.results['E[W1]']
        self.results['E[Nq2]'] = self.entry_rate*self.results['E[W2]']
        self.results['E[N1]']  = self.entry_rate*self.results['E[T1]']
        self.results['E[N2]']  = self.entry_rate*self.results['E[T2]']
        if self.service_policy == FCFS:
            self.results['V(W1)'] = (4.0*self.utilization)/(2.0 - self.utilization)
        elif self.service_policy == LCFS:
            self.results['V(W1)'] = (4.0*self.entry_rate)*(self.entry_rate**2 - self.entry_rate + 1)/((1.0 - self.entry_rate)**3)
    
    # Método que exibe os resultados encontrados e os retorna.
    def report(self):
        print "Exibindo os resultados analíticos: "
        for key in self.results.keys():
            print key, ': ', self.results[key]
        
        return self.results;
    