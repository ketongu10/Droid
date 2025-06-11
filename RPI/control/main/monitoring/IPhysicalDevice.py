import numpy as np
import matplotlib.pyplot as plt
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Process
from time import time
from RPI.control.project_settings import SHM_CLIENT_SYSSTR_TIME

class IPhysicalDevice:


    view_process = None

    def set_subscription_values(self, parameters: dict):
        for key, value in parameters.items():
            if isinstance(self.__getattribute__(key), IPhysicalDevice):
                self.__getattribute__(key).set_subscription_values(value)
                # self.__setattr__(key, self.__getattribute__(key).set_subscription_values(value))
            else:
                self.__setattr__(key, value)

    def get_subscribers(self) -> dict:
        ret = {}
        for key, value in self.__dict__.items():
            if isinstance(value, IPhysicalDevice):
                ret[key] = value.get_subscribers()
            else:
                ret[key] = value
        return ret

    def get_info(self) -> tuple: ...

    def on_activate_viewer(self, key):
        self.view_process = Process(target=self.start_monitoring_process, args=(key, self.get_info(),))
        self.view_process.start()

    def on_deactivate_viewer(self):
        if self.view_process.is_alive():
            self.view_process.terminate()

    def update_viewer(self):
        pass

    def check_alive_viewer(self):
        """RETURNS True if alive"""
        return self.view_process.is_alive()

    @staticmethod
    def start_monitoring_process(name, args) -> None:

        shms = [SharedMemory(name=nm[0]) for nm in args]
        shms_t = [SharedMemory(name=SHM_CLIENT_SYSSTR_TIME) for nm in args]
        n_shms = len(shms)
        Ys = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms]
        Xs = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms_t]
        Y_lims = [item[1:3] for item in args]
        names = [item[3] for item in args]
        X_last = [0 for i in shms]

        fig, axs = plt.subplots(nrows=n_shms, ncols=1, sharex=True, figsize=(7, 3))
        if n_shms == 1:
            axs = [axs]

        for j in range(n_shms):
            axs[j].set_ylim(Y_lims[j])

        fig.suptitle(name, fontsize=16)
        for i in range(n_shms):
            axs[i].set_ylabel(names[i])
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
                for name_i in range(n_shms):
                    axs[name_i].set_ylabel(names[name_i])
            i += 1
            print((time() - t0))
            plt.pause(0.0005)