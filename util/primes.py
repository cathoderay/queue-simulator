import math

#Helper for prime number manipulation

#Sieve algorithm: (Returns a list of prime numbers < n)
#Credits:
    # Code from: <dickinsm@gmail.com>, Nov 30 2006
    # http://groups.google.com/group/comp.lang.python/msg/f1f10ced88c68c2d

def primes(n):
	if n <= 2:
		return []
	sieve = range(3, n, 2)
	top = len(sieve)
	for si in sieve:
		if si:
			bottom = (si*si - 3) // 2
			if bottom >= top:
				break
			sieve[bottom::si] = [0] * -((bottom - top) // si)
	return [2] + [el for el in sieve if el]

max = 1500000
list = primes(max)
limit = len(list)
