import random
import pygame.time

from other.play_sound import play_sound


from other.settings import *


class TextManager:
    def __init__(self, interactor):
        self.interactor = interactor

        if self.interactor.role == "hero":
            dialogue = random.choice(ALLY_DIALOGUE).upper()
        else:
            dialogue = NPC_DIALOGUE[self.interactor.id].upper() if not isinstance(NPC_DIALOGUE[self.interactor.id],
                                                                                  list) else NPC_DIALOGUE[
                self.interactor.id]

        if isinstance(dialogue, list):
            self.dialogue_index = 0
            self.full_dialogue = dialogue
            self.dialogue = self.full_dialogue[self.dialogue_index]
        else:
            self.dialogue = dialogue
            self.full_dialogue = None


        self.font = pygame.font.Font(FONT_ONE, 16)
        self.text = self.interactor.name.upper() + ": "
        self.text_surface = self.font.render(self.text, True, (236, 226, 196))

        self.delay_time = 50
        self.delay = pygame.time.get_ticks() + self.delay_time

        self.text_index = 0
        self.done = False
        self.name_surface = self.font.render(self.interactor.name.upper() + ":", True, (100, 200, 100))

        self.dialogue_bg = UI["battle_message_box"]["large_background"]
        self.bg_pos = pygame.Vector2(
            WINDOW_WIDTH // 2 - self.dialogue_bg.get_width() // 2,
            WINDOW_HEIGHT - self.dialogue_bg.get_height() - 64
        )
        self.text_pos = self.bg_pos + (40, 6)
        self.icon_pos = self.bg_pos + (4, 0)


    def update_text(self):
        if pygame.time.get_ticks() >= self.delay and not self.text_index >= len(self.dialogue):
            play_sound("ui", "dialogue", None)
            self.text += self.dialogue[self.text_index].upper()
            self.text_surface = self.font.render(self.text, True, (236, 226, 196))
            self.text_index += 1
            self.delay = pygame.time.get_ticks() + self.delay_time

    def hotkeys(self, event) -> None:
        """Hotkey to pick up item."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.delay_time = 0 # I'd say change this to holding

            # either end or next sequence of dialogue
            # e.g., it's equal to a set number of characters (self.next.sequence = True)
            if self.text_index == len(self.dialogue):
                if not self.full_dialogue:
                    self.done = True
                    self.interactor.interacting = False
                else:
                    if self.dialogue_index == len(self.full_dialogue) - 1:
                        self.done = True
                        self.interactor.interacting = False
                    else:
                        self.delay_time = 50
                        self.text = self.interactor.name.upper() + ": "
                        self.text_index = 0
                        self.dialogue_index += 1
                        self.dialogue = self.full_dialogue[self.dialogue_index]


    def draw(self, window):
        self.update_text()
        window.blit(self.dialogue_bg, self.bg_pos)

        window.blit(self.text_surface, self.text_pos)
        window.blit(self.name_surface, self.text_pos)
        window.blit(self.interactor.icon, self.icon_pos)


