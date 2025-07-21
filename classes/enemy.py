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
        self.sprite_dict, self.moves, self.critical_hit_chance, self.blocking_chance, self.speed = self.initialize_enemy()


        # Battle related
        self.level = 1
        self.hp = 15
        self.dmg = 5


        # Location
        self.x = pos[0]
        self.y = pos[1]

        # Image
        self.image = surf
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)
        self.exclamation_mark = pygame.image.load(EXCLAMATION_MARK)

        self.screen_position = None




    def initialize_enemy(self) -> list or None:
        if self.monster_name == "Skeleton":
            return skeleton_sprites, ["sword_slash", "heal"], 0.25, 0.75, 2
        elif self.monster_name == "Slime":
            return slime_sprites, ["stomp"], 0.25, 0.75, 3
        elif self.monster_name == "Goblin":
            return goblin_sprites, ["sword_slash"], 0.25, 0.50, 4
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
        self.update_pos(offset)

        if not player.in_battle: self.get_status(player)

        self.update_animations()





