INCOMING = 1
SERVER_OUT = 2
SERVER_1_IN = 3
SERVER_2_IN = 4
QUEUE_2_IN = 5

class Event:
  def __init__(self, event_type, time):
    self.event_type = event_type
    self.time = time

  def __str__(self):
    return "[Event type: %s | Event time: %s]" % (self.event_type, self.time)
