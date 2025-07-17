import pygame.sprite
from other.settings import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, group, start_pos, end_pos, speed):
        super().__init__(group)
        self.direction = "left" if (end_pos - start_pos).normalize().x < 0 else "right"
        self.frame = 0
        self.pos = pygame.Vector2(start_pos)
        self.end_pos = pygame.Vector2(end_pos)
        self.image = fireball_sprites["sprites"][self.direction][int(self.frame)]
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = speed
        self.hit = False
        self.kill_delay = 0
        self.hit_center = None  # Store center position when hit starts

    def update(self, target):
        self.animations(target)
        self.directions()
        self.death()

    def directions(self):
        try:
            direction = (self.end_pos - self.pos).normalize()
        except ValueError:
            # Vector zero-length, means projectile reached target
            if not self.hit:
                self.hit = True
                self.kill_delay = pygame.time.get_ticks() + 1500
                self.hit_center = self.rect.center  # Save center at hit start
            return

        if not self.hit:
            self.pos += direction * self.speed
            self.rect.center = self.pos

            if direction.x < 0 and self.rect.x <= self.end_pos.x:
                self.hit = True
                self.kill_delay = pygame.time.get_ticks() + 1500
                self.hit_center = self.rect.center  # Save center at hit start

            elif direction.x > 0 and self.rect.x >= self.end_pos.x:
                self.hit = True
                self.kill_delay = pygame.time.get_ticks() + 1500
                self.hit_center = self.rect.center  # Save center at hit start

            self.direction = "left" if direction.x < 0 else "right"

    def death(self):
        if self.hit:
            current_time = pygame.time.get_ticks()
            if current_time >= self.kill_delay:
                self.kill()
                self.hit_center = None  # Reset for safety

    def animations(self, target):
        self.frame += 0.17
        sprites_list = fireball_sprites["sprites"]["right"]  # Assuming right and left have same length
        if self.frame >= len(sprites_list):
            self.frame = 0

        if self.hit:
            self.image = fireball_sprites["sprites"]["hit"][int(self.frame)]
            if self.hit_center is not None:
                shifted_center = (target[0] + 48, target[1] + 32)  # Shift right by 32px once
                self.rect = self.image.get_rect(center=shifted_center)
            else:
                self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = fireball_sprites["sprites"][self.direction][int(self.frame)]
            self.rect = self.image.get_rect(center=self.rect.center)
