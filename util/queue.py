from collections import deque

def leave(wait_queue, index, service_policy, time, x, server_client, server_occupied):
	"""processing for the client leaving the [wait_queue] of index [index] to the server,
	   adding queue leaving [time] and calculated time of the client in the server([x])
	   given the [service_policy](1 for FCFS, 2 for LCFS)"""
	if service_policy == 1:
		wait_queue[0].set_leave(index, time)
		wait_queue[0].set_server(index, x)
		server_client = wait_queue.popleft()
	elif service_policy == 2:
		wait_queue[-1].set_leave(index, time)
		wait_queue[-1].set_server(index, x)
		server_client = wait_queue.pop()
	
	server_occupied = index
	
	return wait_queue
	
	