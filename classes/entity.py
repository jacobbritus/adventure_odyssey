import math

import pygame

from classes.Tiles import ActionTile


class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)

        # Position related.
        self.x: int = 0
        self.y: int = 0

        # Image related.
        self.sprite_dict = None
        self.rect = None
        self.hitbox = None
        self.width = None
        self.height = None

        # Animation related.
        self.frame = 0
        self.animation_speed = 0.12

        # Action related.
        self.direction = "down"
        self.action = "idle"
        self.sprinting = None
        self.speed = 2

        # Other.
        self.in_battle = False
        self.obstacle_sprites = None

        self.approach_trigger = False
        self.return_trigger = False
        self.attack_trigger = False
        self.death = False

    def move(self, move_vector: tuple[int, int]) -> None:
        """Move the player based on the move vector."""
        if self.in_battle and not self.approach_trigger and not self.return_trigger:
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


    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        if self.death and self.frame >= len(self.sprite_dict[self.action][self.direction]):
            return
        iterate_speed: float = 0.2 if self.sprinting else 0.12

        if self.attack_trigger or self.death:
            iterate_speed = 0.1

        self.frame += iterate_speed

        if self.frame >= len(self.sprite_dict[self.action][self.direction]): self.frame = 0

    def obstacle_collisions(self) -> bool:
        """Check if the player is colliding with any other obstacle sprite."""
        self.hitbox = pygame.Rect(self.x + (self.width // 2), self.y + self.height // 2, 8, 8)
        for sprite in self.obstacle_sprites:
            if self.hitbox.colliderect(sprite.hitbox):
                return True
        return False


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


    def approach_animation(self, target):
        self.sprinting = True
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.action = "running"
            self.direction = "right" if dx > 0 else "left"
            self.move((dx * 2 / distance, dy * 2 / distance))



            if self.rect.inflate(-self.rect.width + 8, -self.rect.height // 2).colliderect(
                        target.rect.inflate(-target.rect.width // 2, -target.rect.height // 2)):

                self.frame = 0

                self.approach_trigger = False
                self.attack_trigger = True
                self.sprinting = False

    def attack_animation(self, target):
        self.action = "sword_slash"

        if self.frame != 0 and self.action != "sword_slash":
            self.frame = 0

        if target.hp <= 0 and self.frame > 3:
            target.death = True
            target.death_animation()

        if self.frame >= len(self.sprite_dict[self.action][self.direction]) - 1:
            self.action = "idle"

            if self.frame >= len(self.sprite_dict[self.action][self.direction]) - 1:
                self.attack_trigger = False
                self.action = "running"
                self.return_trigger = True

    def death_animation(self):
        # Only reset once at the start of the death animation
        if self.frame != 0 and self.action != "death":
            self.frame = 0

            self.action = "death"

        # Play the animation frame by frame
        if self.frame < len(self.sprite_dict[self.action][self.direction]) - 1:
            self.frame = len(self.sprite_dict[self.action][self.direction]) - 1



    def return_animation(self, origin):
        self.sprinting = True

        dx = origin.x - self.x + self.width // 2
        dy = origin.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.action = "running"
            self.direction = "right" if dx > 0 else "left"
            self.move((dx * 2 / distance, dy * 2 / distance))

            if distance < 30:
                self.direction = "left" if self.direction == "right" else "right"
                self.action = "idle"

                if self.frame != 0 and self.action != "sword_slash":
                    self.frame = 0
                if self.frame < len(self.sprite_dict[self.action][self.direction]) - 1:
                    self.return_trigger = False
                    self.sprinting = False





