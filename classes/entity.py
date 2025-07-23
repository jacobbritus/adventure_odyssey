import math
import random

import pygame.mixer

from classes.states import AnimationState
from classes.spells import Spells
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
        self.animation_speed = 0.6

        # Action related.
        self.direction = "down"
        self.action = "idle"
        self.sprinting = None
        self.movement_speed = None
        self.walking_speed = 1
        self.sprint_speed = None

        # Battle related.
        self.in_battle = False
        self.pre_battle_pos = None
        self.obstacle_sprites = None
        self.critical_hit_chance = None
        self.blocking_chance = None
        self.current_attack = None

        self.death = False
        self.hit_landed = False
        self.blocking = False
        self.current_attack = None

        self.perfect_block = False
        self.perfect_block_messages = []
        self.critical_hit = False
        self.critical_hit_is_done = False
        self.critical_hit_messages = []
        self.dmg_taken = []
        self.dmg_position = None

        self.mana_messages = []


        # projectiles
        self.spawn_projectile = False
        self.projectiles = pygame.sprite.Group()

        # Sound
        self.sound_played = False

        # Stats
        self.hp = None
        self.max_hp = None
        self.dmg = None

        # Animation states
        self.animation_state = AnimationState.IDLE

    def update_pos(self) -> None:
        self.rect.topleft = (self.x, self.y)  # update rect
        self.hitbox.center = self.rect.center

    def move(self, move_vector: tuple[int or float, int or float]) -> bool or None:
        """Move the player based on the move vector."""
        if self.in_battle and not self.animation_state in [AnimationState.APPROACH, AnimationState.RETURN]:
            return None
        dx, dy = move_vector
        if self.in_battle:
            self.movement_speed = 2
        elif self.sprinting:
            self.movement_speed = self.sprint_speed
        else:
            self.movement_speed = self.walking_speed

        dx *= self.movement_speed
        dy *= self.movement_speed

        # ___move horizontally___
        self.x += dx
        self.update_pos()

        if self.obstacle_collisions():
            self.x -= dx
            self.update_pos()
            return True

        # ___move vertically___
        self.y += dy
        self.update_pos()

        if self.obstacle_collisions():
            self.y -= dy
            self.update_pos()
            return True
        return False

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed: float = 0.1 if self.sprinting else 0.06

        self.frame += iterate_speed

        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]): self.frame = 0

        self.image = self.sprite_dict[self.action]["sprites"][self.direction][int(self.frame)]

    def obstacle_collisions(self) -> bool:
        """Check if the player is colliding with any other obstacle sprite."""

        for sprite in self.obstacle_sprites:
            if self.hitbox.colliderect(sprite.hitbox):
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
        """Approach the target in battle."""
        self.sprinting = True
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.action = "running"
            if dx > 0:
                self.direction = "right"
            else:
                self.direction = "left"

            self.move((dx / distance, dy / distance))

            # inflate to get a bit more distance depending on the move
            distance = 8 if self.current_attack == "punch" else 24
            if self.hitbox.colliderect(target.hitbox.inflate(+ distance, 0)):
                self.sprinting = False
                self.animation_state = AnimationState.WAIT

    def wait(self):
        """Idle before attacking."""
        self.action = "idle"

    def buff_animation(self):
        """Stationary battle actions"""
        if not self.spawn_projectile:
            position = pygame.Vector2(self.hitbox.centerx, self.hitbox.centery)

            Spells(self.projectiles, self.current_attack, position, None, None)
            self.spawn_projectile = True
            self.hp += 5
            if self.hp > self.max_hp: self.hp = self.max_hp
            pygame.mixer.Sound(moves[self.current_attack]["sound"]).play()

        if not self.projectiles:
            self.animation_state = AnimationState.IDLE

            self.spawn_projectile = False

    def projectile_animation(self, target):
        """Projectile battle actions."""
        if not self.spawn_projectile and self.current_attack == "fire_ball":
            offset = pygame.Vector2(12, 12)
            Spells(self.projectiles, "fire_ball",pygame.Vector2(self.hitbox.centerx, self.hitbox.centery) + offset,
                   pygame.Vector2(target.rect.centerx , target.rect.centery), 2.5)
            pygame.mixer.Sound(fireball_sprites["sound"][0]).play()
            self.spawn_projectile = True

        elif not self.spawn_projectile and self.current_attack == "lightning_strike":
            offset = pygame.Vector2(0, -106)
            Spells(self.projectiles, self.current_attack, pygame.Vector2(target.hitbox.centerx, target.hitbox.centery) + offset, None, None)
            self.spawn_projectile = True

        for projectile in self.projectiles:
            if projectile.hit and not self.hit_landed:
                self.handle_attack_impact(target)
                self.hit_landed = True

        if not self.projectiles:

            # ___end attack sequence___
            self.action = "idle"
            self.critical_hit = False
            target.perfect_block = False
            target.blocking = False
            self.hit_landed = False

            self.animation_state = AnimationState.IDLE


    def attack_animation(self, target, action) -> None:
        """Perform the action argument."""

        if moves[action]["type"] == "special":
            if not self.spawn_projectile:
                self.frame = 0
                self.action = "cast"

            self.projectile_animation(target)
            self.current_attack = action
            return

        # ___sprite frame reset___
        if not self.action == self.current_attack:
            self.frame = 0
            self.action = self.current_attack

        # ___impact frame logic____
        if self.sprite_dict[self.action]["impact_frame"] is not None:
            impact_frame = self.sprite_dict[self.action]["impact_frame"]
            if self.frame > impact_frame and not self.hit_landed and not target.death:
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
                self.animation_state = AnimationState.ATTACK

                self.critical_hit = False
                self.critical_hit_is_done = True
                target.perfect_block = False
                target.blocking = False


            # ___end attack sequence___
            else:
                self.action = "idle" # done to reset for the second hit, not necessary for crits that dont repeat
                self.animation_state = AnimationState.RETURN
                self.critical_hit_is_done = False
                self.critical_hit = False
                target.blocking = False
                target.perfect_block = False

    def handle_attack_impact(self, target):
        base_dmg = moves[self.current_attack]["dmg"]

        if self.blocking and not self.critical_hit_is_done:
            if self.type == "player":
                pygame.mixer.Channel(3).play(pygame.mixer.Sound(CRITICAL_HIT))
                self.critical_hit = True
                self.critical_hit_messages.append("")

            elif self.type == "enemy":
                bools = [True, False]
                weights = [self.critical_hit_chance, 1 - self.critical_hit_chance]
                self.critical_hit = random.choices(bools, k=1, weights = weights)[0]
                if self.critical_hit:
                    self.critical_hit_messages.append("")
                    pygame.mixer.Channel(3).play(pygame.mixer.Sound(CRITICAL_HIT))

            # for projectile-based / non-repeating attacks:
            if moves[self.current_attack]["type"] == "special":
                base_dmg *= 2

        # player attacks, enemy block chance
        if target.type == "enemy":
            bools = [True, False]
            weights = [target.blocking_chance, 1 - target.blocking_chance]
            target.blocking = random.choices(bools, k=1, weights=weights)[0]

        if target.blocking:
            target.perfect_block = True
            target.perfect_block_messages.append("")

            base_dmg //= 2
            pygame.mixer.Channel(1).play(pygame.mixer.Sound(PERFECT_BLOCK))


        if len(moves[self.current_attack]["sound"]) == 1:
            pygame.mixer.Sound(moves[self.current_attack]["sound"][0]).play()
        else:
            pygame.mixer.Sound(moves[self.current_attack]["sound"][1]).play()
        self.sound_played = True
        #
        # if not self.sound_played and not self.current_attack in ["fire_ball", "combustion"]:
        #     pygame.mixer.Sound(self.sprite_dict[self.action]["sound"]).play()
        #     self.sound_played = True
        # else:
        #     pygame.mixer.Sound(fireball_sprites["sound"][1]).play()
        #     self.sound_played = False


        target.hp -= base_dmg

        target.dmg_taken.append(base_dmg)

        if not target.hp <= 0:
            target.frame = 0
            target.action = "death" # hurt


    def death_animation(self) -> None:
        # Only reset once at the start of the death animation
        if self.action != "death":
            self.frame = 0
            self.action = "death"

        # Play the animation frame by frame
        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]) - 2:
            self.death = True

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

                self.animation_state = AnimationState.IDLE
                self.sprinting = False


    def update_animations(self) -> None:
        if self.hp <= 0:
            self.direction = "left"
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


        if not self.death:
            self.animations()

