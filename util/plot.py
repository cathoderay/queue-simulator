from math import sin, cos
import matplotlib.pyplot as plt

def plot(list, *args, **kwargs):
    plt.plot(xrange(len(list)), list, *args, **kwargs)

def show(title):
    plt.title(title)
    plt.grid()
    plt.show()

if __name__ == "__main__":
    x = range(100)
    y = [sin(item) for item in range(100)]
    z = [cos(item) for item in range(100)]
    plot(x, y, 'b-')
    plot(x, z, 'r-')
    show()
