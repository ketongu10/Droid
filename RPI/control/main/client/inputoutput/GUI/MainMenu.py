from enum import Enum

import pygame, pygame_gui
import sys

from RPI.control.main.client.inputoutput.GUI.BaseManager import BaseManager
from RPI.control.main.client.inputoutput.GUI.DigitalManager import DigitalManager
from RPI.control.main.client.inputoutput.GUI.Utils import EnergySprite
from RPI.control.main.client.inputoutput.Subproc.PosViewer import PosViewer
from RPI.control.main.monitoring.Profiler import Profiler
from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring
from RPI.control.main.server.hardware.Orders import ControlMode
from RPI.control.project_settings import RUNS, RESOURCES





class MainMenu:
    def __init__(self, main_screen, sys_mon: SystemMonitoring):
        # Links to connected classes
        self.screen = main_screen
        self.sys_mon = sys_mon

        # for input handler
        self.SPEEDS = {"trucks": 2, "arm": 2}

        # Managers
        self.manager = pygame_gui.UIManager((1280, 768))
        self.managers_list = [self]
        self.is_active = True

        # Labeling and buttons
        LEFT_POS = 800
        MID_POS = 950
        settings = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((LEFT_POS, 25), (100, 50)), text='Settings', manager=self.manager, object_id='#button1')
        self.buttons = {settings: self.open_settings}
        self.settings_manager = BaseManager(self, self.managers_list,
                                            {'PosViewer': PosViewer(self.sys_mon),
                                             'accumulator': sys_mon.accumulator,
                                             'trucks': {
                                                 "left_truck": sys_mon.body.trucks.left_truck_VA,
                                                 "right_truck": sys_mon.body.trucks.right_truck_VA
                                             },
                                             'right_arm': {
                                                 "hand": sys_mon.body.right_arm.hand,
                                                 # "forearm_forward": sys_mon.body.right_arm.forearm_forward,
                                             }
                                             })



        self.current = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 500), (100, 50)), html_text=f'{sys_mon.accumulator.A} A', manager=self.manager)
        self.voltage = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 500), (100, 50)), html_text=f'{sys_mon.accumulator.V} V', manager=self.manager)

        self.trucks_speed = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 550), (100, 50)), html_text='2nd speed', manager=self.manager)
        self.arms_speed = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 600), (100, 50)), html_text='2nd speed', manager=self.manager)
        self.fps = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((LEFT_POS, 650), (100, 80)), html_text=f'{Profiler.subscribers["system_ping"]}', manager=self.manager)


        self.shoulder_forward = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 400), (200, 50)), html_text=f'shoulder_forward: {sys_mon.body.right_arm.shoulder_forward.angle}', manager=self.manager)
        self.shoulder_side = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 450), (200, 50)), html_text=f'shoulder_side: {sys_mon.body.right_arm.shoulder_side.angle}', manager=self.manager)
        self.elbow_side = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 500), (200, 50)), html_text=f'elbow_side: {sys_mon.body.right_arm.elbow_side.angle}', manager=self.manager)
        self.forearm_forward = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 550), (200, 50)), html_text=f'forearm_forward: {sys_mon.body.right_arm.forearm_forward.angle}', manager=self.manager)
        self.forearm_side = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 600), (200, 50)), html_text=f'forearm_side: {sys_mon.body.right_arm.forearm_side.angle}', manager=self.manager)
        self.hand = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((MID_POS, 650), (200, 50)), html_text=f'hand: {sys_mon.body.right_arm.hand.angle}', manager=self.manager)





        sprite_list = pygame.sprite.Group()
        self.battery_sprite = EnergySprite(self.sys_mon, sprite_list, pos=(LEFT_POS, 700))
        self.battery = pygame_gui.elements.UIStatusBar(pygame.Rect((LEFT_POS, 700), (450, 50)), self.manager, sprite=self.battery_sprite, percent_method=self.battery_sprite.get_percentage)
        self.battery_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((LEFT_POS, 700), (450, 50)),
                                                    text=f'{self.battery_sprite.get_percentage()*100:0.1f}%',
                                                    manager=self.manager)


        # MODE CONTROL
        self.CONTROL_MODE = ControlMode.M
        dropdown_options = [str(member.value) for member in ControlMode]
        self.mode_button = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((MID_POS, 25), (100, 50)),
                                           starting_option=str(ControlMode.M.value),
                                           options_list=dropdown_options,
                                           manager=self.manager)

        self.digital_mode_manager = DigitalManager(self, self.managers_list)




        self.battery.bar_filled_colour = (0, 255, 0)
        self.battery.border_colour = (128, 128, 0)
        self.battery.bar_unfilled_colour = (78, 78, 78)





    def process_events(self, event: pygame.event.Event):

        if self.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                button_func = self.buttons.get(event.ui_element)
                if button_func:
                    button_func()

            # Closes menu after choice and process switch mode
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.mode_button:
                    self.CONTROL_MODE = ControlMode.get_by_value(event.text)
                    self.mode_button.selected_option = event.text
                    self.mode_button.menu_active = False
                    self.digital_mode_manager.is_active = self.CONTROL_MODE == ControlMode.P
                    print(f"switched: {self.CONTROL_MODE == ControlMode.P} {self.CONTROL_MODE} {ControlMode.P}")

            # Closes menu after left click elsewhere
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    if not self.mode_button.relative_rect.collidepoint(event.pos):
                        self.mode_button.menu_active = False

            self.manager.process_events(event)

    def update(self, ticks: float):
        if self.is_active:
            self.battery_sprite.update_()
            perc = self.battery_sprite.get_percentage()
            self.battery.bar_filled_colour = (int(255 * (1 - perc) ** 2), int(255*perc**2), 0)
            self.battery_label.set_text(f'{self.battery_sprite.get_percentage()*100:0.1f}%')

            self.current.set_text(f'{self.sys_mon.accumulator.A.last_values[-10:].mean():0.3f} A')
            self.voltage.set_text(f'{self.sys_mon.accumulator.V} V')

            self.fps.set_text(f'{Profiler.subscribers["rec_time"]} | {Profiler.subscribers["system_ping"]}')

            self.trucks_speed.set_text(f'{self.SPEEDS["trucks"]}th speed')
            self.arms_speed.set_text(f'{self.SPEEDS["arm"]}th speed')

            self.shoulder_forward.set_text(f'shoulder_forward: {self.sys_mon.body.right_arm.shoulder_forward.angle}')
            self.shoulder_side.set_text(f'shoulder_side: {self.sys_mon.body.right_arm.shoulder_side.angle}')
            self.elbow_side.set_text(f'elbow_side: {self.sys_mon.body.right_arm.elbow_side.angle}')
            self.forearm_forward.set_text(f'forearm_forward: {self.sys_mon.body.right_arm.forearm_forward.angle}')
            self.forearm_side.set_text(f'forearm_side: {self.sys_mon.body.right_arm.forearm_side.angle}')
            self.hand.set_text(f'hand: {self.sys_mon.body.right_arm.hand.angle}')

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










if __name__ == "__main__":
    Profiler.register("system_ping")
    Profiler.register("rec_time")

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

        screen.fill((0, 0, 0))
        received_img = pygame.image.load(RESOURCES / 'image_received2.png').convert_alpha()
        screen.blit(received_img, received_img.get_rect())

        main_menu.draw_ui_all(screen)
        pygame.display.update()