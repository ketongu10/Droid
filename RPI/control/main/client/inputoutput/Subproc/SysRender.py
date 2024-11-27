
import numpy as np
from time import time, sleep
import matplotlib.pyplot as plt
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Process


def generator(shm_name, fps, N):
    t0 = time()
    shms = SharedMemory(name=shm_name)
    shms_t = SharedMemory(name=shm_name+"_t")
    Y = np.ndarray(shape=(N, ), dtype=np.float32, buffer=shms.buf)
    X = np.ndarray(shape=(N, ), dtype=np.float32, buffer=shms_t.buf)
    while True:
        t_start = time()
        Y[0] = np.random.random()
        X[0] = t_start-t0
        Y[:] = np.roll(Y, -1, 0)
        X[:] = np.roll(X, -1, 0)
        #print(time()-t_start)
        sleep(1/fps)



def main(name, args: list | tuple):



    shms = [SharedMemory(name=nm[0]) for nm in args]
    shms_t = [SharedMemory(name=nm[0]+'_t') for nm in args]
    n_shms = len(shms)
    Ys = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms]
    Xs = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms_t]
    Y_lims = [item[1:] for item in args]
    X_last = [0 for i in shms]


    fig, axs = plt.subplots(nrows=n_shms, ncols=1, sharex=True, figsize=(10, 10))
    if n_shms == 1:
        axs = [axs]

    for j in range(n_shms):
        axs[j].set_ylim(Y_lims[j])
    fig.suptitle(name, fontsize=16)
    axs[0].set_ylabel('V')
    axs[1].set_ylabel('A')
    i = 1
    LAST_N = 100
    working = True
    while working:
        t0 = time()



        Xcp = np.array(Xs)
        x_min = np.max(Xcp[:, 0])
        x_max = np.min(Xcp[:, -1])
        print(x_min, x_max)
        for j in range(n_shms):

            axs[j].set_xlim([x_min, x_max])


            if i % LAST_N == 0:
                axs[j].cla()
                axs[j].set_ylim(Y_lims[j])
                inds = np.where((Xs[j] >= x_min) & (Xs[j] <= x_max))

                axs[j].plot(Xs[j][inds], Ys[j][inds], c='r')
            else:
                inds = np.where((Xs[j] >= X_last[j]) & (Xs[j] <= x_max))
                axs[j].plot(Xs[j][inds], Ys[j][inds], c='r')

        if i % LAST_N == 0:
            axs[0].set_ylabel('V')
            axs[1].set_ylabel('A')
        i += 1
        print((time()-t0))
        plt.pause(0.0005)

if __name__ == "__main__":

    N = 100
    shms = SharedMemory(name="shm_1", create=True, size=N*4)
    shms_t = SharedMemory(name="shm_1_t", create=True, size=N*4)
    shms2 = SharedMemory(name="shm_2", create=True, size=N*4)
    shms2_t = SharedMemory(name="shm_2_t", create=True, size=N*4)


    P1 = Process(target=generator, args=('shm_1',120, N))
    P2 = Process(target=generator, args=('shm_2',10, N))
    P1.start()
    P2.start()
    P3 = Process(target=main, args=('loh', [('shm_1', -1, 1), ('shm_2', 0 ,1)],))
    P3.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        for P in [P1, P2, P3]:
            P.terminate()