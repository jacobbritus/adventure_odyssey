import pygame.sprite
from other.settings import *

class StationarySpell(pygame.sprite.Sprite):
    def __init__(self, spell_name, group, pos):
        super().__init__(group)
        self.spell_name = spell_name
        self.sprites, self.life_time, self.fade_time = self.get_sprites()
        self.frame = 0
        self.image = self.sprites[self.frame]
        self.rect = self.image.get_rect(center = pos)
        self.position = pos

        self.opacity = 255

    def update(self, pos):
        self.rect.center = pos
        print(self.position)
        self.handle_life_time()
        self.animations()

    def draw(self, window):
        window.blit(self.image, self.position)


    def get_sprites(self):
        if self.spell_name == "heal":
            return heal_sprites, pygame.time.get_ticks() + 3000, pygame.time.get_ticks() + 2000
        return None

    def handle_life_time(self):
        current_time = pygame.time.get_ticks()

        if current_time >= self.fade_time:
            self.opacity -= 10
            if self.opacity >= 0:
                self.image.set_alpha(max(self.opacity, 0))
        if current_time >= self.life_time:
            self.kill()



    def animations(self):
        self.frame += 0.06
        last_frame = len(self.sprites) - 1
        if self.frame >= last_frame: self.frame = 0

        self.image = self.sprites[int(self.frame)]

class Spells(pygame.sprite.Sprite):
    def __init__(self, group, spell_type, start_pos, end_pos, speed):
        super().__init__(group)
        self.frame = 0
        self.type = spell_type
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
            return fireball_sprites, 0.05, None, None
        if self.type == "heal":
            return heal_sprites, 0.05, pygame.time.get_ticks() + 3000, pygame.time.get_ticks() + 2000
        if self.type == "lightning_strike":
            return lightning_sprites, 0.06, pygame.time.get_ticks() + 1200, pygame.time.get_ticks() + 800

        if self.type == "level_up":
            return level_up_sprites, 0.06, pygame.time.get_ticks() + 3000, pygame.time.get_ticks() + 2000

        return None

    def update(self, pos, offset, target):
        if self.end_pos:
            self.directions()
            self.rect.center = (self.pos.x - offset[0], self.pos.y - offset[1])
        else:
            self.rect.center = pos

        self.projectile_animations(offset, target)

        self.handle_life_time()


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
                self.opacity -= 10
                if self.opacity >= 0:
                    self.image.set_alpha(max(self.opacity, 0))
            if current_time >= self.life_time :
                    self.kill()

    def projectile_animations(self, offset, target):
        self.frame += self.iterate_speed
        sprites_list = self.sprites["sprites"]["hit"] if self.hit and self.type == "fire_ball" else self.sprites["sprites"][self.direction]

        if self.frame >= len(sprites_list):
            self.frame = 0

        if self.hit and self.type == "fire_ball" and not target.blocking:
            self.image = self.sprites["sprites"]["hit"][int(self.frame)]
            if self.hit_center is not None:
                shifted_center = (self.end_pos[0] - offset.x , self.end_pos[1] - offset.y)  # Shift right by 32px once
                self.rect = self.image.get_rect(center=shifted_center)

            else:

                self.rect = self.image.get_rect(center=self.end_pos)

        elif hasattr(target, "blocking") and target.blocking:
            self.kill()

        else:
            self.image = self.sprites["sprites"][self.direction][int(self.frame)].copy()
            self.image.set_alpha(self.opacity)

