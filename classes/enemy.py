import random

import pygame.mixer

from classes.entity import Entity, BlockShield
from other.settings import *
import math

class Enemy(Entity):
    def __init__(self, name, surf, pos, group, obstacle_sprites):
        super().__init__(group)
        self.name = name
        self.group = group


        # General
        self.type = "enemy"
        self.obstacle_sprites = obstacle_sprites
        self.detected_player = False
        self.sprite_dict, self.core_stats, self.moves, self.critical_hit_chance, self.blocking_chance = self.initialize_enemy()


        # Battle related
        self.level = 1
        self.exp = 500
        self.hp = int(10 + 1.5 * self.core_stats["vitality"])
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.dmg = 5


        # Location and Movement
        self.spawn = pygame.Vector2(pos)
        self.x, self.y = pygame.Vector2(pos)
        self.sprint_speed = 150


        # Image
        self.image = surf
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)
        self.exclamation_mark = pygame.image.load(EXCLAMATION_MARK)

        self.screen_position = None

        self.respawn_time = pygame.time.get_ticks() + 0
        self.moving_randomly = False

        self.random_target = None
        self.random_target_reached = True
        self.move_delay = pygame.time.get_ticks() + 0

    def initialize_enemy(self) -> list or None:
        combat_moves = critical_hit_chance = blocking_chance = core_stats = None
        if self.name == "Skeleton":
            core_stats = {
            "vitality": 7,
            "defense": 7,
            "strength": 7,
            "magic": 0,
            "speed": 7,
            "luck": 7,
        }
            combat_moves = ["sword_slash"]
            critical_hit_chance = 0.5
            blocking_chance = 1
            return skeleton_sprites, core_stats, combat_moves, critical_hit_chance, blocking_chance

        elif self.name == "Goblin":
            core_stats = {
                "vitality": 7,
                "defense": 7,
                "strength": 7,
                "magic": 0,
                "speed": 10,
                "luck": 7,
            }

            combat_moves = ["sword_slash"]
            critical_hit_chance = 1
            blocking_chance = 0.25
            return goblin_sprites, core_stats, combat_moves, critical_hit_chance, blocking_chance
        else:
            return None

    def chase_player(self, player) -> None:
        # Calculate distances between enemy and player
        x_distance = player.x - self.x  # Positive if player is to the right
        y_distance = player.y - self.y  # Positive if player is below
        
        # Calculate total distance using Pythagorean theorem
        distance = math.hypot(x_distance, y_distance)

        # Define detection radius (how far the enemy can see)
        detection_radius = 200  # Adjust this value as needed
        
        if distance <= detection_radius:
            # Enemy sees player - start chasing
            self.action = "running"
            self.sprinting = True

            if not self.detected_player:
                pygame.mixer.Channel(1).play(sound_effects["gameplay"]["enemy_alert"])


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


            if distance > 0 and not abs(self.spawn.y - self.y) > 300 and not abs(self.spawn.x - self.x) > 300: # Prevent division by zero
                dx = x_distance / distance  # Creates value between -1 and 1
                dy = y_distance / distance  # Creates value between -1 and 1
                self.move((dx, dy))
            else:
                self.action = "idle"
        else:
            # Player is too far - enemy stops
            self.detected_player = False
            self.sprinting = False

    def random_movement(self):
        current_time = pygame.time.get_ticks()

        # 1. If target was reached and delay passed → get new target
        if self.random_target_reached and current_time >= self.move_delay:
            target_range = 128
            self.random_target = pygame.Vector2(
                self.spawn.x + random.randint(-target_range, target_range),
                self.spawn.y + random.randint(-target_range, target_range)
            )
            self.random_target_reached = False  # Start moving again
            self.action = "running"
            self.moving_randomly = True

        # 2. If target not reached → move toward it
        if not self.random_target_reached:
            x_distance = self.random_target.x - self.x
            y_distance = self.random_target.y - self.y
            distance = math.hypot(x_distance, y_distance)

            # Set direction
            if abs(x_distance) > abs(y_distance):
                self.direction = "right" if x_distance > 0 else "left"
            else:
                self.direction = "down" if y_distance > 0 else "up"


            # Move
            if distance > 1:
                dx = x_distance / distance
                dy = y_distance / distance

                collision = self.move((dx, dy))

                if collision:
                    self.random_target_reached = True
                    self.move_delay = current_time + 3000  # wait half a second before next target
                    self.moving_randomly = False
                    self.action = "idle"

            else:
                # Target reached
                self.random_target_reached = True
                self.move_delay = current_time + 3000  # wait half a second before next target
                self.moving_randomly = False
                self.action = "idle"

    def clone(self, pos):
        return Enemy(self.name, self.image, pos, self.group, self.obstacle_sprites)


    def update_enemy(self, player, window, offset) -> None:
        self.blocking_mechanics(window, offset)
        self.update_pos()
        self.screen_position = pygame.math.Vector2(self.x - offset.x,
                                                   self.y - offset.y)
        dmg_offset = 32
        self.dmg_position = pygame.Vector2(self.screen_position.x + dmg_offset + self.hitbox.width // 2,
                                           self.screen_position.y)


        mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 0, 0, 120),
                                                               unsetcolor=(0, 0, 0, 0))
        window.blit(mask, self.rect.topleft - offset)





            # mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
            # window.blit(mask, self.screen_position)

        if not self.detected_player and not self.in_battle: self.random_movement()

        if not player.in_battle:
            self.chase_player(player)

        self.update_animations()





