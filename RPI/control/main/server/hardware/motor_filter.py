import numpy as np
from matplotlib import pyplot as plt



class MotorFilter:
    def __init__(self, size=5, sigma=1, func=(lambda x: x)):
        self.last_values = np.array([0]*size, dtype=np.float32)
        self.sigma = sigma
        self.size = size
        self.func = func
        self.linear = np.array([np.exp(-((i-size//2)**2)/sigma**2) for i in range(size)], dtype=np.float32)
        self.linear /= np.sum(self.linear)
        print(self.linear)


    def __call__(self, x):
        self.last_values = np.roll(self.last_values, -1)
        self.last_values[-1] = x
        return self.last_values.dot(self.linear)




if __name__=="__main__":
    a = np.array([1]*10+[-1]*10)
    funcs = [np.log,
             np.sqrt,
             lambda x: x**3]
    b = []
    f = MotorFilter(size=7,sigma=2)
    for x in a:
       b.append(f(x))


    print(a)
    print(b)
    plt.plot(a)
    plt.plot(b)
    plt.show()


