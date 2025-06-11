import numpy as np
import pygame
from time import time

from RPI.control.main.client.inputoutput.GUI.MainMenu import MainMenu
from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.project_settings import RUNS


class ClientMainScreen:
    SCREEN_SIZE = 1280, 768
    screen = None
    speed_text = None

    main_menu: MainMenu = None

    @staticmethod
    def init_screen(sys_mon):
        ClientMainScreen.screen = pygame.display.set_mode(ClientMainScreen.SCREEN_SIZE)
        ClientMainScreen.main_menu = MainMenu(ClientMainScreen.screen, sys_mon)

        # For text rendering
        pygame.font.init()
        ClientMainScreen.speed_text = pygame.font.SysFont('Comic Sans MS', 30)

        return ClientMainScreen.main_menu

    @staticmethod
    @Profiler.register("render_screen")
    def render_screen(client, tick):
        ClientMainScreen.main_menu.update_all(tick)
        ClientMainScreen.screen.fill((0, 0, 0))  # Заполняем экран черным = clear screen
        if client.network.video_stream.received_data is not None:
            with open(RUNS/'tmp/image_received2.png', 'wb') as f:
                f.write(client.network.video_stream.received_data)
            received_img = pygame.image.load(RUNS/'tmp/image_received2.png').convert_alpha()
            ClientMainScreen.screen.blit(received_img, received_img.get_rect())
        else:
            ClientMainScreen.screen.fill((0, 0, 0))

        ClientMainScreen.main_menu.draw_ui_all(ClientMainScreen.screen)
        pygame.display.update()
