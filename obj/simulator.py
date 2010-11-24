# -*- coding:utf-8 -*-
#Simulator object
import sys
import math
import numpy as np
from collections import deque
from util.constants import *
from util.progress_bar import ProgressBar
from util import estimator as est
from util import dist
from client import *
from event_heap import *


class Simulator:

    def __init__(self, entry_rate, warm_up, service_policy, clients, samples, server_rate=1.0):
        self.total_clients = warm_up + clients
        self.samples = samples
        self.server_rate = server_rate
        self.entry_rate = entry_rate
        self.warm_up = warm_up
        if service_policy == FCFS:
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_fcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_fcfs
            self.service_policy = 'First Come First Served (FCFS)'
        elif service_policy == LCFS:
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_lcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_lcfs
            self.service_policy = 'Last Come First Served (LCFS)'
        self.init_sample()
        self.sums = { 'm_s_W1': 0, 'm_s_s_W1': 0, 'v_s_W1': 0, 'v_s_s_W1': 0,            
                      'm_s_N1': 0, 'm_s_s_N1': 0, 'm_s_Nq1': 0, 'm_s_s_Nq1': 0,            
                      'm_s_T1': 0, 'm_s_s_T1': 0, 'm_s_W2': 0, 'm_s_s_W2': 0,            
                      'v_s_W2': 0, 'v_s_s_W2': 0, 'm_s_N2': 0, 'm_s_s_N2': 0,
                      'm_s_Nq2': 0, 'm_s_s_Nq2': 0, 'm_s_T2': 0, 'm_s_s_T2': 0 }
        self.results = {}
        
    def init_sample(self):
        self.queue1 = deque([])
        self.queue2 = deque([])
        self.server_current_client = None
        self.clients = []
        self.N_samples = { 'Nq_1': 0, 'N_1': 0, 'Nq_2': 0, 'N_2': 0 }
        self.warm_up_sample = self.warm_up
        self.t = 0.0
        self.previous_event_time = 0.0
        self.events = EventHeap()
        self.events.push((dist.exp_time(self.entry_rate), INCOMING))

    def process_event(self): 
        self.t, event_type = self.events.pop()

        if event_type == INCOMING:
            self.update_n()
            if self.warm_up_sample > 0:
                new_client = Client(TRANSIENT)
                self.warm_up_sample -= 1
            else:
                new_client = Client(EQUILIBRIUM)
            new_client.set_queue(1)
            new_client.set_arrival(self.t)
            self.queue1.append(new_client)
            self.clients.append(new_client)
            self.events.push((self.t + dist.exp_time(self.entry_rate), INCOMING))
            if not self.server_current_client:
                self.events.push((self.t, SERVER_1_IN))

        elif event_type == SERVER_1_IN:
            server_time = dist.exp_time(self.server_rate)
            self.server_current_client = self.pop_queue1()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            self.events.push((self.t + server_time, SERVER_OUT))        

        elif event_type == SERVER_2_IN:
            server_time = dist.exp_time(self.server_rate)
            self.server_current_client = self.pop_queue2()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            self.events.push((self.t + server_time, SERVER_OUT))                

        elif event_type == SERVER_OUT:
            self.update_n()
            if self.queue1:
                self.events.push((self.t, SERVER_1_IN))
            elif self.queue2 or self.server_current_client.queue == 1:
                self.events.push((self.t, SERVER_2_IN))
                
            if self.server_current_client.queue == 1:
                self.queue_2_in()
            else:
                self.server_current_client.set_served(1)
            self.server_current_client = None

    def queue_2_in(self):
        client = self.server_current_client
        self.queue2.append(client)
        client.set_queue(2)
        client.set_arrival(self.t)

    def update_n(self):
        delta = self.t - self.previous_event_time
        n1 = len(self.queue1)
        n2 = len(self.queue2)
        self.N_samples['Nq_1'] += n1*delta
        self.N_samples['Nq_2'] += n2*delta
        if self.server_current_client:
            if self.server_current_client.queue == 1:
                n1 += 1
            elif self.server_current_client.queue == 2:
                n2 += 1
        self.N_samples['N_1'] += n1*delta
        self.N_samples['N_2'] += n2*delta
        self.previous_event_time = self.t

    def discard_clients(self):
        """Descarta os clientes da fase transiente e os clientes que ainda estao no sistema. """
        served_clients = []
        for client in self.clients:
            if client.served and client.color == EQUILIBRIUM:
                served_clients.append(client)
        self.clients = served_clients
        
    def process_sample(self):
        s_wait_1 = 0; s_s_wait_1 = 0
        s_wait_2 = 0; s_s_wait_2 = 0
        s_server_1 = 0; s_server_2 = 0

        for client in self.clients:
            s_wait_1 += client.wait(1)
            s_s_wait_1 += client.wait(1)**2
            s_server_1 += client.server[1]
            s_wait_2 += client.wait(2)
            s_s_wait_2 += client.wait(2)**2
            s_server_2 += client.server[2]
            
        self.sums['m_s_W1'] += est.mean(s_wait_1, len(self.clients))
        self.sums['m_s_s_W1'] += est.mean(s_wait_1, len(self.clients))**2
        self.sums['v_s_W1'] += est.variance(s_wait_1, s_s_wait_1, len(self.clients))
        self.sums['v_s_s_W1'] += est.variance(s_wait_1, s_s_wait_1, len(self.clients))**2
        self.sums['m_s_N1'] += est.mean(self.N_samples['N_1'], self.t)
        self.sums['m_s_s_N1'] += est.mean(self.N_samples['N_1'], self.t)**2
        self.sums['m_s_Nq1'] += est.mean(self.N_samples['Nq_1'], self.t)
        self.sums['m_s_s_Nq1'] += est.mean(self.N_samples['Nq_1'], self.t)**2
        self.sums['m_s_T1'] += est.mean(s_wait_1, len(self.clients)) + est.mean(s_server_1, len(self.clients))
        self.sums['m_s_s_T1'] += (est.mean(s_wait_1, len(self.clients)) + est.mean(s_server_1, len(self.clients)))**2
        self.sums['m_s_W2'] += est.mean(s_wait_2, len(self.clients))
        self.sums['m_s_s_W2'] += est.mean(s_wait_2, len(self.clients))**2
        self.sums['v_s_W2'] += est.variance(s_wait_2, s_s_wait_2, len(self.clients))
        self.sums['v_s_s_W2'] += est.variance(s_wait_2, s_s_wait_2, len(self.clients))**2
        self.sums['m_s_N2'] += est.mean(self.N_samples['N_2'], self.t)
        self.sums['m_s_s_N2'] += est.mean(self.N_samples['N_2'], self.t)**2
        self.sums['m_s_Nq2'] += est.mean(self.N_samples['Nq_2'], self.t)
        self.sums['m_s_s_Nq2'] += est.mean(self.N_samples['Nq_2'], self.t)**2
        self.sums['m_s_T2'] += est.mean(s_wait_2, len(self.clients)) + est.mean(s_server_2, len(self.clients))
        self.sums['m_s_s_T2'] += (est.mean(s_wait_2, len(self.clients)) + est.mean(s_server_2, len(self.clients)))**2
        self.init_sample()

    def start(self):
        prog = ProgressBar(0, self.samples, 77, mode='fixed', char='#')
        print "Processando as amostras:"
        print prog, '\r',
        sys.stdout.flush()        
        for i in xrange(self.samples):
            while len(self.clients) < self.total_clients:
                self.process_event()
            self.discard_clients()
            self.process_sample()
            prog.increment_amount(1)
            print prog, '\r',
            sys.stdout.flush()
        print  
            
    def valid_confidence_interval(self):
        return (2.0*self.results['E[N1]']['c_i']  <= 0.1*self.results['E[N1]']['value']) and \
               (2.0*self.results['E[N2]']['c_i']  <= 0.1*self.results['E[N2]']['value']) and \
               (2.0*self.results['E[T1]']['c_i']  <= 0.1*self.results['E[T1]']['value']) and \
               (2.0*self.results['E[T2]']['c_i']  <= 0.1*self.results['E[T2]']['value']) and \
               (2.0*self.results['E[Nq1]']['c_i'] <= 0.1*self.results['E[Nq1]']['value']) and \
               (2.0*self.results['E[Nq2]']['c_i'] <= 0.1*self.results['E[Nq2]']['value']) and \
               (2.0*self.results['E[W1]']['c_i']  <= 0.1*self.results['E[W1]']['value']) and \
               (2.0*self.results['E[W2]']['c_i']  <= 0.1*self.results['E[W2]']['value']) and \
               (2.0*self.results['V(W1)']['c_i']  <= 0.1*self.results['V(W1)']['value']) and \
               (2.0*self.results['V(W2)']['c_i']  <= 0.1*self.results['V(W2)']['value'])

    def report(self):
        self.results = {
            'E[N1]'  : { 'value' : est.mean(self.sums['m_s_N1'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_N1'], self.sums['m_s_s_N1'], self.samples) },
            'E[N2]'  : { 'value' : est.mean(self.sums['m_s_N2'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_N2'], self.sums['m_s_s_N2'], self.samples) },
            'E[T1]'  : { 'value' : est.mean(self.sums['m_s_T1'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_T1'], self.sums['m_s_s_T1'], self.samples) },
            'E[T2]'  : { 'value' : est.mean(self.sums['m_s_T2'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_T2'], self.sums['m_s_s_T2'], self.samples) },
            'E[Nq1]' : { 'value' : est.mean(self.sums['m_s_Nq1'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_Nq1'], self.sums['m_s_s_Nq1'], self.samples) },
            'E[Nq2]' : { 'value' : est.mean(self.sums['m_s_Nq2'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_Nq2'], self.sums['m_s_s_Nq2'], self.samples) },
            'E[W1]'  : { 'value' : est.mean(self.sums['m_s_W1'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_W1'], self.sums['m_s_s_W1'], self.samples) },
            'E[W2]'  : { 'value' : est.mean(self.sums['m_s_W2'], self.samples), 'c_i' : est.confidence_interval(self.sums['m_s_W2'], self.sums['m_s_s_W2'], self.samples) },
            'V(W1)'  : { 'value' : est.mean(self.sums['v_s_W1'], self.samples), 'c_i' : est.confidence_interval(self.sums['v_s_W1'], self.sums['v_s_s_W1'], self.samples) },
            'V(W2)'  : { 'value' : est.mean(self.sums['v_s_W2'], self.samples), 'c_i' : est.confidence_interval(self.sums['v_s_W2'], self.sums['v_s_s_W2'], self.samples) }
        }

        if self.valid_confidence_interval():
            print "Intervalos de confiança estimados válidos!"
            print "Exibindo os resultados:"
            for key in self.results.keys():
                print key, ': ', self.results[key]['value'], ' - I.C: ', self.results[key]['c_i']
            return self.results
        else:
            print "Intervalos de confiança estimados inválidos. Aumente o numero de amostras ou de clientes por amostra."
            print "Programa terminando..."
            return None
    
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
