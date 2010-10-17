import random

#Helper for seed generation...
#TODO: check intersection given different seeds

#Method that checks if a given odd number is prime (Naive method)
def is_prime(n):
	factors = range(3, n, 2)
	for f in factors:
		if n % f == 0:
			return 0
	return 1

#Method that returns the n-th prime number
def get_prime(n):
	if n == 1: 
		print "prime number found!: 2"
		return 2
	get_prime2(n)

#Done this to avoid making (if n == 1) test over and over..
def get_prime2(n):
	#Get only odd numbers first
	prime = 3 + ((n - 2)*2)
	if is_prime(prime):
		print "prime number found!: ", prime
		return prime
	get_prime2(n+1)

def set_seed(n):
	random.seed(get_prime(n))

def take_random_number():
	"Rounds by 2 decimal."
	return round(random.random(), 2)

def generate_random_numbers(seed, n):
	"Generate [n] random numbers starting with [seed]."
	set_seed(seed)
	return [take_random_number() for i in range(n)]

if __name__ == "__main__":
	"Testing..."
	print generate_random_numbers(6, 10)	
