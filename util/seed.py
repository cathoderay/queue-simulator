import random
import primes

#Helper for seed generation...

def set_seed(n):
    """A seed is defined giving an index to a prime number list.
    If the index is higher than the prime list limit, it uses 
    the limit value as an index instead."""
    if n > primes.limit:
        n = primes.limit
    random.seed(primes.list[n])

def take_random_number():
    "Rounds by 2 decimal."
    return round(random.random(), 2)

def generate_random_numbers(seed, n):
    "Generate [n] random numbers starting with [seed]."
    set_seed(seed)
    return [take_random_number() for i in range(n)]

if __name__ == "__main__":
    "Testing..."
    print generate_random_numbers(50000, 10)	
