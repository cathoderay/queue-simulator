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
    r = round(random.random(), 2)
    while(r >= 1.0):
        r = round(random.random(), 2)
    return r

if __name__ == "__main__":
    "Testing..."
    print generate_random_numbers(50000)
