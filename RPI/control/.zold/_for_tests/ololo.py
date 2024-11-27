

import numpy as np
from time import time
import matplotlib.pyplot as plt

from multiprocessing import Process
#plt.axis([0, 10, 0, 1])


# Y = [0]
#
# plt.scatter(0, Y[0])
# for i in range(1, 10):
#     t0 = time()
#     x = np.random.random()
#     y = np.random.random()
#     Y.append(y)
#     plt.scatter(i, y)
#     plt.plot([i-1, i], Y[-2:], c='r')
#     print(time() - t0)
#     plt.pause(0.005)
# plt.show()

def main():
    N = 2
    Y = [[0] for i in range(N)]
    X = [[0] for i in range(N)]


    fig, axs = plt.subplots(nrows=N, ncols=1, sharex=True, figsize=(10, 10))
    if N == 1:
        axs = [axs]

    i = 1
    LAST_N = 100
    working = True
    while working:
        t0 = time()

        for j in range(N):
            y = np.random.random()
            Y[j].append(y)
            X[j].append(i)
            axs[j].set_xlim([i-LAST_N, i])

            if i>LAST_N:
                if i % LAST_N == 0:
                    axs[j].cla()
                    axs[j].plot(X[j][-LAST_N:], Y[j][-LAST_N:], c='r')
                else:
                    axs[j].plot(X[j][-2:], Y[j][-2:], c='r')


        if i > LAST_N:
            plt.pause(0.0005)



        i += 1




        #print(f'{(time() - t0):0.4f}')



if __name__ == '__main__':
    Ps = []
    for i in range(2):
        P = Process(target=main)
        P.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        for P in Ps:
            P.terminate()
