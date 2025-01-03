import pygame, pygame_gui
import sys

from RPI.control.main.client.inputoutput.GUI.BaseManager import BaseManager
from RPI.control.main.client.inputoutput.GUI.Utils import EnergySprite
from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.project_settings import RUNS, RESOURCES


class MainMenu:
    def __init__(self, main_screen, sys_mon: SystemMonitoring):
        self.screen = main_screen
        self.sys_mon = sys_mon
        self.manager = pygame_gui.UIManager((1280, 768))
        self.managers_list = [self]
        self.is_active = True
        LEFT_POS = 800
        MID_POS = 950
        settings = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LEFT_POS, 25), (100, 50)), text='Settings', manager=self.manager, object_id='#button1')
        self.buttons = {settings: self.open_settings}
        self.settings_manager = BaseManager(self, self.managers_list,
                                            {'accumulator': sys_mon.accumulator,
                                             'trucks': {
                                                 "left_truck": sys_mon.body.trucks.left_truck_VA,
                                                 "right_truck": sys_mon.body.trucks.right_truck_VA
                                             },
                                             'right_arm': {
                                                 "shoulder_forward": sys_mon.body.right_arm.shoulder_forward.angle,
                                                 "forearm_forward": sys_mon.body.right_arm.forearm_forward.angle,
                                             }
                                             })#SettingsMenu(self)



        self.current = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 500), (100, 50)), html_text=f'{sys_mon.accumulator.A} A', manager=self.manager)
        self.voltage = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 500), (100, 50)), html_text=f'{sys_mon.accumulator.V} V', manager=self.manager)

        trucks = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 550), (100, 50)), html_text='2nd speed', manager=self.manager)
        arms = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 600), (100, 50)), html_text='2nd speed', manager=self.manager)
        self.fps = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 650), (100, 50)), html_text=f'{Profiler.subscribers["system_ping"]}', manager=self.manager)


        self.shoulder_forward = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 600), (200, 50)), html_text=f'shoulder_forward: {sys_mon.body.right_arm.shoulder_forward.angle:.01f}', manager=self.manager)
        self.forearm_forward = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 650), (200, 50)), html_text=f'forearm_forward: {sys_mon.body.right_arm.forearm_forward.angle:.01f}', manager=self.manager)

        sprite_list = pygame.sprite.Group()
        self.battery_sprite = EnergySprite(self.sys_mon, sprite_list, pos=(LEFT_POS, 700))
        self.battery = pygame_gui.elements.UIStatusBar(pygame.Rect((LEFT_POS, 700), (450, 50)), self.manager, sprite=self.battery_sprite, percent_method=self.battery_sprite.get_percentage)
        self.battery_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LEFT_POS, 700), (450, 50)),
                                                    text=f'{self.battery_sprite.get_percentage()*100:0.1f}%',
                                                    manager=self.manager)


        self.battery.bar_filled_colour = (0, 255, 0)
        self.battery.border_colour = (128, 128, 0)
        self.battery.bar_unfilled_colour = (78, 78, 78)



    def process_events(self, event: pygame.event.Event):

        if self.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                button_func = self.buttons.get(event.ui_element)
                if button_func:
                    button_func()
            self.manager.process_events(event)

    def update(self, ticks: float):
        if self.is_active:
            self.battery_sprite.update_()
            perc = self.battery_sprite.get_percentage()
            self.battery.bar_filled_colour = (int(255 * (1 - perc) ** 2), int(255*perc**2), 0)
            self.battery_label.set_text(f'{self.battery_sprite.get_percentage()*100:0.1f}%')

            self.current.set_text(f'{self.sys_mon.accumulator.A.last_values[-10:].mean():0.3f} A')
            self.voltage.set_text(f'{self.sys_mon.accumulator.V} V')

            self.fps.set_text(f'{Profiler.subscribers["rec_time"]}')

            self.shoulder_forward.set_text(f'shoulder_forward: {self.sys_mon.body.right_arm.shoulder_forward.angle:.01f}')
            self.forearm_forward.set_text(f'forearm_forward: {self.sys_mon.body.right_arm.forearm_forward.angle:.01f}')

            self.manager.update(ticks)

    def draw_ui(self, surface: pygame.surface.Surface):
        if self.is_active:
            self.manager.draw_ui(surface)

    def process_events_all(self, event: pygame.event.Event):
        for manager_ in self.managers_list:
            manager_.process_events(event)

    def update_all(self, ticks: float):
        for manager_ in self.managers_list:
            manager_.update(ticks)

    def draw_ui_all(self, surface: pygame.surface.Surface):
        for manager_ in self.managers_list:
            manager_.draw_ui(surface)

    def open_settings(self):
        print('opened')
        self.is_active = False
        self.settings_manager.is_active = True
        self.battery_sprite.current_energy *= 0.9
        self.screen.fill((0, 0, 0))

class SettingsMenu:

    def __init__(self, main_menu):
        self.main_menu: MainMenu = main_menu
        self.manager = pygame_gui.UIManager((1280, 768))
        self.is_active = False
        LEFT_POS = 334






        sprite_list = pygame.sprite.Group()
        self.battery_sprite = EnergySprite(sprite_list, pos=(LEFT_POS, 700))
        self.battery_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LEFT_POS, 700), (450, 50)),
                                                    text=f'{self.battery_sprite.get_percentage()*100:0.1f}%',
                                                    manager=self.manager)
        fps = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 650), (100, 50)), html_text='60 fps', manager=self.manager) #, container=self.scr)

        current = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 500), (100, 50)), html_text='0 A', manager=self.manager) #, container=self.scr)

        trucks = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 550), (100, 50)), html_text='2nd speed', manager=self.manager) #, container=self.scr)
        arms = pygame_gui.elements.UIStatusBar(relative_rect=pygame.Rect((LEFT_POS, 600), (100, 50)),  manager=self.manager) #, container=self.scr)
        settings = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LEFT_POS, 25), (100, 50)), text='Settings',
                                                manager=self.manager, object_id='#button1')
        self.settings = settings
        self.buttons = {self.settings: self.open_settings}

        self.bar = pygame_gui.elements.UIVerticalScrollBar(pygame.Rect((LEFT_POS, 200), (15, 150)), manager=self.manager, visible_percentage=0.5)


        # self.battery.bar_filled_colour = (0, 255, 0)
        # self.battery.border_colour = (128, 128, 0)
        # self.battery.bar_unfilled_colour = (78, 78, 78)
        #self.toggle = pygame_gui.elements.UI2DSlider(pygame.Rect((LEFT_POS, 700), (450, 50)), 0.5, (0.6, 0.7), 0.5, (0.6, 0.7), manager=self.manager)
        #self.toggle.scroll_position
        #self.scr = pygame_gui.elements.UIScrollingContainer(pygame.Rect((LEFT_POS, 200), (550, 450)), manager=self.manager)
        #self.battery = pygame_gui.elements.UIStatusBar(pygame.Rect((LEFT_POS, 700), (450, 50)), self.manager, sprite=self.battery_sprite, percent_method=self.battery_sprite.get_percentage)



    def process_events(self, event: pygame.event.Event):

        if self.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                button_func = self.buttons.get(event.ui_element)
                if button_func:
                    button_func()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_active = False
                    self.main_menu.is_active = True
                    self.main_menu.screen.fill((0, 0, 0))
                    print('close')

            self.manager.process_events(event)


    def update(self, ticks: float):
        if self.is_active:
            perc = self.battery_sprite.get_percentage()
            pos_y = self.bar.scroll_position
            a = pygame.Rect()

            self.settings.set_position(pygame.Rect((334, 25), (100, 50)).move(0, pos_y*10))
            self.manager.update(ticks)


    def draw_ui(self, surface: pygame.surface.Surface):
        if self.is_active:
            self.manager.draw_ui(surface)

    def open_settings(self):
        print('LOH')
        #print(self.toggle.scroll_position)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 768))
    clock = pygame.time.Clock()

    working = True
    sys_mon = SystemMonitoring()
    main_menu = MainMenu(screen, sys_mon)

    while working:

        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Проверяем на выход из игры
                working = False
                pygame.quit()
                sys.exit()
            main_menu.process_events_all(event)


        main_menu.update_all(time_delta)

        received_img = pygame.image.load(RESOURCES / 'image_received2.png').convert_alpha()
        screen.blit(received_img, received_img.get_rect())

        main_menu.draw_ui_all(screen)
        pygame.display.update()