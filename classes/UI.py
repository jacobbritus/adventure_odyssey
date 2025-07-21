import pygame

from other.settings import *

class Damage:
    def __init__(self, pos, damage):
        self.font = pygame.font.Font(FONT_ONE, 16)
        self.damage = self.font.render(damage , True, (99, 61, 76))
        self.pos = pos


    def draw(self, window):
        window.blit(self.damage, self.pos)


class Hpbar:
    def __init__(self, side, current_hp: int, max_hp: int, current_mana, max_mana, name: str):
        # ___load assets___
        self.hp_mana_box = pygame.image.load(STAT_BOX)
        self.hp_bar = pygame.image.load(HP_BAR3)
        self.mana_bar = pygame.image.load(MANA_BAR)

        # ___font and text___
        title_font = pygame.font.Font(FONT_TWO, 22 )
        text_font = pygame.font.Font(FONT_TWO, 8)
        self.name = title_font.render(name, True, (61, 41, 54))


        self.hp_status = text_font.render(f"{current_hp}/{max_hp}",True, (255, 255, 255))

        # ___padding___
        x_padding = 10

        if side == "left":
            self.background_box = pygame.image.load(BACKGROUND_BOX3)
            y_padding = WINDOW_HEIGHT // 1.2 + self.background_box.get_height() // 2

            base_x = x_padding
        else:
            self.background_box = pygame.image.load(ENEMY_BACKGROUND_BOX)
            y_padding = WINDOW_HEIGHT // 1.2 + self.background_box.get_height() // 1.5

            base_x = WINDOW_WIDTH - self.background_box.get_width() - x_padding

        base_y = WINDOW_HEIGHT - y_padding
        self.box_pos = pygame.Vector2(base_x, base_y)

        # ___hp and mana bar positions___
        self.hp_box_pos = self.box_pos + pygame.Vector2(6, self.hp_mana_box.get_height() // 0.6)
        hp_bar_offset = pygame.Vector2(7, 6)
        self.hp_bar_pos = self.hp_box_pos + hp_bar_offset
        self.mana_bar_pos = self.hp_bar_pos + pygame.Vector2(0, self.mana_bar.get_height() + 2)

        # ___text positions___
        self.name_pos = self.box_pos + pygame.Vector2(6,2)
        self.hp_status_pos = (self.hp_bar_pos +
                              pygame.Vector2(self.hp_bar.get_width() - self.hp_status.get_width() - 2, -2 ))

        self.smooth_speed = 3

        self.bars = {
            "hp": {
                "current_amount": current_hp,
                "max_amount": max_hp,
                "current_width": int(self.hp_bar.get_width() * current_hp / max_hp),
                "target_width": self.hp_bar.get_width(),
                "bar_width": self.hp_bar.get_width()},
            "mana": {
                "current_amount": current_mana,
                "max_amount": max_mana,
                "current_width": int(self.mana_bar.get_width() * current_mana / max_mana),
                "target_width": self.hp_bar.get_width(),
                "bar_width": self.mana_bar.get_width()}
        }

    def set_bar(self, stat, new_stat):
        new_stat = max(0, min(new_stat, self.bars[stat]["max_amount"]))
        self.bars[stat]["current_amount"] = new_stat

        stat_ratio = self.bars[stat]["current_amount"] / self.bars[stat]["max_amount"]

        self.bars[stat]["target_width"] = int(self.bars[stat]["bar_width"] * stat_ratio)

    def update(self):
        for stat in self.bars:
            if self.bars[stat]["current_width"] > self.bars[stat]["target_width"]:
                self.bars[stat]["current_width"] -= self.smooth_speed

                if self.bars[stat]["current_width"] < self.bars[stat]["target_width"]:
                    self.bars[stat]["current_width"] = self.bars[stat]["target_width"]

            elif self.bars[stat]["current_width"] < self.bars[stat]["target_width"]:
                self.bars[stat]["current_width"] += self.smooth_speed

                if self.bars[stat]["current_width"] > self.bars[stat]["target_width"]:
                    self.bars[stat]["current_width"] = self.bars[stat]["target_width"]

        text_font = pygame.font.Font(FONT_TWO, 11)
        current_hp = self.bars["hp"]["current_amount"]
        max_hp = self.bars["hp"]["max_amount"]
        self.hp_status = text_font.render(f"{current_hp}/{max_hp}", True, (61, 41, 54))
        self.hp_status_pos = (self.hp_bar_pos +
                              pygame.Vector2(self.hp_bar.get_width() + self.hp_status.get_width() // 2.5 , -4))

    def draw(self, window):
        hp_bar_crop = pygame.Rect(0, 0, self.bars["hp"]["current_width"], self.hp_bar.get_height())
        hp_bar_cropped = self.hp_bar.subsurface(hp_bar_crop).copy()

        # mana_bar_crop = pygame.Rect(0, 0, self.bars["mana"]["current_width"], self.mana_bar.get_height())
        # mana_bar_cropped = self.mana_bar.subsurface(mana_bar_crop).copy()

        window.blit(self.background_box, self.box_pos)
        window.blit(self.hp_mana_box, self.hp_box_pos)
        window.blit(hp_bar_cropped, self.hp_bar_pos)
        # window.blit(mana_bar_cropped, self.mana_bar_pos)
        window.blit(self.name, self.name_pos)
        window.blit(self.hp_status, self.hp_status_pos)



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
            self.font = pygame.font.Font(FONT_ONE, 16)
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
    def __init__(self, attacks: list[str], functions):

        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.attacks: list[str] = attacks
        self.functions = functions

        # skills background
        self.background_image: pygame.Surface = pygame.image.load(LARGE_BACKGROUND_BOX)
        self.background_image_position: pygame.Vector2 = pygame.Vector2(WINDOW_WIDTH // 2 - self.background_image.get_width() // 2,
                                                        WINDOW_HEIGHT // 2 - self.background_image.get_height() // 2)

        self.skills_title_image: pygame.Surface = pygame.image.load(SKILLS_TITLE)
        size = self.skills_title_image.get_size()
        self.skills_title_position: pygame.Vector2 = pygame.Vector2(self.background_image_position.x + size[0] // 8, self.background_image_position.y + 12 )

        self.state: str = ""


    def draw(self, window) -> None:
        self.update()

        if self.state == "main_menu":
            self.main_menu()

        elif self.state == "skills":
            window.blit(self.background_image, self.background_image_position)
            window.blit(self.skills_title_image, self.skills_title_position)

        elif self.state == "end_screen":
            self.end_screen()

        for button in self.buttons_group:
            button.draw(window)
            button.update()


    def update(self) -> None:
        for button in self.buttons_group:
            if button.delete and button.action_text == "BACK":
                self.state = "main_menu"
                self.buttons_group = pygame.sprite.Group()

            elif button.delete and button.action_text == "END":
                self.state = "done"
                for buttons in self.buttons_group:
                    buttons.kill()

            elif button.delete and not button.text == "BACK":
                self.state = "done"  # reset to main when calling again
                for buttons in self.buttons_group:
                    buttons.kill()



    def main_menu(self) -> None:
        if not self.buttons_group:
            width = pygame.image.load(BUTTON_TWO_NORMAL).get_width()
            Button(self.buttons_group, "no parameter", self.show_skills, "SKILLS", "medium",
                            ((WINDOW_WIDTH // 2) - width, WINDOW_HEIGHT // 1.25))
            Button(self.buttons_group, "no parameter", self.functions[1], "RUN", "medium",
                   ((WINDOW_WIDTH // 2) + width // 5,
                                 WINDOW_HEIGHT // 1.25))

    def end_screen(self):

        if not self.buttons_group:
            width = pygame.image.load(BUTTON_NORMAL).get_size()
            pos = (self.background_image_position.x + width[0] // 3, self.background_image_position.y + 188)
            Button(self.buttons_group, "no parameter", self.functions[2], "END", "small", pos)


    def show_skills(self) -> None:
            self.buttons_group = pygame.sprite.Group()
            self.state = "skills"

            # Skill buttons
            if not self.buttons_group:
                for index, attack_name in enumerate(self.attacks):
                    width = pygame.image.load(LARGE_BUTTON_NORMAL).get_size()
                    y_offset = 48
                    pos = (self.background_image_position.x + width[0] // 8, self.background_image_position.y + y_offset + width[1] * index)
                    name = attack_name.replace("_", " ")
                    Button(self.buttons_group, "parameter", self.functions[0], name.upper(), "large", pos)

                # Back button
                width = pygame.image.load(BUTTON_NORMAL).get_size()
                pos = (self.background_image_position.x + width[0] // 3, self.background_image_position.y + 188)
                Button(self.buttons_group, "no parameter",  self.main_menu, "BACK", "small", pos)


