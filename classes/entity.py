import pygame

from classes.Tiles import ActionTile


class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

        # Position related.
        self.x: int = 0
        self.y: int = 0

        # Image related.
        self.rect = None
        self.hitbox = None

        # Animation related.
        self.frame_index = 0
        self.animation_speed = 0.12

        # Action related.
        self.direction = "down"
        self.action = "idle"
        self.sprinting = None
        self.speed = 2

        # Other.
        self.in_battle_position = False
        self.obstacle_sprites = None

    def move(self, move_vector: tuple[int, int]) -> None:
        """Move the player based on the move vector."""
        if self.in_battle_position:
            return
        dx, dy = move_vector
        self.speed = 4 if self.sprinting else 2
        dx *= self.speed
        dy *= self.speed

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

    def teleport_to_spot(self, spot) -> None:
        self.x = spot.rect.centerx - self.rect.width // 2
        self.y = spot.rect.centery - self.rect.height // 2
        self.rect.topleft = (self.x, self.y)
        self.hitbox = pygame.Rect(self.x + 12, self.y + 24, 12, 12)
        self.action = "idle"

    def face_target(self, target) -> None:
        dx: int = target.rect.centerx - self.rect.centerx
        dy: int = target.rect.centery - self.rect.centery

        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def find_two_closest_battle_spots(self, battle_spots: list[ActionTile]) -> list[pygame.sprite.Sprite]:
        """Returns the two closest battle spots sorted from left to right."""
        # Calculate distance to all spots
        spots_with_distance = []
        for spot in battle_spots:
            dx = spot.rect.centerx - self.rect.centerx
            dy = spot.rect.centery - self.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5
            spots_with_distance.append((distance, spot))

        # Sort by distance
        spots_with_distance.sort(key=lambda x: x[0])

        # Get two closest
        two_closest = [s[1] for s in spots_with_distance[:2]]

        # Sort by x (left to right)
        two_closest.sort(key=lambda s: s.rect.centerx)
        return two_closest





