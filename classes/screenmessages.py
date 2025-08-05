import pygame

from other.settings import *
from other.text_bg_effect import text_bg_effect


class ScreenMessages(pygame.sprite.Sprite):
    def __init__(self, group, value, color, counter, participant):
        super().__init__(group)
        self.participant = participant
        self.text = value
        self.font = pygame.font.Font(FONT_ONE, 16)
        self.color = color

        self.image = self.font.render(str(self.text), True, self.color)

        self.counter = counter
        self.rect = pygame.Surface.get_rect(self.image, topleft = self.participant.dmg_position)
        self.timer = 150
        self.opacity = 255
        self.y_float = 0

    def update(self):
        self.y_float += 0.25

        self.timer -= 1
        if self.timer <= 0:
            self.kill()

        if self.timer <= 50:
            self.opacity -= 10
            self.image.set_alpha(min(self.opacity, 0))

    def draw(self, window):
        self.update()

        # Regenerate text with updated opacity
        text_surface = self.font.render(str(self.text), True, self.color)
        text_surface.set_alpha(self.opacity)

        # Use updated pos
        pos = pygame.Vector2(
            self.participant.dmg_position.x + 32 * self.counter,
            self.participant.dmg_position.y - self.y_float
        )

        # Generate background effect elements
        bg_elements = text_bg_effect(str(self.text), self.font, pos, None)

        # Draw the background layers
        for surface, draw_pos in bg_elements:
            surface.set_alpha(self.opacity)
            window.blit(surface, draw_pos)

        # Draw main text
        window.blit(text_surface, pos)




