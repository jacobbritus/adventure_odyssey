import pygame.sprite

from other.settings import *


class FloatingDamage(pygame.sprite.Sprite):
    def __init__(self, value, position, counter):
        super().__init__()
        self.font = pygame.font.Font(TEXT_ONE, 16)
        self.image = self.font.render(str(value), True, (255, 255, 255))
        self.position = None
        self.counter = counter
        self.rect = pygame.Surface.get_rect(self.image, topleft = position)
        self.timer = 60
        self.position = None
        self.is_expired = False
        self.opacity = 255

        self.y_float = 0

    def update(self, position):
        self.position = position

        self.rect.topleft = (position.x + 32 * self.counter, position.y - self.y_float)

        self.y_float += 0.5

        self.timer -= 1
        if self.timer <= 0:
            self.kill()

        if self.timer <= 30:
            self.opacity -= 10
            if self.opacity >= 0: self.image.set_alpha(self.opacity)
            else: self.image.set_alpha(0)

