#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
from copy import copy
from obj.simulator import *
from obj.analytic import *
from obj.result_parser import *


if __name__ == "__main__":
    warm_up = input("Entre com o número de clientes da fase transiente:")
    clients = input("Entre com o número de clientes que serão avaliados:")
    samples = input("Entre com o número total de rodadas:")
    entry_rates = [0.1, 0.2, 0.3, 0.4, 0.45]
    service_policies = [
        { 'value' : FCFS, 'name' : "F.C.F.S (First Come First Served)" },
        { 'value' : LCFS, 'name' : "L.C.F.S (Last Come First Served)"  }
    ]
    
    results = {
        FCFS : {
            0.2 : { 'simulator' : {}, 'analytic' : {} },
            0.4 : { 'simulator' : {}, 'analytic' : {} },
            0.6 : { 'simulator' : {}, 'analytic' : {} },
            0.8 : { 'simulator' : {}, 'analytic' : {} },
            0.9 : { 'simulator' : {}, 'analytic' : {} }
        },
        LCFS : {
            0.2 : { 'simulator' : {}, 'analytic' : {} },
            0.4 : { 'simulator' : {}, 'analytic' : {} },
            0.6 : { 'simulator' : {}, 'analytic' : {} },
            0.8 : { 'simulator' : {}, 'analytic' : {} },
            0.9 : { 'simulator' : {}, 'analytic' : {} }
        }        
    }
    
    for entry_rate in entry_rates:
        for service_policy in service_policies:
            print "taxa de entrada =", entry_rate
            print "política de atendimento =", service_policy['name']
            
            print "Iniciando simulação:"
            simulator = Simulator(entry_rate=entry_rate, warm_up=warm_up, clients=clients, samples=samples, service_policy=service_policy['value'])
            simulator.start()
            simulator_result = simulator.report()
            if simulator_result:
                results[service_policy['value']][2.0*entry_rate]['simulator'] = simulator_result
            else:
                sys.exit()
                            
            print "Iniciando cálculo analítico:"
            analytic = Analytic(entry_rate=entry_rate, service_policy=service_policy['value'])
            analytic.start()
            results[service_policy['value']][2.0*entry_rate]['analytic'] = analytic.report()

    print "Gerando as tabelas com os resultados"
    parsed_result = ResultParser(results)
    parsed_result.parse()
    parsed_result.write('resultados.html')
    print "Tabelas geradas com sucesso no arquivo 'resultados.html'"
    