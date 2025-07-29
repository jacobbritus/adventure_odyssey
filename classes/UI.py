from classes.states import BookState, CombatMenuState, ButtonType
from other.play_sound import play_sound
from other.settings import *

class HpBar:
    def __init__(self, side: str, y_offset, level: int, current_hp: int, max_hp: int, mana: int | None, name: str):
        # === dynamic stats ===
        self.max_hp: int = max_hp
        self.hp: int = current_hp

        # === images ===
        self.background_box: pygame.Surface = pygame.image.load(BACKGROUND_BOX)

        self.hp_box: pygame.Surface = pygame.image.load(HP_BOX)
        self.hp_bar: pygame.Surface = pygame.image.load(HP_BAR)
        self.hp_icon: pygame.Surface = pygame.image.load(HP_ICON)

        self.font: pygame.font = pygame.font.Font(FONT_ONE, 16)
        self.title_box: pygame.Surface = pygame.image.load(TITLE_BOX)

        self.hp_text: pygame.Surface = self.font.render(f"{current_hp}/{max_hp}", True, (99, 61, 76))
        self.name: pygame.Surface = self.font.render(name,True, (255, 194, 161))

        self.level_box: pygame.Surface = pygame.image.load(LEVEL_BOX)
        self.level: pygame.Surface = self.font.render(str(level),True, (255, 255, 255))

        if side == "left":
            self.mana_box = pygame.image.load(MANA_BOX)
            self.mana = self.font.render(f"{mana}", True, (150, 206, 255))
        else:
            self.mana = None

        # === positions ====
        y_padding, x_padding, image_position_offsets = self.initialize_position(side)
        y_padding += y_offset

        self.background_box_pos = pygame.Vector2(x_padding, y_padding)
        self.title_box_pos = self.background_box_pos + image_position_offsets["title"]
        self.name_pos = self.title_box_pos + image_position_offsets["name"]

        self.hp_bar_pos = self.background_box_pos + image_position_offsets["hp_bar"]
        self.hp_icon_pos = self.hp_bar_pos - image_position_offsets["hp_icon"]
        self.hp_text_pos = self.hp_icon_pos + image_position_offsets["hp_status"]

        self.level_box_pos = self.title_box_pos + image_position_offsets["level_box"]
        self.level_pos = self.level_box_pos + image_position_offsets["level"]

        if self.mana:
            self.mana_box_pos = self.title_box_pos + image_position_offsets["mana_box"]
            self.mana_pos = self.mana_box_pos + image_position_offsets["mana"]

        # === updating the hp bar ===
        self.bar_size = self.hp_bar.get_size()
        self.hp_bar_cropped = self.hp_bar
        self.current_width = int(self.bar_size[0] * self.hp / self.max_hp)
        self.target_width = self.bar_size[0]
        self.smooth_speed = 3

    def initialize_position(self, side) -> tuple[int, int, dict[str: pygame.Vector2]]:
        """Return the paddings and offsets for the images"""
        if side == "left":
            return WINDOW_HEIGHT // 10, 16, {
                "title": pygame.Vector2(0, -8),
                "name": pygame.Vector2(self.title_box.get_width() // 2 - self.name.get_width() // 2, 7),
                "level_box": pygame.Vector2(self.background_box.get_width() - self.level_box.get_width() + 4, 4),
                "level": pygame.Vector2(self.level_box.get_width() // 2 - self.level.get_width() // 2 + 1,
                                        self.level_box.get_height() // 2 - self.level.get_height() // 2 - 1),
                "mana_box": pygame.Vector2(self.background_box.get_width() - self.mana_box.get_width() + 4, self.background_box.get_height() - self.mana_box.get_height() // 2),
                "mana": pygame.Vector2(self.mana_box.get_width() // 2 - self.mana.get_width() // 2 + 1, self.mana_box.get_height() // 2 - self.mana.get_height() // 2 - 1),
                "hp_bar": pygame.Vector2(34, 18),
                "hp_icon": pygame.Vector2(26, 4),
                "hp_status": pygame.Vector2(30, 24),
            }
        else:
            return WINDOW_HEIGHT // 10, WINDOW_WIDTH - (self.background_box.get_width() + 16), {
                "title": pygame.Vector2(48, -8),
                "name": pygame.Vector2(self.title_box.get_width() // 2 - self.name.get_width() // 2, 7),
                "level_box": pygame.Vector2(- self.level_box.get_width() - 16, 4),
                "level": pygame.Vector2(self.level_box.get_width() // 2 - self.level.get_width() // 2 + 1,
                                        self.level_box.get_height() // 2 - self.level.get_height() // 2 - 1),
                "hp_bar": pygame.Vector2(14, 18),
                "hp_icon": pygame.Vector2(-self.hp_bar.get_width() + 6, 4),
                "hp_status": pygame.Vector2(-36, 24),
            }

    def set_hp(self, new_hp: int) -> None:
        """Update the hp bar target length making it relative to the current-hp to max-hp ratio."""
        new_hp = max(0, min(new_hp, self.max_hp)) # clamp
        self.hp = new_hp
        hp_ratio = self.hp / self.max_hp
        self.target_width = int(self.bar_size[0] * hp_ratio)

    def set_mana(self, new_mana) -> None:
        """Update the mana text."""
        self.mana = self.font.render(f"{new_mana}", True, (150, 206, 255))

    def update_hp_bar(self) -> None:
        """Slowly increase or decrease the current bar width until equal to the target width."""
        # === decrease the current width ===
        if self.current_width > self.target_width:
            self.current_width -= self.smooth_speed
            if self.current_width < self.target_width:
                self.current_width = self.target_width

        # === increase the current width ===
        elif self.current_width < self.target_width:
            self.current_width += self.smooth_speed

            if self.current_width > self.target_width:
                self.current_width = self.target_width

        # === update the hp text ===
        self.hp_text = self.font.render(f"{self.hp}/{self.max_hp}", True, (99, 61, 76))

        hp_bar_crop = pygame.Rect(0, 0, self.current_width, self.bar_size[1])
        self.hp_bar_cropped = self.hp_bar.subsurface(hp_bar_crop).copy()

    def draw(self, window) -> None:
        """Draw all the images on the window"""
        elements: list[tuple[pygame.Surface, pygame.Vector2]] = [
            (self.background_box, self.background_box_pos),
            (self.hp_box, self.hp_bar_pos),
            (self.hp_bar_cropped, self.hp_bar_pos),
            (self.hp_icon, self.hp_icon_pos),
            (self.hp_text, self.hp_text_pos),
            (self.title_box, self.title_box_pos),
            (self.name, self.name_pos),
            (self.level_box, self.level_box_pos),
            (self.level, self.level_pos)
        ]
        if self.mana:
            elements.append((self.mana_box, self.mana_box_pos))
            elements.append((self.mana, self.mana_pos))

        for surface, pos in elements:
            window.blit(surface, pos)






class Button(pygame.sprite.Sprite):
    def __init__(self, group, action_type, action, text, size, pos, disabled:bool):
        super().__init__(group)
        self.size = size
        self.image_normal, self.image_pressed, self.image_selected = self.get_images()
        self.image = self.image_normal

        self.text_string = text

        self.pos = pos

        self.rect = self.image.get_rect(topleft = self.pos)

        self.action = action
        self.button_type = action_type
        self.disabled = disabled

        if text:
            self.font = pygame.font.Font(FONT_ONE, 16)
            self.text = self.font.render(text,True, (99, 61, 76)
)
            self.size = self.text.get_size()
            self.text_position = (self.rect.centerx - self.size[0] // 2, self.rect.centery - self.size[1] // 2)

        else:
            self.text = None




        # Status
        self.clicked = False
        self.hovering = False
        self.delete_delay = 0
        self.delete = False

        self.sound_played = False
        self.click_sound_played = False


    def get_images(self):
        if self.size == "extra_small":
            return BUTTON_SMALL_NORMAL, BUTTON_SMALL_PRESSED, BUTTON_SMALL_SELECTED

        elif self.size == "small":
            return pygame.image.load(BUTTON_NORMAL), pygame.image.load(BUTTON_PRESSED), pygame.image.load(BUTTON_SELECTED)

        elif self.size == "medium":
            return pygame.image.load(BUTTON_TWO_NORMAL), pygame.image.load(BUTTON_TWO_PRESSED), pygame.image.load(BUTTON_TWO_SELECTED)
        elif self.size == "large":
            return pygame.image.load(LARGE_BUTTON_NORMAL), pygame.image.load(LARGE_BUTTON_PRESSED), pygame.image.load(LARGE_BUTTON_SELECTED)
        return None

    def update(self):
        self.kill_delay()

        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]

        if self.rect.inflate(- 16, - 16).collidepoint(mouse_pos) and press or self.clicked:
            self.image = self.image_pressed

            if not self.disabled:
                if not self.click_sound_played: play_sound("ui", "press", None)

                self.click_sound_played = True
                self.clicked = True
            else:
                if not self.click_sound_played: play_sound("ui", "disabled", None)
                self.click_sound_played = True

        elif self.rect.inflate(-16, -16).collidepoint(mouse_pos) or self.hovering:
            self.image = self.image_selected
            if not self.sound_played: play_sound("ui", "hover", None)
            self.sound_played = True
            self.click_sound_played = False

        else:
            self.image = self.image_normal
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
                else:
                    self.action()
        return None

    def draw(self, window):
        window.blit(self.image, self.pos)
        if self.text: window.blit(self.text, self.text_position)


class CombatMenu:
    def __init__(self, player_skills: list[str], functions):
        # === player's attacks and functions ===
        # e.g., attack(name of button clicked) and player_run(no parameter)
        self.formatted_skills: list[str] = [attack.replace("_", " ").upper() for attack in player_skills]
        self.attack_function = functions[0]
        self.run_function = functions[1]

        # === sprite group for the buttons ===
        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.large_button_size = pygame.image.load(LARGE_BUTTON_NORMAL).get_size()
        self.normal_button_size = pygame.image.load(BUTTON_NORMAL).get_size()
        self.normal_button_two_width = pygame.image.load(BUTTON_TWO_NORMAL).get_width()

        # === skills menu state images and their positions ===
        self.background_image: pygame.Surface = pygame.image.load(LARGE_BACKGROUND_BOX)
        self.background_image_position: pygame.Vector2 = pygame.Vector2(WINDOW_WIDTH // 2 - self.background_image.get_width() // 2,
                                                        WINDOW_HEIGHT // 2 - self.background_image.get_height() // 2)
        self.skills_title_image: pygame.Surface = pygame.image.load(SKILLS_TITLE)
        size = self.skills_title_image.get_size()
        self.skills_title_position: pygame.Vector2 = pygame.Vector2(self.background_image_position.x + size[0] // 8, self.background_image_position.y + 12 )

        # === enum states ===
        self.state = CombatMenuState.MAIN_MENU

        # === player's mana amount ===
        self.player_mana: int = 0

    def draw(self, window: pygame.Surface, current_mana: int) -> None:
        """Draw the buttons and images associated with the current state."""
        self.update()
        self.player_mana = current_mana
        if self.state == CombatMenuState.MAIN_MENU:
            self.draw_main_menu()

        # === buttons are drawn through the main menu skills button's function ===
        elif self.state == CombatMenuState.SKILLS_MENU:
            window.blit(self.background_image, self.background_image_position)
            window.blit(self.skills_title_image, self.skills_title_position)

        elif self.state == CombatMenuState.END_MENU:
            self.draw_end_menu()

        for button in self.buttons_group:
            button.draw(window)
            button.update()

    def update(self) -> None:
        """Update the state based on the button clicked."""
        for button in self.buttons_group:
            if button.delete:
                # === skills menu -> main menu ===
                if button.text_string == "BACK":
                    self.state = CombatMenuState.MAIN_MENU
                    self.buttons_group = pygame.sprite.Group()

                # === skills menu -> player animation ===
                elif button.text_string in self.formatted_skills:
                    self.state = None
                    for buttons in self.buttons_group:
                        buttons.kill()

                # === end screen -> overworld ===
                elif button.text_string == "END":
                    self.state = None
                    for buttons in self.buttons_group:
                        buttons.kill()

    def draw_main_menu(self) -> None:
        """Draw the buttons for the main menu."""
        if not self.buttons_group:
            Button(self.buttons_group, "no parameter", self.draw_skills_menu, "SKILLS", "medium",
                   ((WINDOW_WIDTH // 2) - self.normal_button_two_width, WINDOW_HEIGHT // 1.25), False)
            Button(self.buttons_group, "no parameter", self.run_function, "RUN", "medium",
                   ((WINDOW_WIDTH // 2) + self.normal_button_two_width // 5,
                                 WINDOW_HEIGHT // 1.25), False)

    def draw_end_menu(self) -> None:
        """Draw the buttons for the end menu."""
        if not self.buttons_group:
            pos = (self.background_image_position.x + self.normal_button_size[0] // 3, WINDOW_HEIGHT // 1.25)
            Button(self.buttons_group, "no parameter", self.run_function, "END", "small", pos, False)

    def draw_skills_menu(self) -> None:
        """Draw the buttons for the skills menu."""
        self.buttons_group = pygame.sprite.Group()
        self.state = CombatMenuState.SKILLS_MENU

        def can_use_skill(name, mana_amount) -> bool:
            """check if the player has enough mana"""
            internal_name = name.replace(" ", "_").lower()
            return mana_amount >= moves[internal_name]["mana"]

        if not self.buttons_group:
            for index, skill_name in enumerate(self.formatted_skills):
                y_offset = 48
                pos = (self.background_image_position.x + self.large_button_size[0] // 8, self.background_image_position.y + y_offset + self.large_button_size[1] * index)

                if can_use_skill(skill_name, self.player_mana):
                    Button(self.buttons_group, ButtonType.PARAMETER, self.attack_function, skill_name, "large", pos, False)
                else:
                    Button(self.buttons_group, ButtonType.PARAMETER, self.attack_function, skill_name, "large", pos, True)

            # === skills menu > main menu button ===
            pos = (self.background_image_position.x + self.normal_button_size[0] // 3, self.background_image_position.y + self.background_image.get_height() - self.normal_button_size[1] * 1.25)
            Button(self.buttons_group, ButtonType.NO_PARAMETER, self.draw_main_menu, "BACK", "small", pos, False)


class MenuBook:
    def __init__(self, player):
        self.player = player
        self.image = pygame.image.load(BOOK)
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

        self.content = [{"title": pygame.image.load(INFO_TITLE), "content": self.info_page}]
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
            self.image = pygame.image.load(BOOK)
            self.pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.image.get_width() // 2,
                                      WINDOW_HEIGHT // 2 - self.image.get_height() // 2)



    def contents(self, window):
        title = self.content[self.current_page]["title"]
        self.content[self.current_page]["content"](window)

        container_width = 100
        title_pos = self.base_pos + (container_width - title.get_width() // 2, 28)
        divider = pygame.image.load(DIVIDER)
        divider_pos = title_pos + (title.get_width() // 2 - divider.get_width() // 2 + 16, 8)
        window.blit(divider, divider_pos)
        window.blit(title, title_pos)

    def info_page(self, window):
        image = pygame.image.load(INFO_PAGE)
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



