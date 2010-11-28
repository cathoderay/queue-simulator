# -*- coding:utf-8 -*-
# Rotina que executa os testes de correção.

from obj.simulator import *


if __name__ == "__main__":
    print "Testando a correção do simulador..."
    entry_data = [[0.1, 30000], [0.2, 40000]]
    service_policies = [
        { 'value' : FCFS, 'name' : "F.C.F.S (First Come First Served)" },
        { 'value' : LCFS, 'name' : "L.C.F.S (Last Come First Served)"  }
    ]
    clients = 100000
    
    for entry_datum in entry_data:
        entry_rate = entry_datum[0]
        warm_up = entry_datum[1]
        for service_policy in service_policies:
            print "teste com taxa", entry_rate, ", tamanho de fase transiente igual a", warm_up, ",", clients, "clientes avaliados", \
                  "e política de atendimento", service_policy['name']
            simulator = Simulator(entry_rate=entry_rate, warm_up=warm_up, clients=clients, service_policy=service_policy['value'], test=True)
            simulator.start()
            simulator.report()