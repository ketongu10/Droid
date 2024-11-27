import pygame

class EnergySprite(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.AbstractGroup, pos: tuple[int, int]):
        super().__init__(*groups)

        self.image = pygame.Surface([50, 50])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.max_energy = 100
        self.current_energy = 75

    def get_percentage(self) -> float:
        return self.current_energy/self.max_energy