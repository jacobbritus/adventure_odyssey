from other.settings import *

class Hpbar:
    def __init__(self, pos: tuple[int, int], pos2, current_hp: int, max_hp: int):
        self.max_hp = max_hp
        self.hp = current_hp

        self.box = pygame.image.load(get_file_location("sprites/UI/Slider01_Box.png"))

        self.bar = pygame.image.load(get_file_location("sprites/UI/Slider01_Bar02.png"))
        self.bar_size = self.bar.get_size()

        x_padding = 10
        y_padding = pos[1] // 3
        if pos2 == "left":
            self.position = (0 + x_padding, pos[1] - y_padding)
        else:
            self.position = (pos[0] - (self.bar.get_width() + x_padding), pos[1]- y_padding)




        self.current_width = int(self.bar_size[0] * self.hp / self.max_hp)
        self.target_width = self.bar_size[0]

        self.crop = pygame.Rect(0, 0, self.bar_size[0] - self.current_width, self.bar_size[1])

        self.bar_cropped = self.bar.subsurface(self.crop).copy()

        self.smooth_speed = 1

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

    def draw(self, window):
        self.crop = pygame.Rect(0, 0, self.current_width, self.bar_size[1])
        self.bar_cropped = self.bar.subsurface(self.crop).copy()
        window.blit(self.box, self.position)
        window.blit(self.bar_cropped, self.position)



class Button(pygame.sprite.Sprite):
    def __init__(self, group, pos: tuple[int, int], action, text):
        super().__init__(group)
        self.image_normal = pygame.image.load(get_file_location("sprites/UI/Button_01A_Normal.png"))
        self.image_pressed = pygame.image.load(get_file_location("sprites/UI/Button_01A_Pressed.png"))
        self.image_selected = pygame.image.load(get_file_location("sprites/UI/Button_01A_Selected.png"))
        self.image = self.image_normal

        self.pos = (pos[0] - self.image.get_size()[0] // 2, pos[1])
        self.rect = self.image.get_rect(topleft = self.pos)

        self.action = action

        if text:
            self.font = pygame.font.Font(get_file_location("sprites/fonts/FantasyRPGtext.ttf"), 16)
            self.text = self.font.render(text,True, (99, 61, 76)
)
            self.size = self.text.get_size()
            self.text_position = (self.rect.centerx - self.size[0] // 2, self.rect.centery - self.size[1] // 2)
        else:
            self.text = None


        # Sounds
        self.hover_sound = pygame.mixer.Sound("/Users/jacobbritus/Downloads/adventure_odyssey/sounds/hover.wav")
        self.click_sound = pygame.mixer.Sound("/Users/jacobbritus/Downloads/adventure_odyssey/sounds/click.wav")
        self.hover_sound.set_volume(0.3)
        self.click_sound.set_volume(0.3)

        # Status
        self.clicked = False
        self.hovering = False
        self.delete_delay = 0
        self.delete = False


    def update(self):
        self.kill_delay()

        if self.clicked:
            return

        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos) and press or self.clicked:
            self.image = self.image_pressed
            self.click_sound.play()
            self.clicked = True

        elif self.rect.collidepoint(mouse_pos):
            self.image = self.image_selected
            if not self.hovering: self.hover_sound.play()
            self.hovering = True
        else:
            self.image = self.image_normal
            self.hovering = False


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


