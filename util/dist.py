import math
import random
import estimator

#Helper method to calculate Poisson and Exponential distribution properties

def exp_time(rate):
	"""Returns 1 random Time of an exponential distribution given the rate [rate]."""
	return -(math.log(1.0 - random.random())/rate)
	
if __name__ == "__main__":
	"Testing..."
	print estimator.mean(exp_time(2, 650))