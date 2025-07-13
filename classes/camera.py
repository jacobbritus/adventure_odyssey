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

        self.enemy_sprites: list = []
        self.obstacles: []

        # Screen transition into battle.
        self.transition_time: int = 0
        self.transition: bool = False

        # Game state
        self.state = "OVERWORLD"
        self.battle_participants = None
        self.current_music = None
        self.player_position = None
        self.battle_loop = None
        self.battle_position: pygame.math.Vector2 = pygame.math.Vector2()

        self.animation_camera = None

    def update_soundtrack(self):
        if not hasattr(self, 'current_music'):
            self.current_music = None

        if self.state == "OVERWORLD" and self.current_music != "forest":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(FOREST_MUSIC)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            self.current_music = "forest"

        elif self.state == "BATTLE" and self.current_music != "battle":
            pygame.mixer.music.stop()
            pygame.mixer.music.load(BATTLE_MUSIC_1)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            self.current_music = "battle"

    def get_visible_sprites(self):
        """Get all sprites that are visible on the screen."""
        inflated_display_rect = self.display_rect.inflate(200, 300)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            if inflated_display_rect.collidepoint(offset_pos):
                yield sprite

    def custom_draw(self, player):
        # Get how far the player is from the screen center (1000 - 600 = 300, move everything by this amount)
        # Move all sprites by the offset calculated here

        if self.state == "OVERWORLD":
            self.offset.x = player.rect.centerx - self.screen_center_x  # Move all sprite
            self.offset.y = player.rect.centery - self.screen_center_y

        elif self.state == "BATTLE":
            camera_speed = 0.2

            if self.animation_camera == "player_animation":
                target_x = player.rect.centerx - self.screen_center_x
                target_y = player.rect.centery - self.screen_center_y

            elif self.animation_camera == "enemy_animation":
                target_x = self.battle_participants[1].rect.centerx - self.screen_center_x
                target_y = self.battle_participants[1].rect.centery - self.screen_center_y

            else:
                target_x = self.battle_position[0] - self.screen_center_x
                target_y = self.battle_position[1] - self.screen_center_y

            # Smoothly move offset toward the target
            self.offset.x += (target_x - self.offset.x) * camera_speed
            self.offset.y += (target_y - self.offset.y) * camera_speed

        # If the camera / player.x increases, all the sprite's x positions decrease
        # If player move right all sprites move left

        # Draw all the ground sprites.
        ground_sprites = [sprite for sprite in self.get_visible_sprites() if
                          sprite.type and sprite.type in ["ground", "water"]]
        for sprite in ground_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # Draw the other sprites with overlapping.
        other_sprites = [sprite for sprite in self.get_visible_sprites() if
                         sprite.type in ["player", "tree", "enemy", "battle_spot"]]
        for sprite in sorted(other_sprites,
                             key=lambda sprite: sprite.rect.centery + (32 if sprite.type == "tree" else 0)):
            offset_pos = sprite.rect.topleft - self.offset  # draw all the elements in a different spot
            if hasattr(sprite, "image"): self.display_surface.blit(sprite.image, offset_pos)

        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

    def update_enemies(self, player):
        """Updates all the enemy sprites based on the player's position."""
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]
        for sprite in self.enemy_sprites:
            sprite.update_enemy(player)

    def start_battle(self):
        if self.state == "OVERWORLD":

            player, enemy = self.battle_participants

            spots2 = self.find_battle_spot(player.rect)

            if spots2:
                self.state = "BATTLE"
                self.player_position = (player.x, player.y) # Used to put the player back to where the battle was initiated.

                def get_positions_in_rect(rect, n):
                    spacing = 450
                    y = rect.centery
                    return [(rect.left + spacing * i, y) for i in range(1, n + 1)]

                positions = get_positions_in_rect(spots2, 2)

                # Start battle loop.
                self.transition = True

                enemy.in_battle = True
                player.in_battle = True

                enemy.x, enemy.y = positions[1]
                enemy.rect.topleft = (int(enemy.x), int(enemy.y))

                player.x, player.y = positions[0]
                player.rect.topleft = (int(player.x), int(player.y))

                player.face_target(enemy)
                enemy.face_target(player)

                player.action = "idle"
                enemy.action = "idle"

                battle_center_x = (player.rect.centerx + enemy.rect.centerx) // 2
                battle_center_y = (player.rect.centery + enemy.rect.centery) // 2
                self.battle_position.update(battle_center_x, battle_center_y)

                self.battle_loop = BattleLoop(player, enemy, self.display_surface)


    def enemy_collision(self, player):
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

        # checks all battle spots instead of just the visible ones
        for enemy in self.enemy_sprites:
            if player.rect.inflate(-player.rect.width // 2, -player.rect.height // 2).colliderect(
                    enemy.rect.inflate(-enemy.rect.width // 2, -enemy.rect.height // 2)):
                self.battle_participants = [player, enemy]
                break

    def darken_screen(self):
        if self.transition_time <= 255:  # max alpha value for fade
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)  # enable per-pixel alpha
            alpha_value = int(self.transition_time)  # alpha must be int between 0-255
            overlay.fill((0, 0, 0, alpha_value))  # fill with black + alpha
            self.display_surface.blit(overlay, (0, 0))
            self.transition_time += 5  # increase alpha faster for visible fade
        else:
            self.transition = False  # Transition finished
            self.transition_time = 0

    def end_battle(self):
        self.state = "OVERWORLD"
        player, enemy = self.battle_participants

        # Put the participants out of the battle state.
        player.in_battle = False
        enemy.in_battle = False

        # Stop the battle loop
        self.battle_loop = None

        # Kill whoever lost. (Removes them from all sprite groups)
        enemy.kill()
        self.battle_participants = None

        # Set player to initiate location.
        player.rect.topleft = self.player_position
        player.x, player.y = self.player_position

        # Transition into the overworld.
        self.transition = True

    def find_battle_spot(self, player_rect, search_radius = 1000, step = 1):
        """Find a nearby unobstructed rectangular area for battle."""

        spot_size = (1000, 48)

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