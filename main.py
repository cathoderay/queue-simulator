#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import sys
import os
import webbrowser
import psyco
from copy import copy
from obj.simulator import *
from obj.analytic import *
from obj.result_parser import *

psyco.full()

if __name__ == "__main__":
    clients = input("Entre com o número de clientes que serão avaliados:")
    #dados de entrada (taxa de entrada e valor da fase transiente)
    entry_data = [[0.1, 30000], [0.2, 40000], [0.3, 80000], [0.4, 400000], [0.45, 500000]]
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
            
            simulator = Simulator(entry_rate=entry_rate, warm_up=warm_up, clients=clients, service_policy=service_policy['value'])
            os.system("date")
            start = time.time()
            psyco.bind(simulator.start)
            simulator.start()
            finish = time.time()
            print "Tempo total de execução :", (finish - start)
            
            # O simulador retorna dois resultados em uma lista: 
            #      O dicionario com os estimadores calculados em [0];
            #      O numero de rodadas processadas em [1];
            simulator_results = simulator.report()
            results[service_policy['value']][2.0*entry_rate]['simulator'] = simulator_results[0]
            print "Número de rodadas :", simulator_results[1]
                                            
            print "Iniciando cálculo analítico:"
            analytic = Analytic(entry_rate=entry_rate, service_policy=service_policy['value'])
            analytic.start()
            results[service_policy['value']][2.0*entry_rate]['analytic'] = analytic.report()

    print "Gerando as tabelas com os resultados"
    parsed_result = ResultParser(results)
    parsed_result.parse()
    parsed_result.write('resultados.html')
    print "Tabelas geradas com sucesso no arquivo 'resultados.html'. Abrindo..."
    webbrowser.open('resultados.html')
    