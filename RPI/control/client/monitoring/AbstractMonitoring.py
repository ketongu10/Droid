
import pygame.display
import numpy as np
from RPI.control.client.monitoring.IPhysicalDevice import IPhysicalDevice
from RPI.control.client.monitoring.Renderer import Renderer


class AbstractMonitor:
    def __init__(self, bufsize, bounds=(-1, 1)):
        self.last_values = np.zeros(shape=(bufsize,),dtype=np.float32)
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


class VACharacteristics(IPhysicalDevice):
    def __init__(self, bufsize, V_bounds=(-1, 1), A_bounds=(-1, 1)):
        self.V = AbstractMonitor(bufsize, V_bounds)
        self.A = AbstractMonitor(bufsize, A_bounds)

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
        received_img = pygame.image.load("../image_received2.png").convert_alpha()
        screen.blit(received_img, received_img.get_rect())

        CURRENT.update_buffer()
        CURRENT.render(renderer, screen, (768, 0))
        text_surface = speed_text.render(f"TRUCKS |{SPEEDS['trucks']}|\nARMS    |{SPEEDS['arm']}|", False, (0, 255, 0))
        screen.blit(text_surface, (400, 250))
        pygame.display.update()
        clock.tick(60)
        print(clock.get_fps())