import math

import pygame.image

from classes.entity import Entity, BlockShield
from classes.spells import ProjectileSpell, StationarySpell
from classes.states import AnimationState
from other.play_sound import play_sound
from other.settings import *

class Player(Entity):
    """The player class."""
    def __init__(self, group, spawn_coordinates: tuple, direction: str, obstacle_sprites, dust_particles):
        super().__init__(group)

        # General
        self.type = "player"
        self.name = "Jacob"

        # Location
        self.x: int = spawn_coordinates[0]
        self.y: int = spawn_coordinates[1]
        self.screen_position = pygame.math.Vector2
        self.visibility = True

        # Movement
        self.sprinting: bool = False
        self.direction_pause = 0
        self.direction: str = direction
        self.action: str = "idle"
        self.blocking = False
        self.block_shield = BlockShield("right")

        self.sprint_speed = 200

        # Image
        self.sprite_dict: dict[str: str: list] = player_sprites
        self.icon = PLAYER_ICON
        self.image = self.sprite_dict[self.action]["sprites"][self.direction][math.floor(self.frame)]
        self.width, self.height = pygame.Surface.get_size(self.image)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)

        # Stats
        self.level = 1
        self.exp_to_level = 50
        self.leveled_up = True
        self.stat_points = 5

        self.exp = 0

        # === core stats ===
        self.core_stats = {
            "vitality": 10,
            "defense": 10,
            "strength": 10,
            "magic": 7,
            "speed": 9,
            "luck": 7,
        }

        self.hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.mana: int = 2
        self.max_mana = 5


        # Other
        self.obstacle_sprites = obstacle_sprites
        self.dust_spawn_time = 0
        self.dust_cooldown = 400
        self.dust_particles = dust_particles
        self.level_up_visual = pygame.sprite.Group()

        self.attacks = ["sword_slash", "punch", "fire_ball", "heal", "lightning_strike"]
        self.post_battle_iframes = pygame.time.get_ticks() + 0
        self.block_cooldown_end = pygame.time.get_ticks() + 0

    def blocking_critical_hotkey(self, event) -> None:
        """The player's block | crit hotkey with its delay."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            if not self.blocking and pygame.time.get_ticks() >= self.block_cooldown_end:
                self.blocking = True
                self.block_cooldown_end = pygame.time.get_ticks() + 2000

    def controls(self) -> None:
        """Perform actions based on the key pressed"""
        key_pressed = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if self.in_battle:
            return

        # Overworld controls

        if key_pressed[pygame.K_LSHIFT]:
            self.sprinting = True
            # self.footstep_delay = 200
            self.dust_cooldown = 200
        else:
            self.sprinting = False
            # self.footstep_delay = 400
            self.dust_cooldown = 400

        # movement keys with directions and move vectors
        movement_keys = {
            pygame.K_w: ("up", pygame.Vector2(0, -1)),
            pygame.K_s: ("down", pygame.Vector2(0, 1)),
            pygame.K_a: ("left", pygame.Vector2(-1, 0)),
            pygame.K_d: ("right", pygame.Vector2(1, 0))
        }

        move_dir = pygame.Vector2(0, 0)
        # handle movement keys
        for key, (direction, move_vector) in movement_keys.items():
            if key_pressed[key]:
                move_dir += move_vector
                self.direction = direction

            if current_time - self.dust_spawn_time > self.dust_cooldown and self.sprinting:
                self.dust_particles()
                self.dust_spawn_time = current_time

        if move_dir.length() > 0:
            move_dir = move_dir.normalize()
            self.action = "running"
            self.move((move_dir.x, move_dir.y))
        else:
            self.action = "idle"



    def recalculate_stats(self):
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])

    def handle_exp_gain(self, exp_amount):
        """Handle experience gained from battles."""
        self.exp += exp_amount
        self.leveled_up = False

        levels_gained = 0
        current_exp_to_level = self.exp_to_level
        remaining_exp = self.exp

        for _ in range(100):
            if remaining_exp >= current_exp_to_level:
                remaining_exp -= current_exp_to_level
                current_exp_to_level *= 2
                levels_gained += 1
            else:
                break

        if levels_gained > 0:
            self.level += levels_gained
            self.stat_points += levels_gained
            self.exp = remaining_exp
            self.exp_to_level = current_exp_to_level
            self.leveled_up = True

    def level_up_animation(self, offset, window) -> None:
        """Draws an animating shining light on the player upon leveling up."""
        if self.leveled_up:
            StationarySpell("level_up", self.level_up_visual, self.hitbox.center - pygame.Vector2(int(offset.x), int(offset.y)))
            play_sound("gameplay", "level_up", None)

            self.leveled_up = False



    def update_player(self, offset: pygame.Vector2, window) -> None:
        """Draw the player in the game window."""
        # debug_surface = pygame.Surface((self.hitbox.width, self.hitbox.height), pygame.SRCALPHA)
        # debug_surface.fill((255, 0, 0, 100))  # RGBA: red with 100 alpha
        # window.blit(debug_surface, (self.hitbox.topleft - offset))
        self.update_pos()
        self.screen_position = pygame.math.Vector2(int(self.x) - offset.x,
                                                   int(self.y) - offset.y)

        dmg_offset = 32
        self.dmg_position = pygame.Vector2(self.screen_position.x + dmg_offset + self.hitbox.width // 2,
                                           self.screen_position.y)


        self.mask(window, offset)

        self.blocking_mechanics(window, offset)


        self.controls()

        self.update_animations()
        self.level_up_animation(offset, window)





class DustParticle(pygame.sprite.Sprite):
    """A class to manage dust particles."""

    def __init__(self, player, group) -> None:
        super().__init__(group)
        # Create a copy of the original images to avoid modifying the source
        self.original_images: list[pygame.Surface] = [img.copy() for img in sprite_dust]
        self.type: str = "ground"
        self.player = player

        # Position the dust based on player direction
        self.offset_x = 36  # Default X offset
        self.offset_y = 48  # Default Y offset

        self.images = self.get_images()

        self.image = self.images[0]

        self.x, self.y = (player.x + self.offset_x, player.y + self.offset_y)
        self.rect = pygame.Rect(player.x + self.offset_x, player.y + self.offset_y, 24, 24)

        self.frame_index = 0

    def get_images(self) -> list[pygame.Surface] or None:
        """Adjust the images and offset based on the player's direction."""
        if self.player.direction == "up":
            self.offset_y += 8  # Position dust below player when moving up

            return [pygame.transform.rotate(pygame.transform.flip(img, False, True), 90)
                           for img in self.original_images]

        elif self.player.direction == "down":
            self.offset_y -= 8  # Position dust above player when moving down

            return [pygame.transform.flip(img, False, True) for img in self.original_images]

        elif self.player.direction == "left":
            self.offset_x += 16  # Position dust to the right when moving left

            return self.original_images.copy()

        elif self.player.direction == "right":
            self.offset_x -= 8  # Position dust to the left when moving right

            return [pygame.transform.flip(img, True, False) for img in self.original_images]

        return None


    def update(self) -> None:
        """Update the image and remove."""

        # Update animation
        self.image = self.images[int(self.frame_index)]
        if self.frame_index >= len(self.images) - 1:
            self.kill()

        # Update hitbox
        self.y -= 1
        self.rect.y += -1 # makes it go up a little
        self.frame_index += 0.2


