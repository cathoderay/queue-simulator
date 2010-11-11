class client:
	def __init__(self, id):
		self.id = id
		#Times of the client in the system
		self.arrival = {}
		self.leave = {}
		self.server = {}
	
	def set_arrival(self, queue, arrival):
		self.arrival[queue] = arrival
	
	def set_leave(self, queue, leave):
		self.leave[queue] = leave
	
	def set_server(self, queue, server):
		self.server[queue] = server
		
	def wait(self, queue, unit):
		return (self.leave[queue] - self.arrival[queue])*unit