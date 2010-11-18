from math import sin, cos
import matplotlib.pyplot as plt

def plot(x, y, c):
	plt.plot(x, y, c, linewidth=1)	
	
def show():
	plt.grid()
	plt.show()

if __name__ == "__main__":
	x = range(100)
	y = [sin(item) for item in range(100)]
	z = [cos(item) for item in range(100)]
	plot(x, y, 'b-')
	plot(x, z, 'r-')
	show()
