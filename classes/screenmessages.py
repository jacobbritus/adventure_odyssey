from other.settings import *


class ScreenMessages(pygame.sprite.Sprite):
    def __init__(self, group, value, color, counter, participant):
        super().__init__(group)
        self.participant = participant

        font = pygame.font.Font(FONT_ONE, 16)

        self.image = font.render(str(value), True, color)
        self.counter = counter
        self.rect = pygame.Surface.get_rect(self.image, topleft = self.participant.dmg_position)
        self.timer = 75
        self.opacity = 255
        self.y_float = 0

    def update(self):
        position = self.participant.dmg_position

        self.rect.topleft = (position.x + 32 * self.counter, position.y - self.y_float )

        self.y_float += 0.5

        self.timer -= 1
        if self.timer <= 0:
            self.kill()

        if self.timer <= 50:
            self.opacity -= 10
            if self.opacity >= 0: self.image.set_alpha(self.opacity)
            else: self.image.set_alpha(0)

