
import pygame_gui
import pygame
from RPI.control.main.client.inputoutput.GUI.BaseManager import Activator, SettingsLabeling

LEFT_POS = 800
MID_POS = 950

class DigitalManager:
    def __init__(self, parent, managers_list):
        self.parent = parent
        self.manager = pygame_gui.UIManager(SettingsLabeling.manager_screen)
        managers_list.append(self)
        self.is_active = False

        self.accept_pos = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((MID_POS, 75), (120, 50)), text='Accept Position',
                                                manager=self.manager)

    def process_events(self, event: pygame.event.Event):

        if self.is_active and self.parent.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.accept_pos:
                    print("SENDING POSITION")

            self.manager.process_events(event)

    def draw_ui(self, surface: pygame.surface.Surface):
        if self.is_active and self.parent.is_active:
            self.manager.draw_ui(surface)

    def update(self, ticks: float):
        if self.is_active and self.parent.is_active:
            self.manager.update(ticks)