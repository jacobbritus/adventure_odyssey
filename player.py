import pygame
import math
from png_to_sprite import player_sprites

class Player:
    def __init__(self, spawn_coordinates: tuple, direction: str, obstacle_sprites):
        # location related
        self.x: int = spawn_coordinates[0]
        self.y: int = spawn_coordinates[1]

        self.obstacle_sprites = obstacle_sprites

        # image related
        self.sprite_dict: dict[str: str: list] = player_sprites
        self.direction: str = direction
        self.action: str = "idle"
        self.frame: int = 0

        self.size: tuple[int, int] = pygame.Surface.get_size(pygame.transform.scale(self.sprite_dict[self.action][self.direction][math.floor(self.frame)], (96, 96)))
        self.width, self.height = self.size
        self.image = None

        # movement related
        self.sprinting: bool = False
        self.direction_pause = 0

    def move(self, move_vector: tuple[int, int]):
        dx, dy = move_vector
        speed = 2 if self.sprinting else 1
        dx *= speed
        dy *= speed

        # Move on X axis
        self.x += dx
        if self.collision():
            self.x -= dx

        # Move on Y axis
        self.y += dy
        if self.collision():
            self.y -= dy

    def controls(self) -> None:
        """Perform actions based on the key pressed"""
        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_LSHIFT]:
            self.sprinting = True
        else:
            self.sprinting = False

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
                break
        else:
            self.direction_pause = 0
            self.action = "idle"

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed = 0.2 if self.sprinting else 0.12
        self.frame += iterate_speed
        if self.frame >= len(self.sprite_dict[self.action][self.direction]): self.frame = 0

    def collision(self) -> bool:
        player_rect = pygame.Rect(self.x + 12, self.y + 12, 8, 8)
        for sprite in self.obstacle_sprites:
            if player_rect.colliderect(sprite.rect):
                return True
        return False



    def draw(self, window) -> None:
        """Draw the player in the game window."""
        self.controls()
        self.animations()

        self.image = self.sprite_dict[self.action][self.direction][math.floor(self.frame)]

        self.collision()

        window.blit(self.image, (self.x, self.y))