# -*- coding:utf-8 -*-
# Classe que contém toda a lógica do simulador de filas.


import sys, random, math
from collections import deque
from util.constants import *
from util.progress_bar import ProgressBar
from util import estimator as est
from util import dist
from client import *
from event_heap import *


class Simulator:

    # Inicialização do simulador
    def __init__(self, entry_rate, warm_up, service_policy, clients, server_rate=1.0, test=False):
        # Número total de clientes = fase transiente + clientes a serem avaliados 
        self.total_clients = warm_up + clients
        self.samples = 1
        self.server_rate = server_rate
        self.entry_rate = entry_rate
        self.warm_up = warm_up
        # Definido aqui o método a ser utilizado para retirar os clientes da fila e coloca-los no servidor,
        # dependendo da política de atendimento usada.
        if service_policy == FCFS:
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_fcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_fcfs
            self.service_policy = 'First Come First Served (FCFS)'
        elif service_policy == LCFS:
            Simulator.__dict__['pop_queue1'] = Simulator.pop_queue1_lcfs
            Simulator.__dict__['pop_queue2'] = Simulator.pop_queue2_lcfs
            self.service_policy = 'Last Come First Served (LCFS)'
        self.init_sample()
        # Define o dicionário que irá guardar a soma e a soma dos quadrados das médias e variâncias estimadas a cada rodada.
        self.sums = { 'm_s_W1': 0, 'm_s_s_W1': 0, 'v_s_W1': 0, 'v_s_s_W1': 0,            
                      'm_s_N1': 0, 'm_s_s_N1': 0, 'm_s_Nq1': 0, 'm_s_s_Nq1': 0,            
                      'm_s_T1': 0, 'm_s_s_T1': 0, 'm_s_W2': 0, 'm_s_s_W2': 0,            
                      'v_s_W2': 0, 'v_s_s_W2': 0, 'm_s_N2': 0, 'm_s_s_N2': 0,
                      'm_s_Nq2': 0, 'm_s_s_Nq2': 0, 'm_s_T2': 0, 'm_s_s_T2': 0 }
        # Dicionário que irá guardar os resultados de cada estimador calculados pelo simulador.
        self.results = {}
        # Define a lista com os clientes que serão testados, caso o simulador esteja em modo de teste.
        self.test = test
        self.test_list = []
        if self.test:
            self.init_test()
    
    # Inicializa as estruturas de dados para cada rodada
    def init_sample(self):
        # Filas do sistema.
        self.queue1 = deque([])
        self.queue2 = deque([])
        # Cliente que está no servidor ( Quando esta variável for nula significa que o servidor está ocioso )
        self.server_current_client = None
        # Lista dos clientes que entraram no sistema durante a rodada.
        self.clients = []
        # Dicionário com a soma das variáveis que indicam o número de pessoas nas filas (N) e em espera (Nq)
        self.N_samples = { 'Nq_1': 0, 'N_1': 0, 'Nq_2': 0, 'N_2': 0 }
        self.warm_up_sample = self.warm_up
        # Tempo do simulador.
        self.t = 0.0
        # Tempo do evento anterior ao que está sendo processado.
        self.previous_event_time = 0.0
        # Lista de eventos.
        self.events = EventHeap()
        # Inicializa o simulador com o evento de chegada do primeiro cliente ao sistema.
        self.events.push((dist.exp_time(self.entry_rate), INCOMING))
    
    # Inicia o simulador
    def start(self):
        # Inicializa a barra usada para medir o progresso do simulador
        # Ela é contabilizada de acordo com o valor do menor intervalo de confiança encontrado a cada rodada,
        # Chegando a 100% quando o intervalo chega a 10% da média do estimador
        # Mostrada quando o simulador não está definido na forma de teste
        if not(self.test):
            prog = ProgressBar(0, 0.9, 77, mode='fixed', char='#')
            print "Processando as rodadas:"
            print prog, '\r',
            sys.stdout.flush()
        
        # Loop principal do simulador.
        # Termina quando todos os intervalos de confiança forem menores que 10% da média do estimador.
        while not(self.valid_confidence_interval()):
            # Loop de cada rodada, processa um evento a cada iteração.
            while len(self.clients) <= self.total_clients:
                self.process_event()
            self.discard_clients()
            # Processa os dados gerados por uma rodada.
            self.process_sample()
            if self.samples > 1:
                self.calc_results()
                prog.update_amount(max(prog.amount, self.pb_amount()))
                print prog, '\r',
            self.samples += 1
            sys.stdout.flush()
            # Linha para forçar o teste a executar apenas 1 rodada.
            if self.test:
                break
        print
    
    # Método que processa um evento
    def process_event(self):
        # Remove um evento da lista para ser processado e atualiza o tempo do simulador
        self.t, event_type = self.events.pop()

        # Evento do tipo: Chegada ao sistema.
        if event_type == INCOMING:
            self.update_n()
            # Define a cor do cliente, verificando se ele chegou durante a fase transiente ou não.
            if self.warm_up_sample > 0:
                new_client = Client(len(self.clients), TRANSIENT)
                self.warm_up_sample -= 1
            else:
                new_client = Client(len(self.clients), EQUILIBRIUM)
            # Adiciona o cliente na fila 1 e define o seu tempo de chegada nessa fila.
            new_client.set_queue(1)
            new_client.set_arrival(self.t)
            self.queue1.append(new_client)
            self.clients.append(new_client)
            # Teste de correção
            if self.test and (new_client.id in self.test_list):
                print "Cliente", new_client.id, "gerou o evento Chegada ao sistema."
                print "Cliente", new_client.id, "entrou na fila 1."
            # Assim que uma chegada é processada, adiciona outro evento de chegada, dando o tempo que ela irá ocorrer.
            self.events.push((self.t + dist.exp_time(self.entry_rate), INCOMING))
            # Se o servidor estiver ocioso, adiciona o evento Entrada ao servidor pela fila 1 para esse cliente na lista.
            if not self.server_current_client:
                self.events.push((self.t, SERVER_1_IN))

        # Evento do tipo: Entrada ao servidor pela fila 1.
        elif event_type == SERVER_1_IN:
            # Define o tempo que o cliente vai ficar no servidor.
            server_time = dist.exp_time(self.server_rate)
            # Adiciona o cliente no servidor e define o seu tempo de saída da fila 1.
            self.server_current_client = self.pop_queue1()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            # Teste de correção
            if self.test and (self.server_current_client.id in self.test_list):
                print "Cliente", self.server_current_client.id, "gerou o evento Entrada ao servidor pela fila 1."
                print "Cliente", self.server_current_client.id, "entrou no servidor."
            # Adiciona o evento Saída do servidor na lista.
            self.events.push((self.t + server_time, SERVER_OUT))        

        # Evento do tipo: Entrada ao servidor pela fila 2.
        elif event_type == SERVER_2_IN:
            # Define o tempo que o cliente vai ficar no servidor.        
            server_time = dist.exp_time(self.server_rate)
            # Adiciona o cliente no servidor e define o seu tempo de saída da fila 2.
            self.server_current_client = self.pop_queue2()
            self.server_current_client.set_leave(self.t)
            self.server_current_client.set_server(server_time)
            # Teste de correção
            if self.test and (self.server_current_client.id in self.test_list):
                print "Cliente", self.server_current_client.id, "gerou o evento Entrada ao servidor pela fila 2."
                print "Cliente", self.server_current_client.id, "entrou no servidor."
            # Adiciona o evento Saída do servidor na lista.
            self.events.push((self.t + server_time, SERVER_OUT))                

        # Evento do tipo: Saída do servidor.
        elif event_type == SERVER_OUT:
            self.update_n()
            # Se a fila 1 possuir clientes, adiciona o evento Entrada ao servidor pela fila 1 na lista.
            if self.queue1:
                self.events.push((self.t, SERVER_1_IN))
            # Se a fila 2 possuir clientes e a fila 1 vazia, ou se o sistema estiver vazio e o cliente que
            # está no servidor entrou nele pela fila 1, adiciona o evento Entrada ao servidor pela fila 2 na lista.
            elif self.queue2 or self.server_current_client.queue == 1:
                self.events.push((self.t, SERVER_2_IN))
            
            # Teste de correção
            if self.test and (self.server_current_client.id in self.test_list):
                print "Cliente", self.server_current_client.id, "gerou o evento Saída do servidor."
            
            # Se o cliente que está no servidor entrou nele pela fila 1, adiciona ele na fila 2.
            if self.server_current_client.queue == 1:
                self.queue_2_in()
            # Senão, define que ele foi servido e saiu do sistema.
            else:
                self.server_current_client.set_served(1)
            self.server_current_client = None

    # Método que trata a entrada de um cliente na fila 2. Encapsulado para melhor legibilidade.
    def queue_2_in(self):
        # Pega o cliente do servidor e o adiciona na fila 2, definindo seu tempo de chegada na mesma.
        client = self.server_current_client
        self.queue2.append(client)
        client.set_queue(2)
        client.set_arrival(self.t)
        # Teste de correção
        if self.test and (client.id in self.test_list):
            print "Cliente", client.id, "entrou na fila 2."

    # Atualiza o número de pessoas nas filas a cada chegada, é chamado no início de eventos que
    # fazem o tempo do simulador passar (Chegada ao sistema e Saída do servidor)
    def update_n(self):
        # Calcula o intervalo de tempo entre o evento atual e o imediatamente anterior.
        delta = self.t - self.previous_event_time
        # Define o número de pessoas nas filas de espera
        n1 = len(self.queue1)
        n2 = len(self.queue2)
        # Soma às variáveis estimadas (Nq1) e (Nq2) o número de clientes na fila de espera multiplicado pelo
        # intervalo de tempo (delta) em que as filas ficaram com esse número de clientes.
        self.N_samples['Nq_1'] += n1*delta
        self.N_samples['Nq_2'] += n2*delta
        # Testa se o cliente que está no servidor, se ele estiver ocupado, veio da fila 1 ou da fila 2.
        if self.server_current_client:
            if self.server_current_client.queue == 1:
                n1 += 1
            elif self.server_current_client.queue == 2:
                n2 += 1
        # Soma às variáveis estimadas (N1) e (N2) o número de clientes na fila multiplicado pelo
        # intervalo de tempo (delta) em que as filas ficaram com esse número de clientes.
        self.N_samples['N_1'] += n1*delta
        self.N_samples['N_2'] += n2*delta
        # Atualiza o valor do tempo do evento anterior pelo evento atual, já que o simulador vai processar o próximo evento.
        self.previous_event_time = self.t

    # Método que descarta os clientes da fase transiente e os clientes que ainda estão no sistema após o término do processamento
    # da rodada.
    def discard_clients(self):
        served_clients = []
        for client in self.clients:
            if client.served and client.color == EQUILIBRIUM:
                served_clients.append(client)
        self.clients = served_clients

    # Método que processa os dados gerados por uma rodada.
    def process_sample(self):
        s_wait_1 = 0; s_s_wait_1 = 0
        s_wait_2 = 0; s_s_wait_2 = 0
        s_server_1 = 0; s_server_2 = 0

        # Loop que faz a soma e a soma dos quadrados dos tempos de espera e a soma dos tempos em servidor
        # Dos clientes na fila 1 e na fila 2.
        for client in self.clients:
            s_wait_1 += client.wait(1)
            s_s_wait_1 += client.wait(1)**2
            s_server_1 += client.server[1]
            s_wait_2 += client.wait(2)
            s_s_wait_2 += client.wait(2)**2
            s_server_2 += client.server[2]
            
        # Adiciona à soma e à soma dos quadrados dos estimadores os valores estimados na rodada.
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
        # Inicializa as estruturas de dados para a próxima rodada.
        self.init_sample()
    
    # Método que calcula os resultados (valor e intervalo de confiança) para cada estimador.
    def calc_results(self):
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
    
    # Método que atualiza a barra de progresso com o valor do menor intervalo de confiança encontrado a cada rodada.
    def pb_amount(self):
        return 1 - max((2.0*self.results['E[N1]']['c_i']/self.results['E[N1]']['value']), \
                       (2.0*self.results['E[N2]']['c_i']/self.results['E[N2]']['value']), \
                       (2.0*self.results['E[T1]']['c_i']/self.results['E[T1]']['value']), \
                       (2.0*self.results['E[T2]']['c_i']/self.results['E[T2]']['value']), \
                       (2.0*self.results['E[Nq1]']['c_i']/self.results['E[Nq1]']['value']), \
                       (2.0*self.results['E[Nq2]']['c_i']/self.results['E[Nq2]']['value']), \
                       (2.0*self.results['E[W1]']['c_i']/self.results['E[W1]']['value']), \
                       (2.0*self.results['E[W2]']['c_i']/self.results['E[W2]']['value']), \
                       (2.0*self.results['V(W1)']['c_i']/self.results['V(W1)']['value']), \
                       (2.0*self.results['V(W2)']['c_i']/self.results['V(W2)']['value']))
            
    # Método que testa se todos os intervalos de confiança são válidos.
    # Só faz a validação a partir da terceira rodada.
    def valid_confidence_interval(self):
        return not(self.samples <= 2) and \
               (2.0*self.results['E[N1]']['c_i']  <= 0.1*self.results['E[N1]']['value']) and \
               (2.0*self.results['E[N2]']['c_i']  <= 0.1*self.results['E[N2]']['value']) and \
               (2.0*self.results['E[T1]']['c_i']  <= 0.1*self.results['E[T1]']['value']) and \
               (2.0*self.results['E[T2]']['c_i']  <= 0.1*self.results['E[T2]']['value']) and \
               (2.0*self.results['E[Nq1]']['c_i'] <= 0.1*self.results['E[Nq1]']['value']) and \
               (2.0*self.results['E[Nq2]']['c_i'] <= 0.1*self.results['E[Nq2]']['value']) and \
               (2.0*self.results['E[W1]']['c_i']  <= 0.1*self.results['E[W1]']['value']) and \
               (2.0*self.results['E[W2]']['c_i']  <= 0.1*self.results['E[W2]']['value']) and \
               (2.0*self.results['V(W1)']['c_i']  <= 0.1*self.results['V(W1)']['value']) and \
               (2.0*self.results['V(W2)']['c_i']  <= 0.1*self.results['V(W2)']['value'])

    # Método que exibe os resultados junto com o número de rodadas processadas e os retorna.
    def report(self):
        print "Exibindo os resultados:"
        for key in self.results.keys():
            print key, ': ', self.results[key]['value'], ' - I.C: ', self.results[key]['c_i']
        print "Número de rodadas :", self.samples
        return self.results
        
    # Método que inicializa a lista dos clientes que serão testados.
    def init_test(self):
        for i in range(10):
            self.test_list.append(math.floor(random.random()*self.total_clients))
    
    # Métodos que tratam o trânsito dos clientes das filas para o servidor, de acordo com a política de atendimento usada.
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
