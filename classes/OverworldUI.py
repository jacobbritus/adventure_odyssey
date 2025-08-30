import random

import pygame.sprite

from classes.UI import Button
from classes.states import ButtonVariant
from classes.text_manager import TextManager
from other.settings import *

class OverworldUI:
    def __init__(self):
        self.active = None
        self.picked_up_item: bool = False

        self.bg_bar = UI["battle_message_box"]["small_background"]
        self.bg_bar_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.bg_bar.get_width() // 2,
                                  WINDOW_HEIGHT - self.bg_bar.get_height() - 64)

        self.buttons_group = pygame.sprite.Group()
        self.item_button = Button(pygame.sprite.Group(), None, None, "PICK UP ITEM", ButtonVariant.WIDE, self.bg_bar_pos,
                                  False)
        self.dialogue_button = Button(pygame.sprite.Group(), None, None, "INTERACT", ButtonVariant.WIDE,
                                  self.bg_bar_pos,
                                  False)
        self.dialogue = False
        self.dialogue_bg = UI["battle_message_box"]["large_background"]
        self.dialogue_pos = pygame.Vector2(
            WINDOW_WIDTH // 2 - self.dialogue_bg.get_width() // 2,
            WINDOW_HEIGHT - self.dialogue_bg.get_height() - 64
        )

        self.text_manager = None


        self.button = None


        self.item_messages = pygame.sprite.Group()


    def interact_prompt(self, window, variant, **kwargs) -> None:
        """Display a pick-up prompt whenever colliding with an item."""
        if variant == "item":
            self.button = self.item_button

            item = kwargs.get("item")
            if self.button and self.button.delete:
                self.picked_up_item = True

                if item.name in [item_message.item.name for item_message in self.item_messages]:

                    for item_message in list(self.item_messages):
                        if item.name == item_message.item.name:
                            item_message.quantity += 1
                            item_message.message_time = pygame.time.get_ticks() + 7500
                else:
                    ItemMessage(item, len(list(self.item_messages)), self.item_messages)
                self.button.clicked = False
                self.button.delete = False

        elif variant == "dialogue":
            self.active = True
            self.button = self.dialogue_button
            
            if self.button and self.button.clicked:
                self.dialogue = True
                self.text_manager = TextManager(kwargs.get("character").upper(), random.choice(ALLY_DIALOGUE).upper(), self.dialogue_pos + (16, 6))

                self.button.delete = False
                self.button.clicked = False
        else:

            self.button = None

        if self.button and not self.dialogue:
            self.button.draw(window)

    def draw_dialogue(self, window):
        if self.dialogue:
            window.blit(UI["battle_message_box"]["large_background"], self.dialogue_pos)
            self.text_manager.draw(window)



    def hotkeys(self, event) -> None:
        """Hotkey to pick up item."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c and (self.button or self.dialogue):
            self.button.clicked = True

            if self.dialogue:
                self.text_manager.delay_time = 0

                if self.text_manager.text_index == len(self.text_manager.dialogue):
                    self.dialogue = False

    def draw_item_messages(self, window):
        for item_message in self.item_messages:
            item_message.draw(window)


class ItemMessage(pygame.sprite.Sprite):
    def __init__(self, item, count, group):
        super().__init__(group)

        self.item = item
        self.quantity = item.quantity
        self.message_time = pygame.time.get_ticks() + 7000

        self.font = pygame.font.Font(FONT_ONE, 16)

        # === message box ===
        self.message_box = UI["battle_message_box"]["large_background"]
        self.message_box_pos = pygame.Vector2(
            WINDOW_WIDTH - self.message_box.get_width() // 2,
            30 + 34 * count
        )
        self.message_box_pos_x = WINDOW_WIDTH

    def draw(self, window):
        """Display the item and quantity picked up."""
        if not pygame.time.get_ticks() >= self.message_time:
            diff = abs(self.message_box_pos_x - self.message_box_pos.x) * 0.1

            if not pygame.time.get_ticks() >= self.message_time - 5000:
                self.message_box_pos_x = max(self.message_box_pos_x - diff, int(self.message_box_pos.x))
            else:
                self.message_box_pos_x = min(self.message_box_pos_x + diff, WINDOW_WIDTH)

            message_box_pos = pygame.Vector2(self.message_box_pos_x, self.message_box_pos.y)
            message_name_pos = message_box_pos + (8, 6)

            window.blit(self.message_box, message_box_pos)

            item_name_surface = self.font.render(self.item.name.upper().replace("_", " "), True, (236, 226, 196))
            window.blit(item_name_surface, message_name_pos)

            message_quantity_pos = message_box_pos + (item_name_surface.get_width() + 32, 6)

            window.blit(
                self.font.render("x" + str(self.quantity), True,(236, 226, 196)),
                message_quantity_pos
            )

            message_item_pos = message_quantity_pos + (16, -7)

            window.blit(self.item.item_image, message_item_pos)
        else:
            self.kill()







