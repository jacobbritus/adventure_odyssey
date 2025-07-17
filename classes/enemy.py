import pygame.mixer

from classes.entity import Entity
from other.settings import *
import math

class Enemy(Entity):
    def __init__(self, monster_name, surf, pos, group, obstacle_sprites):
        super().__init__(group)
        self.monster_name = monster_name


        # General
        self.type = "enemy"
        self.obstacle_sprites = obstacle_sprites
        self.detected_player = True

        # Stats
        self.hp = 15
        self.dmg = 5

        # Location
        self.x = pos[0]
        self.y = pos[1]

        # Image
        self.sprite_dict = self.get_sprites()
        self.image = surf
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-16, -48)
        self.exclamation_mark = pygame.image.load(EXCLAMATION_MARK)

        self.screen_position = None


    def get_sprites(self) -> list or None:
        if self.monster_name == "Skeleton":
            return skeleton_sprites
        elif self.monster_name == "Slime":
            return slime_sprites
        else:
            return None

    def get_status(self, player) -> None:
        # Calculate distances between enemy and player
        x_distance = player.x - self.x  # Positive if player is to the right
        y_distance = player.y - self.y  # Positive if player is below
        
        # Calculate total distance using Pythagorean theorem
        distance = math.sqrt(x_distance**2 + y_distance**2)
        
        # Define detection radius (how far the enemy can see)
        detection_radius = 200  # Adjust this value as needed
        
        if distance <= detection_radius:
            # Enemy sees player - start chasing
            self.action = "running"

            if not self.detected_player:
                sound = pygame.mixer.Sound(ENEMY_ALERT)
                pygame.mixer.Sound.set_volume(sound, 0.1)
                pygame.mixer.Sound(sound).play()

            self.detected_player = True

            # Determine primary direction based on largest distance
            if abs(x_distance) > abs(y_distance):
                # Horizontal distance is larger
                if x_distance > 0:
                    self.direction = "right"  # Player is to the right
                else:
                    self.direction = "left"   # Player is to the left
            else:
                # Vertical distance is larger
                if y_distance > 0:
                    self.direction = "down"   # Player is below
                else:
                    self.direction = "up"     # Player is above
        
            # Normalize movement vector for consistent speed
            if distance > 0:  # Prevent division by zero
                dx = x_distance / distance  # Creates value between -1 and 1
                dy = y_distance / distance  # Creates value between -1 and 1
                self.move((dx, dy))
        else:
            # Player is too far - enemy stops
            self.action = "idle"
            self.detected_player = False


    def update_enemy(self, player, window, offset) -> None:
        self.screen_position = pygame.math.Vector2(self.x - offset.x,
                                                   self.y - offset.y)
        hitbox_offset = self.width if self.monster_name == "Skeleton" else 0
        self.hitbox.topleft = (int(self.screen_position.x + hitbox_offset), int(self.screen_position.y + self.height // 2))

        # pygame.draw.rect(window, (255, 0, 0), self.hitbox, 2)  # Red rectangle with 2px border

        if self.detected_player and not self.in_battle:
            window.blit(self.exclamation_mark, (self.rect.centerx - offset.x + self.width // 2, self.rect.y - offset.y - 8))

        if not self.in_battle: self.get_status(player)

        self.update_animations()





