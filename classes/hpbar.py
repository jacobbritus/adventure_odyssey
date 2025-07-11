import pygame

# calculate the change in hp in percentage
# apply amount to crop width

# full hp is 20, new hp = 15, change = 5, percentage = 25
# change hp by (96 // 100) * 25 = 24
# crop width = 24
# lower bar animation to updated bar width


class Hpbar:
    def __init__(self, pos: tuple[int, int], current_hp: int, max_hp: int):
        self.max_hp = max_hp
        self.hp = current_hp

        self.position = pos# change based on the sprites position
        self.box = pygame.image.load("/Users/jacobbritus/Downloads/adventure_odyssey/sprites/UI/Slider01_Box.png")


        self.bar = pygame.image.load("/Users/jacobbritus/Downloads/adventure_odyssey/sprites/UI/Slider01_Bar02.png")
        self.bar_size = self.bar.get_size()

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
