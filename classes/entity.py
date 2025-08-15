import math
import random

import pygame.mixer

from archive.corruption_test import apply_dark_purple_tint
from classes.inventory import Item
from classes.states import AnimationState
from classes.spells import ProjectileSpell, StationarySpell
from other.play_sound import play_sound
from other.settings import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        # General
        self.type = None
        self.occupation = None
        self.group = group

        # Position related.
        self.x: float = 0
        self.y: float = 0
        self.screen_position = None
        self.visibility = False
        self.obstacle_sprites = None


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
        self.walking_speed = 100
        self.sprint_speed = None
        self.delta_time = FPS / 1000

        # === battle stuff ===
        self.hp_bar = None
        self.in_battle = False
        self.pre_battle_pos = None
        self.battle_pos = None
        self.current_attack = None
        self.selected = False

        self.critical_hit_chance = None
        self.blocking_chance = None

        self.death = False
        self.hit_landed = False
        self.current_attack = None
        self.hurt_time = pygame.time.get_ticks() + 200
        self.hurt_mask_opacity = 50

        self.shake_screen = False

        self.used_item = False
        self.item = None


        # === blocking ===
        self.blocked = False
        self.block_shield = BlockShield("left")
        self.blocking = False
        self.block_duration = pygame.time.get_ticks() + 0
        self.block_cooldown_end = pygame.time.get_ticks() + 0


        # === critical hit
        self.critical_hit = False
        self.critical_hit_is_done = False

        # === screen messages ===
        self.dmg_position = None
        self.screen_messages = []

        # === spells ===
        self.spawn_projectile = False
        self.projectiles = pygame.sprite.Group()
        self.stationary_spells = pygame.sprite.Group()
        self.spells = pygame.sprite.Group()

        # === items ===
        self.item_sprites = pygame.sprite.Group()

        self.item_use_delay = None
        self.inventory = None

        # === vital stats ===
        self.hp = None
        self.max_hp = None

        self.mana = None
        self.max_mana = None
        self.exp = None
        self.max_exp = None

        # === level ===
        self.level = None
        self.total_exp = 0
        self.close_hp_bar_time = None
        self.stat_points = 0
        self.leveling = False

        # === core stats ===
        self.core_stats = None

        # === animation states ===
        self.animation_state = None

        self.footstep_delay = 500

        # === status effects ===
        self.status_effect = None
        self.status_effect_count = 0

        # === corruption ===
        self.corrupted = False

    def calculate_exp(self):
        close_time = 4000

        if not self.exp >= self.total_exp and not self.exp == self.max_exp:
            # toggle hp_bar
            self.leveling = True
            self.hp_bar.visible = True
            self.hp_bar.display_exp = True

            speed = max(abs(self.exp - self.total_exp) * 0.025, 0.025)
            self.exp = min(self.exp + speed, self.max_exp)
            self.close_hp_bar_time = pygame.time.get_ticks() + close_time

        if self.exp == self.max_exp:
            if pygame.time.get_ticks() >= self.close_hp_bar_time - close_time // 2:
                self.level += 1
                self.stat_points += 1
                self.exp = 0
                self.total_exp = max(self.total_exp - self.max_exp, 0)
                self.max_exp += 20

        if pygame.time.get_ticks() >= self.close_hp_bar_time and self.leveling:
            self.leveling = False
            self.hp_bar.visible = False
            self.exp = round(self.exp)

    def recalculate_stats(self):
        self.max_hp: int = int(10 + 1.5 * self.core_stats["vitality"])
        self.hp = self.max_hp

    def blocking_mechanics(self, window, offset) -> None:
        if self.blocking:
            # if not self.action == "blocking":
            #     # self.action = "blocking"
            #     self.frame = 0

            if self.animation_state in [AnimationState.IDLE, AnimationState.DEATH, AnimationState.HURT]:

                self.block_shield.direction = self.direction
                if self.direction == "right":
                    block_jump = 16
                    shield_offset = (8, -36)
                else:
                    block_jump = -16
                    shield_offset = (-34, -36)

                pos = pygame.Vector2(self.hitbox.center - pygame.Vector2(int(offset.x), int(offset.y)) + shield_offset, offset)

                if self.blocked:
                    pos += (block_jump, 0)
                else:
                    pos = pygame.Vector2(
                        self.hitbox.center - pygame.Vector2(int(offset.x), int(offset.y)) + shield_offset, offset)

                self.block_shield.draw(window, pos)

            if pygame.time.get_ticks() >= self.block_duration:
                self.blocking = False
        else:
            self.block_duration = pygame.time.get_ticks() + 300


    def update_pos(self, **kw) -> None:
        self.rect.topleft = (round(self.x), round(self.y))  # update rect
        self.hitbox.center = self.rect.center

        offset = kw.get("offset")

        if offset:

            self.screen_position = pygame.math.Vector2(int(self.x) - offset.x,
                                                   int(self.y) - offset.y)

            dmg_offset = 32
            self.dmg_position = pygame.Vector2(self.screen_position.x + dmg_offset + self.hitbox.width // 2,
                                           self.screen_position.y)


    def get_dt(self, dt):
        self.delta_time = dt / 1000

    def footstep_sounds(self):
        if not pygame.time.get_ticks() >= self.footstep_delay and self.visibility:
            return


        footstep_sound = random.choice(GRASS_FOOTSTEPS)

        if self.type == "player" or self.in_battle:
            footstep_sound.set_volume(EFFECT_VOLUME)
        else:
            footstep_sound.set_volume(EFFECT_VOLUME /2)


        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(footstep_sound)
        else:
            footstep_sound.play()
        delay = 400 if not self.sprinting else 200
        self.footstep_delay = pygame.time.get_ticks() + delay

    def move(self, move_vector: tuple[int or float, int or float]) -> bool or None:
        """Move the player based on the move vector."""
        if self.in_battle and not self.animation_state in [AnimationState.APPROACH, AnimationState.RETURN]:
            return None
        dx, dy = move_vector
        if self.in_battle:
            self.movement_speed = 200
        elif self.sprinting:
            self.movement_speed = self.sprint_speed
        else:
            self.movement_speed = self.walking_speed

        dx *= self.movement_speed * self.delta_time
        dy *= self.movement_speed * self.delta_time

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
        self.footstep_sounds()

        return False

    def animations(self) -> None:
        """Iterate over the sprite list assigned to the action > direction."""
        iterate_speed: float = 0.2 if self.sprinting else 0.12

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
            distance = 8 if self.current_attack == "punch" else 10
            if self.hitbox.colliderect(target.hitbox.inflate(+ distance, 0)):
                self.y = target.y
                self.sprinting = False
                self.animation_state = AnimationState.WAIT

    def wait(self):
        """Idle before attacking."""
        self.action = "idle"

    def item_animation(self, window):
        item = self.current_attack

        if not self.used_item:
            Item(self.item_sprites, item, None, self.screen_position)
            self.use_item(item)
            self.used_item = True

        self.action = "idle"

        if self.item_sprites:
            for item in self.item_sprites:
                item.draw(window, self.dmg_position + (-16, 28), True)

    def use_item(self, item):
        if ITEMS[item]["type"] == "consumable":
            # self.hp_bar.visible = True

            # === access stats ====
            stat_name = ITEMS[item]["stat"]
            current_value = getattr(self, stat_name)
            max_value = getattr(self, f"max_{stat_name}")
            item_effect = ITEMS[item]["effect"]

            # === don't use item if no effect ===
            if current_value == max_value:
                return

            # === update stat
            setattr(self, stat_name, min(current_value + item_effect, max_value))

            self.screen_messages.append(("hp_recovered", 5, (0, 255, 0)))
            self.item_use_delay = pygame.time.get_ticks() + 3000
            self.inventory.items[item] -= 1

            self.used_item = False









    def buff_animation(self):
        """Stationary battle actions"""
        if not self.spawn_projectile:
            position = pygame.Vector2(self.hitbox.centerx, self.hitbox.centery)

            if self.current_attack == "heal":
                StationarySpell("heal", [self.spells, self.stationary_spells],
                                position)

                self.spawn_projectile = True
                heal_amount = SKILLS[self.current_attack]["hp"]
                self.hp += heal_amount
                self.hp = min(self.hp, self.max_hp)

                self.screen_messages.append(("hp_recovered", 5, (0, 255, 0)))

                pygame.mixer.Sound(SKILLS[self.current_attack]["sound"]).play()

        if not self.projectiles:
            self.animation_state = AnimationState.WAIT

            self.spawn_projectile = False

    def projectile_animation(self, target):
        """Projectile battle actions."""
        if not self.spawn_projectile and self.current_attack == "fire_ball":
            offset = pygame.Vector2(12, 12)
            ProjectileSpell([self.projectiles, self.spells], "fire_ball", pygame.Vector2(self.hitbox.centerx, self.hitbox.centery) + offset,
                            pygame.Vector2(target.rect.centerx , target.rect.centery), 4)
            pygame.mixer.Sound(fireball_sprites["sound"][0]).play()
            self.spawn_projectile = True

        if not self.spawn_projectile and self.current_attack == "lightning_strike":
            StationarySpell("lightning_strike", [self.stationary_spells, self.spells], pygame.Vector2(target.hitbox.centerx, target.hitbox.centery))
            self.spawn_projectile = True


        for projectile in self.spells:
            if projectile.hit and not self.hit_landed:
                play_sound("moves", self.current_attack, 1)
                self.handle_attack_impact(target)
                self.hit_landed = True

        if not self.projectiles and not self.stationary_spells:

            # ___end attack sequence___
            self.action = "idle"
            self.critical_hit = False
            self.hit_landed = False

            self.animation_state = AnimationState.IDLE


    def attack_animation(self, target, action) -> None:
        """Perform the action argument."""

        if SKILLS[action]["type"] == "special":
            if not self.spawn_projectile:
                self.frame = 0
                self.action = "cast"
            self.projectile_animation(target)
            self.current_attack = action
            return

        # ___sprite frame reset___
        if not self.action == self.current_attack and not self.hit_landed:
            self.frame = 0
            self.action = self.current_attack

        # ___impact frame logic____
        if self.sprite_dict[self.action]["impact_frame"] and not self.hit_landed:
            impact_frame = self.sprite_dict[self.action]["impact_frame"]
            if self.frame > impact_frame and not self.hit_landed and not target.death:
                if not self.shake_screen:
                    self.shake_screen = 1000
                self.hit_landed = True

                play_sound("moves", self.current_attack, None)

                self.handle_attack_impact(target)

                if target.blocking:
                    if not self.shake_screen:
                        self.shake_screen = 1000
                    pygame.time.wait(20)
                    self.frame = len(self.sprite_dict[self.action]["sprites"][self.direction]) - 1
                    target.blocked = True
                    push_back = -16 if self.direction == "right" else 16
                    self.x += push_back
                else:
                    pygame.time.wait(20)

        # === wait for a bit ===
        if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]) - 1 or target.hp <= 0:
            if self.action != "idle":
                self.action = "idle"
                self.frame = 0

            # ___hit ends____
            if self.frame >= len(self.sprite_dict[self.action]["sprites"][self.direction]) - 1:
                self.hit_landed = False

                # ___if critical hit___
                if self.critical_hit and not self.critical_hit_is_done and not target.hp <= 0:
                    if target.blocked:
                        pull_close = 16 if self.direction == "right" else -16
                        self.x += pull_close
                    self.critical_hit_is_done = True
                    target.blocked = False




                # ___end attack sequence___
                else:
                    target.blocked = False
                    self.animation_state = AnimationState.RETURN
                    self.critical_hit_is_done = False
                    self.critical_hit = False

    def hurt_animation(self):
        if self.action != "death":
            self.frame = 0
            self.action = "death"  # will be changed to AnimationState.HURT




    def calculate_damage(self):
        skill = self.current_attack
        base = SKILLS[skill]["base_damage"]
        stat_name = SKILLS[skill]["stat"]
        multiplier = SKILLS[skill]["multiplier"]

        stat_value = self.core_stats[stat_name]
        bonus = stat_value * multiplier

        total_damage = base + bonus

        return int(total_damage)

    def handle_attack_impact(self, target):
        damage = self.calculate_damage()

        if not self.critical_hit_is_done:

            if self.type == "player" and self.blocking:
                play_sound("gameplay", "critical_hit", None)
                self.critical_hit = True
                self.screen_messages.append(("critical_hit", "CRITICAL HIT!", (255, 255, 102)))

                # for projectile-based / non-repeating attacks:
                if SKILLS[self.current_attack]["type"] == "special":
                    damage *= 2


            if self.type == "npc" and not self.critical_hit_is_done:
                bools = [True, False]
                weights = [self.critical_hit_chance, 1 - self.critical_hit_chance]
                self.critical_hit = random.choices(bools, k=1, weights = weights)[0]
                if self.critical_hit:
                    target.block_cooldown_end = pygame.time.get_ticks() + 0
                    self.screen_messages.append(("critical_hit", "CRITICAL HIT!", (255, 255, 102)))
                    play_sound("gameplay", "critical_hit", None)

                # for projectile-based / non-repeating attacks:
                if SKILLS[self.current_attack]["type"] == "special":
                    damage *= 2

        # player attacks, enemy block chance
        if target.type == "npc":
            bools = [True, False]
            weights = [target.blocking_chance, 1 - target.blocking_chance]
            target.blocking = random.choices(bools, k=1, weights=weights)[0]

        if target.blocking:
            target.screen_messages.append(("perfect_block", "PERFECT BLOCK!", (200, 255, 150)))

            damage //= 2
            play_sound("gameplay", "perfect_block", None)


        target.hp -= damage
        target.hp = max(target.hp, 0)
        target.screen_messages.append(("hp_dealt", "-" + str(damage), (217, 87, 99)))

        if not target.hp <= 0 and not target.blocking:

            # === afflict the status effect if applicable
            status_effect = SKILLS[self.current_attack].get("status_effect")
            if status_effect and not target.status_effect:
                target.status_effect = status_effect
                status_effect_name = status_effect.value["name"]
                color = status_effect.value["color"]

                target.screen_messages.append(("perfect_block", status_effect_name, color))


            target.animation_state = AnimationState.HURT
        elif target.hp <= 0:
            target.animation_state = AnimationState.DEATH

    def handle_status_effect(self):
        if self.status_effect:
            play_sound("gameplay", self.status_effect.value["name"].lower(), None)

            if self.status_effect == StatusEffects.BURNED:
                damage = 2
                self.hp -= damage
                self.screen_messages.append(("hp_dealt", "-" + str(damage), (255, 87, 34)))
                self.status_effect_count += 1

            elif self.status_effect == StatusEffects.POISONED:
                damage = 1
                self.hp -= 1
                self.screen_messages.append(("hp_dealt", "-" + str(damage), (102, 205, 170)))
                self.status_effect_count += 1

            if self.status_effect_count > StatusEffects.BURNED.value["turns"]:
                self.status_effect = None



    def death_animation(self) -> None:
        # === reset action to death once when called ===
        if self.action != "death":
            self.frame = 0
            self.action = "death"
            self.hurt_time = pygame.time.get_ticks() + 500


        death_frame = len(self.sprite_dict["death"]["sprites"][self.direction]) - 1
        if self.frame >= death_frame:
            self.death = True
            # = set to None to make the animation phases continue after a death (AnimationState.DEATH).
            self.animation_state = None


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

        if self.action == "cast":
            last_frame = len(self.sprite_dict[self.action]["sprites"][self.direction]) - 2

            if self.frame >= last_frame:
                self.action = "idle"



        if not self.death:
            self.animations()
            if self.animation_state == AnimationState.DEATH:
                self.death_animation()


        else:
            self.image = self.sprite_dict[self.action]["sprites"][self.direction][-1]

    def mask(self, window, offset):
            if self.type == "enemy" and self.corrupted:
                self.image = apply_dark_purple_tint(self.image)
                #
                # mask = pygame.mask.from_surface(self.image).to_surface(
                #     setcolor=(48, 25, 52, 150),
                #     unsetcolor=(0, 0, 0, 0))
                # window.blit(mask, pygame.Vector2(self.x, self.y) - offset)



            if self.animation_state in (AnimationState.HURT, AnimationState.DEATH):
                if not pygame.time.get_ticks() >= self.hurt_time - 250:
                    self.hurt_mask_opacity += 25
                    self.hurt_mask_opacity = min(200, self.hurt_mask_opacity)

                elif pygame.time.get_ticks() >= self.hurt_time - 250:
                    self.hurt_mask_opacity -= 25
                    self.hurt_mask_opacity = max(0, self.hurt_mask_opacity)

                mask = pygame.mask.from_surface(self.image).to_surface(
                    setcolor=(180, 0, 0, self.hurt_mask_opacity),
                    unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)
            elif not self.occupation == "hero" and not self.selected and self.animation_state == AnimationState.IDLE:
                mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(0, 0, 0, 100),
                                                                       unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)

            elif self.status_effect == StatusEffects.BURNED:

                mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 87, 34, 100),
                                                                       unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)

            elif self.status_effect == StatusEffects.POISONED:

                mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(102, 205, 170, 100),
                                                                       unsetcolor=(0, 0, 0, 0))
                window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)



            else:
                self.hurt_mask_opacity = 0
            #
            # if self.blocking:
            #     mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(255, 255, 255, 150),
            #                                                            unsetcolor=(0, 0, 0, 0))
            #     window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)

            # if self.used_item and ITEMS[self.current_attack]["type"] == "healing":
            #     mask = pygame.mask.from_surface(self.image).to_surface(setcolor=(0, 255, 0, 150),
            #                                                                unsetcolor=(0, 0, 0, 0))
            #     window.blit(mask, pygame.Vector2(self.rect.topleft) - offset)




class BlockShield:
    def __init__(self, direction):
        self.sprites = block_shield_sprites
        self.frame = 0
        self.direction = direction
        self.image = self.sprites["sprites"][self.direction][int(self.frame)]
        self.offset = 0

    def draw(self, window, pos):
        self.update()
        window.blit(self.image, pos + (self.offset, 0))

    def update(self):
        self.frame += 0.2

        if self.frame >= len(self.sprites["sprites"][self.direction]) - 1:
            self.frame = 0

        self.image = self.sprites["sprites"][self.direction][int(self.frame)]