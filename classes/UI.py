import pygame

from classes.states import BookState, CombatMenuState, ButtonVariant
from other.play_sound import play_sound
from other.settings import *
from other.text_bg_effect import text_bg_effect


class StatusBar:
    def __init__(self, owner, y_offset):
        self.owner = owner
        self.has_mana = hasattr(owner, "mana")
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

        self.normal_speed = None
        self.delayed_speed = None
        self.bg_bar = None

        self.bars = None

        self.setup_small_hp_bar()
        self.stats = ["hp"]

        self.opacity = UI_OPACITY

        if self.owner.type == "player":
            self.stats.extend(["mana", "exp"])

            self.setup_hero_status_bar(y_offset)
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

        self.background_box_pos = pygame.Vector2(WINDOW_WIDTH - bg_width, WINDOW_HEIGHT - menu_height + y_offset)
        self.name_surface = self.font.render(str(self.owner.name).upper(), True, (255, 255, 255))
        self.name_pos = self.background_box_pos + pygame.Vector2(36, 2)

        icon = self.owner.icon
        rect = pygame.Rect(0, icon.get_height() - bg_height, 32, bg_height - 4)
        self.char_icon = icon.subsurface(rect).copy()
        self.char_icon_pos = self.background_box_pos + pygame.Vector2(4, 2)

        # === bar positions ===
        self.hp_bar_pos = self.background_box_pos + (165, 12)
        self.mana_bar_pos = self.background_box_pos + (257, 12)
        self.exp_bar_pos = self.background_box_pos + (165, 12)

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
        self.exp_icon = self.font.render("EXP", True, (153, 229, 80))
        self.exp_icon_pos = self.exp_bar_pos + pygame.Vector2(-24, -7)

        self.exp = self.owner.exp
        self.exp_text_surface = self.font.render(f"{self.owner.exp}/{self.owner.max_exp}", True, (255, 255, 255))
        self.exp_text_pos = self.exp_bar_pos + (ui["exp_box"].get_width() - self.exp_text_surface.get_width(), -14)


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
            additional_elements = [
                (UI["status_bar"]["exp_box"], self.exp_bar_pos),
                (self.bars["exp"]["bar"], self.exp_bar_pos),
                (self.exp_text_surface, self.exp_text_pos),

                (self.exp_icon, self.exp_icon_pos),


            ]
            elements += additional_elements

            additional_text_bgs = [
                *text_bg_effect(f"EXP", self.font, self.exp_icon_pos, None),

                 *text_bg_effect(f"{int(self.exp)}/{self.owner.max_exp}", self.font, self.exp_text_pos, None),
            ]
            text_bgs += additional_text_bgs

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
                mask = pygame.mask.from_surface(self.bars["exp"]["bar"]).to_surface(setcolor=(170, 250, 170, min(self.opacity, 250)),
                                                                 unsetcolor=(0, 0, 0, 0))
                window.blit(mask, self.exp_bar_pos)
                self.opacity += 10



            else:
                self.opacity = 0

    def interact(self):
        mouse_pos = pygame.mouse.get_pos()

        rect = self.bg_bar.get_rect(topleft = self.background_box_pos)

        print(rect)

        if rect.collidepoint(mouse_pos):
            self.opacity = UI_OPACITY
        else:
            self.opacity = 150

    def draw(self, window, display_exp: bool) -> None:
        """Draw all the images on the window"""
        self.display_exp = display_exp

        self.set_bars()

        self.update_bars()

        self.update_stat_text()


        elements = self.draw_components()
        self.interact()
        for surface, pos in elements:
            surface.set_alpha(self.opacity)

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



    def draw(self, window, dynamic_pos, *args) -> None:
        self.dynamic_pos(dynamic_pos)


        self.set_bars()
        self.update_bars()

        elements = self.draw_components()
        self.update_stat_text()


        for surface, pos in elements:
            if self.owner.death and self.bars["hp"]["bg_width"] == 0:
                self.opacity -= 1
                surface.set_alpha(max(0, self.opacity))

            window.blit(surface, pos)

        self.mask(window, elements)


class Button(pygame.sprite.Sprite):
    def __init__(self, group, parameter, function, text: str, variant, pos: pygame.Vector2, disabled: bool):
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
        self.color = self.mana_color = (99, 61, 76)

        if text:
            if text in MOVES.keys():
                self.text_string = text.replace("_", " ").upper()
                self.text_surface = self.font.render(self.text_string, True, self.color)
                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.left + 5, self.rect.centery - self.text_size[1] // 2)

                self.mana_cost = str(MOVES[text]["mana"])
                self.mana_cost_surface = self.font.render(self.mana_cost, True, self.color)
                self.mana_cost_position = pygame.Vector2(self.rect.right - 32,
                                                         self.rect.centery - self.mana_cost_surface.get_height() // 2 - 1)

                self.mana_icon = self.font.render("SP", True, self.color)

                self.mana_icon_pos = self.mana_cost_position + (12, 0)
            else:
                self.mana_cost_surface = None
                self.text_string = text

                self.text_surface = self.font.render(self.text_string, True, self.color)

                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.centerx - self.text_size[0] // 2,
                                                    self.rect.centery - self.text_size[1] // 2)
        else:
            self.text_surface = None
            self.mana_cost_surface = None

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
        if variant == ButtonVariant.MEDIUM:
            buttons = [root[variant.value + "_" + status] for status in statuses]

        elif variant == ButtonVariant.WIDE:
            buttons = [root[variant.value + "_" + status] for status in statuses]

        elif variant == ButtonVariant.SMALL:
            buttons = [root[variant.value + "_" + status] for status in statuses]


        else:
            buttons = None


        return buttons

    def update(self):
        self.kill_delay()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed:
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
                self.color = (236, 226, 196)
                self.mana_color = (99, 155, 255)

                if not self.hover_sound_played: play_sound("ui", "hover", None)
                self.hovering = True

                self.hover_sound_played = True
                self.click_sound_played = False
        else:
            self.image = self.image_normal
            self.color = (99, 61, 76)
            self.mana_color = (60, 109, 196)

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

    def draw(self, window, opacity):
        window.blit(self.image, self.pos)

        if self.text_surface:
            self.text_surface = self.font.render(self.text_string, True, self.color)
            self.text_surface.set_alpha(opacity)
            window.blit(self.text_surface, self.text_position)

        if self.mana_cost_surface:
            self.mana_cost_surface = self.font.render(self.mana_cost, True, self.mana_color)
            text_bg_effect(self.mana_cost, self.font, self.mana_cost_position, window)
            window.blit(self.mana_cost_surface, self.mana_cost_position)

            self.mana_icon = self.font.render("SP", True, self.mana_color)
            text_bg_effect("SP", self.font, self.mana_icon_pos, window)
            window.blit(self.mana_icon, self.mana_icon_pos)

        if self.disabled:
            mask = pygame.mask.from_surface(self.image).to_surface(
                setcolor=(255, 0, 0, 100),
                unsetcolor=(0, 0, 0, 0))
            window.blit(mask, self.pos)

        self.update()



class BattleMenu:
    def __init__(self, performer, functions):
        # === player's attacks and functions ===
        # e.g., attack(name of button clicked) and player_run(no parameter)
        self.performer = performer
        self.formatted_skills: list[str] = [attack.replace("_", " ").upper() for attack in self.performer.skills]
        self.attack_function = functions[0]
        self.run_function = functions[1]

        # === sprite groups for the buttons ===
        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.skills_buttons: pygame.sprite.Group = pygame.sprite.Group()

        # === main menu position ===
        self.main_menu_bg_pos = pygame.Vector2(0, WINDOW_HEIGHT - UI["battle_menu"]["main_background"].get_height())

        # === skills menu position ===
        self.skills_bg_pos = self.main_menu_bg_pos + (112, 0)

        # === end menu position ===
        self.end_menu_pos = pygame.Vector2(WINDOW_WIDTH // 2 - UI["battle_menu"]["skills_background"].get_width() // 2,
                                           WINDOW_HEIGHT // 2 - UI["battle_menu"]["skills_background"].get_height() // 2)
        self.victory_text_pos = pygame.Vector2(WINDOW_WIDTH // 2 - UI["titles"]["victory_title"].get_width() // 2,
                                               self.end_menu_pos.y + 4)

        # === enum states ===
        self.state = CombatMenuState.MAIN_MENU
        self.opacity = 0
        self.visible = False
        self.main_menu_bg = UI["battle_menu"]["main_background"]
        self.skills_menu_bg = UI["battle_menu"]["skills_background"]
        self.main_menu_bg.set_alpha(self.opacity)
        self.skills_menu_bg.set_alpha(self.opacity)


    def draw(self, window: pygame.Surface, performer) -> None:
        """Draw the buttons and images associated with the current state."""
        if self.visible:
            self.opacity = min(self.opacity + 10, UI_OPACITY)

        else:
            self.opacity = max(self.opacity - 10, 0)

        self.main_menu_bg.set_alpha(self.opacity)
        self.skills_menu_bg.set_alpha(self.opacity)

        self.update()
        self.performer = performer
        if not self.state == CombatMenuState.END_MENU and self.state:
            window.blit(self.main_menu_bg, self.main_menu_bg_pos)
            self.draw_main_menu()

        # === buttons are drawn through the main menu skills button's function ===
        if self.state == CombatMenuState.SKILLS_MENU:
            window.blit(self.skills_menu_bg, self.skills_bg_pos)

        elif self.state == CombatMenuState.END_MENU:
            # window.blit(UI["battle_menu"]["skills_background"], self.end_menu_pos)
            # window.blit(UI["titles"]["victory_title"], self.victory_text_pos)
            self.draw_end_menu()

        for button in self.buttons_group:
            button.draw(window, self.opacity)

    def update(self) -> None:
        """Update the state based on the button clicked."""
        for button in self.buttons_group:
            button.image.set_alpha(self.opacity)
            if button.delete:
                # === main menu <-> skills menu ===
                if button.text_string == "SKILLS":
                    # === close skills menu ===
                    if self.state == CombatMenuState.SKILLS_MENU:
                        self.state = CombatMenuState.MAIN_MENU
                        for other_button in self.skills_buttons:
                            other_button.kill()

                    # === open skills menu ===
                    else:
                        self.state = CombatMenuState.SKILLS_MENU
                        self.draw_skills_menu()  # re-populate skill buttons

                    # reset the main menu button pressed
                    button.clicked = False
                    button.delete = False
                    button.delete_delay = 0

                # === skills menu -> player animation ===
                elif button.text_string in self.formatted_skills:
                    self.state = None
                    self.buttons_group = pygame.sprite.Group()

                # === end screen -> overworld ===
                elif button.text_string == "END":
                    self.state = None
                    self.buttons_group = pygame.sprite.Group()

    def draw_main_menu(self) -> None:
        """Draw the buttons for the main menu."""
        if not self.buttons_group:
            button_offset = (6, 7)
            pos = self.main_menu_bg_pos + button_offset

            Button(self.buttons_group, None, None, "SKILLS", ButtonVariant.MEDIUM,
                   pos, False)

            y_offset = (0, 34)
            Button(self.buttons_group, None, self.run_function, "ITEMS", ButtonVariant.MEDIUM,
                   pos + y_offset, False)

            y_offset = (0, 68)
            Button(self.buttons_group, None, self.run_function, "RUN", ButtonVariant.MEDIUM,
                   pos + y_offset, False)

    def draw_end_menu(self) -> None:
        """Draw the buttons for the end menu."""
        if not self.buttons_group:
            button_offset = (6, 92)
            pos = self.end_menu_pos + button_offset
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
            cost = MOVES[name]["mana"]
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


class MenuBook:
    def __init__(self, player):
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

        self.content = [{"title": UI["titles"]["info_title"], "content": self.info_page}]
        self.current_page = 0
        self.buttons_group = pygame.sprite.Group()

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
            if self.frame >= len(book_sprites[self.animations[self.state]["sprites"]]) - 1:
                if self.state == BookState.CLOSE_BOOK: self.running = False
                self.state = None

            else:
                self.pos = self.animations[self.state]["offset"]
                self.frame += 0.17
                self.image = book_sprites[self.animations[self.state]["sprites"]][round(self.frame)]
        else:
            self.frame = 0
            self.image = UI["book"]["default_image"]
            self.pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                      WINDOW_HEIGHT // 2 - self.image.get_height() // 2)

    def contents(self, window):
        title = self.content[self.current_page]["title"]
        self.content[self.current_page]["content"](window)

        container_width = 100
        title_pos = self.base_pos + (container_width - title.get_width() // 2, 28)
        divider = UI["book"]["divider"]
        divider_pos = title_pos + (title.get_width() // 2 - divider.get_width() // 2 + 16, 8)
        window.blit(divider, divider_pos)
        window.blit(title, title_pos)

    def info_page(self, window):
        image = UI["book"]["info_page"]
        image_pos = self.base_pos + (68, 64)
        window.blit(image, image_pos)

        font = pygame.font.Font(FONT_ONE, 16)

        base_stats = {
            "LEVEL": str(self.player.level),
            "HP": f"{str(self.player.hp)}/{str(self.player.max_hp)}",
            "MANA": str(self.player.mana),
            "EXP": f"{str(self.player.exp)}/{str(self.player.max_exp)}"
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

        core_stats = self.player.core_stats

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

        if self.player.stat_points:
            base_x = 70
            text = font.render(str(f"STAT POINTS: {str(self.player.stat_points)}").upper(), True, (255, 255, 255))
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
                self.player.core_stats[stat] += 1
                self.player.stat_points -= 1
                self.player.recalculate_stats()
                self.buttons_group = pygame.sprite.Group()
