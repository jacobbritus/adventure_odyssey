import pygame

from classes.states import BookState, CombatMenuState, ButtonType
from other.play_sound import play_sound
from other.settings import *

class HpBar:
    def __init__(self, owner, y_offset):
        self.owner = owner
        self.mana = hasattr(self.owner, "mana")

        # === images ===
        font = pygame.font.Font(FONT_ONE, 16)
        self.name = font.render(str(owner.name).upper(), True, (236, 226, 196))
        self.name_bg = font.render(str(owner.name).upper(), True, (81, 57, 44))

        # === positions ===
        self.background_box_pos = pygame.Vector2(WINDOW_WIDTH - NEW_HP_BG.get_width() - 16, WINDOW_HEIGHT - COMBAT_MENU_MAIN_BG.get_height() - 16 + y_offset)
        name_pos_offset = (10, 2)
        self.name_pos = self.background_box_pos + name_pos_offset
        name_bg_offset = (2, 0)
        self.name_bg_pos = self.name_pos + name_bg_offset
        hp_bar_offset = (118, 4)
        self.hp_bar_pos = self.background_box_pos + hp_bar_offset
        mana_bar_offset = (114, 14)
        self.mana_bar_pos = self.background_box_pos + mana_bar_offset

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
        if self.mana:
            self.bars.update({"mana": {
                "image": NEW_MANA_BAR,
                "current_width": int(NEW_MANA_BAR.get_width() * self.owner.mana / self.owner.max_mana),
                "target_width": NEW_MANA_BAR.get_width(),
                "bar": None,
                "bg_bar": None,
                "bg_width": int(NEW_MANA_BAR.get_width() * self.owner.mana / self.owner.max_mana),
            }
            })

        self.opacity = 150

    def mask(self, window, elements):
        if self.owner.type == "enemy" and not self.owner.selected and not self.owner.death:
            for item, pos in elements:
                mask = pygame.mask.from_surface(item).to_surface(setcolor=(0, 0, 0, 100),
                                                                       unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pos)

    def set_bars(self) -> None:
        """Update the hp bar target length making it relative to the current-hp to max-hp ratio."""
        ratio = max(0, min(self.owner.hp / self.owner.max_hp, 1))
        target = int(NEW_HP_BAR.get_width() * ratio)
        self.bars["hp"]["target_width"] = target

        if self.mana:
            ratio = max(0, min(self.owner.mana / self.owner.max_mana, 1))
            target = int(NEW_MANA_BAR.get_width() * ratio)
            self.bars["mana"]["target_width"] = target

    def update_bars(self) -> None:
        """Slowly increase or decrease the current bar width until equal to the target width."""
        stats = ["hp", "mana"] if self.mana else ["hp"]
        for key in stats:
            bar = self.bars[key]

            # === modify the foreground bar ===
            if bar["current_width"] < bar["target_width"]:
                bar["current_width"] = min(bar["current_width"] + self.normal_speed, bar["target_width"])
            else:
                bar["current_width"] = max(bar["current_width"] - self.normal_speed, bar["target_width"])

            # === modify the background bar ===
            if bar["bg_width"] < bar["target_width"]:
                bar["bg_width"] = min(bar["bg_width"] + self.delayed_speed, bar["target_width"])
            else:
                bar["bg_width"] = max(bar["bg_width"] - self.delayed_speed, bar["target_width"])

            crop = pygame.Rect(0, 0, bar["current_width"], bar["image"].get_height())
            bar["bar"] = bar["image"].subsurface(crop).copy()

            bg_crop = pygame.Rect(0, 0, int(bar["bg_width"]), bar["image"].get_height())
            bar["bg_bar"] = self.bg_bar.subsurface(bg_crop).copy()

    def draw_components(self, dynamic_pos):
        if self.owner.type == "enemy":
            return [
                (NEW_HP_BOX, self.hp_bar_pos),
                (self.bars["hp"]["bg_bar"], self.hp_bar_pos),

                (self.bars["hp"]["bar"], self.hp_bar_pos)]
        else:
            return [
                (NEW_HP_BG, self.background_box_pos),
                (self.name_bg, self.name_bg_pos),
                (self.name, self.name_pos),
                (self.bars["mana"]["bg_bar"], self.mana_bar_pos),
                (self.bars["hp"]["bg_bar"], self.hp_bar_pos),

                (self.bars["hp"]["bar"], self.hp_bar_pos),
                (self.bars["mana"]["bar"], self.mana_bar_pos)]


    def draw(self, window, dynamic_pos: None or pygame.Vector2) -> None:
        """Draw all the images on the window"""
        self.set_bars()
        self.update_bars()

        elements = self.draw_components(dynamic_pos)
        if dynamic_pos: self.hp_bar_pos = dynamic_pos
        for surface, pos in elements:
            surface.set_alpha(self.opacity)
            if self.owner.death and self.bars["hp"]["bg_width"] == 0:
                self.opacity -= 5
                surface.set_alpha(max(0, self.opacity))
            window.blit(surface, pos)

        self.mask(window, elements)






class Button(pygame.sprite.Sprite):
    def __init__(self, group, action_type, action, text, size, pos, disabled:bool):
        super().__init__(group)
        self.text_size = size
        self.image_normal, self.image_pressed, self.image_selected = self.get_images()
        self.image = self.image_normal

        self.text_string = text

        self.pos = pos

        self.rect = self.image.get_rect(topleft = self.pos)

        self.action = action
        self.button_type = action_type
        self.disabled = disabled

        self.font = pygame.font.Font(FONT_ONE, 16)
        self.color = (236, 226, 196)

        if text:
            if text in MOVES.keys():
                self.text_string = text.replace("_", " ").upper()
                self.text = self.font.render(self.text_string, True, self.color)
                self.text_size = self.text.get_size()
                self.text_position = pygame.Vector2(self.rect.left + 5 , self.rect.centery - self.text_size[1] // 2)

                self.mana_cost = str(MOVES[text]["mana"])
                self.mana_text = self.font.render(self.mana_cost, True, self.color)
                self.mana_cost_position = (self.rect.right - 12, self.rect.centery - self.mana_text.get_height() // 2)


            else:
                self.mana_text = None
                self.text_string = text

                self.text = self.font.render(self.text_string, True, self.color)


                self.text_size = self.text.get_size()
                self.text_position = (self.rect.centerx - self.text_size[0] // 2, self.rect.centery - self.text_size[1] // 2)


        else:
            self.text = None
            self.mana_text = None



        # Status
        self.clicked = False
        self.hovering = False
        self.delete_delay = 0
        self.delete = False

        self.sound_played = False
        self.click_sound_played = False


    def get_images(self):
        if self.text_size == "simple":
            return BUTTON_SIMPLE_NORMAL, BUTTON_SIMPLE_PRESSED, BUTTON_SIMPLE_SELECTED

        if self.text_size == "simple_large":
            return BUTTON_LARGE_SIMPLE_NORMAL, BUTTON_LARGE_SIMPLE_PRESSED, BUTTON_LARGE_SIMPLE_SELECTED


        if self.text_size == "extra_small":
            return BUTTON_SMALL_NORMAL, BUTTON_SMALL_PRESSED, BUTTON_SMALL_SELECTED

        return None

    def update(self):
        self.kill_delay()

        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos) and press or self.clicked:
            self.image = self.image_pressed

            if not self.disabled:
                if not self.click_sound_played: play_sound("ui", "press", None)

                self.click_sound_played = True
                self.clicked = True
            else:
                if not self.click_sound_played: play_sound("ui", "disabled", None)
                self.click_sound_played = True

        elif self.rect.collidepoint(mouse_pos) or self.hovering:
            self.color = (236, 226, 196)

            self.image = self.image_selected
            if not self.sound_played: play_sound("ui", "hover", None)
            self.sound_played = True
            self.click_sound_played = False

        else:
            self.image = self.image_normal
            self.color = (99, 61, 76)
            self.hovering = False
            self.sound_played = False
            self.click_sound_played = False


    def kill_delay(self):
        if self.clicked:
            self.delete_delay += 0.1


            if self.delete_delay >= 2:
                self.delete = True

                if self.button_type == ButtonType.PARAMETER:
                    self.action(self.text_string)
                elif not self.action:
                    pass
                else:
                    self.action()
        return None

    def draw(self, window):
        if self.text: self.text = self.font.render(self.text_string, True, self.color)
        if self.mana_text: self.mana_text = self.font.render(self.mana_cost, True, self.color)


        window.blit(self.image, self.pos)
        if self.text: window.blit(self.text, self.text_position)
        if self.mana_text: window.blit(self.mana_text, self.mana_cost_position)

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

        # === sprite group for the buttons ===
        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.skills_buttons: pygame.sprite.Group = pygame.sprite.Group()

        # === main menu ===
        self.main_menu_bg_pos = pygame.Vector2(16, WINDOW_HEIGHT - COMBAT_MENU_MAIN_BG.get_height() - 16)
        self.main_menu_buttons = ["SKILLS", "ITEMS", "RUN"]

        # === skills menu state images and their positions ===

        self.skills_bg_pos = self.main_menu_bg_pos + (112, 0)
        self.skill_mana_cost = None

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
            self.draw_end_menu()

        for button in self.buttons_group:
            button.draw(window)
            button.update()

    def update(self) -> None:
        """Update the state based on the button clicked."""
        for button in self.buttons_group:
            if button.delete:
                if button.text_string == "SKILLS":
                    if self.state == CombatMenuState.SKILLS_MENU:
                        self.state = CombatMenuState.MAIN_MENU
                        for other_button in self.skills_buttons:
                            other_button.kill()
                        # self.buttons_group = pygame.sprite.Group()
                        # self.draw_main_menu()
                    else:
                        self.state = CombatMenuState.SKILLS_MENU
                        self.draw_skills_menu()  # re-populate skill buttons
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

            Button(self.buttons_group, "no parameter", None, "SKILLS", "simple",
                   pos, False)

            y_offset = (0, 34)
            Button(self.buttons_group, "no parameter", self.run_function, "ITEMS", "simple",
                   pos + y_offset, False)

            y_offset = (0, 68)
            Button(self.buttons_group, "no parameter", self.run_function, "RUN", "simple",
                   pos + y_offset, False)

    def draw_end_menu(self) -> None:
        """Draw the buttons for the end menu."""
        if not self.buttons_group:
            pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            Button(self.buttons_group, "no parameter", self.run_function, "END", "simple", pos, False)

    def draw_skills_menu(self) -> None:
        """Draw the buttons for the skills menu."""

        def can_use_skill(name, mana_amount) -> bool:
            """check if the player has enough mana"""
            cost = MOVES[name]["mana"]
            return mana_amount >= cost

        if len(list(self.buttons_group)) == 3:
            for index, skill_name in enumerate(self.player_skills):

                y_offset = 20
                pos = self.skills_bg_pos + (6, 6 + index * y_offset)
                if can_use_skill(skill_name, self.player_mana):
                    Button([self.buttons_group, self.skills_buttons], ButtonType.PARAMETER, self.attack_function, skill_name, "simple_large", pos, False)
                else:
                    Button([self.buttons_group, self.skills_buttons], ButtonType.PARAMETER, self.attack_function, skill_name, "simple_large", pos, True)




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
                    Button(self.buttons_group, ButtonType.NO_PARAMETER, self.level_up, "", "extra_small", position, False)

            for button in self.buttons_group:
                button.draw(window)
                button.update()


    def level_up(self):
        for button in self.buttons_group:
            if button.delete:
                index = list(self.buttons_group).index(button)

                stat = list(self.player.core_stats.keys())[index]
                self.player.core_stats[stat] += 1
                self.player.stat_points -= 1
                self.player.recalculate_stats()
                self.buttons_group = pygame.sprite.Group()



