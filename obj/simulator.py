# -*- coding:utf-8 -*-
#Simulator object
from collections import deque
from util import dist, seed, estimator, plot
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
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_fcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_fcfs
            self.service_policy = 'First Come First Served (FCFS)'
        elif service_policy == LCFS:
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_lcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_lcfs
            self.service_policy = 'Last Come First Served (LCFS)'
        self.init_sample()
        self.results = {
            'm_s_W1': 0,
            'm_s_s_W1': 0,
            'm_s_N1': 0,
            'm_s_Nq1': 0,
            'm_s_X1': 0,
            'm_s_W2': 0,
            'm_s_s_W2': 0,
            'm_s_N2': 0,
            'm_s_Nq2': 0,
            'm_s_X2': 0
        }
        
    def init_sample(self):
        seed.set_seed(self.sample_seed)    
        self.queue1 = deque([])
        self.queue2 = deque([])
        self.server_current_client = None
        self.clients = []
        self.N_samples = {
            'Nq_1': 0,
            'N_1': 0,
            'Nq_2': 0,
            'N_2': 0,
        }
        self.t = 0.0
        self.previous_event_time = 0.0
        self.event_list_head = Node(Event(INCOMING, dist.exp_time(self.entry_rate)))
        self.occupied_period = 0.0
        self.idle_period = 0.0
        self.utilization = []

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
            self.update_n()
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
            self.update_n()
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

    def update_n(self):
        delta = self.t - self.previous_event_time
        n1 = len(self.queue1)
        n2 = len(self.queue2)
        self.N_samples['Nq_1'] += n1*delta
        self.N_samples['Nq_2'] += n2*delta
        if self.server_current_client:
            self.occupied_period += delta
            if self.server_current_client.queue == 1:
                n1 += 1
            elif self.server_current_client.queue == 2:
                n2 += 1
        elif self.occupied_period > 0.0:
            self.utilization.append(self.occupied_period/(self.occupied_period + self.idle_period))
            self.occupied_period = 0.0
            self.idle_period = delta
        else:
            self.idle_period = delta
        self.N_samples['N_1'] += n1*delta
        self.N_samples['N_2'] += n2*delta
        self.previous_event_time = self.t

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

            wait_1 = []; server_1 = []
            wait_2 = []; server_2 = []

            for j in xrange(len(self.clients)):
                wait_1.append(self.clients[j].wait(1))
                server_1.append(self.clients[j].server[1])
                wait_2.append(self.clients[j].wait(2))
                server_2.append(self.clients[j].server[2])
            self.results['m_s_W1'] += estimator.sample_mean(wait_1)
            self.results['m_s_s_W1'] += estimator.sample_mean(wait_1)**2
            self.results['m_s_X1'] += estimator.sample_mean(server_1)
            self.results['m_s_W2'] += estimator.sample_mean(wait_2)
            self.results['m_s_s_W2'] += estimator.sample_mean(wait_2)**2
            self.results['m_s_X2'] += estimator.sample_mean(server_2)
            self.results['m_s_N1'] += self.N_samples['N_1']/self.t
            self.results['m_s_Nq1'] += self.N_samples['Nq_1']/self.t
            self.results['m_s_N2'] += self.N_samples['N_2']/self.t
            self.results['m_s_Nq2'] += self.N_samples['Nq_2']/self.t
            self.sample_seed += 1
            print len(self.clients)
            print "-"*34
            print len(wait_1)
            plot.plot(xrange(len(self.utilization)), self.utilization)
            self.init_sample()
            

    def report(self):
        print "Politica de atendimento: ", self.service_policy
        print "Rô calculado: ", (2*self.entry_rate)/self.server_rate
        print "E[N1]: ", estimator.mean(self.results['m_s_N1'], self.samples)
        print "E[N2]: ", estimator.mean(self.results['m_s_N2'], self.samples)
        print "E[T1]: ", (estimator.mean(self.results['m_s_W1'], self.samples) + estimator.mean(self.results['m_s_X1'], self.samples))
        print "E[T2]: ", (estimator.mean(self.results['m_s_W2'], self.samples) + estimator.mean(self.results['m_s_X2'], self.samples))
        print "E[Nq1]: ", estimator.mean(self.results['m_s_Nq1'], self.samples)
        print "E[Nq2]: ", estimator.mean(self.results['m_s_Nq2'], self.samples)
        print "E[W1]: ", estimator.mean(self.results['m_s_W1'], self.samples)
        print "E[W2]: ", estimator.mean(self.results['m_s_W2'], self.samples)
        print "V[W1]: ", estimator.variance(self.results['m_s_W1'], self.results['m_s_s_W1'], self.samples)
        print "V[W2]: ", estimator.variance(self.results['m_s_W2'], self.results['m_s_s_W2'], self.samples)
                 
    
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
