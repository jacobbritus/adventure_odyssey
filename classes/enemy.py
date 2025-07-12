from classes.entity import Entity
from other.settings import *
import math

class Enemy(Entity):
    def __init__(self, monster_name, surf, pos, group, obstacle_sprites):
        super().__init__(group)

        # General Setup.
        self.type = "enemy"
        self.obstacle_sprites = obstacle_sprites
        self.sprite_dict = skeleton_sprites

        # Graphics Setup.
        self.image = surf
        self.x = pos[0]
        self.y = pos[1]
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(32, 32)

        self.frame = 0
        self.sprinting = False

        self.monster_name = monster_name

        # battle stuff
        self.hp = 15
        self.dmg = 3



    def get_status(self, player):
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

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed: float = 0.2 if self.sprinting else 0.12
        self.frame += iterate_speed
        if self.frame >= len(self.sprite_dict[self.action][self.direction]): self.frame = 0


    def enemy_update(self, player) -> None:
        """Draw the player in the game window."""
        if not self.in_battle: self.get_status(player)
        self.animations()
        self.image = self.sprite_dict[self.action][self.direction][int(self.frame)]

