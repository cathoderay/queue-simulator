# Estrutura de dados para a lista de eventos do simulador


import heapq


class EventHeap(list):
    # Adicionar evento a lista
    def push(self, (time, event_type)):
        heapq.heappush(self, (time, event_type))

    # Remover evento da lista
    def pop(self):
        return heapq.heappop(self)