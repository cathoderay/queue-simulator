import math
import seed
import estimator

#Helper method to calculate Poisson and Exponential distribution properties

def exp_time(rate):
	"""Returns 1 random Time of an exponential distribution given the rate [rate]."""
	return round(-(math.log(1.0 - seed.take_random_number())/rate), 3)
	
if __name__ == "__main__":
	"Testing..."
	print estimator.mean(exp_time(2, 650))