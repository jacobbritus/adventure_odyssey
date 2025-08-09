import pygame

from other.settings import *

class OverworldUI:
    def __init__(self):
        self.pickup_prompt = None
        self.pickup_message = None
        self.picked_up_item = False
        self.message_time = 3000

        self.bg_bar = UI["battle_message_box"]["small_background"]
        self.bg_bar_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.bg_bar.get_width() // 2,
                                  WINDOW_HEIGHT - self.bg_bar.get_height() - 64)
        self.pickup_text = pygame.font.Font(FONT_ONE, 16).render("PICK UP ITEM", True, (255, 255, 255))
        self.pickup_text_pos = pygame.Vector2(self.bg_bar_pos.x + self.bg_bar.get_width() // 2 - self.pickup_text.get_width() // 2,
                                              self.bg_bar_pos.y + self.bg_bar.get_height() // 2 - self.pickup_text.get_height() // 2,)





    def show_pickup_prompt(self,  window):


        window.blit(self.bg_bar, self.bg_bar_pos)
        window.blit(self.pickup_text, self.pickup_text_pos)


    def hotkeys(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self.picked_up_item = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.picked_up_item = True

