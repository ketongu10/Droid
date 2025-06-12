
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
    def __init__(self, bufsize, bounds=(-1, 1), side=Side.Client, sh_mem_name=None):
        if side == Side.Client:
            sh_mem_name_ = sh_mem_name if sh_mem_name is not None else AbstractMonitor.get_unique_name()
            self.shm = SharedMemory(name=sh_mem_name_, create=True, size=bufsize*4)
            self.last_values = np.ndarray(shape=(bufsize,), dtype=np.float32, buffer=self.shm.buf)
        else:
            self.last_values = np.ndarray(shape=(bufsize,), dtype=np.float32)
        self.max = bounds[1]
        self.min = bounds[0]

    def last(self):
        return f'{self.last_values[-1]:0.4f}'

    def update_buffer(self, source=None):
        self.last_values[0:-1] = self.last_values[1:]
        self.last_values[-1] = np.random.uniform(self.min, self.max) if source is None else float(source)

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
        print("New buffer name", AbstractMonitor.unique_name)
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
        return {"V": self.V.last(), "A": self.A.last()}

    def set_subscription_values(self, parameters: dict):
        self.update_buffer(parameters["V"], parameters["A"])

    def get_info(self) -> tuple:
        return (*self.V.get_info(), 'V'), (*self.A.get_info(), 'A')



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