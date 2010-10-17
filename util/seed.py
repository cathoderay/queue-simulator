import random


#Helper for seed generation...
#TODO: check intersection given different seeds


def set_seed(n):
	random.seed(n)


def take_random_number():
	"Rounds by 2 decimal."
	return round(random.random(), 2)


def generate_random_numbers(seed, n):
	"Generate [n] random numbers starting with [seed]."
	set_seed(seed)
	random_numbers = []
	for i in range(n):
		 random_numbers.append(take_random_number())
	return random_numbers


if __name__ == "__main__":
	"Testing..."
	print generate_random_numbers(1, 10)	
