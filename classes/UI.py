import pygame

from classes.pointer import Pointer
from classes.states import BookState, BattleMenuState, ButtonVariant
from other.play_sound import play_sound
from other.settings import *
from other.text_bg_effect import text_bg_effect


class StatusBar:
    def __init__(self, owner, y_offset):
        self.owner = owner
        self.y_offset = y_offset

        if owner.type == "player" or owner.role == "hero":
            self.has_mana = True
        else:
            self.has_mana = False


        self.font = pygame.font.Font(FONT_ONE, 16)
        self.opacity = 0

        self.hp_text_surface = None
        self.hp_icon = None

        self.background_box_pos = None
        self.name_surface = None
        self.name_pos = None

        self.char_icon = None
        self.char_icon_pos = None

        self.hp_bar_pos = None
        self.mana_bar_pos = None
        self.exp_bar_pos = None

        self.hp = None
        self.hp_icon = None
        self.hp_icon_pos = None

        self.hp_text_pos = None

        self.mana_icon = None
        self.mana_icon_pos = None

        self.mana = None
        self.mana_text_surface = None
        self.mana_text_pos = None

        self.exp_icon = None
        self.exp_icon_pos = None

        self.display_exp = None
        self.exp = None
        self.exp_text_surface = None
        self.exp_text_pos = None

        self.level_surface = None
        self.level_pos = None

        self.normal_speed = None
        self.delayed_speed = None
        self.bg_bar = None

        self.bars = None


        self.setup_small_hp_bar()
        self.stats = ["hp"]

        self.opacity = UI_OPACITY
        self.visible = False
        self.press_delay = 0
        self.x_offset = UI["status_bar"]["background"].get_width() - 32

        if self.owner.type == "player" or self.owner.role == "hero":
            self.stats.extend(["mana", "exp"])

            self.setup_hero_status_bar(y_offset, )
        self.setup_status_bars()

    def setup_small_hp_bar(self):
        self.hp = self.owner.hp
        self.hp_text_surface = self.font.render(f"{self.owner.hp}/{self.owner.max_hp}", True, (255, 255, 255))
        self.hp_icon = self.font.render("HP", True, (217, 87, 99))

    def setup_hero_status_bar(self, y_offset):
        ui = UI["status_bar"]
        menu_height = UI["battle_menu"]["main_background"].get_height()
        bg_width = ui["background"].get_width()
        bg_height = ui["background"].get_height()

        self.bg_bar = UI["status_bar"]["background"]

        self.background_box_pos = pygame.Vector2(WINDOW_WIDTH - bg_width + self.x_offset, WINDOW_HEIGHT - menu_height + self.y_offset)
        self.name_surface = self.font.render(str(self.owner.name).upper(), True, (255, 255, 255))
        self.name_pos = self.background_box_pos + pygame.Vector2(36, 2)

        icon = self.owner.icon
        rect = pygame.Rect(0, icon.get_height() - bg_height, 32, bg_height - 4)
        self.char_icon = icon.subsurface(rect).copy()
        self.char_icon_pos = self.background_box_pos + pygame.Vector2(4, 2)

        # === bar positions ===
        self.hp_bar_pos = self.background_box_pos + (165, 12)
        self.mana_bar_pos = self.background_box_pos + (257, 12)
        self.exp_bar_pos = self.background_box_pos + (188, 12)

        # === hp ===
        self.hp_icon = self.font.render("HP", True, (217, 87, 99))
        self.hp_icon_pos = self.hp_bar_pos + pygame.Vector2(-16, -7)

        self.hp_text_pos = self.hp_bar_pos + pygame.Vector2(ui["hp_box"].get_width() - self.hp_text_surface.get_width(), -14)

        # === sp ===
        self.mana_icon = self.font.render("SP", True, (99, 155, 255))
        self.mana_icon_pos = self.mana_bar_pos + pygame.Vector2(-16, -7)

        self.mana = self.owner.mana
        self.mana_text_surface = self.font.render(f"{self.owner.mana}/{self.owner.max_mana}", True, (255, 255, 255))
        self.mana_text_pos = self.mana_bar_pos + (ui["hp_box"].get_width() - self.mana_text_surface.get_width(), -14)

        # === exp ===
        self.exp_icon = self.font.render("EXP", True, (255, 215, 0))
        self.exp_icon_pos = self.exp_bar_pos + pygame.Vector2(-24, -7)

        self.exp = self.owner.exp
        self.exp_text_surface = self.font.render(f"{self.owner.exp}/{self.owner.max_exp}", True, (255, 255, 255))
        self.exp_text_pos = self.exp_bar_pos + (ui["exp_box"].get_width() - self.exp_text_surface.get_width(), -14)

        self.level_surface = self.font.render(str(self.owner.level), True, (255, 215, 0))
        self.level_pos = self.background_box_pos + (10, 2)

    def setup_status_bars(self) -> None:
        self.normal_speed = 2
        self.delayed_speed = 0.25

        self.bars = {}

        for stat in self.stats:
            stat_image: pygame.Surface = UI["status_bar"][stat + '_bar']
            current_value: int = getattr(self.owner, stat)
            max_value: int = getattr(self.owner, "max_" + stat)

            self.bars[stat] = {
                "image": stat_image,
                "current_width": int(stat_image.get_width() * current_value / max_value),
                "target_width": stat_image.get_width(),
                "bar": None,
                "bg_bar": None,
                "bg_width": int(stat_image.get_width() * current_value / max_value),
            }

    def set_bars(self) -> None:
        """Update the stat bars target lengths, making them relative to the current-value to max-value ratio."""
        for stat in self.stats:
            current_value = getattr(self.owner, stat)
            max_value = getattr(self.owner, "max_" + stat)
            ratio = max(0, min(current_value / max_value, 1))
            target = int(self.bars[stat]["image"].get_width() * ratio)
            self.bars[stat]["target_width"] = max(target, 4) if not current_value == 0 else 0

    def update_bars(self) -> None:
        """Slowly increase or decrease the current bar width until equal to the target width."""
        for key in self.stats:
            bar = self.bars[key]
            # self.normal_speed = 4 if key == "exp" else 2


            diff = bar["target_width"] - bar["current_width"]
            self.normal_speed = max(diff * 0.2, 1)


            # === modify the foreground bar ===
            if bar["current_width"] < bar["target_width"]:
                bar["current_width"] = min(bar["current_width"] + self.normal_speed, bar["target_width"])
            elif key == "exp":
                bar["current_width"] = bar["target_width"]
            else:
                bar["current_width"] = max(bar["current_width"] - self.normal_speed, bar["target_width"])

            crop = pygame.Rect(0, 0, bar["current_width"], bar["image"].get_height())

            bar["bar"] = bar["image"].subsurface(crop).copy()



            # === modify the background bar ===
            if key in ["hp", "mana"]:

                diff = bar["bg_width"] - bar["current_width"]
                self.delayed_speed = max(diff * 0.025, 0.005)
                # self.delayed_speed = max(abs((bar["bg_width"] - bar["target_width"]) // 20), 0.25)

                if bar["bg_width"] < bar["target_width"]:
                    bar["bg_width"] = min(bar["bg_width"] + self.normal_speed, bar["target_width"])
                else:
                    bar["bg_width"] = max(bar["bg_width"] - self.delayed_speed, bar["target_width"])
                bg_crop = pygame.Rect(0, 0, int(bar["bg_width"]), bar["image"].get_height())
                bar["bg_bar"] = UI["status_bar"]["delay_bar"].subsurface(bg_crop).copy()

    def draw_components(self):
        elements = [(self.bg_bar, self.background_box_pos),
                    (self.char_icon, self.char_icon_pos),
                    (self.name_surface, self.name_pos),
                    ]
        text_bgs = [
            *text_bg_effect(self.owner.name.upper(), self.font, self.name_pos, None)
        ]

        if self.display_exp:
            self.char_icon_pos += (23, 0)
            self.name_pos += (23,0)

            additional_elements = [
                (UI["status_bar"]["exp_box"], self.exp_bar_pos),
                (self.bars["exp"]["bar"], self.exp_bar_pos),
                (self.exp_text_surface, self.exp_text_pos),
                (self.level_surface, self.level_pos),

                (self.exp_icon, self.exp_icon_pos),


            ]
            elements += additional_elements

            text_bgs = [
                *text_bg_effect(str(self.owner.level), self.font, self.level_pos, None),

                *text_bg_effect(self.owner.name.upper(), self.font, self.name_pos, None),
                *text_bg_effect(f"EXP", self.font, self.exp_icon_pos, None),

                 *text_bg_effect(f"{int(self.exp)}/{self.owner.max_exp}", self.font, self.exp_text_pos, None),
            ]

        else:
            additional_elements = [
                (UI["status_bar"]["hp_box"], self.hp_bar_pos),
                (UI["status_bar"]["hp_box"], self.mana_bar_pos),
                (self.hp_icon, self.hp_icon_pos),
                (self.mana_icon, self.mana_icon_pos),


                (self.hp_text_surface, self.hp_text_pos),
                (self.mana_text_surface, self.mana_text_pos),
                (self.bars["mana"]["bg_bar"], self.mana_bar_pos),
                (self.bars["hp"]["bg_bar"], self.hp_bar_pos),

                (self.bars["hp"]["bar"], self.hp_bar_pos),
                (self.bars["mana"]["bar"], self.mana_bar_pos)]
            elements += additional_elements

            additional_text_bgs = [
                *text_bg_effect(self.owner.name.upper(), self.font, self.name_pos, None),
                *text_bg_effect(f"{int(self.mana)}/{self.owner.max_mana}", self.font, self.mana_text_pos, None),
                *text_bg_effect(f"{int(self.hp)}/{self.owner.max_hp}", self.font, self.hp_text_pos, None),
                *text_bg_effect(f"HP", self.font, self.hp_icon_pos, None),
                *text_bg_effect(f"SP", self.font, self.mana_icon_pos, None)
            ]
            text_bgs += additional_text_bgs



        for text_bg in text_bgs:
            elements.insert(2, text_bg)

        return elements

    def update_stat_text(self) -> None:
        def animate_stat(current, target, speed=self.normal_speed / 2):
            if current > target:
                return max(current - speed, target)
            else:
                return min(current + speed, target)

        def render_stat_text(value, max_value, font, fg_color=(255, 255, 255)):
            text = f"{int(value)}/{max_value}"
            return font.render(text, True, fg_color)

        def update_stat_display(current_value, target_value, max_value, font, text_pos):
            current = animate_stat(current_value, target_value)
            text_surface = render_stat_text(int(current), max_value, font)

            x_offset = UI["status_bar"]["exp_box"].get_width() if self.display_exp else UI["status_bar"]["hp_box"].get_width()
            offset = (x_offset - text_surface.get_width(), -14)
            text_pos = text_pos + offset
            return current, text_surface, text_pos

        # === animate and render hp ===
        self.hp, self.hp_text_surface, self.hp_text_pos = update_stat_display(self.hp, self.owner.hp, self.owner.max_hp,
                                                                              self.font, self.hp_bar_pos)

        # === animate and render mana ===
        if self.has_mana:
            self.mana, self.mana_text_surface, self.mana_text_pos = update_stat_display(self.mana, self.owner.mana,
                                                                                        self.owner.max_mana, self.font,
                                                                                        self.mana_bar_pos)
        if self.display_exp:
            self.exp, self.exp_text_surface, self.exp_text_pos = update_stat_display(self.exp, self.owner.exp,
                                                                                        self.owner.max_exp, self.font,
                                                                                        self.exp_bar_pos)

            if self.owner.exp <= 1:
                self.exp = 0


    def mask(self, window, elements):
        """Used to darken unselected enemy hp bars."""


        if self.owner.type == "enemy" and not self.owner.selected and not self.owner.death:
            for item, pos in elements:
                mask = pygame.mask.from_surface(item).to_surface(setcolor=(0, 0, 0, 50),
                                                                 unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pos)

        if self.display_exp:
            # if round(self.bars["exp"]["current_width"]) == round(self.bars["exp"]["target_width"]):
            if self.owner.exp == self.owner.max_exp:
                self.opacity = min(self.opacity + 5, 225)

                for element, pos in elements:

                    mask = pygame.mask.from_surface(element).to_surface(setcolor=(255, 255, 255, self.opacity),
                                                                 unsetcolor=(0, 0, 0, 0))

                    window.blit(mask, pos)

                    if self.opacity >= 150:
                        self.level_up_text(window)

            else:
                self.opacity = 0

    def level_up_text(self, window):
        text = "L    E    V    E    L        U    P"
        # text2 = strin

        level_up_text = self.font.render(text, True, (255, 215, 0))
        level_up_text.set_alpha(self.opacity)
        level_up_text_pos = self.exp_icon_pos - (72, 4)

        bg = text_bg_effect(text, self.font, level_up_text_pos, None)

        for text, bg_pos in bg:
            text.set_alpha(self.opacity)
            window.blit(text, bg_pos)

        window.blit(level_up_text, level_up_text_pos)



    def mouse_interactions(self) -> None: # will be used for a feature (status effects?)
        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()


        rect = self.bg_bar.get_rect(topleft = self.background_box_pos)

        if rect.collidepoint(mouse_pos):
            if press[0] and pygame.time.get_ticks() >= self.press_delay:
                if not self.visible:
                    self.visible = True
                else:
                    self.visible = False

                self.press_delay = pygame.time.get_ticks() + 250

            if press[2] and pygame.time.get_ticks() >= self.press_delay:
                if not self.display_exp:
                    self.display_exp = True

                else:
                    self.display_exp = False

                self.press_delay = pygame.time.get_ticks() + 250

        if self.visible:
            diff =  self.x_offset / self.bg_bar.get_width()
            speed = max(diff * 25, 0.3)
            self.x_offset = max(self.x_offset + -speed, 0)
            self.setup_hero_status_bar(0)
        elif not self.visible:
            diff = self.x_offset
            speed = max(diff * 0.25, 0.3)
            self.x_offset = min(self.x_offset + speed, self.bg_bar.get_width() - 32)
            self.setup_hero_status_bar(0)

            if self.x_offset == self.bg_bar.get_width() - 32:
                self.display_exp = False

    def draw(self, window) -> None:
        """Draw all the images on the window"""
        self.mouse_interactions()

        self.set_bars()

        self.update_bars()

        self.update_stat_text()

        elements = self.draw_components()
        for surface, pos in elements:

            window.blit(surface, pos)

        self.mask(window, elements)


class EnemyStatusBar(StatusBar):
    def __init__(self, owner):
        super().__init__(owner, None)

    def draw_components(self, *args):
        elements = [
            (UI["status_bar"]["hp_box"].copy(), self.hp_bar_pos),  # copied as its opacity gets lowered upon owner death
            (self.bars["hp"]["bg_bar"], self.hp_bar_pos),
            (self.bars["hp"]["bar"], self.hp_bar_pos),
            (self.hp_icon, self.hp_icon_pos),
            (self.hp_text_surface, self.hp_text_pos)]


        text_bgs = [
            *text_bg_effect(f"{int(self.hp)}/{self.owner.max_hp}", self.font, self.hp_text_pos, None),
            *text_bg_effect(f"HP", self.font, self.hp_icon_pos, None)
        ]
        for text_bg in text_bgs:
            elements.insert(2, text_bg)
        return elements

    def dynamic_pos(self, dynamic_pos):
        hp_icon_offset = (-16, -7)
        hp_text_offset = (74 - self.hp_text_surface.get_width(), -14)

        self.hp_bar_pos = dynamic_pos
        self.hp_icon_pos = self.hp_bar_pos + hp_icon_offset
        self.hp_text_pos = self.hp_bar_pos + hp_text_offset



    def draw(self, window, **kwargs) -> None:

        self.dynamic_pos(kwargs.get("pos"))


        self.set_bars()
        self.update_bars()

        elements = self.draw_components()
        self.update_stat_text()


        for surface, pos in elements:
            surface.set_alpha(max(0, self.opacity))

            if self.owner.death and self.bars["hp"]["bg_width"] <= 5:
                self.opacity -= 1

            window.blit(surface, pos)

        self.mask(window, elements)


class Button(pygame.sprite.Sprite):
    def __init__(self, group, parameter, function, text: str or tuple, variant, pos: pygame.Vector2, disabled: bool):
        super().__init__(group)

        # === image ===
        self.image_normal, self.image_pressed, self.image_selected = self.get_images(variant)
        self.image: pygame.Surface = self.image_normal

        # === position ===
        self.pos: pygame.Vector2 = pos
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.pos)

        # === functioning ===
        self.function = function
        self.parameter = parameter
        self.disabled = disabled

        # === text ===
        self.text_string: str = text
        self.font: pygame.font = pygame.font.Font(FONT_ONE, 16)

        color = (99, 61, 76)
        self.mana_color = (60, 109, 196)

        # change these into parameters please
        if text:
            if text in SKILLS.keys():
                self.button_type = "skill_button"
                self.text_string = text.replace("_", " ").upper()
                self.text_surface = self.font.render(self.text_string, True, color)
                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.left + 5, self.rect.centery - self.text_size[1] // 2)

                self.mana_cost = str(SKILLS[text]["mana"])
                self.mana_cost_surface = self.font.render(self.mana_cost, True, color)
                self.mana_cost_position = pygame.Vector2(self.rect.right - 32,
                                                         self.rect.centery - self.mana_cost_surface.get_height() // 2 - 1)

                self.mana_icon = self.font.render("SP", True, color)

                self.mana_icon_pos = self.mana_cost_position + (12, 0)

            elif type(text) == tuple:
                self.button_type = "item_button"

                self.text_surface = self.font.render(self.text_string[0], True, color)
                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.left + 5, self.rect.centery - self.text_size[1] // 2)

                self.quantity = self.font.render(self.text_string[1], True, color)
                self.quantity_pos = pygame.Vector2(self.rect.right - 6,
                                                         self.rect.centery - self.quantity.get_height() // 2 - 1)

            else:
                self.button_type = "normal_button"

                self.text_string = text

                self.text_surface = self.font.render(self.text_string, True, color)

                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.centerx - self.text_size[0] // 2,
                                                    self.rect.centery - self.text_size[1] // 2)
        else:
            self.button_type = "no_text"


        # === status ===
        self.clicked: bool = False
        self.hovering: bool = False
        self.delete_delay: int or float = 0
        self.delete: bool = False

        self.hover_sound_played: bool = False
        self.click_sound_played: bool = False

    @staticmethod
    def get_images(variant):
        """Return button images based on the variant parameter"""
        root = UI["buttons"]
        statuses = ["unselected", "pressed", "selected"]
        buttons = [root[variant.value + "_" + status].copy() for status in statuses]

        return buttons

    def update(self):
        self.kill_delay()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos) or self.clicked:
            if mouse_pressed or self.clicked:
                self.image = self.image_pressed

                if not self.disabled:
                    if not self.click_sound_played: play_sound("ui", "press", None)
                    self.click_sound_played = True
                    self.clicked = True
                else:
                    if not self.click_sound_played: play_sound("ui", "disabled", None)
                    self.click_sound_played = True
            else:
                self.image = self.image_selected

                if not self.hover_sound_played: play_sound("ui", "hover", None)
                self.hovering = True

                self.hover_sound_played = True
                self.click_sound_played = False
        else:
            self.image = self.image_normal


            self.hovering = False
            self.hover_sound_played = False
            self.click_sound_played = False



    def kill_delay(self):
        if self.clicked:
            self.delete_delay += 0.1

            if self.delete_delay >= 2:
                self.delete = True
                self.perform_function()

        return None

    def perform_function(self):
        if self.parameter:
            self.function(self.text_string)
        elif self.function and not self.parameter:
            self.function()
        else:
            pass

    def draw(self, window):
        window.blit(self.image, self.pos)

        if not self.button_type == "no_text":
            color = (99, 61, 76) if not self.hovering else (236, 226, 196)
            text = self.text_string[0] if self.button_type == "item_button" else self.text_string
            self.text_surface = self.font.render(text, True, color)
            window.blit(self.text_surface, self.text_position)

        if self.button_type == "skill_button":
            color = (99, 155, 255) if self.hovering else (60, 109, 196)
            self.mana_cost_surface = self.font.render(self.mana_cost, True, color)
            text_bg_effect(self.mana_cost, self.font, self.mana_cost_position, window)
            window.blit(self.mana_cost_surface, self.mana_cost_position)

            self.mana_icon = self.font.render("SP", True, color)
            text_bg_effect("SP", self.font, self.mana_icon_pos, window)
            window.blit(self.mana_icon, self.mana_icon_pos)
        elif self.button_type == "item_button":
            color = (255, 255, 255) if self.hovering else (200, 200, 200)


            self.quantity = self.font.render(self.text_string[1], True, color)

            pos = self.quantity_pos - (self.quantity.get_width(), 0)
            text_bg_effect(self.text_string[1], self.font, pos, window)
            window.blit(self.quantity, pos)



        if self.disabled:
            mask = pygame.mask.from_surface(self.image).to_surface(
                setcolor=(255, 0, 0, 100),
                unsetcolor=(0, 0, 0, 0))
            window.blit(mask, self.pos)

        self.update()



class BattleMenu:
    def __init__(self, player, performer, functions):
        # === player's attacks and functions ===
        # e.g., attack(name of button clicked) and player_run(no parameter)
        self.player = player
        self.performer = performer
        self.formatted_skills: list[str] = [attack.replace("_", " ").upper() for attack in self.performer.skills]
        self.attack_function = functions[0]
        self.run_function = functions[1]

        # === sprite groups for the buttons ===
        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.skills_buttons: pygame.sprite.Group = pygame.sprite.Group()

        # === main menu position ===
        self.main_menu_bg = UI["battle_menu"]["main_background"]

        self.main_menu_bg_pos = pygame.Vector2(0, WINDOW_HEIGHT - UI["battle_menu"]["main_background"].get_height())

        # === skills menu position ===
        self.skills_menu_bg = UI["battle_menu"]["skills_background"]

        self.skills_bg_pos = self.main_menu_bg_pos + (112, 0)

        # === end menu position ===
        self.end_menu_pos = pygame.Vector2(WINDOW_WIDTH // 2 - UI["battle_menu"]["skills_background"].get_width() // 2,
                                           WINDOW_HEIGHT // 2 - UI["battle_menu"]["skills_background"].get_height() // 2)
        self.victory_text_pos = pygame.Vector2(WINDOW_WIDTH // 2 - UI["titles"]["victory_title"].get_width() // 2,
                                               self.end_menu_pos.y + 4)

        # === inventory
        self.inventory_buttons = None

        # === enum states ===
        self.state = None
        self.visible = True

        self.selected_option = 0
        self.mouse_navigation = False
        self.pointer = Pointer(variant = "hand_pointer")


    def draw_pointer(self, window):
        for button in self.buttons_group:
            if button.hovering:
                if not button.text_string in ["SKILLS", "ITEMS", "RUN"]:
                    x_offset = (28, 6)
                else:
                    x_offset = (8, 0)

                self.pointer.draw(window, pygame.Vector2(button.rect.topleft) - x_offset , "right")

    def hotkeys(self, event):
        if event.type == pygame.KEYDOWN and self.state and not self.mouse_navigation:
            if not self.selected_option: self.selected_option = 0
            if event.key in [pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a]:
                pre = self.selected_option
                if event.key == pygame.K_w:
                    self.selected_option = max(self.selected_option - 1, 0)

                elif event.key == pygame.K_s:
                    self.selected_option = min(self.selected_option + 1, len(list(self.buttons_group)) - 1)

                elif event.key == pygame.K_d and len(list(self.buttons_group)) > 3:
                    self.selected_option = 3

                elif event.key == pygame.K_a and len(list(self.buttons_group)) > 3:
                    self.selected_option = 0



                post = self.selected_option
                if not pre == post:
                    play_sound("ui", "hover", None)

            # === click the selected button ===
            if event.key == pygame.K_c and self.selected_option >= 0:
                if not list(self.buttons_group)[self.selected_option].disabled: list(self.buttons_group)[self.selected_option].clicked = True


    def hotkey_button_selection(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.buttons_group and self.selected_option >= 0:
            list(self.buttons_group)[self.selected_option].hovering = True
            list(self.buttons_group)[self.selected_option].image = list(self.buttons_group)[self.selected_option].image_selected

        rects = [self.main_menu_bg.get_rect(topleft = self.main_menu_bg_pos)]
        if self.state in [BattleMenuState.INVENTORY_MENU, BattleMenuState.SKILLS_MENU]:
            rects.append(self.skills_menu_bg.get_rect(topleft = self.skills_bg_pos))

        for rect in rects:
            if rect.collidepoint(mouse_pos):
                self.mouse_navigation = True

                self.selected_option = -1
            else:
                self.mouse_navigation = False


    def draw(self, window: pygame.Surface, performer) -> None:
        """Draw the buttons and images associated with the current state."""
        self.update()

        self.performer = performer
        self.formatted_skills: list[str] = [attack.replace("_", " ").upper() for attack in self.performer.skills]

        if not self.state == BattleMenuState.END_MENU and self.state:
            window.blit(self.main_menu_bg, self.main_menu_bg_pos)
            self.draw_main_menu()

        # === buttons are drawn through the main menu skills button's function ===
        if self.state == BattleMenuState.SKILLS_MENU:
            window.blit(self.skills_menu_bg, self.skills_bg_pos)

        elif self.state == BattleMenuState.END_MENU:
            self.draw_end_menu()

        elif self.state == BattleMenuState.INVENTORY_MENU:
            window.blit(self.skills_menu_bg, self.skills_bg_pos)

        for button in self.buttons_group:
            button.draw(window)

        self.hotkey_button_selection()
        self.draw_pointer(window)


    def update(self) -> None:
        """Update the state based on the button clicked."""
        for button in self.buttons_group:
            if button.delete:
                # === main menu flow ===
                if button.text_string in ["SKILLS", "ITEMS"]:
                    # === clear the active inventory menu or skill menu buttons ===
                    for other_button in self.buttons_group:
                        if not other_button.text_string in ["SKILLS", "ITEMS", "RUN"]:
                            other_button.kill()

                    # === open skills menu if not active ===
                    if button.text_string == "SKILLS" and not self.state == BattleMenuState.SKILLS_MENU:
                        self.state = BattleMenuState.SKILLS_MENU
                        self.draw_skills_menu()


                    # === open inventory menu ===
                    elif button.text_string == "ITEMS" and not self.state == BattleMenuState.INVENTORY_MENU:
                        self.state = BattleMenuState.INVENTORY_MENU
                        self.draw_inventory_menu()
                        if self.player.inventory.items:
                            self.selected_option = 3


                    # === if the state is equal to the button for it pressed,
                    # e.g., SKILLS clicked and self.state == SKILLS MENU, go back to the main menu.
                    else:
                        self.selected_option = 0
                        self.state = BattleMenuState.MAIN_MENU

                    # reset the button pressed
                    button.clicked = False
                    button.delete = False
                    button.hovering = False
                    button.delete_delay = 0

                    if self.state == BattleMenuState.SKILLS_MENU:
                        if self.selected_option >= 0:
                            self.selected_option = 3
                    elif self.state == BattleMenuState.INVENTORY_MENU and self.player.inventory.items:
                        if self.selected_option >= 0:
                            self.selected_option = 3


                # === skills menu -> player animation ===
                elif button in self.skills_buttons:
                    self.state = None
                    self.buttons_group = pygame.sprite.Group()
                    self.selected_option = 0


                elif self.inventory_buttons and button in self.inventory_buttons:
                    self.state = None
                    self.buttons_group = pygame.sprite.Group()
                    self.selected_option = 0


                # === end screen -> overworld ===
                elif button.text_string == "END":
                    self.state = None


    def draw_main_menu(self) -> None:
        """Draw the buttons for the main menu."""
        if not self.buttons_group:
            button_offset = (6, 7)
            pos = self.main_menu_bg_pos + button_offset

            Button(self.buttons_group, None, None, "SKILLS", ButtonVariant.MEDIUM,
                   pos, False)

            y_offset = (0, 34)
            Button(self.buttons_group, None, None, "ITEMS", ButtonVariant.MEDIUM,
                   pos + y_offset, False)

            y_offset = (0, 68)
            Button(self.buttons_group, None, self.run_function, "RUN", ButtonVariant.MEDIUM,
                   pos + y_offset, False)

    def draw_end_menu(self) -> None:
        """Draw the buttons for the end menu."""
        if not self.buttons_group:
            pos = pygame.Vector2(
                WINDOW_WIDTH // 2 - UI["buttons"]["medium_selected"].get_width() // 2,
                WINDOW_HEIGHT // 2 - UI["buttons"]["medium_selected"].get_height() // 2

            )

            Button(self.buttons_group, None, self.run_function, "END", ButtonVariant.MEDIUM, pos, False)

    def draw_skills_menu(self) -> None:
        """Draw the buttons for the skills menu."""
        self.skills_buttons = pygame.sprite.Group()

        def can_use_skill(name, mana_amount) -> bool:
            """check if the player has enough mana"""
            cost = SKILLS[name]["mana"]
            return mana_amount >= cost

        if not self.skills_buttons:
            for index, skill_name in enumerate(self.performer.skills):

                y_offset = (0, 20 * index)
                padding = (6, 6)
                pos = self.skills_bg_pos + padding + y_offset
                if can_use_skill(skill_name, self.performer.mana):
                    Button([self.buttons_group, self.skills_buttons], skill_name, self.attack_function, skill_name,
                           ButtonVariant.WIDE, pos, False)
                else:
                    Button([self.buttons_group, self.skills_buttons], skill_name, self.attack_function, skill_name,
                           ButtonVariant.WIDE, pos, True)

    def draw_inventory_menu(self) -> None:
        """Draw the buttons for the skills menu."""
        self.inventory_buttons = pygame.sprite.Group()

        if not self.inventory_buttons:
            for index, item in enumerate(self.player.inventory.items.keys()):
                y_offset = (0, 20 * index)
                padding = (6, 6)
                pos = self.skills_bg_pos + padding + y_offset
                formatted_item_name = item.replace("_", " ").upper()

                # === disable item usage ===
                if self.player.inventory.items[item] <= 0:
                    Button([self.buttons_group, self.inventory_buttons], item.upper(), self.attack_function,
                           (formatted_item_name, str(self.player.inventory.items[item])),
                           ButtonVariant.WIDE, pos, True)
                else:
                    Button([self.buttons_group, self.inventory_buttons], item.upper(), self.attack_function, (formatted_item_name, str(self.player.inventory.items[item])),
                       ButtonVariant.WIDE, pos, False)


class MenuBook:
    def __init__(self, player):
        self.sound_played = False
        self.player = player
        self.image = UI["book"]["default_image"]
        self.book_width, self.book_height = self.image.get_size()
        self.frame = 0
        self.state = None
        self.base_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                       WINDOW_HEIGHT // 2 - self.image.get_height() // 2)

        self.pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                  WINDOW_HEIGHT // 2 - self.image.get_height() // 2)

        self.running = False

        self.animations = {
            BookState.NEXT_PAGE: {"sprites": "next_page", "offset": self.pos + pygame.Vector2(0, -32)},
            BookState.PREVIOUS_PAGE: {"sprites": "previous_page", "offset": self.pos + pygame.Vector2(0, -32)},
            BookState.OPEN_BOOK: {"sprites": "open_book", "offset": self.pos + pygame.Vector2(0, -160)},
            BookState.CLOSE_BOOK: {"sprites": "close_book", "offset": self.pos + pygame.Vector2(0, -160)}
        }

        self.content = [{"title": UI["titles"]["info_title"], "content": self.info_page},
                        {"title": UI["titles"]["inventory_title"], "content": self.inventory_page}]
        self.current_page = 0
        self.buttons_group = pygame.sprite.Group()
        self.font = pygame.font.Font(FONT_ONE, 16)
        self.selected_item = None
        self.click_delay = pygame.time.get_ticks() + 0
        self.team_member_index = 0
        self.selected_team_member = self.player


    def draw(self, window):
        self.update()
        if self.running:
            window.blit(self.image, self.pos)

        if not self.state and self.running: self.contents(window)

    def keybinds(self, event):
        if event.type == pygame.KEYDOWN and not self.state:
            if event.key == pygame.K_m:
                if self.running:
                    self.state = BookState.CLOSE_BOOK
                else:
                    self.running = True
                    self.state = BookState.OPEN_BOOK

            if event.key == pygame.K_n and not self.current_page >= len(self.content) - 1:
                self.current_page += 1
                self.state = BookState.NEXT_PAGE
            elif event.key == pygame.K_p and not self.current_page == 0:
                self.current_page -= 1
                self.state = BookState.PREVIOUS_PAGE

    def update(self):

        if self.state:
            if not self.sound_played:
                play_sound("ui", "book", None)
                self.sound_played = True

            # === reset the buttons ===
            self.buttons_group = pygame.sprite.Group()
            if self.frame >= len(book_sprites[self.animations[self.state]["sprites"]]) - 1:
                if self.state == BookState.CLOSE_BOOK: self.running = False
                self.state = None

            else:
                self.pos = self.animations[self.state]["offset"]
                self.frame += 0.17
                self.image = book_sprites[self.animations[self.state]["sprites"]][round(self.frame)]
        else:
            self.sound_played = False

            self.frame = 0
            self.image = UI["book"]["default_image"]
            self.pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                      WINDOW_HEIGHT // 2 - self.image.get_height() // 2)

    def contents(self, window):

        title = self.content[self.current_page]["title"]
        if self.content[self.current_page]["content"]:
            self.content[self.current_page]["content"](window)

        title_pos = self.base_pos + (58, 30)
        divider = UI["book"]["divider"]
        divider_pos = title_pos + (0, 8)
        window.blit(divider, divider_pos)
        window.blit(title, title_pos)

    def info_page(self, window):


        font = pygame.font.Font(FONT_ONE, 16)

        long_divider = UI["book"]["long_divider"]
        window.blit(long_divider, self.base_pos + (68, 118))

        # === character icon and switching between team members ===
        team_members = [self.player, *self.player.active_allies]

        character_icon = UI["icons"][team_members[self.team_member_index].name.lower()]
        character_icon_pos = self.base_pos + (65, 75)
        window.blit(character_icon, character_icon_pos)

        mouse = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]

        if character_icon.get_rect(topleft = character_icon_pos).collidepoint(mouse) and press\
                and pygame.time.get_ticks() >= self.click_delay:

            self.team_member_index = min(self.team_member_index + 1, len(team_members))

            if self.team_member_index == len(team_members):
                self.team_member_index = 0

            self.selected_team_member = team_members[self.team_member_index]


            self.click_delay = pygame.time.get_ticks() + 300


        base_stats = {
            "HP": f"{str(self.selected_team_member.hp)}/{str(self.selected_team_member.max_hp)}",
            "MANA": f"{str(self.selected_team_member.mana)}/{str(self.selected_team_member.max_mana)}",
            "LEVEL": str(self.selected_team_member.level),

            "EXP": f"{str(self.selected_team_member.exp)}/{str(self.selected_team_member.max_exp)}"
        }

        base_y = 58
        base_x = 105
        distance_between = 14
        for index, key in enumerate(list(base_stats.keys())):
            position = self.base_pos + (base_x, base_y + distance_between * index)
            text = font.render(key, True, (255, 238, 131))
            window.blit(text, position)
        base_x = 185
        for index, value in enumerate(list(base_stats.values())):
            position = self.base_pos + (base_x, base_y + distance_between * index)
            text = font.render(value, True, (255, 255, 255))
            window.blit(text, position)

        core_stats = self.selected_team_member.core_stats

        base_y = 125
        base_x = 70
        distance_between = 18
        for index, key in enumerate(list(core_stats.keys())):
            position = self.base_pos + (base_x, base_y + distance_between * index)
            text = font.render(key.upper(), True, (255, 238, 131))
            window.blit(text, position)

        base_x = 185
        distance_between = 18
        for index, value in enumerate(list(core_stats.values())):
            position = self.base_pos + (base_x, base_y + distance_between * index)
            text = font.render(str(value).upper(), True, (255, 255, 255))
            window.blit(text, position)

        if self.selected_team_member.stat_points:
            base_x = 70
            text = font.render(str(f"STAT POINTS: {str(self.selected_team_member.stat_points)}").upper(), True, (255, 255, 255))
            position = self.base_pos + (base_x, self.book_height // 1.37)
            window.blit(text, position)

            base_x = 208
            distance_between = 18

            if not self.buttons_group:
                for index in range(len(list(core_stats.values()))):
                    position = self.base_pos + (base_x, base_y + distance_between * index - 6)
                    Button(self.buttons_group, None, self.level_up, "", ButtonVariant.SMALL, position, False)

            for button in self.buttons_group:
                button.draw(window)

    def level_up(self):
        for button in self.buttons_group:
            if button.delete:
                index = list(self.buttons_group).index(button)

                stat = list(self.player.core_stats.keys())[index]
                self.selected_team_member.core_stats[stat] += 1
                self.selected_team_member.stat_points -= 1
                self.selected_team_member.recalculate_stats()
                self.buttons_group = pygame.sprite.Group()

    def inventory_page(self, window):
        base_x = 54
        base_y = 64
        distance = 42
        items = []
        hover_surface = pygame.Surface((192, 32))
        hover_surface.set_alpha(100)
        hover_surface.fill((255, 255, 255))

        for index, item in enumerate(self.player.inventory.items.keys()):

            # === item select rect ===
            rect_pos = self.base_pos + (base_x, base_y + distance * index)

            item_rect = pygame.Rect(rect_pos.x, rect_pos.y, 192, 32)
            items.append((item_rect, item))

            window.blit(UI["book"]["divider"], rect_pos + (2 ,18))


            # === item slot ===
            item_slot = UI["book"]["item_slot"]
            window.blit(item_slot, rect_pos)

            # === item image ===
            item_image = ITEMS[item]["image"]
            item_image.set_alpha(UI_OPACITY)
            item_image_pos = rect_pos
            window.blit(item_image, item_image_pos)

            # === item quantity ===
            item_quantity = self.player.inventory.items[item]
            quantity_surface = self.font.render(str(item_quantity), True, (255, 255, 255))
            quantity_pos = item_image_pos + (24, 16)
            window.blit(quantity_surface, quantity_pos)

            # === item name ===
            item_name_pos = rect_pos + (36, 0)
            item_name = item.replace("_", " ").upper()
            item_name_surface = self.font.render(item_name, True, (255, 255, 255))
            window.blit(item_name_surface, item_name_pos)

            # === item description ===
            item_desc = ITEMS[item]["inventory_desc"].upper()
            item_desc_surface = self.font.render(item_desc, True, (164, 125, 114))
            item_desc_pos = item_name_pos + (0, 12)
            window.blit(item_desc_surface, item_desc_pos)


        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        mouse_press = pygame.mouse.get_pressed()[2]

        for rect, item in items:
            if rect.collidepoint(mouse_pos):
                if mouse_press and not self.player.inventory.items[item] <= 0:
                    self.buttons_group = pygame.sprite.Group()

                    self.selected_item = (rect, item)

                if not self.selected_item:
                    window.blit(hover_surface, rect.topleft)

        if self.selected_item:
            rect, item = self.selected_item
            window.blit(hover_surface, rect.topleft)
            window.blit(UI["battle_menu"]["skills_background"], pygame.Vector2(rect.topleft) + (0, 32))

            # === buttons and stuff ===
            if not self.buttons_group:
                pos = pygame.Vector2(self.selected_item[0].topleft)
                Button(self.buttons_group, None, None, "USE", ButtonVariant.WIDE, pos + (6,56), False)
                Button(self.buttons_group, None, None, None, ButtonVariant.EXIT, pos + (160, 28), False)


        for button in self.buttons_group:
            button.draw(window)

            if button.clicked and not button.text_string:
                self.selected_item = None
                self.buttons_group = pygame.sprite.Group()
                break

            elif button.clicked and button.text_string == "USE":
                item = self.selected_item[1]
                if pygame.time.get_ticks() >= self.click_delay:
                    self.player.use_item(item)
                    self.click_delay = pygame.time.get_ticks() + 500

                if self.player.inventory.items[item] <= 0:
                    self.selected_item = None
                    self.buttons_group = pygame.sprite.Group()
                    break
                else:
                    button.clicked = False
                    button.delete = False


