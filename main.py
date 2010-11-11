# Main code that will generate a single sample
import sys
sys.path.append('util')
sys.path.append('obj')
from collections import deque
import dist
import seed
import estimator
import queue
import client

wait_queue1 = deque([])
wait_queue2 = deque([])
#0 = ocioso; 1 = cliente da fila 1; 2 = cliente da fila 2
server_occupied = 0
server_client = None
next = 0
x = 0 #time being served ( E[x] = 1/mi = 1 )
unit = 0.1
clients = []

# testing
time = 360000
entry_rate = 0.5
seed.set_seed(14)
# 1 = FCFS; 2 = LCFS
service_policy = 2
#########

i = 0
while i < time or wait_queue1 or wait_queue2:
	#chegou alguem
	if next <= 0:
		clients.append(client.client(len(clients)))
		clients[-1].set_arrival(1, i)
		next = dist.exp_time(entry_rate)
		#se filas vazias e servidor ocioso
		if not(wait_queue1 or wait_queue2 or server_occupied):
			server_client = clients[-1]
			server_occupied = 1
			x = dist.exp_time(1)
			clients[-1].set_leave(1, i)
			clients[-1].set_server(1, x)
		else:
			wait_queue1.append(clients[-1])
	elif i < time:
		next -= unit
	
	#servico terminou
	if x <= 0:
		x = dist.exp_time(1)
		#se quem estava no servidor era da fila 1, manda-lo para a fila 2
		if server_occupied == 1:
			wait_queue2.append(server_client)
			wait_queue2[-1].set_arrival(2, i)
		#fila 1 nao esta vazia
		if wait_queue1:
			#wait_queue1 = queue.leave(wait_queue1, 1, service_policy, i, x, server_client, server_occupied)
			if service_policy == 1:
				wait_queue1[0].set_leave(1, i)
				wait_queue1[0].set_server(1, x)
				server_client = wait_queue1.popleft()
			elif service_policy == 2:
				wait_queue1[-1].set_leave(1, i)
				wait_queue1[-1].set_server(1, x)
				server_client = wait_queue1.pop()			
			server_occupied = 1
		#fila 1 vazia, testar se existem clientes na fila 2
		elif wait_queue2:
			#wait_queue2 = queue.leave(wait_queue2, 2, service_policy, i, x, server_client, server_occupied)
			if service_policy == 1:
				wait_queue2[0].set_leave(2, i)
				wait_queue2[0].set_server(2, x)
				server_client = wait_queue2.popleft()
			elif service_policy == 2:
				wait_queue2[-1].set_leave(2, i)
				wait_queue2[-1].set_server(2, x)
				server_client = wait_queue2.pop()
			server_occupied = 2
		else:
			server_client = None
			server_occupied = 0
	else:
		x -= unit
	
	i += 1


print "Media dos tempos de espera na fila 1: ", estimator.mean([clients[i].wait(1, unit) for i in range(len(clients))])
print "Media dos tempos no servidor de clientes da fila 1: ", estimator.mean([clients[i].server[1] for i in range(len(clients))])
print "Media dos tempos de espera na fila 2: ", estimator.mean([clients[i].wait(2, unit) for i in range(len(clients))])
print "Media dos tempos no servidor de clientes da fila 2: ", estimator.mean([clients[i].server[2] for i in range(len(clients))])



