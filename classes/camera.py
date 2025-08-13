import random

import pygame

from classes.UI import StatusBar
from classes.inventory import Item
from classes.states import BattleState, LevelState, AnimationState
from other.settings import *
from classes.battleloop import BattleLoop

class YSortCameraGroup(pygame.sprite.Group):
    """A custom sprite group that draws sprites with a camera offset, so the player stays centered.
       It also handles the player and enemy sprites and the game states.
    """
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.display_rect = self.display_surface.get_rect()


        # Calculate the center of the screen.
        self.screen_center_x = self.display_surface.get_width() // 2
        self.screen_center_y = self.display_surface.get_height() // 2

        # Used to track how far the player has moved from the center.
        self.offset = pygame.math.Vector2()
        self.offset_float = pygame.math.Vector2()

        self.enemy_sprites: list = []
        self.obstacles: []

        # Game state
        self.state = LevelState.OVERWORLD
        self.battle_participants = None
        self.player_pre_battle_pos = None
        self.enemy_pre_battle_pos = None
        self.battle_loop = None
        self.battle_position: pygame.math.Vector2 = pygame.math.Vector2()

        self.animation_camera = None

        self.delay = pygame.time.get_ticks() + 0
        self.transition_timer = 0
        self.delay_time = 3000

        self.shake_duration = 0
        self.shake_intensity = 2
        self.shake_offset = pygame.Vector2(0, 0)
        self.active_shake = False

        self.item_sprites = None

    def get_visible_sprites(self):
        """Get all sprites that are visible on the screen."""
        inflated_display_rect = self.display_rect.inflate(200, 300)
        for sprite in self.sprites():

            offset_pos = sprite.rect.topleft - self.offset
            if inflated_display_rect.collidepoint(offset_pos):

                if sprite.type == "enemy":
                    sprite.visibility = True

                yield sprite

    def update_camera(self, player):
        player.update_player(self.offset, self.display_surface)

        if self.state == LevelState.OVERWORLD:
            camera_speed = 0.1  # or try 0.2 ~ 0.4 for feel

            target_x = player.x - self.screen_center_x + 32
            target_y = player.y - self.screen_center_y + 32

            self.offset_float.x += (target_x - self.offset_float.x) * camera_speed
            self.offset_float.y += (target_y - self.offset_float.y) * camera_speed

            self.offset.x = self.offset_float.x
            self.offset.y = self.offset_float.y

        elif self.state == LevelState.BATTLE:
            camera_speed = 0.1  # adjust for snappiness

            # === standard camera target ===
            target = self.battle_position

            performer = self.battle_loop.performer
            attack_target = self.battle_loop.target

            # === camera shake trigger ===
            if performer.hit_landed and attack_target.blocking:# and MOVES[performer.current_attack]["shake"]:
                    self.shake_duration = 2000
                    self.shake_intensity = 1

            if performer.shake_screen:
                    self.shake_duration = 2000
                    self.shake_intensity = 1



            if performer.current_attack and performer.current_attack in performer.skills and MOVES[performer.current_attack]["type"] == "special":
                if performer.animation_state in [AnimationState.BUFF, AnimationState.WAIT]:
                    performer.stationary_spells.update((performer.hitbox.center - self.offset))
                    target = performer.rect.center
                elif performer.animation_state == AnimationState.ATTACK:
                    performer.projectiles.update(performer.hitbox.center - self.offset, self.offset, attack_target)
                    performer.stationary_spells.update((attack_target.hitbox.center - self.offset))
                    target = self.battle_position

            elif self.battle_loop.state in [BattleState.PLAYER_ANIMATION, BattleState.ENEMY_ANIMATION]:
                target = performer.rect.center

            # === apply camera shake ===
            if performer.shake_screen or attack_target and attack_target.shake_screen > 0:
                self.shake_offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offset.y = random.randint(-self.shake_intensity, self.shake_intensity)
                performer.shake_screen -= 100
            else:
                self.shake_offset = pygame.Vector2(0, 0)

            # === move offset to target by camera speed amount increments ===
            self.offset_float.x += (target[0] - self.screen_center_x - self.offset_float.x) * camera_speed
            self.offset_float.y += (target[1] - self.screen_center_y - self.offset_float.y) * camera_speed

            self.offset.x = self.offset_float.x + self.shake_offset.x
            self.offset.y = self.offset_float.y + self.shake_offset.y

    def draw_sprites(self):
        visible_sprites = list(self.get_visible_sprites())

        # === draw the ground sprites ===
        ground_sprites = [sprite for sprite in visible_sprites if
                          sprite.type and sprite.type in ["ground", "water"]]
        for sprite in ground_sprites:
            offset_pos = sprite.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
            self.display_surface.blit(sprite.image, offset_pos)


        overlapping_sprites = [sprite for sprite in visible_sprites
                         if sprite.type in ["player", "tree", "enemy", "item"]]

        # === draw the battle performer last ===
        draw_performer_last = self.battle_loop

        # === sort by ascending y positions ===
        sorted_sprites = sorted(overlapping_sprites,
                                key=lambda sprite: sprite.rect.centery + (32 if sprite.type == "tree" else 0))

        # === draw the y sorted sprites ===
        for sprite in sorted_sprites:
            if draw_performer_last and sprite == self.battle_loop.performer:
                continue
            if hasattr(sprite, "image"):
                # === draw player not using rect as that uses int ===
                if sprite.type == "player":
                    offset_pos = (sprite.x, sprite.y) - pygame.math.Vector2(self.offset.x, self.offset.y)

                else:
                    offset_pos = sprite.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
                self.display_surface.blit(sprite.image, offset_pos)

        if draw_performer_last:
            offset_pos = self.battle_loop.performer.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
            self.display_surface.blit(self.battle_loop.performer.image, offset_pos)

        self.offset += self.shake_offset

        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]


        self.item_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "item"]
        # for item in self.item_sprites:
        #     offset_pos = item.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
        #
        #     self.display_surface.blit(item.image, offset_pos)



    def start_battle(self):
        player = self.battle_participants["heroes"][0]
        heroes = self.battle_participants["heroes"]
        enemies = self.battle_participants["enemies"]

        second_enemy = random.choices([True, False], k=1, weights = [0.1, 0.9])[0]
        if second_enemy: enemies.append(enemies[0].clone("Skeleton"))

        heroes.append(enemies[0].clone("Goblin"))

        # for i, hero in enumerate(heroes):
        #
        #     if hero == player:
        #         continue
        #
        #     hero.mana = 5
        #
        #     setattr(hero, "mana", 5)
        #     setattr(hero, "max_mana", 5)
        #
        #     setattr(hero, "exp", 5)
        #     setattr(hero, "max_exp", 5)
        #
        #     hero.hp_bar = StatusBar(
        #     owner=hero,
        #     y_offset= i * 32)







        for participant in [*enemies, *heroes]:
            participant.in_battle = True
            participant.action = "idle"

        spots2 = self.find_battle_spot(player.rect)

        if spots2:
            self.state = LevelState.BATTLE

            def get_positions_in_rect(rect, n):
                spacing = 320
                y = rect.centery
                return [pygame.Vector2(rect.left + spacing * i, y) for i in range(1, n + 1)]

            def enemy_battle_spots(pos, n):
                spacing = 80
                positions = []

                total_height = spacing * (n - 1)  # total space between all enemies
                start_y = pos.y - total_height / 2  # first enemy starts above pos.y

                for i in range(n):
                    y = start_y + spacing * i
                    positions.append(pygame.Vector2(pos.x, y))  # same X, shifted Y

                return positions


            positions = get_positions_in_rect(spots2, 2)

            player_positions = enemy_battle_spots(positions[0], len(heroes))
            enemy_positions = enemy_battle_spots(positions[1], len(enemies))


            for index, hero in enumerate(heroes):
                hero.pre_battle_pos = (hero.x, hero.y)

                hero.x, hero.y = player_positions[index]
                hero.rect.topleft = (int(hero.x), int(hero.y))
                hero.battle_pos = pygame.Vector2(hero.x - 64, hero.y)


            for index, enemy in enumerate(enemies):
                enemy.pre_battle_pos = (enemy.x, enemy.y)

                enemy.x, enemy.y = enemy_positions[index]
                enemy.rect.topleft = (int(enemy.x), int(enemy.y))
                enemy.battle_pos = pygame.Vector2(enemy.x - 32, enemy.y)

                enemy.face_target(player)
                enemy.sprinting = False


            for hero in heroes:
                hero.face_target(enemies[0])
                hero.sprinting = False


            battle_center_x = (player.rect.centerx + enemies[0].rect.centerx) // 2

            if len(heroes) > 1:
                y_offset = 16 * len(list(heroes))
            else:
                y_offset = 16 * len(list(enemies))


            battle_center_y = (player.rect.centery + enemies[0].rect.centery) // 2 + y_offset
            self.battle_position.update(battle_center_x, battle_center_y)

            self.battle_loop = BattleLoop(heroes, enemies, self.display_surface, self.offset)



    def transition_screen(self):
        if self.transition_timer:
            now = pygame.time.get_ticks()
            time_elapsed = now - self.transition_timer
            alpha = int((time_elapsed / self.delay_time) * 1000)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  # enable per-pixel alpha

            overlay.fill((0, 0, 0, min(alpha, 255)))  # fill with black + alpha


            self.display_surface.blit(overlay, (0, 0))

            if now > self.delay:
                self.delay = None

                self.transition_timer = None

    def end_battle(self):
        heroes = self.battle_participants["heroes"]
        player = self.battle_participants["heroes"][0]
        original_enemy = self.battle_participants["enemies"][0]
        enemies = self.battle_participants["enemies"]

        for index, enemy in enumerate(enemies):
            if not index == 0: enemy.kill()

        if self.battle_loop.winner == heroes:
            original_enemy.respawn_time = pygame.time.get_ticks() + 600000

        else:
            player.hp = player.max_hp
            player.mana = player.max_mana
            player.death = False
            player.x, player.y = player.spawn
            player.rect.topleft = player.spawn

            for enemy in enemies:
                enemy.death = False
                enemy.hp = enemy.max_hp


        # === go back to initiate pos ====
        for participant in [player, original_enemy]:
            if participant == player and self.battle_loop.winner == enemies:
                participant.in_battle = False
                continue
            participant.in_battle = False
            participant.rect.topleft = participant.pre_battle_pos
            participant.x, participant.y = participant.pre_battle_pos

        self.battle_loop = None
        self.battle_participants = None
        self.state = LevelState.OVERWORLD
        player.hp_bar.display_exp = False



    def find_battle_spot(self, player_rect, search_radius = 640, step = 32) -> pygame.Rect or None:
        """Find a nearby unobstructed rectangular area for battle."""

        spot_size = (640, 128)

        obstacles = [sprite for sprite in self.sprites() if sprite.type == "tree"]

        cx, cy = player_rect.center # center of the player position

        # scan positions in a square area around the player
        for dx in range(-search_radius, search_radius + 1, step):
            for dy in range(-search_radius, search_radius + 1, step):
                # define candidate battle spot rectangle centered at (cx + dx, cy + cy)
                candidate = pygame.Rect(0,0, *spot_size)
                candidate.center = (cx + dx, cy + dy)

                collision = False

                for ob in obstacles:
                    if candidate.colliderect(ob.rect):
                        collision = True
                        break

                if not collision:
                    # pygame.draw.rect(self.display_surface, (255, 0,0), candidate)
                    return candidate
        return None