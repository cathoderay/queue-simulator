# -*- coding:utf-8 -*-
#Simulator object
from collections import deque
import new
from util import dist, seed, estimator
from client import *
from event import *
from node import *

FCFS = 1
LCFS = 2

class Simulator:
    def print_events(self):
        node = self.event_list_head
        while node:
            print node
            node = node.next
            
    def __init__(self, sample_seed, entry_rate, service_policy, samples, T=28800, server_rate=1):
        self.T = T
        self.samples = samples
        self.server_rate = server_rate
        self.entry_rate = entry_rate
        self.sample_seed = sample_seed
        if service_policy == FCFS:
            Simulator.__dict__['pop_queue1'] = new.instancemethod(Simulator.pop_queue1_fcfs, self, Simulator)
            Simulator.__dict__['pop_queue2'] = new.instancemethod(Simulator.pop_queue2_fcfs, self, Simulator)
            self.service_policy = 'First Come First Served (FCFS)'
        elif service_policy == LCFS:
            Simulator.__dict__['pop_queue1'] = new.instancemethod(Simulator.pop_queue1_lcfs, self, Simulator)
            Simulator.__dict__['pop_queue2'] = new.instancemethod(Simulator.pop_queue2_lcfs, self, Simulator)
            self.service_policy = 'Last Come First Served (LCFS)'
        self.init_sample()
        self.means = []
        self.variances = []

    def init_sample(self):
        seed.set_seed(self.sample_seed)    
        self.queue1 = deque([])
        self.queue2 = deque([])
        self.server_current_client = None
        self.clients = []
        self.t = 0
        self.event_list_head = Node(Event(INCOMING, dist.exp_time(self.entry_rate)))

    def generate_event(self, event_type, time):
        node = self.event_list_head
        new_node = Node(Event(event_type, time))
        while node:
            if not(node.next):
                node.next = new_node
                break
            elif (node.value.time <= new_node.value.time and node.next.value.time >= new_node.value.time):
                next_node = node.next
                node.next = new_node
                new_node.next = next_node
                break
            node = node.next

    def process_event(self):
        current_event = self.event_list_head.value
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
            server_time = dist.exp_time(self.server_rate)
            self.server_current_client = self.pop_queue1()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            self.generate_event(SERVER_OUT, self.t + server_time)

        elif current_event.event_type == SERVER_2_IN:
            server_time = dist.exp_time(self.server_rate)
            self.server_current_client = self.pop_queue2()
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
        self.event_list_head = self.event_list_head.next

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
        for i in xrange(self.samples):
            while self.t < self.T:
                self.process_event()
                self.remove_event()
            self.discard_remaining_clients()
            data = [[], [], [], []]
            for i in xrange(len(self.clients)):
                data[0].append(self.clients[i].wait(1))
                data[1].append(self.clients[i].server[1])
                data[2].append(self.clients[i].wait(2))
                data[3].append(self.clients[i].server[2])
            self.means.append([estimator.mean(data[0]), estimator.mean(data[1]),
                               estimator.mean(data[2]), estimator.mean(data[3])])
            self.variances.append([estimator.variance(data[0]), estimator.variance(data[1]),
                                   estimator.variance(data[2]), estimator.variance(data[3])])
            self.sample_seed += 1
            self.init_sample()

    def report(self):
        print "Politica de atendimento: ", self.service_policy
        print "Medias", self.means
        print "Variancias", self.variances
    
    @staticmethod
    def pop_queue1_fcfs(instance):
        return instance.queue1.popleft()
        
    @staticmethod
    def pop_queue2_fcfs(instance):
        return instance.queue2.popleft()
        
    @staticmethod
    def pop_queue1_lcfs(instance):
        return instance.queue1.pop()
        
    @staticmethod
    def pop_queue2_lcfs(instance):
        return instance.queue2.pop()
