# -*- coding:utf-8 -*-
# Classe com os dados de um cliente que entra no sistema simulado.

class Client:
    def __init__(self, id, color):
        # Identificador do cliente, usada para o teste de correção.
        self.id = id
        # Tempo de chegada ao servidor (fila 1 e fila 2)
        self.arrival = {}
        # Tempo de saída do servidor (fila 1 e fila 2)
        self.leave = {}
        # Tempo no servidor (fila 1 e fila 2)
        self.server = {}
        # Indicador que diz qual fila o cliente está no momento
        self.queue = 0
        # Indicador que diz se o cliente já foi servido e saiu do sistema
        self.served = 0
        # Cor do cliente (TRANSIENT e EQUILIBRIUM)
        self.color = color

    def set_arrival(self, arrival):
        self.arrival[self.queue] = arrival

    def set_leave(self, leave):
        self.leave[self.queue] = leave

    def set_server(self, server):
        self.server[self.queue] = server

    def set_queue(self, queue):
        self.queue = queue
        
    def set_served(self, served):
        self.served = served

    # Tempo de espera na fila = Tempo de saída da fila para o servidor - Tempo de chegada na fila.
    def wait(self, queue):
        return (self.leave[queue] - self.arrival[queue])
