from math import sin
import matplotlib.pyplot as plt

def plot(x, y):
	plt.plot(x, y, 'b-', linewidth=1)
	plt.show()


if __name__ == "__main__":
	x = range(100)
	y = [sin(item) for item in range(100)]
	plot(x, y)

