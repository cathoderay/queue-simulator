import math
import seed
import estimator

#Helper method to calculate Poisson and Exponential distribution properties

def exp_time(rate, s, n):
	"""Returns [n] random Times of an exponential distribution given the rate [rate], 
	using [s] for the seed of the random function."""
	return [round(-(math.log(1.0 - r)/rate), 3) for r in seed.generate_random_numbers(s, n)]
	
	
if __name__ == "__main__":
	"Testing..."
	print estimator.average(exp_time(2, 650, 1000000))