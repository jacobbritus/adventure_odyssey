from classes.UI import Button
from classes.states import ButtonVariant
from other.settings import *

class OverworldUI:
    def __init__(self):
        self.picked_up_item: bool = False

        self.bg_bar = UI["battle_message_box"]["small_background"]
        self.bg_bar_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.bg_bar.get_width() // 2,
                                  WINDOW_HEIGHT - self.bg_bar.get_height() - 64)

        self.buttons_group = pygame.sprite.Group()
        self.button = Button(pygame.sprite.Group(), None, None, "PICK UP ITEM", ButtonVariant.WIDE, self.bg_bar_pos,
                             False)

        self.item_to_display = None
        self.message_time = pygame.time.get_ticks() + 0
        self.message_box = UI["battle_message_box"]["large_background"]
        self.message_box_pos = pygame.Vector2(
            WINDOW_WIDTH - self.message_box.get_width() // 2,
            30
        )
        self.message_box_pos_x = WINDOW_WIDTH

        self.font = pygame.font.Font(FONT_ONE, 16)


    def show_pickup_prompt(self,  window, item) -> None:
        """Display a pick-up prompt whenever colliding with an item."""
        self.button.draw(window)

        if self.button.clicked:
            self.item_to_display = item
            self.picked_up_item = True
            self.message_time = pygame.time.get_ticks() + 7500
            self.button.clicked = False

    def hotkeys(self, event) -> None:
        """Hotkey to pick up item."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.button.clicked = True

    def item_message(self, window):
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

            item_name_surface = self.font.render(self.item_to_display.name.upper().replace("_", " "), True, (236, 226, 196))
            window.blit(item_name_surface, message_name_pos)

            message_quantity_pos = message_box_pos + (item_name_surface.get_width() + 32, 6)

            window.blit(
                self.font.render("x" + str(self.item_to_display.quantity), True,(236, 226, 196)),
                message_quantity_pos
            )

            message_item_pos = message_quantity_pos + (16, -7)

            window.blit(self.item_to_display.item_image, message_item_pos)






