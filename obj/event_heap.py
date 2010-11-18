import heapq


INCOMING = 1
SERVER_OUT = 2
SERVER_1_IN = 3
SERVER_2_IN = 4
QUEUE_2_IN = 5


class EventHeap(list):
    def push(self, (time, event_type)):
        heapq.heappush(self, (time, event_type))
        
    def pop(self):
        return heapq.heappop(self)