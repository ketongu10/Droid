import numpy as np
import pygame

from RPI.control.main.monitoring.SystemMonitoring import SystemMonitoring


class EnergySprite(pygame.sprite.Sprite):
    def __init__(self, sys_mon: SystemMonitoring,  *groups: pygame.sprite.AbstractGroup, pos: tuple[int, int]):
        super().__init__(*groups)
        self.sys_mon = sys_mon
        self.image = pygame.Surface([50, 50])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.max_energy = 16.8
        self.current_energy = 16.8

    def get_percentage(self) -> float:
        return self.current_energy/self.max_energy

    def update_(self) -> None:
        self.current_energy = min(np.mean(self.sys_mon.accumulator.V.last_values), self.max_energy)

