import numpy as np
import pygame
from time import time
from RPI.control.client.monitoring.Profiler import Profiler
from RPI.control.client.inputoutput.InputHandler import InputHandler


class ClientMainScreen:
    SCREEN_SIZE = 1280, 768
    screen = None
    speed_text = None

    @staticmethod
    def init_screen():
        ClientMainScreen.screen = pygame.display.set_mode(ClientMainScreen.SCREEN_SIZE)

        # For text rendering
        pygame.font.init()
        ClientMainScreen.speed_text = pygame.font.SysFont('Comic Sans MS', 30)

    @staticmethod
    @Profiler.register("render_screen")
    def render_screen(client):
        render_t0 = time()
        ClientMainScreen.screen.fill((0, 0, 0))  # Заполняем экран черным = clear screen
        if client.network.video_stream.re is not None:
            with open('../tmp/image_received2.png', 'wb') as f:
                f.write(client.network.view)
            # received_img = pygame.image.frombytes(client.view, (1023, 1023), "RGBA") # pygame.image.load("image_received.jpg").convert_alpha()
            received_img = pygame.image.load("../tmp/image_received2.png").convert_alpha()
            ClientMainScreen.screen.blit(received_img, received_img.get_rect())

            # print(f"RENDERING TIME={time() - t0}")

        else:
            ClientMainScreen.screen.fill((0, 0, 0))
            # sсreen.blit(default_image,  default_image.get_rect())
        #Client.CurrentManagerInstance.render(_screen=ClientMainScreen.screen, pos=(800, 0))
        text_surface = ClientMainScreen.speed_text.render(f"TRUCKS     |{InputHandler.SPEEDS['trucks']}|"
                                                f"\nARMS       |{InputHandler.SPEEDS['arm']}|"
                                                f"\nRENDER     |{int((time() - render_t0) * 1000)}|")
                                                #f"\nCURRENT    |{np.mean(Client.CurrentManagerInstance.last_values[-50:]):.4f}|"
                                                #f"\nCURRENT_sig|{np.std(Client.CurrentManagerInstance.last_values):.4f}|", False, (0, 255, 0))
        ClientMainScreen.screen.blit(text_surface, (800, 200))
        pygame.display.update()
