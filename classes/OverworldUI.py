import pygame

from classes.UI import Button
from classes.states import ButtonVariant
from other.settings import *

class OverworldUI:
    def __init__(self):
        self.pickup_prompt = None
        self.pickup_message = None
        self.picked_up_item = False

        self.bg_bar = UI["battle_message_box"]["small_background"]
        self.bg_bar_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.bg_bar.get_width() // 2,
                                  WINDOW_HEIGHT - self.bg_bar.get_height() - 64)

        self.buttons_group = pygame.sprite.Group()
        self.pickup_text = pygame.font.Font(FONT_ONE, 16).render("PICK UP ITEM", True, (255, 255, 255))
        self.pickup_text_pos = pygame.Vector2(self.bg_bar_pos.x + self.bg_bar.get_width() // 2 - self.pickup_text.get_width() // 2,
                                              self.bg_bar_pos.y + self.bg_bar.get_height() // 2 - self.pickup_text.get_height() // 2,)

        self.button = Button(pygame.sprite.Group(), None, None, "PICK UP ITEM", ButtonVariant.WIDE, self.bg_bar_pos,
                             False)

        self.item_to_display = None
        self.message_time = pygame.time.get_ticks() + 0
        self.message_box = UI["battle_message_box"]["large_background"]
        self.message_box_pos = pygame.Vector2(
            WINDOW_WIDTH - self.message_box.get_width() // 2,
            30
        )
        self.message_item_pos = self.message_box_pos + (10, -1)
        self.message_quantity_pos = self.message_item_pos + (32, 6)
        self.x = WINDOW_WIDTH

        self.font = pygame.font.Font(FONT_ONE, 16)


    def show_pickup_prompt(self,  window, item):
        self.button.draw(window, 255)

        if self.button.clicked:
            self.item_to_display = item
            self.picked_up_item = True
            self.button.clicked = False
            self.message_time = pygame.time.get_ticks() + 5000


    def hotkeys(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            self.button.clicked = True

    def item_message(self, window):
        if not pygame.time.get_ticks() >= self.message_time:
            diff = abs(self.x - self.message_box_pos.x) * 0.1

            if not pygame.time.get_ticks() >= self.message_time - 2500:
                self.x = max(self.x - diff, int(self.message_box_pos.x))
            else:
                self.x = max(self.x + diff, int(self.message_box_pos.x))

            message_box_pos = pygame.Vector2(self.x, self.message_box_pos.y)


            message_name_pos = message_box_pos + (8, 6)

            message_item_pos = message_box_pos + (186, -1)
            message_quantity_pos = message_item_pos + (32, 6)

            window.blit(self.message_box, message_box_pos)
            window.blit(self.font.render(self.item_to_display.name.upper().replace("_", " "), True, (255,255,255)), message_name_pos)

            window.blit(self.item_to_display.item_image, message_item_pos)
            window.blit(self.font.render("x" + str(self.item_to_display.quantity), True,
                                                              (255, 255, 255)),
                        message_quantity_pos)

        else:
            self.x = WINDOW_WIDTH + 64




