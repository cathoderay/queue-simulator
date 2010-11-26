#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import sys
from copy import copy
from obj.simulator import *
from obj.analytic import *
from obj.result_parser import *


if __name__ == "__main__":
    clients = input("Entre com o número de clientes que serão avaliados:")
    samples = input("Entre com o número total de rodadas:")
    #dados de entrada (taxa de entrada e valor da fase transiente)
    entry_data = [[0.1, 30000], [0.2, 40000], [0.3, 80000], [0.4, 600000], [0.45, 600000]]
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
    
    for entry_datum in entry_data:
        entry_rate = entry_datum[0]
        warm_up = entry_datum[1]
        for service_policy in service_policies:
            print "taxa de entrada =", entry_rate
            print "tamanho da fase transiente =", warm_up
            print "política de atendimento =", service_policy['name']
            
            print "Iniciando simulação:"
            
            simulator = Simulator(entry_rate=entry_rate, warm_up=warm_up, clients=clients, samples=samples, service_policy=service_policy['value'])
            start = time.time()
            simulator.start()
            finish = time.time()
            print finish - start
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
    