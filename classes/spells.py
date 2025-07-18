import pygame.sprite
from other.settings import *

class Spells(pygame.sprite.Sprite):
    def __init__(self, group, type,  start_pos, end_pos, speed):
        super().__init__(group)
        self.frame = 0
        self.type = type
        if end_pos:
            self.direction = "left" if (end_pos - start_pos).normalize().x < 0 else "right"
            self.end_pos = pygame.Vector2(end_pos)
            self.speed = speed
        else:
            self.direction = "right"
            self.end_pos = None
        self.pos = pygame.Vector2(start_pos)
        self.sprites, self.iterate_speed, self.life_time, self.fade_time = self.get_sprites()
        self.image = self.sprites["sprites"][self.direction][int(self.frame)]
        self.rect = self.image.get_rect(center=start_pos)
        self.hit = False
        self.kill_delay = 0
        self.hit_center = None  # Store center position when hit starts

        self.opacity = 255


    def get_sprites(self):
        if self.type == "fire_ball":
            return fireball_sprites, 0.17, None, None
        if self.type == "heal":
            return heal_sprites, 0.1, pygame.time.get_ticks() + 3000, pygame.time.get_ticks() + 2000
        if self.type == "lightning_strike":
            return lightning_sprites, 0.13, pygame.time.get_ticks() + 1200, pygame.time.get_ticks() + 800

        return None

    def update(self, offset):
        if self.end_pos:
            self.directions()
            self.rect.center = (self.pos.x - offset[0], self.pos.y - offset[1])
        else:
            self.rect.center = (self.pos.x - offset[0], self.pos.y - offset[1])

        self.projectile_animations(offset)

        self.handle_life_time()

        print(self.rect)

        # Set rect position relative to camera offset for drawing

    def register_hit(self):
        if not self.hit:
            self.hit = True
            self.kill_delay = pygame.time.get_ticks() + 1500
            self.hit_center = self.rect.center  # Save center at hit start

    def directions(self):
        try:
            direction = (self.end_pos - self.pos).normalize()
        except ValueError:
            # Vector zero-length, means projectile reached target
            self.register_hit()
            return

        if not self.hit:
            self.pos += direction * self.speed
            self.rect.center = self.pos

            if direction.x < 0 and self.rect.x <= self.end_pos.x:
                self.register_hit()


            elif direction.x > 0 and self.rect.x >= self.end_pos.x:
                self.register_hit()

            self.direction = "left" if direction.x < 0 else "right"

    def handle_life_time(self):
        current_time = pygame.time.get_ticks()
        if self.hit:
            if current_time >= self.kill_delay:
                self.kill()
                self.hit_center = None  # Reset for safety
        if not self.end_pos:
            if current_time >= self.fade_time :
                self.hit = True
                print(self.opacity)
                self.opacity -= 10
                if self.opacity >= 0:
                    self.image.set_alpha(max(self.opacity, 0))
            if current_time >= self.life_time :
                    self.kill()


    def projectile_animations(self, offset):
        self.frame += self.iterate_speed
        sprites_list = self.sprites["sprites"]["hit"] if self.hit and self.type == "fire_ball" else self.sprites["sprites"][self.direction]

        if self.frame >= len(sprites_list):
            self.frame = 0

        if self.hit and self.type == "fire_ball":
            self.image = self.sprites["sprites"]["hit"][int(self.frame)]
            if self.hit_center is not None:
                shifted_center = (self.end_pos[0] - offset.x , self.end_pos[1] - offset.y)  # Shift right by 32px once
                self.rect = self.image.get_rect(center=shifted_center)

            else:
                self.rect = self.image.get_rect(center=self.end_pos)
        else:
            self.image = self.sprites["sprites"][self.direction][int(self.frame)].copy()
            self.image.set_alpha(self.opacity)

