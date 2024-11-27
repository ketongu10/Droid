from multiprocessing import Process

import pygame
import pygame_gui

from RPI.control.main.monitoring.IPhysicalDevice import IPhysicalDevice


class SettingsLabeling:
    x_start = 334
    y_start = 50
    but_h = 100
    but_w = 300
    interval = 25
    opened_color = (255, 0, 0)
    manager_screen = (1280, 768)


class Activator:

    def activate(self) -> None: ...

    def update(self) -> None:
        pass

class OpenMonitoring(Activator):
    def __init__(self, but, key, value: IPhysicalDevice):
        self.button: pygame_gui.elements.UIButton = but
        self.key = key
        self.device = value
        self.is_opened = False
        self.process = None

    def activate(self) -> None:
        if self.is_opened:
            print('closing')
            self.button.colours['normal_bg'] = pygame.Color(76, 80, 82, 255)
            if self.process.is_alive():
                self.process.terminate()
        else:
            print(f'activated {self.key}')
            self.button.colours['normal_text'] = pygame.Color(255, 0, 0, 255) #(76, 80, 82, 255)]
            print(self.button.colours)
            self.process = Process(target=self.device.start_monitoring_process, args=(self.key, self.device.get_info(), ))
            self.process.start()

        self.is_opened = not self.is_opened

    def update(self) -> None:
        if self.is_opened:
            if not self.process.is_alive():
                print('SSSSSS')


class OpenManager(Activator):
    def __init__(self, parent, key, value, managers_list):
        self.key = key
        self.manager = BaseManager(parent, managers_list, value)

    def activate(self) -> None:
        self.manager.parent.is_active = False
        self.manager.is_active = True

class BaseManager:

    def __init__(self, parent, managers_list, child_dict: dict):
        self.parent = parent
        self.manager = pygame_gui.UIManager(SettingsLabeling.manager_screen)
        managers_list.append(self)
        self.buttons: dict[pygame_gui.core.UIElement, Activator] = {}
        self.is_active = False


        cur_shift = 0
        for key, value in child_dict.items():
            butt = pygame_gui.elements.UIButton(text=str(key),
                                                manager=self.manager,
                                                relative_rect=pygame.Rect((SettingsLabeling.x_start,
                                                                           SettingsLabeling.y_start+cur_shift),
                                                                          (SettingsLabeling.but_w,
                                                                           SettingsLabeling.but_h)))
            if isinstance(value, dict):
                self.buttons[butt] = OpenManager(self, key, value, managers_list)
            else:
                self.buttons[butt] = OpenMonitoring(butt, key, value)
            cur_shift += SettingsLabeling.but_h + SettingsLabeling.interval

    def process_events(self, event: pygame.event.Event):

        if self.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                button_activator = self.buttons.get(event.ui_element)
                if button_activator:
                    button_activator.activate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_active = False
                    self.parent.is_active = True
                    #self.parent.manager.screen.fill((0, 0, 0))
                    print('close')

            self.manager.process_events(event)

    def draw_ui(self, surface: pygame.surface.Surface):
        if self.is_active:
            self.manager.draw_ui(surface)

    def update(self, ticks: float):
        if self.is_active:
            for but, act in self.buttons.items():
                act.update()

            self.manager.update(ticks)
