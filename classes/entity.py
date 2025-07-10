import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

        self.frame_index = 0
        self.animation_speed = 0.12
        self.direction = "down"
        self.action = "idle"



    def move(self, move_vector: tuple[int, int]):
        """Move the player based on the move vector."""
        dx, dy = move_vector
        speed = 4 if self.sprinting else 2
        dx *= speed
        dy *= speed

        # Move on X axis
        self.x += dx
        if self.obstacle_collisions():
            self.x -= dx

        # Move on Y axis
        self.y += dy
        if self.obstacle_collisions():
            self.y -= dy
        self.rect.topleft = (self.x, self.y)

    def obstacle_collisions(self) -> bool:
        """Check if the player is colliding with any other obstacle sprite."""
        self.hitbox = pygame.Rect(self.x + 12, self.y + 24, 12, 12)
        for sprite in self.obstacle_sprites:

            if self.hitbox.colliderect(sprite.hitbox):


                return True
        return False


