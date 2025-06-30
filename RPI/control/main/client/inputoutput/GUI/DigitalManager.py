import json

import pygame_gui
import pygame

from RPI.control.main.client.inputoutput.Subproc.PosViewer import BoneTranslation
from RPI.control.project_settings import UNITY
from RPI.control.main.client.inputoutput.GUI.BaseManager import Activator, SettingsLabeling

LEFT_POS = 800
MID_POS = 950

class DigitalManager:
    def __init__(self, parent, managers_list):
        self.parent = parent
        self.manager = pygame_gui.UIManager(SettingsLabeling.manager_screen)
        managers_list.append(self)
        self.is_active = False
        self.should_send = False
        self.positions = {}

        self.accept_pos = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((MID_POS+100,25), (120, 50)), text='Accept Position',
                                                manager=self.manager)

        self.unity_translation_config = {}
        with open(UNITY / 'translation_config.json', 'r') as f:
            data = json.load(f)
            for key, value in data["Bones"].items():
                self.unity_translation_config[key] = BoneTranslation(**value)
                self.unity_translation_config[key].parse_reg_name(self.parent.sys_mon)


    def process_events(self, event: pygame.event.Event):

        if self.is_active and self.parent.is_active:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.accept_pos:

                    with open(UNITY/'ViewPosition_Data/StreamingAssets/transfered_pos_out.json', 'r') as f:
                        data = json.load(f)
                        for key, value in data["angles"].items():
                            bone = self.unity_translation_config[key]
                            self.positions[key] = (self.clip360(value)-bone.bias)/bone.k

                    self.should_send = True
                    print("SENDING POSITION")

            self.manager.process_events(event)

    def draw_ui(self, surface: pygame.surface.Surface):
        if self.is_active and self.parent.is_active:
            self.manager.draw_ui(surface)

    def update(self, ticks: float):
        if self.is_active and self.parent.is_active:
            self.manager.update(ticks)

    def clip360(self, value):
        value = float(value)
        if value > 180:
            return value-360
        return value