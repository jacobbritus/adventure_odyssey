import pygame
import math

from classes.entity import Entity
from other.png_to_sprite import player_sprites, sprite_dust


class Player(Entity):
    """The player class."""
    def __init__(self, group, spawn_coordinates: tuple, direction: str, obstacle_sprites, dust_particles, enemy_sprites):
        super().__init__(group)
        self.dust_spawn_time = 0
        self.dust_cooldown = 400
        self.dust_particles = dust_particles

        # location related
        self.x: int = spawn_coordinates[0]
        self.y: int = spawn_coordinates[1]

        self.obstacle_sprites = obstacle_sprites
        self.enemy_sprites = enemy_sprites
        self.type = "player"

        # image related
        self.sprite_dict: dict[str: str: list] = player_sprites
        self.direction: str = direction
        self.action: str = "idle"
        self.frame: int = 0

        self.image = self.sprite_dict[self.action][self.direction][math.floor(self.frame)]
        self.width, self.height = pygame.Surface.get_size(self.image)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.hitbox = pygame.Rect(self.x + 12, self.y + 24, 12, 12)

        # movement related
        self.sprinting: bool = False
        self.direction_pause = 0

        # sound related
        self.footstep_sound = pygame.mixer.Sound("sounds/Walk/Grass/GRASS - Walk 7.wav")
        self.footstep_sound.set_volume(0.2)

        self.footstep_timer = 0
        self.footstep_delay = 50
        self.last_footstep_time = pygame.time.get_ticks()



    def controls(self) -> None:
        """Perform actions based on the key pressed"""
        key_pressed = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

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

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed: float = 0.2 if self.sprinting else 0.12
        self.frame += iterate_speed
        if self.frame >= len(self.sprite_dict[self.action][self.direction]): self.frame = 0


    def enemy_collisions(self):
        self.hitbox = pygame.Rect(self.x + 12, self.y + 24, 12, 12)
        for sprite in self.enemy_sprites:

            if self.hitbox.colliderect(sprite.hitbox):
                print("yes")


    def update(self) -> None:
        """Draw the player in the game window."""
        self.enemy_collisions()
        self.controls()
        self.animations()
        self.image = self.sprite_dict[self.action][self.direction][math.floor(self.frame)]


class DustParticle(pygame.sprite.Sprite):
    """A class to manage dust particles."""

    def __init__(self, player, group) -> None:
        super().__init__(group)
        # Create a copy of the original images to avoid modifying the source
        self.original_images: list[pygame.Surface] = [img.copy() for img in sprite_dust]
        self.type: str = "ground"
        self.player = player

        # Position the dust based on player direction
        offset_x = 4  # Default X offset
        offset_y = 32  # Default Y offset

        # Transform all frames based on direction
        if player.direction == "up":
            self.images = [pygame.transform.rotate(pygame.transform.flip(img, False, True), 90)
                           for img in self.original_images]
            offset_y += 6  # Position dust below player when moving up

        elif player.direction == "down":
            self.images = [pygame.transform.flip(img, False, True) for img in self.original_images]
            offset_y -= 8  # Position dust above player when moving down

        elif player.direction == "left":
            self.images = self.original_images.copy()
            offset_x += 16  # Position dust to the right when moving left

        elif player.direction == "right":
            self.images = [pygame.transform.flip(img, True, False) for img in self.original_images]
            offset_x -= 8  # Position dust to the left when moving right


        self.image = self.images[0]



        self.rect = pygame.Rect(player.x + offset_x, player.y + offset_y, 24, 24)

        self.frame_index = 0

    def update(self) -> None:
        """Update the position of the dust particle."""

        # Update animation
        self.image = self.images[int(self.frame_index)]
        if self.frame_index >= len(self.images) - 1:
            self.kill()

        self.rect.y += -1
        self.frame_index += 0.2
