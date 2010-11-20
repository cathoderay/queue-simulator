import heapq


class EventHeap(list):
    def push(self, (time, event_type)):
        heapq.heappush(self, (time, event_type))
        
    def pop(self):
        return heapq.heappop(self)