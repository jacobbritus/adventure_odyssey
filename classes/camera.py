import random

import pygame

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
        self.shake_intensity = 5
        self.shake_offset = pygame.Vector2(0, 0)



    def get_visible_sprites(self):
        """Get all sprites that are visible on the screen."""
        inflated_display_rect = self.display_rect.inflate(200, 300)
        for sprite in self.sprites():
            if sprite.type == "enemy":
                sprite.visibility = True
            offset_pos = sprite.rect.topleft - self.offset
            if inflated_display_rect.collidepoint(offset_pos):
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
            camera_speed = 0.2  # adjust for snappiness

            # Fallback to battle position
            target = self.battle_position
            enemy = self.battle_participants["enemies"][0]
            player = self.battle_participants["heroes"][0]

            # CHANGE TO THE ONE IN TURN
            performer = self.battle_loop.performer
            attack_target = self.battle_loop.target

            if performer.spells:
                if performer.animation_state in [AnimationState.BUFF, AnimationState.WAIT]:
                    performer.stationary_spells.update((performer.hitbox.center - self.offset))
                    target = performer.rect.center
                if performer.animation_state == AnimationState.ATTACK:
                    performer.projectiles.update(performer.hitbox.center - self.offset, self.offset, attack_target)
                    performer.stationary_spells.update((attack_target.hitbox.center - self.offset))
                    target = self.battle_position


            elif self.battle_loop.state in [BattleState.PLAYER_ANIMATION, BattleState.ENEMY_ANIMATION] and not performer.animation_state == AnimationState.IDLE:
                target = performer.rect.center

            # elif self.battle_loop.state == BattleState.PLAYER_ANIMATION and not player.animation_state == AnimationState.IDLE :
            #     target = player.rect.center
            # elif self.battle_loop.state == BattleState.ENEMY_ANIMATION and not enemy.animation_state == AnimationState.IDLE :
            #     target = enemy.rect.center

            # Apply shake
            if self.shake_duration > 0:
                self.shake_offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offset.y = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_duration -= 1
            else:
                self.shake_offset = pygame.Vector2(0, 0)

            # Smooth camera
            self.offset_float.x += (target[0] - self.screen_center_x - self.offset_float.x) * camera_speed
            self.offset_float.y += (target[1] - self.screen_center_y - self.offset_float.y) * camera_speed

            self.offset.x = self.offset_float.x + self.shake_offset.x
            self.offset.y = self.offset_float.y + self.shake_offset.y

    def draw_sprites(self):
        # Get how far the player is from the screen center (1000 - 600 = 300, move everything by this amount)
        # Move all sprites by the offset calculated here
        # If the camera / player.x increases, all the sprite's x positions decrease
        # If player move right all sprites move left
        # Draw all the ground sprites.
        visible_sprites = list(self.get_visible_sprites())
        ground_sprites = [sprite for sprite in visible_sprites if
                          sprite.type and sprite.type in ["ground", "water"]]
        for sprite in ground_sprites:
            offset_pos = sprite.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
            self.display_surface.blit(sprite.image, offset_pos)

        # Draw the other sprites with overlapping.
        # Get all visible sprites
        overlapping_sprites = [sprite for sprite in visible_sprites
                         if sprite.type in ["player", "tree", "enemy", "battle_spot"]]

        # Decide if enemy needs to be drawn last
        draw_enemy_last = self.animation_camera == BattleState.ENEMY_ANIMATION
        enemy_sprite = self.battle_participants["enemies"][0] if draw_enemy_last else None

        # Sort by Y (with optional tree offset)
        sorted_sprites = sorted(overlapping_sprites,
                                key=lambda sprite: sprite.rect.centery + (32 if sprite.type == "tree" else 0))

        # Draw all sprites except enemy (if drawing last)
        for sprite in sorted_sprites:
            if draw_enemy_last and sprite == enemy_sprite:
                continue  # Skip for now
            offset_pos = sprite.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
            if hasattr(sprite, "image"):
                if sprite.type == "player":
                    pos = (sprite.x, sprite.y) - pygame.math.Vector2(self.offset.x, self.offset.y)
                    self.display_surface.blit(sprite.image, pos)
                else:
                    self.display_surface.blit(sprite.image, offset_pos)
                # else it's invisible

        # Now draw the enemy on top
        if draw_enemy_last and enemy_sprite:
            offset_pos = enemy_sprite.rect.topleft - pygame.math.Vector2(self.offset.x, self.offset.y)
            self.display_surface.blit(enemy_sprite.image, offset_pos)

        self.offset += self.shake_offset

    def update_enemies(self, player):
        """Updates all the enemy sprites based on the player's position."""
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

        for enemy in self.enemy_sprites:
            if not enemy.death:
                enemy.update_enemy(player, self.display_surface, self.offset)
            else:
                if not enemy.in_battle and pygame.time.get_ticks() >= enemy.respawn_time:
                    enemy.hp = enemy.max_hp
                    enemy.action = "idle"
                    enemy.death = False

    def start_battle(self):
        player = self.battle_participants["heroes"][0]
        enemies = self.battle_participants["enemies"]
        enemy = self.battle_participants["enemies"][0]

        second_enemy = random.choices([True, False], k=1, weights = [1, 0])[0]
        if second_enemy: enemies.append(enemy.clone((enemy.x, enemy.y)))


        for participant in enemies:
            participant.in_battle = True
            participant.action = "idle"

        spots2 = self.find_battle_spot(player.rect)

        if spots2:
            self.state = LevelState.BATTLE

            def get_positions_in_rect(rect, n):
                spacing = 320
                y = rect.centery
                return [pygame.Vector2(rect.left + spacing * i, y) for i in range(1, n + 1)]

            positions = get_positions_in_rect(spots2, 2)
            player.pre_battle_pos = (player.x, player.y)




            player.x, player.y = positions[0]
            player.rect.topleft = (int(player.x), int(player.y))
            player.battle_pos = pygame.Vector2(player.x - player.width, player.y)

            def enemy_battle_spots(pos, n):
                spacing = 96
                positions = []

                total_height = spacing * (n - 1)  # total space between all enemies
                start_y = pos.y - total_height / 2  # first enemy starts above pos.y

                for i in range(n):
                    y = start_y + spacing * i
                    positions.append(pygame.Vector2(pos.x, y))  # same X, shifted Y

                return positions

            enemy_positions = enemy_battle_spots(positions[1], len(self.battle_participants["enemies"]))

            for index, enemy in enumerate(enemies):
                enemy.pre_battle_pos = (enemy.x, enemy.y)

                enemy.x, enemy.y = enemy_positions[index]
                enemy.rect.topleft = (int(enemy.x), int(enemy.y))
                enemy.battle_pos = pygame.Vector2(enemy.x - 32, enemy.y)

                enemy.face_target(player)
                enemy.sprinting = False

            player.face_target(enemies[0])

            player.sprinting = False


            battle_center_x = (player.rect.centerx + enemies[0].rect.centerx) // 2
            battle_center_y = (player.rect.centery + enemies[0].rect.centery) // 2
            self.battle_position.update(battle_center_x, battle_center_y)

            self.battle_loop = BattleLoop(player, enemies, self.display_surface, self.offset)

    def enemy_collision(self, player):
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

        # checks all battle spots instead of just the visible ones
        for enemy in self.enemy_sprites:
            if player.hitbox.colliderect(enemy.hitbox) and pygame.time.get_ticks() >= player.post_battle_iframes:
                if enemy.death:
                    pass
                else:
                    self.battle_participants = {
                        "heroes": [player],
                        "enemies": [enemy]
                    }

                    # self.battle_participants = [player, enemy, enemy.clone((enemy.x, enemy.y))]
                    self.transition_timer = pygame.time.get_ticks()
                    self.delay = pygame.time.get_ticks() + self.delay_time
                    for group in self.battle_participants.values():
                        for participant in group:
                            participant.in_battle = True
                            participant.action = "idle"
                break

    def transition_screen(self):
        if self.transition_timer:
            now = pygame.time.get_ticks()
            time_elapsed = now - self.transition_timer
            alpha = int((time_elapsed / self.delay_time) * 1000)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  # enable per-pixel alpha

            if alpha < 255:
                overlay.fill((0, 0, 0, alpha))  # fill with black + alpha
            else:
                overlay.fill((0, 0, 0, 255))  # fill with black + alpha

            self.display_surface.blit(overlay, (0, 0))

            if now > self.delay:
                self.delay = None

                self.transition_timer = None

    def end_battle(self):
        player = self.battle_participants["heroes"][0]
        original_enemy = self.battle_participants["enemies"][0]
        enemies = self.battle_participants["enemies"]

        exp_gained = 0
        for index, enemy in enumerate(enemies):
            exp_gained += enemy.exp
            if not index == 0: enemy.kill()

        if self.battle_loop.winner == player:
            original_enemy.respawn_time = pygame.time.get_ticks() + 600000
            player.handle_exp_gain(exp_gained)


        # === go back to initiate pos ====
        for participant in [player, original_enemy]:
            participant.in_battle = False
            participant.rect.topleft = participant.pre_battle_pos
            participant.x, participant.y = participant.pre_battle_pos

        self.battle_loop = None
        self.battle_participants = None
        self.state = LevelState.OVERWORLD



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