class Node: 
  def __init__(self, value=None, next=None): 
    self.value = value 
    self.next  = next 

  def __str__(self): 
    return str(self.value)