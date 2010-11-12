SERVER_RATE = 1

class Simulator:
    def print_events(self):
        for event in self.events:
            print event

    def __init__(self, sample_seed, entry_rate, service_policy, T=1000000):
        self.queue1 = deque([])
        self.queue2 = deque([])
        self.server_current_client = None
        self.clients = []
        self.T = T
        self.t = 0
        self.sample_seed = seed.set_seed(sample_seed)
        self.entry_rate = entry_rate
        self.events = [Event(INCOMING, dist.exp_time(self.entry_rate))]
        self.service_policy = service_policy

    def reached_stop_condition(self):
        return self.t > self.T

    def generate_event(self, event_type, time):
        self.events.append(Event(event_type, time))
        self.events.sort(key=lambda event: event.time, reverse=True) #fod„o! =)

    def process_event(self):
        current_event = copy(self.events[-1])
        self.remove_event()
        self.t = current_event.time

        if current_event.event_type == INCOMING:
            new_client = Client(len(self.clients))
            new_client.set_queue(1)
            new_client.set_arrival(self.t)
            self.queue1.append(new_client)
            self.clients.append(new_client)
            self.generate_event(INCOMING, self.t + dist.exp_time(self.entry_rate))
            if not self.server_current_client:
                self.generate_event(SERVER_1_IN, self.t)

        elif current_event.event_type == SERVER_1_IN:
            server_time = dist.exp_time(SERVER_RATE)
            self.server_current_client = self.queue1.popleft()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            self.generate_event(SERVER_OUT, self.t + server_time)

        elif current_event.event_type == SERVER_2_IN:
            server_time = dist.exp_time(SERVER_RATE)
            self.server_current_client = self.queue2.popleft()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            self.generate_event(SERVER_OUT, self.t + server_time)

        elif current_event.event_type == QUEUE_2_IN:
            client = self.queue2[-1]
            client.set_queue(2)
            client.set_arrival(self.t)

        elif current_event.event_type == SERVER_OUT:
            if self.queue1:
                self.generate_event(SERVER_1_IN, self.t)
            elif self.queue2:
                self.generate_event(SERVER_2_IN, self.t)
            if self.server_current_client.queue == 1:
                self.queue2.append(self.server_current_client)
                self.generate_event(QUEUE_2_IN, self.t)
            self.server_current_client = None

    def remove_event(self):
        self.events.pop()

    def discard_remaining_clients(self):
        served_clients = []
        for client in self.clients:
            arrivals = client.arrival
            leaves = client.leave
            if  ((1 in arrivals and 2 in arrivals) and \
                (1 in leaves and 2 in leaves)):
                served_clients.append(client)
        self.clients = served_clients

    def start(self):
        while not self.reached_stop_condition():
            self.process_event()
        self.discard_remaining_clients()

    def report(self):
        print "Media dos tempos de espera na fila 1: ", estimator.mean([self.clients[i].wait(1) for i in range(len(self.clients))])
        print "Media dos tempos no servidor de clientes da fila 1: ", estimator.mean([self.clients[i].server[1] for i in range(len(self.clients))])
        print "Media dos tempos de espera na fila 2: ", estimator.mean([self.clients[i].wait(2) for i in range(len(self.clients))])
        print "Media dos tempos no servidor de clientes da fila 2: ", estimator.mean([self.clients[i].server[2] for i in range(len(self.clients))])
