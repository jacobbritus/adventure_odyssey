import math

import pygame

from classes.entity import Entity
from other.settings import *

class Player(Entity):
    """The player class."""
    def __init__(self, group, spawn_coordinates: tuple, direction: str, obstacle_sprites, dust_particles):
        super().__init__(group)

        # General
        self.type = "player"

        # Location
        self.x: int = spawn_coordinates[0]
        self.y: int = spawn_coordinates[1]
        self.screen_position = pygame.math.Vector2

        # Movement
        self.sprinting: bool = False
        self.direction_pause = 0
        self.direction: str = direction
        self.action: str = "idle"
        self.blocking = False

        # Image
        self.sprite_dict: dict[str: str: list] = player_sprites
        self.image = self.sprite_dict[self.action]["sprites"][self.direction][math.floor(self.frame)]
        self.width, self.height = pygame.Surface.get_size(self.image)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(-64, -48)

        # Sound
        self.footstep_sound = pygame.mixer.Sound(GRASS_FOOTSTEP)
        self.footstep_sound.set_volume(0.2)

        self.footstep_delay = 400
        self.last_footstep_time = pygame.time.get_ticks()

        # Stats
        self.level = 1
        self.hp: int = 20
        self.max_hp: int = 20
        self.mana: int = 5
        self.dmg: int = 5
        self.speed = 3

        self.movement_speed: int = 2 # dont forget to implement this in entity class move()

        # Other
        self.obstacle_sprites = obstacle_sprites
        self.dust_spawn_time = 0
        self.dust_cooldown = 400
        self.dust_particles = dust_particles

        self.mask_image = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))


        self.attacks = ["sword_slash", "punch", "fire_ball", "heal", "lightning_strike"]

    def controls(self) -> None:
        """Perform actions based on the key pressed"""
        key_pressed = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()



        if self.in_battle:
            return

        # Overworld controls

        if key_pressed[pygame.K_LSHIFT]:
            self.sprinting = True
            self.footstep_delay = 200
            self.dust_cooldown = 200
        else:
            self.sprinting = False
            self.footstep_delay = 400
            self.dust_cooldown = 400

        # movement keys with directions and move vectors
        movement_keys = {
            pygame.K_w: ("up", (0, -1)),
            pygame.K_s: ("down", (0, 1)),
            pygame.K_a: ("left", (-1, 0)),
            pygame.K_d: ("right", (1, 0))
        }

        # handle movement keys
        for key, (direction, move_vector) in movement_keys.items():
            if key_pressed[key]:
                self.direction = direction
                x, y = move_vector

                self.direction_pause += 0.1
                if self.direction_pause > 1:
                    self.action = "running"
                    self.move((x , y))

                    if current_time - self.dust_spawn_time > self.dust_cooldown and self.sprinting:
                        self.dust_particles()
                        self.dust_spawn_time = current_time

                    # Play sound effects.
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_footstep_time > self.footstep_delay:
                        self.footstep_sound.play()
                        self.last_footstep_time = current_time
                break
        else:
            self.direction_pause = 0
            self.action = "idle"

    def update_player(self, offset, window) -> None:
        """Draw the player in the game window."""
        # print(offset)

        self.update_pos(offset)
        if self.blocking:
            mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
            window.blit(mask, self.screen_position)

        self.controls()

        self.update_animations()



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
        self.rect.y += -1 # makes it go up a little
        self.frame_index += 0.2


