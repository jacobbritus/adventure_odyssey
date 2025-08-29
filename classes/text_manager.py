import pygame.time

from other.play_sound import play_sound
from other.settings import FONT_ONE
from other.text_bg_effect import text_bg_effect


class TextManager:
    def __init__(self, character, dialogue, pos):
        self.dialogue = dialogue
        self.pos = pos

        self.font = pygame.font.Font(FONT_ONE, 16)
        self.text = character + ": "
        self.text_surface = self.font.render(self.text, True, (236, 226, 196))

        self.delay_time = 50
        self.delay = pygame.time.get_ticks() + self.delay_time

        self.text_index = 0


    def update_text(self):
        if pygame.time.get_ticks() >= self.delay and not self.text_index >= len(self.dialogue):
            play_sound("ui", "dialogue", None)
            self.text += self.dialogue[self.text_index]
            self.text_surface = self.font.render(self.text, True, (236, 226, 196))
            self.text_index += 1
            self.delay = pygame.time.get_ticks() + self.delay_time

    def draw(self, window):
        self.update_text()


        window.blit(self.text_surface, self.pos)

