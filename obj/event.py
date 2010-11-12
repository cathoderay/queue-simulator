INCOMING = 'incoming'
SERVER_OUT = 'server_out'
SERVER_1_IN = 'server_1_in'
SERVER_2_IN = 'server_2_in'
QUEUE_2_IN = 'queue_2_in'
SYSTEM_OUT = 'system_out'

class Event:
  def __init__(self, event_type, time):
    self.event_type = event_type
    self.time = time

  def __str__(self):
    return "[Event type: %s | Event time: %s]" % (self.event_type, self.time)
