import pygame

from other.settings import *

class Damage:
    def __init__(self, pos, damage):
        self.font = pygame.font.Font(TEXT_ONE, 16)
        self.damage = self.font.render(damage , True, (99, 61, 76))
        self.pos = pos


    def draw(self, window):
        window.blit(self.damage, self.pos)



class Hpbar:
    def __init__(self, pos: tuple[int, int], pos2, current_hp: int, max_hp: int, name: str):
        self.max_hp = max_hp
        self.hp = current_hp

        self.background_box = pygame.image.load(BACKGROUND_BOX)
        self.hp_box = pygame.image.load(HP_BOX)
        self.hp_bar = pygame.image.load(HP_BAR)
        self.hp_icon = pygame.image.load(HP_ICON)

        self.font = pygame.font.Font(TEXT_ONE, 8 * SCALE)

        self.title_box = pygame.image.load(TITLE_BOX)
        self.name = self.font.render(name, True, (255, 194, 161))


        self.hp_status = self.font.render(f"{current_hp}/{max_hp}",True, (99, 61, 76))
        self.name = self.font.render(name,True, (255, 194, 161)
)
        name_width = self.name.get_width()


        self.bar_size = self.hp_bar.get_size()

        y_padding = pos[1] // 1.2 + self.background_box.get_width() // 2
        if pos2 == "left":
            x_padding = 8 * SCALE

            self.box_position = (0 + x_padding, pos[1] - y_padding + 20 * SCALE)
            self.title_box_position = (self.box_position[0] + SCALE - 2, self.box_position[1] - 4 * SCALE)
            self.name_position = (
                self.title_box_position[0] + (49 * SCALE - name_width) // 2,
                self.title_box_position[1] + 3 * SCALE
            )

            self.hp_bar_position = (self.box_position[0] + 17 * SCALE, self.box_position[1] + 9 * SCALE)
            self.hp_icon_position = (self.hp_bar_position[0] - 13 * SCALE, self.hp_bar_position[1] - 2 * SCALE)
            self.hp_status_position = (self.hp_icon_position[0] + 16 * SCALE, self.hp_icon_position[1] + 12 * SCALE)

        else:
            x_padding = 32 * SCALE

            self.hp_icon = pygame.transform.flip(self.hp_icon, True, False)
            self.title_box = pygame.transform.flip(self.title_box, True, False)

            self.box_position = (pos[0] - (self.hp_bar.get_width() + x_padding), pos[1] - y_padding + 20 * SCALE)
            self.title_box_position = (self.box_position[0] + 24 * SCALE, self.box_position[1] - 4 * SCALE)
            self.name_position = (
                self.title_box_position[0] + (49 * SCALE - name_width) // 2,
                self.title_box_position[1] + 3 * SCALE
            )

            self.hp_bar_position = (self.box_position[0] + 6 * SCALE, self.box_position[1] + 9 * SCALE)
            self.hp_icon_position = (self.hp_bar_position[0] + 46 * SCALE, self.hp_bar_position[1] - 2 * SCALE)
            self.hp_status_position = (self.hp_icon_position[0] - 24 * SCALE, self.hp_icon_position[1] + 12 * SCALE)


        self.current_width = int(self.bar_size[0] * self.hp / self.max_hp)
        self.target_width = self.bar_size[0]

        self.crop = pygame.Rect(0, 0, self.bar_size[0] - self.current_width, self.bar_size[1])

        self.bar_cropped = self.hp_bar.subsurface(self.crop).copy()

        self.smooth_speed = 3

    def set_hp(self, new_hp: int):
        new_hp = max(0, min(new_hp, self.max_hp))
        self.hp = new_hp
        # Calculate width of remaining HP bar
        hp_ratio = self.hp / self.max_hp
        self.target_width = int(self.bar_size[0] * hp_ratio)


    def update(self):
        # Decrease until equal
        if self.current_width > self.target_width:
            self.current_width -= self.smooth_speed
            # Clamp
            if self.current_width < self.target_width:
                self.current_width = self.target_width
        # Increase until equal
        elif self.current_width < self.target_width:
            self.current_width += self.smooth_speed
            # Clamp
            if self.current_width > self.target_width:
                self.current_width = self.target_width

        self.hp_status = self.font.render(f"{self.hp}/{self.max_hp}", True, (99, 61, 76))


    def draw(self, window):
        self.crop = pygame.Rect(0, 0, self.current_width, self.bar_size[1])
        self.bar_cropped = self.hp_bar.subsurface(self.crop).copy()
        window.blit(self.background_box, self.box_position)
        window.blit(self.hp_box, self.hp_bar_position)
        window.blit(self.bar_cropped, self.hp_bar_position)
        window.blit(self.hp_icon, self.hp_icon_position)
        window.blit(self.hp_status, self.hp_status_position)
        window.blit(self.title_box, self.title_box_position)
        window.blit(self.name, self.name_position)



class Button(pygame.sprite.Sprite):
    def __init__(self, group, action_type, action, text, size, pos):
        super().__init__(group)
        self.size = size
        self.image_normal, self.image_pressed, self.image_selected = self.get_images()
        self.image = self.image_normal

        self.action_text = text

        self.pos = pos

        self.rect = self.image.get_rect(topleft = self.pos)

        self.action = action
        self.action_type = action_type

        if text:
            self.font = pygame.font.Font(TEXT_ONE, 16)
            self.text = self.font.render(text,True, (99, 61, 76)
)
            self.size = self.text.get_size()
            self.text_position = (self.rect.centerx - self.size[0] // 2, self.rect.centery - self.size[1] // 2)

        else:
            self.text = None


        # Sounds
        self.hover_sound = pygame.mixer.Sound(HOVER_SOUND)
        self.click_sound = pygame.mixer.Sound(PRESS_SOUND)
        # self.hover_sound.set_volume(0.3)
        # self.click_sound.set_volume(0.3)

        # Status
        self.clicked = False
        self.hovering = False
        self.delete_delay = 0
        self.delete = False

        self.sound_played = False
        self.click_sound_played = False


    def get_images(self):
        if self.size == "small":
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

        if self.rect.collidepoint(mouse_pos) and press or self.clicked:
            self.image = self.image_pressed
            if not self.click_sound_played: self.click_sound.play()
            self.click_sound_played = True
            self.clicked = True

        elif self.rect.collidepoint(mouse_pos) or self.hovering:
            self.image = self.image_selected
            if not self.sound_played: self.hover_sound.play()
            self.sound_played = True
        else:
            self.image = self.image_normal
            self.hovering = False
            self.sound_played = False


    def kill_delay(self):
        if self.clicked:
            self.delete_delay += 0.1


            if self.delete_delay >= 2:
                self.delete = True

                if self.action_type == "parameter":
                    self.action(self.action_text)
                else:
                    self.action()
        return None

    def draw(self, window):
        window.blit(self.image, self.pos)
        if self.text: window.blit(self.text, self.text_position)


class CombatMenu:
    def __init__(self, attacks, attack):

        self.buttons_group = pygame.sprite.Group()
        self.buttons = []
        self.skill_buttons = []
        self.attacks = attacks
        self.attack_function = attack

        # skills background
        self.background_image = pygame.image.load(LARGE_BACKGROUND_BOX)
        self.background_image_position = pygame.Vector2(WINDOW_WIDTH // 2 - self.background_image.get_width() // 2,
                                                        WINDOW_HEIGHT // 2 - self.background_image.get_height() // 2)

        self.skills_title_image = pygame.image.load(SKILLS_TITLE)
        size = self.skills_title_image.get_size()
        self.skills_title_position = pygame.Vector2(self.background_image_position.x + size[0] // 8, self.background_image_position.y + 12 )

         # main menu buttons

        button = Button(self.buttons_group, "no parameter", self.show_skills, "SKILLS", "medium",
                        ((WINDOW_WIDTH // 2) - pygame.image.load(BUTTON_TWO_NORMAL).get_width(), WINDOW_HEIGHT // 1.25))
        button_two = Button(self.buttons_group, "no parameter", None, "RUN", "medium",
                            ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 5,
                             WINDOW_HEIGHT // 1.25))


        self.buttons.append(button)
        self.buttons.append(button_two)
        self.show_main_menu = True
        self.show_skills_menu = False

        self.option_selected = False


    def draw(self, window):

        if not self.option_selected:
            if self.show_skills_menu:
                window.blit(self.background_image, self.background_image_position)
                window.blit(self.skills_title_image, self.skills_title_position)


            for button in self.buttons_group:
                button.draw(window)
                button.update()

            for button in self.skill_buttons:

                if button.delete and self.show_skills_menu:
                    self.skill_buttons = self.buttons = []
                    self.option_selected = True
                    for buttons in self.buttons_group:
                        buttons.kill()


    def main_menu(self):
        self.skill_buttons = []
        self.buttons_group = pygame.sprite.Group()
        self.show_main_menu = True

        self.show_skills_menu = False
        button = Button(self.buttons_group, "no parameter", self.show_skills, "SKILLS", "medium",
                        ((WINDOW_WIDTH // 2) - pygame.image.load(BUTTON_TWO_NORMAL).get_width(), WINDOW_HEIGHT // 1.25))
        button_two = Button(self.buttons_group, "no parameter", None, "RUN", "medium",
                            ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 5,
                             WINDOW_HEIGHT // 1.25))

        self.buttons.append(button)
        self.buttons.append(button_two)

    def show_skills(self,):
        self.buttons_group = pygame.sprite.Group()
        self.show_main_menu = False
        self.show_skills_menu = True

        if len(self.skill_buttons) != len(self.attacks):
            for index, attack_name in enumerate(self.attacks):
                size = pygame.image.load(LARGE_BUTTON_NORMAL).get_size()
                y_offset = 48
                pos = (self.background_image_position.x + size[0] // 8, self.background_image_position.y + y_offset + size[1] * index)
                name = attack_name.replace("_", " ")
                self.skill_buttons.append(Button(self.buttons_group, "parameter",  self.attack_function, name.upper(), "large", pos))

            size = pygame.image.load(BUTTON_NORMAL).get_size()
            pos = (self.background_image_position.x + size[0] // 3, self.background_image_position.y + 188)
            self.buttons.append(Button(self.buttons_group, "no parameter",  self.main_menu, "Back", "small", pos))


