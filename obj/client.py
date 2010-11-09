class client:
	def __init__(self, id):
		self.id = id
		#Times of the client in the system
		self.arrival = 0
		self.leave = 0
		self.server = 0
	
	def set_arrival(self, arrival):
		self.arrival = arrival
	
	def set_leave(self, leave):
		self.leave = leave
		
	def set_server(self, server):
		self.server = server
		
	def wait(self, unit):
		return (self.leave - self.arrival)*unit