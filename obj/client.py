class Client:
    def __init__(self, id):
        self.id = id
        #Times of the client in the system
        self.arrival = {}
        self.leave = {}
        self.server = {}
        #Number of clients in the queues
        self.N = {}
        self.Nq = {}
        self.queue = 0

    def set_arrival(self, arrival):
        self.arrival[self.queue] = arrival

    def set_leave(self, leave):
        self.leave[self.queue] = leave

    def set_server(self, server):
        self.server[self.queue] = server
        
    def set_N(self, N):
        self.N[self.queue] = N
        
    def set_Nq(self, Nq):
        self.Nq[self.queue] = Nq

    def set_queue(self, queue):
        self.queue = queue

    def wait(self, queue):
        return (self.leave[queue] - self.arrival[queue])
