from other.settings import *


class FloatingDamage(pygame.sprite.Sprite):
    def __init__(self, group, value, position, counter):
        super().__init__(group)
        font = pygame.font.Font(FONT_ONE, 16)
        if value == "CRITICAL HIT":
            color = (0, 0, 255)
        elif value == "PERFECT BLOCK":
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        self.image = font.render(str(value), True, color)
        self.position = None
        self.counter = counter
        self.rect = pygame.Surface.get_rect(self.image, topleft = position)
        self.timer = 75
        self.opacity = 255
        self.y_float = 0

    def update(self, position):
        self.position = position

        self.rect.topleft = (position.x + 32 * self.counter, position.y - self.y_float )

        self.y_float += 0.5

        self.timer -= 1
        if self.timer <= 0:
            self.kill()

        if self.timer <= 50:
            self.opacity -= 10
            if self.opacity >= 0: self.image.set_alpha(self.opacity)
            else: self.image.set_alpha(0)

