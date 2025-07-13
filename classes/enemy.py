from classes.entity import Entity
from other.settings import *
import math

class Enemy(Entity):
    def __init__(self, monster_name, surf, pos, group, obstacle_sprites):
        super().__init__(group)

        # General
        self.type = "enemy"
        self.obstacle_sprites = obstacle_sprites

        # Stats
        self.monster_name = monster_name
        self.hp = 15
        self.dmg = 5

        # Location
        self.x = pos[0]
        self.y = pos[1]

        # Image
        self.sprite_dict = self.get_sprites()
        self.image = surf
        self.width, self.height = pygame.Surface.get_size(surf)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hitbox = self.rect.inflate(32, 32)

    def get_sprites(self) -> list or None:
        if self.monster_name == "Skeleton":
            return skeleton_sprites
        else:
            return None

    def get_status(self, player) -> None:
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

    def update_enemy(self, player) -> None:
        """Draw the player in the game window."""
        if not self.in_battle: self.get_status(player)
        if not self.death: self.animations()
        self.image = self.sprite_dict[self.action]["sprites"][self.direction][int(self.frame)]




