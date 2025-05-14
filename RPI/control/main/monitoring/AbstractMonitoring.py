
import pygame.display
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Process
from time import sleep, time
from RPI.control.main.network.Side import Side
from RPI.control.project_settings import RESOURCES, SHM_CLIENT_SYSSTR_TIME
from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.main.monitoring.Renderer import Renderer


class AbstractMonitor:

    unique_name = 0
    def __init__(self, bufsize, bounds=(-1, 1), side=Side.Client):
        if side == Side.Client:
            self.shm = SharedMemory(name=AbstractMonitor.get_unique_name(), create=True, size=bufsize*4)
            self.last_values = np.ndarray(shape=(bufsize,), dtype=np.float32, buffer=self.shm.buf)
        else:
            self.last_values = np.ndarray(shape=(bufsize,), dtype=np.float32)
        self.max = bounds[1]
        self.min = bounds[0]

    def update_buffer(self, source=None):
        self.last_values[0:-1] = self.last_values[1:]
        self.last_values[-1] = np.random.uniform(self.min, self.max) if source is None else source

    def render(self, renderer_, _screen, pos=(10, 10)):
        renderer_.ax.cla()
        renderer_.ax.set_ylim([self.min, self.max])
        renderer_.ax.plot(self.last_values, color='green', label='test')
        renderer_.fig.canvas.draw()
        _screen.blit(renderer_.fig, pos)

    def get_info(self):
        return self.shm.name, self.min, self.max

    def __str__(self):
        return f"{self.last_values[-1]:.02f}"

    @staticmethod
    def get_unique_name():
        AbstractMonitor.unique_name += 1
        print(AbstractMonitor.unique_name)
        return f'AbstractMonitor_{AbstractMonitor.unique_name}'


class VACharacteristics(IPhysicalDevice):
    def __init__(self, bufsize, V_bounds=(-1, 1), A_bounds=(-1, 1), side=Side.Client):
        self.V = AbstractMonitor(bufsize, V_bounds, side)
        self.A = AbstractMonitor(bufsize, A_bounds, side)

    def update_buffer(self, V_source=None, A_source=None):
        self.V.update_buffer(V_source)
        self.A.update_buffer(A_source)

    def render(self, renderer_, _screen, pos=(10, 10)):
        renderer_.ax.cla()
        renderer_.ax.set_ylim([2.3, 2.8])
        renderer_.ax.plot(self.V.last_values, color='blue', label='Voltage')
        renderer_.ax.plot(self.A.last_values, color='red', label='Current')
        renderer_.fig.canvas.draw()
        _screen.blit(renderer_.fig, pos)

    def get_subscribers(self) -> dict:
        return {"V": float(self.V.last_values[-1]), "A": float(self.A.last_values[-1])}

    def set_subscription_values(self, parameters: dict):
        self.update_buffer(parameters["V"], parameters["A"])

    def get_info(self) -> tuple:
        return self.V.get_info(), self.A.get_info()

    @staticmethod
    def start_monitoring_process(name, args) -> None:

        shms = [SharedMemory(name=nm[0]) for nm in args]
        shms_t = [SharedMemory(name=SHM_CLIENT_SYSSTR_TIME) for nm in args]
        n_shms = len(shms)
        Ys = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms]
        Xs = [np.ndarray(shape=(100,), dtype=np.float32, buffer=shm.buf) for shm in shms_t]
        Y_lims = [item[1:] for item in args]
        X_last = [0 for i in shms]

        fig, axs = plt.subplots(nrows=n_shms, ncols=1, sharex=True, figsize=(7, 3))
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
            print((time() - t0))
            plt.pause(0.0005)


    def on_activate_viewer(self, key):
        self.view_process = Process(target=self.start_monitoring_process, args=(key, self.get_info(),))
        self.view_process.start()

    def on_deactivate_viewer(self):
        if self.view_process.is_alive():
            self.view_process.terminate()


if __name__ == "__main__":
    screen = pygame.display.set_mode((1280, 768))
    pygame.font.init()  # for text
    speed_text = pygame.font.SysFont('Comic Sans MS', 30)
    CURRENT = AbstractMonitor(100)
    clock = pygame.time.Clock()
    show = True
    SPEEDS = {"trucks": 2, "arm": 2}
    renderer = Renderer()
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Stop showing when quit
                show = False
        received_img = pygame.image.load(RESOURCES/"image_received.jpg").convert_alpha()
        screen.blit(received_img, received_img.get_rect())

        CURRENT.update_buffer()
        CURRENT.render(renderer, screen, (768, 0))
        text_surface = speed_text.render(f"TRUCKS |{SPEEDS['trucks']}|\nARMS    |{SPEEDS['arm']}|", False, (0, 255, 0))
        screen.blit(text_surface, (400, 250))
        pygame.display.update()
        clock.tick(60)
        print(clock.get_fps())