from other.settings import *
class Hpbar:
    def __init__(self, pos: tuple[int, int], pos2, current_hp: int, max_hp: int, name: str):
        self.max_hp = max_hp
        self.hp = current_hp

        self.background_box = pygame.image.load(BACKGROUND_BOX)
        self.hp_box = pygame.image.load(HP_BOX)
        self.hp_bar = pygame.image.load(HP_BAR)
        self.hp_icon = pygame.image.load(HP_ICON)

        self.font = pygame.font.Font(FONT_ONE, 8 * SCALE)

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