import pygame

# Создаем класс, который взаимствован от класса Sprite внутри pygame
class Player(pygame.sprite.Sprite):

    # Инициализация
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        # Загружаем спрайт игрока
        self.image = pygame.image.load("player.png").convert_alpha()
        # (400, 300) размеры экрана / 2, не стал делать в переменной
        self.rect = self.image.get_rect(center=pos)