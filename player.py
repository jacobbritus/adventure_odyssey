import pygame
import math

class Player:
    def __init__(self, spawn_coordinates: tuple, sprite_dict: dict[str: str: list], direction: str):
        # location related
        self.x: int = spawn_coordinates[0]
        self.y: int = spawn_coordinates[1]

        # image related
        self.sprite_dict: dict[str: str: list] = sprite_dict
        self.direction: str = direction
        self.action: str = "idle"
        self.frame: int = 0

        self.size: tuple[int, int] = pygame.Surface.get_size(pygame.transform.scale(self.sprite_dict[self.action][self.direction][math.floor(self.frame)], (96, 96)))
        self.width, self.height = self.size

        # movement related
        self.sprinting: bool = False
        self.direction_pause = 0


    def move(self, move_vector: tuple[int, int]) -> None:
        """ Move the player's position on the map."""
        self.x += move_vector[0]
        self.y += move_vector[1]

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
                speed = 2 if self.sprinting else 1
                x, y = move_vector

                self.direction_pause += 0.1
                if self.direction_pause > 1:
                    self.action = "running"
                    self.move((x * speed, y * speed))

                break
        else:
            self.direction_pause = 0
            self.action = "idle"

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed = 0.2 if self.sprinting else 0.12
        self.frame += iterate_speed
        if self.frame >= len(self.sprite_dict[self.action][self.direction]): self.frame = 0

    def draw(self, window) -> None:
        """Draw the player in the game window."""
        self.controls()
        self.animations()
        current_sprite = self.sprite_dict[self.action][self.direction][math.floor(self.frame)]
        rescale = pygame.transform.scale(current_sprite, (96, 96))

        window.blit(rescale, (self.x, self.y))



