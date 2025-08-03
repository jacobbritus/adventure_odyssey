import pygame

from classes.states import BookState, CombatMenuState, ButtonVariant
from other.play_sound import play_sound
from other.settings import *

class HpBar:
    def __init__(self, owner, y_offset):
        self.owner = owner
        self.has_mana = hasattr(self.owner, "mana")

        # === images ===
        self.font = pygame.font.Font(FONT_ONE, 16)
        self.name = self.font.render(str(owner.name).upper(), True, (255, 255, 255))
        self.name_bg = self.font.render(str(owner.name).upper(), True, (81, 57, 44))

        # === positions ===
        self.background_box_pos = pygame.Vector2(WINDOW_WIDTH - HP_BAR_BG.get_width(), WINDOW_HEIGHT - COMBAT_MENU_MAIN_BG.get_height() + y_offset)
        name_pos_offset = (36, 2)
        self.name_pos = self.background_box_pos + name_pos_offset
        self.name_bg_pos = self.name_pos + (2, 0)
        self.name_bg_pos2 = self.name_pos + (2, 2)

        hp_bar_offset = (165, 12)
        self.hp_bar_pos = self.background_box_pos + hp_bar_offset
        mana_bar_offset = (257, 12)
        self.mana_bar_pos = self.background_box_pos + mana_bar_offset

        # === character icon ===
        if self.has_mana:
            char_icon = self.owner.icon
            bg_borders_length = 4
            char_icon_rect = pygame.Rect(0, char_icon.get_height() - NEW_HP_BG.get_height(), 32, NEW_HP_BG.get_height() - bg_borders_length)
            self.char_icon = char_icon.subsurface(char_icon_rect).copy()
            char_icon_offset = (4, 2)
            self.char_icon_pos = self.background_box_pos + char_icon_offset

        # === hp and mana text ===
        self.hp_text_surface = self.font.render(f"{self.owner.hp}/{self.owner.max_hp}", True, (255, 255, 255))
        hp_text_offset = (74 - self.hp_text_surface.get_width(), -14)
        self.hp_text_pos = self.hp_bar_pos + hp_text_offset
        self.hp_text_bg_surface = self.font.render(f"{self.owner.hp}/{self.owner.max_hp}", True, (81, 57, 44))
        self.hp_text_bg1_pos = self.hp_text_pos + (2, 0)
        self.hp_text_bg2_pos = self.hp_text_pos + (2, 2)

        self.hp = self.owner.hp

        if self.has_mana:
            self.mana = self.owner.mana
            self.mana_text_surface = self.font.render(f"{self.owner.mana}/{self.owner.max_mana}", True, (255, 255, 255))
            mana_text_offset = (74 - self.mana_text_surface.get_width(), -14)
            self.mana_text_pos = self.mana_bar_pos + mana_text_offset
            self.mana_text_bg_surface = self.font.render(f"{self.owner.mana}/{self.owner.max_mana}", True, (81, 57, 44))
            self.mana_text_bg1_pos = self.mana_text_pos + (2, 0)
            self.mana_text_bg2_pos = self.mana_text_pos + (2, 2)


        # === stat bars ===
        self.normal_speed = 2
        self.delayed_speed = 0.25
        self.bg_bar = BG_BAR

        self.bars = {
            "hp":{
                "image": NEW_HP_BAR,

                "current_width": int(NEW_HP_BAR.get_width() * self.owner.hp / self.owner.max_hp),
                "target_width": NEW_HP_BAR.get_width(),
                "bar": None,
                "bg_bar": None,
                "bg_width": int(NEW_HP_BAR.get_width() * self.owner.hp / self.owner.max_hp),
            }
        }
        if self.has_mana:
            self.bars.update({
                "mana": {
                    "image": NEW_MANA_BAR,
                    "current_width": int(NEW_MANA_BAR.get_width() * self.owner.mana / self.owner.max_mana),
                    "target_width": NEW_MANA_BAR.get_width(),
                    "bar": None,
                    "bg_bar": None,
                    "bg_width": int(NEW_MANA_BAR.get_width() * self.owner.mana / self.owner.max_mana),
                }})

        self.opacity = 155

    def mask(self, window, elements):
        """Used to darken unselected enemy hp bars."""
        if self.owner.type == "enemy" and not self.owner.selected and not self.owner.death:
            for item, pos in elements:
                mask = pygame.mask.from_surface(item).to_surface(setcolor=(0, 0, 0, 100),
                                                                       unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pos)

    def set_bars(self) -> None:
        """Update the hp bar target length, making it relative to the current-hp to max-hp ratio."""
        ratio = max(0, min(self.owner.hp / self.owner.max_hp, 1))
        target = int(NEW_HP_BAR.get_width() * ratio)
        self.bars["hp"]["target_width"] = target

        if self.has_mana:
            ratio = max(0, min(self.owner.mana / self.owner.max_mana, 1))
            target = int(NEW_MANA_BAR.get_width() * ratio)
            self.bars["mana"]["target_width"] = target

    def update_bars(self) -> None:
        """Slowly increase or decrease the current bar width until equal to the target width."""
        stats = ["hp", "mana"] if self.has_mana else ["hp"]
        for key in stats:
            bar = self.bars[key]

            # === modify the foreground bar ===
            if bar["current_width"] < bar["target_width"]:
                bar["current_width"] = min(bar["current_width"] + self.delayed_speed, bar["target_width"])
            else:
                bar["current_width"] = max(bar["current_width"] - self.normal_speed, bar["target_width"])

            # === modify the background bar ===
            if bar["bg_width"] < bar["target_width"]:
                bar["bg_width"] = min(bar["bg_width"] + self.normal_speed , bar["target_width"])
            else:
                bar["bg_width"] = max(bar["bg_width"] - self.delayed_speed, bar["target_width"])

            crop = pygame.Rect(0, 0, bar["current_width"], bar["image"].get_height())
            bar["bar"] = bar["image"].subsurface(crop).copy()

            bg_crop = pygame.Rect(0, 0, int(bar["bg_width"]), bar["image"].get_height())
            bar["bg_bar"] = self.bg_bar.subsurface(bg_crop).copy()

    def draw_components(self):
        if self.owner.type == "enemy":
            return [
                (NEW_HP_BOX, self.hp_bar_pos),
                (self.bars["hp"]["bg_bar"], self.hp_bar_pos),
                (self.bars["hp"]["bar"], self.hp_bar_pos),
            (self.hp_text_bg_surface, self.hp_text_bg1_pos),
            (self.hp_text_bg_surface, self.hp_text_bg2_pos),
            (self.hp_text_surface, self.hp_text_pos)]
        else:
            return [
                (HP_BAR_BG, self.background_box_pos),
                (self.char_icon, self.char_icon_pos),
                (self.hp_text_bg_surface, self.hp_text_bg1_pos),
                (self.hp_text_bg_surface, self.hp_text_bg2_pos),
                (self.hp_text_surface, self.hp_text_pos),

                (self.mana_text_bg_surface, self.mana_text_bg1_pos),
                (self.mana_text_bg_surface, self.mana_text_bg2_pos),
                (self.mana_text_surface, self.mana_text_pos),

                (self.name_bg, self.name_bg_pos2),
                (self.name_bg, self.name_bg_pos),
                (self.name, self.name_pos),
                (self.bars["mana"]["bg_bar"], self.mana_bar_pos),
                (self.bars["hp"]["bg_bar"], self.hp_bar_pos),

                (self.bars["hp"]["bar"], self.hp_bar_pos),
                (self.bars["mana"]["bar"], self.mana_bar_pos)]

    def update_stat_text(self) -> None:
        def animate_stat(current, target, speed=0.08):
            if current > target:
                return max(current - speed, target)
            else:
                return min(current + speed, target)

        def render_stat_text(value, max_value, font, fg_color=(255, 255, 255), bg_color=(81, 57, 44)):
            text = f"{int(value)}/{max_value}"
            return (
                font.render(text, True, fg_color),
                font.render(text, True, bg_color)
            )

        # Animate and render HP
        self.hp = animate_stat(self.hp, self.owner.hp)
        self.hp_text_surface, self.hp_text_bg_surface = render_stat_text(self.hp, self.owner.max_hp, self.font)

        hp_text_offset = (74 - self.hp_text_surface.get_width(), -14)

        self.hp_text_pos = self.hp_bar_pos + hp_text_offset
        self.hp_text_bg1_pos = self.hp_text_pos + (2, 0)
        self.hp_text_bg2_pos = self.hp_text_pos + (0, 2)

        # Animate and render Mana (if applicable)
        if self.has_mana:
            self.mana = animate_stat(self.mana, self.owner.mana)
            self.mana_text_surface, self.mana_text_bg_surface = render_stat_text(self.mana, self.owner.max_mana,
                                                                                 self.font)

            mana_text_offset = (74 - self.mana_text_surface.get_width(), -14)
            self.mana_text_pos = self.mana_bar_pos + mana_text_offset
            self.mana_text_bg1_pos = self.mana_text_pos + (2, 0)
            self.mana_text_bg2_pos = self.mana_text_pos + (2, 2)

    def dynamic_pos(self, dynamic_pos):
        self.hp_bar_pos = dynamic_pos
        hp_text_offset = (74 - self.hp_text_surface.get_width(), -14)

        self.hp_text_pos = self.hp_bar_pos + hp_text_offset
        self.hp_text_bg1_pos = self.hp_text_pos + (2, 0)
        self.hp_text_bg2_pos = self.hp_text_pos + (0, 2)

    def draw(self, window, dynamic_pos: None or pygame.Vector2) -> None:
        """Draw all the images on the window"""
        self.set_bars()
        self.update_bars()

        elements = self.draw_components()
        self.update_stat_text()

        if dynamic_pos:
            self.dynamic_pos(dynamic_pos)

        for surface, pos in elements:
            if self.owner.type == "enemy":
                surface.set_alpha(self.opacity)
            if self.owner.death and self.bars["hp"]["bg_width"] == 0:
                self.opacity -= 5
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
        self.rect: pygame.Rect = self.image.get_rect(topleft = self.pos)

        # === functioning ===
        self.function = function
        self.parameter = parameter
        self.disabled = disabled

        # === text ===
        self.text_string: str = text
        self.font: pygame.font = pygame.font.Font(FONT_ONE, 16)
        self.color: tuple = (99, 61, 76)

        if text:
            if text in MOVES.keys():
                self.text_string = text.replace("_", " ").upper()
                self.text_surface = self.font.render(self.text_string, True, self.color)
                self.text_size = self.text_surface.get_size()
                self.text_position = pygame.Vector2(self.rect.left + 5 , self.rect.centery - self.text_size[1] // 2)

                self.mana_cost = str(MOVES[text]["mana"])
                self.mana_text_surface = self.font.render(self.mana_cost, True, self.color)
                self.mana_cost_position = (self.rect.right - 12, self.rect.centery - self.mana_text_surface.get_height() // 2)

            else:
                self.mana_text_surface = None
                self.text_string = text

                self.text_surface = self.font.render(self.text_string, True, self.color)


                self.text_size = self.text_surface.get_size()
                self.text_position = (self.rect.centerx - self.text_size[0] // 2, self.rect.centery - self.text_size[1] // 2)
        else:
            self.text_surface = None
            self.mana_text_surface = None

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
        if variant == ButtonVariant.DEFAULT:
            return BUTTON_SIMPLE_NORMAL, BUTTON_SIMPLE_PRESSED, BUTTON_SIMPLE_SELECTED

        if variant == ButtonVariant.WIDE:
            return BUTTON_LARGE_SIMPLE_NORMAL, BUTTON_LARGE_SIMPLE_PRESSED, BUTTON_LARGE_SIMPLE_SELECTED

        if variant == ButtonVariant.SMALL:
            return BUTTON_SMALL_NORMAL, BUTTON_SMALL_PRESSED, BUTTON_SMALL_SELECTED

        return None

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

                if not self.hover_sound_played: play_sound("ui", "hover", None)
                self.hovering = True

                self.hover_sound_played = True
                self.click_sound_played = False
        else:
            self.image = self.image_normal
            self.color = (99, 61, 76)
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
        self.update()
        window.blit(self.image, self.pos)

        if self.text_surface:
            self.text_surface = self.font.render(self.text_string, True, self.color)
            window.blit(self.text_surface, self.text_position)
        if self.mana_text_surface:
            self.mana_text_surface = self.font.render(self.mana_cost, True, self.color)
            window.blit(self.mana_text_surface, self.mana_cost_position)

        if self.disabled:
            mask = pygame.mask.from_surface(self.image).to_surface(
                setcolor=(255, 0, 0, 100),
                unsetcolor=(0, 0, 0, 0))
            window.blit(mask, self.pos)

class CombatMenu:
    def __init__(self, player_skills: list[str], functions):
        # === player's attacks and functions ===
        # e.g., attack(name of button clicked) and player_run(no parameter)
        self.player_skills = player_skills
        self.formatted_skills: list[str] = [attack.replace("_", " ").upper() for attack in player_skills]
        self.attack_function = functions[0]
        self.run_function = functions[1]

        # === sprite groups for the buttons ===
        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.skills_buttons: pygame.sprite.Group = pygame.sprite.Group()

        # === main menu position ===
        self.main_menu_bg_pos = pygame.Vector2(0, WINDOW_HEIGHT - COMBAT_MENU_MAIN_BG.get_height() )

        # === skills menu position ===
        self.skills_bg_pos = self.main_menu_bg_pos + (112, 0)

        # === end menu position ===
        self.end_menu_pos = pygame.Vector2(WINDOW_WIDTH // 2 - SKILLS_MENU_BG.get_width() // 2,
                                           WINDOW_HEIGHT // 2 - SKILLS_MENU_BG.get_height() // 2)
        self.victory_text_pos = pygame.Vector2(WINDOW_WIDTH // 2 - VICTORY_TEXT.get_width() // 2,
                                           self.end_menu_pos.y + 4)

        # === enum states ===
        self.state = CombatMenuState.MAIN_MENU

        # === player's mana amount ===
        self.player_mana: int = 0

    def draw(self, window: pygame.Surface, current_mana: int) -> None:
        """Draw the buttons and images associated with the current state."""
        self.update()
        self.player_mana = current_mana

        if not self.state == CombatMenuState.END_MENU and self.state:
            window.blit(COMBAT_MENU_MAIN_BG, self.main_menu_bg_pos)
            self.draw_main_menu()

        # === buttons are drawn through the main menu skills button's function ===
        if self.state == CombatMenuState.SKILLS_MENU:
            window.blit(SKILLS_MENU_BG, self.skills_bg_pos)

        elif self.state == CombatMenuState.END_MENU:
            window.blit(SKILLS_MENU_BG, self.end_menu_pos)
            window.blit(VICTORY_TEXT, self.victory_text_pos)
            self.draw_end_menu()

        for button in self.buttons_group:
            button.draw(window)

    def update(self) -> None:
        """Update the state based on the button clicked."""
        for button in self.buttons_group:
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

            Button(self.buttons_group, None, None, "SKILLS", ButtonVariant.DEFAULT,
                   pos, False)

            y_offset = (0, 34)
            Button(self.buttons_group, None, self.run_function, "ITEMS", ButtonVariant.DEFAULT,
                   pos + y_offset, False)

            y_offset = (0, 68)
            Button(self.buttons_group, None, self.run_function, "RUN", ButtonVariant.DEFAULT,
                   pos + y_offset, False)

    def draw_end_menu(self) -> None:
        """Draw the buttons for the end menu."""
        if not self.buttons_group:
            button_offset = (6, 92)
            pos = self.end_menu_pos + button_offset

            Button(self.buttons_group, None, self.run_function, "END", ButtonVariant.WIDE, pos, False)

    def draw_skills_menu(self) -> None:
        """Draw the buttons for the skills menu."""
        self.skills_buttons = pygame.sprite.Group()

        def can_use_skill(name, mana_amount) -> bool:
            """check if the player has enough mana"""
            cost = MOVES[name]["mana"]
            return mana_amount >= cost

        if not self.skills_buttons:
            for index, skill_name in enumerate(self.player_skills):

                y_offset = (0, 20 * index)
                padding = (6, 6)
                pos = self.skills_bg_pos + padding + y_offset
                if can_use_skill(skill_name, self.player_mana):
                    Button([self.buttons_group, self.skills_buttons], skill_name, self.attack_function, skill_name, ButtonVariant.WIDE, pos, False)
                else:
                    Button([self.buttons_group, self.skills_buttons], skill_name, self.attack_function, skill_name, ButtonVariant.WIDE, pos, True)

class MenuBook:
    def __init__(self, player):
        self.player = player
        self.image = BOOK_IMAGE
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

        self.content = [{"title": INFO_TITLE, "content": self.info_page}]
        self.current_page = 0
        self.buttons_group = pygame.sprite.Group()

    def draw(self, window):
        self.update()
        if self.running:
            # self.image.set_alpha(235)
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
            self.image = BOOK_IMAGE
            self.pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                      WINDOW_HEIGHT // 2 - self.image.get_height() // 2)



    def contents(self, window):
        title = self.content[self.current_page]["title"]
        self.content[self.current_page]["content"](window)

        container_width = 100
        title_pos = self.base_pos + (container_width - title.get_width() // 2, 28)
        divider = DIVIDER
        divider_pos = title_pos + (title.get_width() // 2 - divider.get_width() // 2 + 16, 8)
        window.blit(divider, divider_pos)
        window.blit(title, title_pos)

    def info_page(self, window):
        image = INFO_PAGE
        image_pos = self.base_pos + (68, 64)
        window.blit(image, image_pos)

        font = pygame.font.Font(FONT_ONE, 16)

        base_stats = {
            "LEVEL": str(self.player.level),
            "HP": f"{str(self.player.hp)}/{str(self.player.max_hp)}",
            "MANA": str(self.player.mana),
            "EXP": f"{str(self.player.exp)}/{str(self.player.exp_to_level)}"
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



