import random

import pygame.mixer

from archive.corruption_test import apply_dark_purple_tint
from classes.UI import StatusBar
from classes.entity import Entity, BlockShield
from classes.inventory import Item, Inventory
from other.settings import *
import math


class NPC(Entity):
    def __init__(self, name, surf, pos, group, obstacle_sprites, role = "neutral"):
        super().__init__(group)
        self.name = name
        self.icon = UI["icons"][name.lower()]

        self.group = group
        self.role = role

        # General
        self.type = "npc"
        self.obstacle_sprites = obstacle_sprites
        self.sprite_dict = CHARACTER_SPRITES[name.lower()]


        # Location and Movement
        self.spawn = pygame.Vector2(pos)
        self.x, self.y = pygame.Vector2(pos)
        self.sprint_speed = 150

        # Image
        self.image = surf
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)

        self.screen_position = None

        # === random movement ===
        self.moving_randomly = False
        self.random_target = None
        self.random_target_reached = True
        self.move_delay = pygame.time.get_ticks() + 0
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

    def recruit(self, player,  name, level):

        if not len(player.active_allies) >= 3:
            new_recruit = Ally(name, level, self.image, self.spawn, self.group, self.obstacle_sprites)

            new_recruit.active = True
            player.active_allies.append(new_recruit)
            new_recruit.hp_bar = StatusBar(new_recruit, 28 * len(player.active_allies))
        else:
            new_recruit = Ally(name, level, self.image, self.spawn, self.group, self.obstacle_sprites)
            new_recruit.active = False
            player.inactive_allies.append(new_recruit)


        new_recruit.sprint_speed = 200
        new_recruit.walking_speed = 100




    def update_npc(self, player, window, offset) -> None:

        self.blocking_mechanics(window, offset)

        if not self.death:
            self.mask(window, offset)
            self.update_pos(offset=offset)

            self.update_animations()

class CombatNPC(NPC):
    def __init__(self, name, surf, pos, group, obstacle_sprites, role):
        super().__init__(name, surf, pos, group, obstacle_sprites, role)

        self.corrupted = random.choices(population=[True, False], weights=[0.25, 0.75], k=1)[0]


    def initialize_enemy(self, corrupted) -> list or None:
        core_stats = combat_moves = critical_hit_chance = blocking_chance = None
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

        # === scale stats to level ===
        for key in core_stats:
            core_stats[key] += self.level

        # === double stats for corruption ===


        return core_stats, combat_moves, critical_hit_chance, blocking_chance

    def item_use_logic(self):
        """Make the enemy use an item depending on certain circumstances."""
        if self.hp / self.max_hp <= 0.5 and not self.inventory.items["small_health_potion"] <= 0:
            self.current_attack = "small_health_potion"

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
                "impact_frame": self.sprite_dict[key]["impact_frame"] if self.sprite_dict[key].get(
                    "impact_frame") else ...
            }

        self.sprite_dict = new_sprite_dict

class Enemy(CombatNPC):
    def __init__(self, name, level, surf, pos, group, obstacle_sprites):
        super().__init__(name, surf, pos, group, obstacle_sprites, role = "enemy")

        # === stat related ===
        self.level = level

        self.core_stats, self.skills, self.critical_hit_chance, self.blocking_chance = self.initialize_enemy(self.corrupted)


        self.exp_given = self.exp_to_level()

        self.hp = int(10 + 1.5 * self.core_stats["vitality"])
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.mana = 0
        self.max_mana = 5

        # === inventory ===
        self.item_drop = "small_health_potion"
        self.inventory = Inventory(item = {"small_health_potion": 2})

        # === other ===
        self.detected_player = False
        self.respawn_time = pygame.time.get_ticks() + 0

        # === corrupted ===
        if self.corrupted:
            for key in self.core_stats:
                self.core_stats[key] = round(self.core_stats[key] * 1.5)
            self.recalculate_stats()

            print(self.core_stats)
            self.exp_given *= 2
            self.initialize_corrupted_enemy()

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

    def clone_enemy(self, name):
        """Spawn additional enemies when triggered before starting a battle."""
        clone = Enemy(name, self.level, self.image, self.screen_position, self.group, self.obstacle_sprites)

        if not self.corrupted:
            clone.corrupted = random.choices(population=[True, False], weights=[0.9, 0.1], k=1)[0]
            if clone.corrupted:
                clone.initialize_corrupted_enemy()

        return clone

    def update_npc(self, player, window, offset) -> None:
        super().update_npc(player, window, offset)

        if not self.death:

            # === chase the player ===
            if not player.in_battle and pygame.time.get_ticks() >= player.post_battle_iframes:
                self.chase_player(player)

            # === random wandering ===
            if not self.detected_player and not self.in_battle:
                self.random_movement()



class Ally(CombatNPC):
    def __init__(self, name, level, surf, pos, group, obstacle_sprites):
        super().__init__(name, surf, pos, group, obstacle_sprites, role = "hero")
        self.level = level
        self.core_stats, self.skills, self.critical_hit_chance, self.blocking_chance = self.initialize_enemy(self.corrupted)

        self.hp = self.max_hp = int(10 + 1.5 * self.core_stats["vitality"])
        self.mana = self.max_mana = self.core_stats["magic"]

        self.exp = 0
        self.max_exp = self.exp_to_level()

        self.active = None


    def follow_player(self, player):
        # Calculate distances between enemy and player
        x_distance = player.x - self.x  # Positive if player is to the right
        y_distance = player.y - self.y  # Positive if player is below

        # Calculate total distance using Pythagorean theorem
        distance = math.hypot(x_distance, y_distance)
        player_distance = 72
        ally_distance = 52 * player.active_allies.index(self)
        stop_distance =  player_distance + ally_distance


        if distance > 500:
            self.x, self.y = player.x, player.y
            self.update_pos()
        elif distance > stop_distance:
            self.sprinting = True
        else:
            self.sprinting = False

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

        if distance > stop_distance - 32:  # Prevent division by zero
            self.action = "running"
            dx = x_distance / distance  # Creates value between -1 and 1
            dy = y_distance / distance  # Creates value between -1 and 1
            self.move((dx, dy))
        else:
            self.action = "idle"


    # allies should have dominant core stats that get leveled rather than every stat
    def level_stats(self) -> None:
        """Automatically scale stats."""
        if self.stat_points > 0:
            for stat in self.core_stats.keys():
                self.core_stats[stat] += 10
            self.stat_points -= 1
        self.recalculate_stats() # domin implement

    def update_npc(self, player, window, offset) -> None:
        super().update_npc(player, window, offset)
        self.level_up_animation(offset)


        if not self.death:
            # === follow the player ===
            if not player.in_battle and self.active:
                self.level_stats()
                self.follow_player(player)






















