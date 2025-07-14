from other.settings import *

class Damage:
    def __init__(self, pos, damage):
        self.font = pygame.font.Font(RPG_TEXT, 16)
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

        self.font = pygame.font.Font(RPG_TEXT, 16)
        self.hp_status = self.font.render(f"{current_hp}/{max_hp}",True, (99, 61, 76))

        self.title_box = pygame.image.load(TITLE_BOX)
        self.name = self.font.render(name,True, (255, 194, 161)
)
        name_width = self.name.get_width()


        self.bar_size = self.hp_bar.get_size()

        y_padding = pos[1] // 3
        if pos2 == "left":
            x_padding = 16

            self.box_position = (0 + x_padding, pos[1] - y_padding + 40)
            self.title_box_position = (self.box_position[0] + 32, self.box_position[1] - 8)
            self.name_position = (
                self.title_box_position[0] + (98 - name_width) // 2,
                self.title_box_position[1] + 6
            )

            self.hp_bar_position = (self.box_position[0] + 48, self.box_position[1] + 24)

            self.hp_icon_position = (self.hp_bar_position[0] - 36, self.hp_bar_position[1] - 4)
            self.hp_status_position = (self.hp_icon_position[0] + 90, self.hp_icon_position[1] + 26)

        else:
            x_padding = 80
            self.box_position = (pos[0] - (self.hp_bar.get_width() + x_padding), pos[1] - y_padding + 40)
            self.title_box_position = (self.box_position[0] + 32, self.box_position[1] - 8)
            self.name_position = (
                self.title_box_position[0] + (98 - name_width) // 2,
                self.title_box_position[1] + 6)

            self.hp_bar_position = (self.box_position[0] + 16, self.box_position[1] + 24)

            self.hp_icon = pygame.transform.flip(self.hp_icon, True, False)
            self.hp_icon_position = (self.hp_bar_position[0] + 100, self.hp_bar_position[1] - 4)

            self.hp_status_position = (self.hp_icon_position[0] - 96, self.hp_icon_position[1] + 26)


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
    def __init__(self, group, pos: tuple[int, int], action, text):
        super().__init__(group)
        self.image_normal = pygame.image.load(BUTTON_NORMAL)
        self.image_pressed = pygame.image.load(BUTTON_PRESSED)
        self.image_selected = pygame.image.load(BUTTON_SELECTED)
        self.image = self.image_normal

        self.pos = (pos[0] - self.image.get_size()[0] // 2, pos[1])
        self.rect = self.image.get_rect(topleft = self.pos)

        self.action = action

        if text:
            self.font = pygame.font.Font(RPG_TEXT, 16)
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

            # if self.delay > 2:
            #     self.image = self.image_normal

            if self.delete_delay >= 2:
                self.delete = True

                self.action()

    def draw(self, window):
        window.blit(self.image, self.pos)
        if self.text: window.blit(self.text, self.text_position)


