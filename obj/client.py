TRANSIENT = 1
EQUILIBRIUM = 2

class Client:
    def __init__(self, id, color):
        self.id = id
        #Times of the client in the system
        self.arrival = {}
        self.leave = {}
        self.server = {}
        self.queue = 0
        self.color = color

    def set_arrival(self, arrival):
        self.arrival[self.queue] = arrival

    def set_leave(self, leave):
        self.leave[self.queue] = leave

    def set_server(self, server):
        self.server[self.queue] = server

    def set_queue(self, queue):
        self.queue = queue

    def wait(self, queue):
        return (self.leave[queue] - self.arrival[queue])
