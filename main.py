#!/usr/bin/python
# -*- coding:utf-8 -*-

import time, sys, os, psyco
from obj.simulator import *
from obj.analytic import *
from obj.result_parser import *

# O psyco é um módulo que agiliza a execu
psyco.full()

if __name__ == "__main__":
    clients = input("Entre com o número de clientes que serão avaliados:")
    #dados de entrada (taxa de entrada e valor da fase transiente)
    entry_data = [[0.1, 30000], [0.2, 40000], [0.3, 80000], [0.4, 400000], [0.45, 500000]]
    service_policies = [
        { 'value' : FCFS, 'name' : "F.C.F.S (First Come First Served)" },
        { 'value' : LCFS, 'name' : "L.C.F.S (Last Come First Served)"  }
    ]
    
    # Dicionário que irá guardar os resultados adquiridos pelo simulador e pelo cálculo analítico
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
    
    # Loop que irá rodar o simulador para todos os casos requeridos
    for entry_datum in entry_data:
        entry_rate = entry_datum[0]
        warm_up = entry_datum[1]
        for service_policy in service_policies:
            print "taxa de entrada =", entry_rate
            print "tamanho da fase transiente =", warm_up
            print "política de atendimento =", service_policy['name']
            
            print "Iniciando simulação:"
            # Chamada e execução do simulador
            simulator = Simulator(entry_rate=entry_rate, warm_up=warm_up, clients=clients, service_policy=service_policy['value'])
            os.system("date")
            start = time.time()
            # Bind ao psyco para acelerar a execução da lógica do simulador
            psyco.bind(simulator.start)
            simulator.start()
            finish = time.time()
            print "Tempo total de execução :", (finish - start)
            results[service_policy['value']][2.0*entry_rate]['simulator'] = simulator.report()
                                            
            print "Iniciando cálculo analítico:"
            # Chamada e execução da classe que executa os cálculos analíticos
            analytic = Analytic(entry_rate=entry_rate, service_policy=service_policy['value'])
            analytic.start()
            results[service_policy['value']][2.0*entry_rate]['analytic'] = analytic.report()

    print "Gerando as tabelas com os resultados"
    # Chamada e execução da classe que formata os resultados encontrados em um arquivo html
    parsed_result = ResultParser(results)
    parsed_result.parse()
    parsed_result.write('resultados.html')
    print "Tabelas geradas com sucesso no arquivo 'resultados.html'.
    