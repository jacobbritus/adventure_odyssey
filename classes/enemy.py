import random

import pygame.mixer

from archive.corruption_test import apply_dark_purple_tint
from classes.entity import Entity, BlockShield
from classes.inventory import Item, Inventory
from other.settings import *
import math


class Enemy(Entity):
    def __init__(self, name, surf, pos, group, obstacle_sprites):
        super().__init__(group)
        self.name = name
        self.group = group

        # General
        self.type = "npc"
        self.obstacle_sprites = obstacle_sprites
        self.detected_player = False
        self.sprite_dict, self.core_stats, self.skills, self.critical_hit_chance, self.blocking_chance = self.initialize_enemy()

        # Battle related (will be moved to initialize and changed depending on the area of spawning)
        self.level = 1
        self.exp_given = 50
        self.hp = int(10 + 1.5 * self.core_stats["vitality"])
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.dmg = 5
        self.mana = 0
        self.max_mana = 5

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

        self.respawn_time = pygame.time.get_ticks() + 600000  #

        self.moving_randomly = False

        self.random_target = None
        self.random_target_reached = True
        self.move_delay = pygame.time.get_ticks() + 0
        self.reached_bounds = False

        self.item_drop = "small_health_potion"
        self.inventory = Inventory()



        # === corrupted ===
        self.corrupted = random.choices(population=[True, False], weights=[0.5, 0.5], k=1)[0]

        self.icon = UI["icons"][name.lower()]

        if self.corrupted:
            self.initialize_corrupted_enemy()

    def initialize_corrupted_enemy(self):
        new_sprite_dict = {}

        for key, data in self.sprite_dict.items():
            new_sprite_dict[key] = {
                "sprites": {
                    action: [
                        apply_dark_purple_tint(image.copy())  # copy surface first
                        for image in images
                    ]
                    for action, images in data["sprites"].items()
                },
                    "impact_frame": self.sprite_dict[key]["impact_frame"] if self.sprite_dict[key].get("impact_frame") else ...
            }

        self.sprite_dict = new_sprite_dict

        for key in self.core_stats.keys():
            self.core_stats[key] *= 2
        self.exp_given *= 2
        self.recalculate_stats()

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
            critical_hit_chance = 0.9
            blocking_chance = 0.25
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

            combat_moves = ["poison_stab", "sword_slash"]
            critical_hit_chance = 0.9
            blocking_chance = 0.25
            return goblin_sprites, core_stats, combat_moves, critical_hit_chance, blocking_chance
        else:
            return None

    def follow_player(self, player):
        # Calculate distances between enemy and player
        x_distance = player.x - self.x  # Positive if player is to the right
        y_distance = player.y - self.y  # Positive if player is below

        # Calculate total distance using Pythagorean theorem
        distance = math.hypot(x_distance, y_distance)

        if distance > 500:
            self.x, self.y = player.x, player.y
            self.update_pos()
            print("yes")
        elif distance > 75:
            self.sprinting = True
        else:
            self.sprinting = False

        # Define detection radius (how far the enemy can see)
        detection_radius = 500  # Adjust this value as needed

        if distance <= detection_radius:
            # Enemy sees player - start chasing
            self.action = "running"

            if not self.detected_player:
                pygame.mixer.Channel(1).play(SOUND_EFFECTS["gameplay"]["enemy_alert"])

            self.detected_player = True

            # Determine primary direction based on largest distance
            if abs(x_distance) > abs(y_distance):
                # Horizontal distance is larger
                if x_distance > 0:
                    self.direction = "right"  # Player is to the right
                else:
                    self.direction = "left"  # Player is to the left
            else:
                # Vertical distance is larger
                if y_distance > 0:
                    self.direction = "down"  # Player is below
                else:
                    self.direction = "up"  # Player is above

            # Normalize movement vector for consistent speed
            if distance > 50:  # Prevent division by zero
                dx = x_distance / distance  # Creates value between -1 and 1
                dy = y_distance / distance  # Creates value between -1 and 1
                self.move((dx, dy))
            else:
                self.action = "idle"

        else:
            # Player is too far - enemy stops
            self.detected_player = False

    def chase_player(self, player) -> None:
        # Calculate distances between enemy and player
        x_distance = player.x - self.x  # Positive if player is to the right
        y_distance = player.y - self.y  # Positive if player is below

        # Calculate total distance using Pythagorean theorem
        distance = math.hypot(x_distance, y_distance)

        # Define detection radius (how far the enemy can see)
        detection_radius = 200  # Adjust this value as needed



        if distance <= detection_radius and not self.reached_bounds:
            # Enemy sees player - start chasing
            self.action = "running"
            self.sprinting = True

            if not self.detected_player:
                pygame.mixer.Channel(1).play(SOUND_EFFECTS["gameplay"]["enemy_alert"])

            self.detected_player = True

            # Determine primary direction based on largest distance
            if abs(x_distance) > abs(y_distance):
                # Horizontal distance is larger
                if x_distance > 0:
                    self.direction = "right"  # Player is to the right
                else:
                    self.direction = "left"  # Player is to the left
            else:
                # Vertical distance is larger
                if y_distance > 0:
                    self.direction = "down"  # Player is below
                else:
                    self.direction = "up"  # Player is above

            # Normalize movement vector for consistent speed
            if distance > 0 and not abs(self.spawn.y - self.y) > 300 and not abs(
                    self.spawn.x - self.x) > 300:  # Prevent division by zero
                dx = x_distance / distance  # Creates value between -1 and 1
                dy = y_distance / distance  # Creates value between -1 and 1
                self.move((dx, dy))
            else:
                self.reached_bounds = True
                self.return_animation(self.spawn)
        else:
            # Player is too far - enemy stops
            self.detected_player = False
            self.sprinting = False

            if not abs(self.spawn.y - self.y) > 150 and not abs(self.spawn.x - self.x) > 150:
                self.reached_bounds = False

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
            self.moving_randomly = True

        # 2. If target not reached → move toward it
        if not self.random_target_reached:
            self.action = "running"

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

    def clone(self, name):
        clone = Enemy(name, self.image, self.screen_position, self.group, self.obstacle_sprites)

        if not self.corrupted:
            clone.corrupted = random.choices(population=[True, False], weights=[0.9, 0.1], k=1)[0]
            if clone.corrupted:
                clone.initialize_corrupted_enemy()

        return clone

    def recruit(self, name):
        new_recruit = Enemy(name, self.image, self.spawn, self.group, self.obstacle_sprites)
        new_recruit.occupation = "hero"
        new_recruit.selected = True

        new_recruit.sprint_speed = 200
        new_recruit.walking_speed = 100



        # use the original's level
        new_recruit.exp = 0
        new_recruit.max_exp = 50

        return new_recruit

    def item_use_logic(self):
        """Make the enemy use an item depending on certain circumstances."""
        if self.hp / self.max_hp <= 0.5 and not self.inventory.items["small_health_potion"] <= 0:
            self.current_attack = "small_health_potion"

    def update_enemy(self, player, window, offset) -> None:

        self.blocking_mechanics(window, offset)

        if not self.death:
            if not self.detected_player and not self.in_battle and not self.occupation == "hero":
                self.random_movement()

            if not player.in_battle:
                if self.occupation == "hero":
                    self.follow_player(player)
                elif pygame.time.get_ticks() >= player.post_battle_iframes:
                    self.chase_player(player)

            self.mask(window, offset)
            self.update_pos(offset=offset)

            self.update_animations()

        # if self.name == "Goblin":
        #     self.action = "death"
        #     self.direction = "right"
        #     self.image = self.sprite_dict[self.action]["sprites"][self.direction][-1]
        #     self.death = True












