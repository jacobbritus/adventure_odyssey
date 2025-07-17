import math
import pygame

from classes.projectile import Projectile
from other.settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        # General
        self.type = None
        self.group = group

        # Position related.
        self.x: int = 0
        self.y: int = 0
        self.screen_position = None

        # Image related.
        self.sprite_dict = None
        self.rect = None
        self.hitbox = None
        self.width = None
        self.height = None
        self.image = None

        # Animation related.
        self.frame = 0
        self.animation_speed = 0.12

        # Action related.
        self.direction = "down"
        self.action = "idle"
        self.sprinting = None
        self.speed = 2

        # Battle related.
        self.in_battle = False
        self.obstacle_sprites = None

        self.approach_trigger = False
        self.return_trigger = False
        self.attack_trigger = False
        self.death = False
        self.hit_landed = False
        self.blocking = False
        self.wait_trigger = False
        self.death_trigger = False
        self.current_action = None

        self.perfect_block = False
        self.perfect_block_messages = []
        self.critical_hit = False
        self.critical_hit_is_done = False
        self.critical_hit_messages = []

        # projectiles
        self.spawn_projectile = False
        self.projectiles = pygame.sprite.Group()
        self.casted_spell = False


        self.dmg_taken = []

        # Sound
        self.sound_played = False

        # Stats
        self.dmg = None

    def move(self, move_vector: tuple[int, int]) -> None:
        """Move the player based on the move vector."""
        if self.in_battle and not self.approach_trigger and not self.return_trigger:
            return
        dx, dy = move_vector
        self.speed = 4 if self.sprinting else 2
        dx *= self.speed
        dy *= self.speed

        self.x += dx
        self.rect.topleft = (self.x, self.y)  # update rect
        self.hitbox.topleft = self.rect.topleft
        if self.obstacle_collisions():
            self.x -= dx
            self.rect.topleft = (self.x, self.y)  # update rect after correction

        # Move on Y
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        if self.obstacle_collisions():
            self.y -= dy
            self.rect.topleft = (self.x, self.y)


    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed: float = 0.2 if self.sprinting else 0.12

        if self.attack_trigger or self.death:
            iterate_speed = 0.12

        self.frame += iterate_speed

        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]): self.frame = 0

        self.image = self.sprite_dict[self.action]["sprites"][self.direction][int(self.frame)]

    def obstacle_collisions(self) -> bool:
        """Check if the player is colliding with any other obstacle sprite."""
        # Centered hitbox of 32x32 relative to current sprite position
        self.hitbox = pygame.Rect(
            self.rect.centerx + 16,
            self.rect.centery  - 16,
            32,
            48
        )
        for sprite in self.obstacle_sprites:
            if self.hitbox.inflate(-16,  -32).colliderect(sprite.hitbox):
                print("yes")
                return True
        return False

    def face_target(self, target) -> None:
        """Update direction based on the target location."""
        dx: int = target.rect.centerx - self.rect.centerx
        dy: int = target.rect.centery - self.rect.centery

        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def approach_animation(self, target) -> None:
        """Run towards the target."""
        self.sprinting = True
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.action = "running"
            if dx > 0:
                self.direction = "right"
                hitbox_offset = 64
            else:
                self.direction = "left"
                hitbox_offset = 0


            self.move((dx / distance, dy / distance))

            self.hitbox.topleft = self.screen_position

            if self.hitbox.inflate(+ hitbox_offset, 0).colliderect(target.hitbox):

                self.approach_trigger = False
                self.frame = 0

                self.sprinting = False

                self.wait_trigger = True

    def wait(self):
        self.action = "idle"

    def projectile_animation(self, target):
        if self.spawn_projectile:
            Projectile(self.projectiles, pygame.Vector2(WINDOW_WIDTH // 2 + 48, WINDOW_HEIGHT // 2 + 16),
                       pygame.Vector2(target.hitbox.x, WINDOW_HEIGHT // 2), 5)
            pygame.mixer.Sound(fireball_sprites["sound"][0]).play()


            self.spawn_projectile = False

        for projectile in self.projectiles:
            if projectile.hit and not self.hit_landed:
                self.handle_attack_impact(target)
                self.hit_landed = True


        if not self.projectiles:

            # ___if critical hit___
            if self.critical_hit and not self.critical_hit_is_done:
                self.action = "idle"
                self.attack_trigger = True
                self.critical_hit = False
                self.critical_hit_is_done = True
                target.perfect_block = False


            # ___end attack sequence___
            else:
                self.action = "idle"
                self.attack_trigger = False
                self.return_trigger = True
                self.critical_hit_is_done = False
                self.critical_hit = False
                target.perfect_block = False
                self.hit_landed = False
                self.casted_spell = False


    def attack_animation(self, target, action) -> None:
        """Perform the action argument."""
        if action == "fire_ball":
            if not self.casted_spell:
                self.frame = 0
                self.action = "cast"
                self.casted_spell = True

            self.projectile_animation(target)
            self.current_action = action

            return
        else:
            self.current_action = action


        # this part could be separated depending on the attack type:

        # ___sprite frame reset___
        if self.frame != 0 and not self.action == self.current_action:
            self.frame = 0
            self.action = self.current_action

        # ___impact frame logic____
        impact_frame = self.sprite_dict[self.action]["impact_frame"]
        if impact_frame is not None and self.frame > impact_frame and not self.hit_landed and not target.death:
            self.hit_landed = True
            self.handle_attack_impact(target)
            # Mask when hit
            target.image = pygame.mask.from_surface(target.image).to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))


        # ___hit ends____
        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]) - 1:
            self.sound_played = False
            self.hit_landed = False
            self.action = "idle"

            # ___if critical hit___
            if self.critical_hit and not self.critical_hit_is_done:
                self.action = "idle" # done to reset for the second hit, not necessary for crits that dont repeat
                self.attack_trigger = True
                self.critical_hit = False
                self.critical_hit_is_done = True
                target.perfect_block = False


            # ___end attack sequence___
            else:
                self.action = "idle" # done to reset for the second hit, not necessary for crits that dont repeat
                self.attack_trigger = False
                self.return_trigger = True
                self.critical_hit_is_done = False
                self.critical_hit = False
                target.perfect_block = False

    def handle_attack_impact(self, target):
        if self.type == "enemy" and not self.critical_hit_is_done:
            self.critical_hit = True
            self.critical_hit_messages.append("")

        if self.blocking and not self.critical_hit_is_done:
            pygame.mixer.Channel(3).play(pygame.mixer.Sound(CRITICAL_HIT))
            self.critical_hit = True
            self.critical_hit_messages.append("")

        if target.blocking:
            target.perfect_block = True
            target.perfect_block_messages.append("")


        if not self.sound_played and not self.current_action == "fire_ball":
            print(self.action)
            pygame.mixer.Sound(self.sprite_dict[self.action]["sound"]).play()
            self.sound_played = True
        else:
            pygame.mixer.Sound(fireball_sprites["sound"][1]).play()
            self.sound_played = False

        base_dmg = self.dmg

        if target.blocking:
            base_dmg //= 2
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(PERFECT_BLOCK))

            target.action = "idle"


        target.hp -= base_dmg

        target.dmg_taken.append(base_dmg)


        # if target.hp <= 0:
        #     target.death_animation()
        #     print("check")

        if not target.hp <= 0:
            target.frame = 0
            target.action = "death"

    def death_animation(self) -> None:
        # Only reset once at the start of the death animation

        if self.action != "death":
            self.frame = 0
            self.action = "death"

        # Play the animation frame by frame
        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]) - 2:
            self.death = True
            print("yes")

    def return_animation(self, origin) -> None:
        """Walk back to the starting position."""

        self.sprinting = True

        dx = origin.x - self.x + self.width // 2
        dy = origin.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.action = "running"
            self.direction = "right" if dx > 0 else "left"
            self.move((dx / distance, dy / distance))

            if distance < 30:
                self.direction = "left" if self.direction == "right" else "right"
                self.action = "idle"

                if self.frame != 0 and self.action != "sword_slash":
                    self.frame = 0
                if self.frame < len(self.sprite_dict[self.action]["sprites"][self.direction]) - 1:
                    self.return_trigger = False
                    self.sprinting = False


    def update_animations(self) -> None:
        if self.hp <= 0:
            death_frame = len(self.sprite_dict["death"]["sprites"][self.direction]) - 1
            if self.frame >= death_frame:
                self.image = self.sprite_dict[self.action]["sprites"][self.direction][death_frame]
            else:
                self.animations()


        if self.action == "cast":
            cast_frame = len(self.sprite_dict[self.action]["sprites"][self.direction]) - 2

            if self.frame >= cast_frame:
                self.action = "idle"

            self.animations()


        elif not self.hp <=0:

            self.animations()

