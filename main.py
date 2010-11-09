# Main code that will generate a single sample
import sys
sys.path.append('util')
sys.path.append('obj')
import dist
import seed
import estimator
import client

wait_queue = []
server_occupied = 0
next = 0
x = 0 #time being served ( E[x] = 1/mi = 1 )
unit = 0.1
clients = []

# testing
time = 36000
entry_rate = 0.9
seed.set_seed(1)

for i in range(time):
	#chegou alguem
	if next <= 0:
		clients.append(client.client(len(clients)))
		clients[-1].set_arrival(i)
		next = dist.exp_time(entry_rate)
		#se fila vazia e servidor ocioso
		if not(wait_queue or server_occupied):
			server_occupied = 1
			x = dist.exp_time(1)			
			clients[-1].set_leave(i)
			clients[-1].set_server(x)
		else:
			wait_queue.append(clients[-1])
	else:
		next -= unit
	
	#servico terminou
	if x <= 0:
		x = dist.exp_time(1)
		#fila nao esta vazia
		if wait_queue:
			wait_queue[0].set_leave(i)
			wait_queue[0].set_server(x)
			wait_queue.pop(0)
		else:
			server_occupied = 0
	else:
		x -= unit
		
print [clients[i].wait(unit) for i in range(len(clients))]
print estimator.mean([clients[i].wait(unit) for i in range(len(clients))])



