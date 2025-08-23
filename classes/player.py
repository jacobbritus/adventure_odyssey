import math

import pygame.image

from classes.UI import StatusBar
from classes.entity import Entity, BlockShield
from classes.inventory import Inventory
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
        self.role = "hero"
        self.name = "jacob"
        self.inventory = Inventory()

        # Location
        self.spawn = spawn_coordinates
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
        self.sprite_dict: dict[str: str: list] = CHARACTER_SPRITES[self.name]
        self.icon = UI["icons"][self.name]
        self.image = self.sprite_dict[self.action]["sprites"][self.direction][math.floor(self.frame)]
        self.width, self.height = pygame.Surface.get_size(self.image)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)

        # Stats
        self.level = 1
        self.exp = 0
        self.max_exp = self.exp_to_level()
        self.close_hp_bar_time = 0


        self.leveling = False
        self.stat_points = 0


        # === core stats ===
        self.core_stats = {
            "vitality": 5,
            "defense": 5,
            "strength": 5,
            "magic": 5,
            "speed": 5,
            "luck": 5,
        }

        self.hp = self.max_hp = int(10 + 2 * self.core_stats["vitality"])
        self.mana = 0
        self.max_mana = self.core_stats["magic"]

        # === allies ===
        self.active_allies = []
        self.inactive_allies = []


        # Other
        self.obstacle_sprites = obstacle_sprites
        self.dust_spawn_time = 0
        self.dust_cooldown = 400
        self.dust_particles = dust_particles
        self.level_up_visual = pygame.sprite.Group()

        self.skills = ["sword_slash", "punch", "overhead_slash", "heal", "lightning_strike"]
        self.post_battle_iframes = pygame.time.get_ticks() + 0
        self.block_cooldown_end = pygame.time.get_ticks() + 0

        # === items ===
        self.item_sprites = pygame.sprite.Group()
        self.item_use_delay = pygame.time.get_ticks() + 0

        self.status_bar = StatusBar(
            owner=self,
            y_offset=0)

    def blocking_critical_hotkey(self, event) -> None:
        """The player's block | crit hotkey with its delay."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            if not self.blocking and pygame.time.get_ticks() >= self.block_cooldown_end:
                self.blocking = True
                self.block_cooldown_end = pygame.time.get_ticks() + 2000

    def hotkeys(self, event, hp_bar):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            if not hp_bar.visible:
                hp_bar.visible = True
            else:
                hp_bar.visible = False


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



    def item_pickup_animation(self, window):
        if not self.in_battle: self.action = "item_use"
        if not self.in_battle: self.direction = "down"
        for item in self.item_sprites:
            item.draw(window, self.screen_position + (32, -16), "life_time")






    def update_player(self, offset: pygame.Vector2, window) -> None:
        """Draw the player in the game window."""
        # debug_surface = pygame.Surface((self.hitbox.width, self.hitbox.height), pygame.SRCALPHA)
        # debug_surface.fill((255, 0, 0, 100))  # RGBA: red with 100 alpha
        # window.blit(debug_surface, (self.hitbox.topleft - offset))
        self.update_pos(offset = offset)

        self.visual_cues(window, offset)




        self.controls()

        self.blocking_mechanics(window, offset)

        self.calculate_exp()

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


