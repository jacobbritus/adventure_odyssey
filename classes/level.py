import pygame
import pytmx

from classes.battleloop import BattleLoop
from classes.enemy import Enemy
from classes.player import Player, DustParticle
from classes.Tiles import StaticTile, AnimatedTile, ActionTile
from pytmx.util_pygame import load_pygame

from other.settings import *


class Level:
    """A class to manage the game level."""
    def __init__(self):
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.tmx_data = load_pygame("tmx/untitled.tmx")
        self.ground_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.obstacle_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.visible_sprites = YSortCameraGroup()
        self.action_sprites: pygame.sprite.Group = pygame.sprite.Group()

        self.player = None
        self.create_map()

    def create_map(self):

        ground_sprites = self.tmx_data.get_layer_by_name("Ground")
        if isinstance(ground_sprites, pytmx.TiledTileLayer):
            for x, y, gid in ground_sprites:
                properties = self.tmx_data.get_tile_properties_by_gid(gid)

                # Check if the tile has animations.
                if properties and properties["frames"]:

                    frames = properties["frames"]

                    frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                    position = (int(x * TILE_SIZE), int(y * TILE_SIZE))

                    AnimatedTile(pos=position, frames=frame_surfaces,
                                 group=(self.obstacle_sprites, self.visible_sprites), tile_type="water",
                                 animation_speed=0.1)

                else:
                    surface = self.tmx_data.get_tile_image_by_gid(gid)
                    position = (int(x * TILE_SIZE), int(y * TILE_SIZE))
                    StaticTile(pos=position, surf=surface, group=(self.ground_sprites, self.visible_sprites),
                               tile_type="ground")

        enemy_sprites = self.tmx_data.get_layer_by_name("Enemies")
        if isinstance(enemy_sprites, pytmx.TiledObjectGroup):
            for obj in enemy_sprites:
                pos = (obj.x, obj.y)
                Enemy(surf=obj.image, pos=pos, monster_name=obj.name, group=(self.enemies, self.visible_sprites),
                      obstacle_sprites=self.obstacle_sprites)

        obstacle_sprites = self.tmx_data.get_layer_by_name("Obstacles")
        if isinstance(obstacle_sprites, pytmx.TiledObjectGroup):
            for obj in obstacle_sprites:
                pos = (obj.x, obj.y)
                properties = self.tmx_data.get_tile_properties_by_gid(obj.gid)

                if obj.image:
                    # Handle obstacles with animations.
                    if properties and properties["frames"]:
                        frames = properties["frames"]
                        frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                        AnimatedTile(pos=pos, frames=frame_surfaces,
                                     group=(self.obstacle_sprites, self.visible_sprites), tile_type="tree",
                                     animation_speed=0.1)
                    else:

                        StaticTile(pos=pos, surf=obj.image, group=(self.obstacle_sprites, self.visible_sprites),
                                   tile_type="tree")

                # separate this
                if obj.name == "Spawn":
                    self.player = Player(
                        group=self.visible_sprites,
                        spawn_coordinates=pos,
                        direction="down",
                        obstacle_sprites=self.obstacle_sprites,
                        dust_particles=self.dust_particle,
                        enemy_sprites=self.enemies
                    )

                # seperate this too
                if obj.name == "battle_spot":
                    ActionTile(pos=pos, size=(obj.width, obj.height),
                               group=(self.action_sprites, self.visible_sprites), tile_type="battle_spot")

    def run(self) -> None:
        if self.visible_sprites.state == "OVERWORLD":
            self.overworld()
        else:
            self.battle()

    def overworld(self) -> None:
        self.visible_sprites.update_soundtrack()
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.update_enemy(self.player)
        self.visible_sprites.simple_initiate_combat(self.player)
        if self.visible_sprites.transition: self.visible_sprites.darken_screen()

        self.visible_sprites.find_battle_spot(self.player.rect)

    def battle(self):
        self.visible_sprites.update_soundtrack()

        self.visible_sprites.battle_loop.handle_input()
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.update_enemy(self.player)

        self.visible_sprites.battle_loop.update()





        # Test Hotkey
        if self.visible_sprites.battle_loop.return_to_overworld:
            self.visible_sprites.end_battle()
        if self.visible_sprites.transition: self.visible_sprites.darken_screen()

    def dust_particle(self):
        DustParticle(self.player, self.visible_sprites)

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

    def update_soundtrack(self):
        if not hasattr(self, 'current_music'):
            self.current_music = None

        if self.state == "OVERWORLD" and self.current_music != "forest":
            pygame.mixer.music.stop()
            pygame.mixer.music.load("sounds/forest_theme.mp3")
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            self.current_music = "forest"

        elif self.state == "BATTLE" and self.current_music != "battle":
            pygame.mixer.music.stop()
            # pygame.mixer.music.load("sounds/battle_music.mp3")
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


        if self.state == "BATTLE":
            self.offset.x = self.battle_position[0] - self.screen_center_x  # Move all sprite
            self.offset.y = self.battle_position[1] - self.screen_center_y
        else:
            self.offset.x = player.rect.centerx - self.screen_center_x  # Move all sprite
            self.offset.y = player.rect.centery - self.screen_center_y

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


    def update_enemy(self, player):
        """Updates all the enemy sprites based on the player's position."""
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]
        for sprite in self.enemy_sprites:
            sprite.enemy_update(player)

    def simple_initiate_combat(self, player):
        if self.state == "OVERWORLD":
            self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

            # checks all battle spots instead of just the visible ones


            battle_spots = [sprite for sprite in self.sprites() if sprite.type == "battle_spot"]

            for enemy in self.enemy_sprites:

                if player.rect.inflate(-player.rect.width // 2, -player.rect.height // 2).colliderect(
                        enemy.rect.inflate(-enemy.rect.width // 2, -enemy.rect.height // 2)):
                    spots2 = self.find_battle_spot(player.rect)


                    if spots2:

                        self.state = "BATTLE"
                        self.battle_participants = [player, enemy] # Used to update their in_battle attribute.
                        self.player_position = (player.x, player.y) # Used to put the player back to where the battle was initiated.

                        def get_positions_in_rect(rect, n):
                            spacing = rect.width // (n + 1)
                            y = rect.centery
                            return [(rect.left + spacing * i, y) for i in range(1, n + 1)]


                        positions = get_positions_in_rect(spots2, 2)

                        spots = player.find_two_closest_battle_spots(battle_spots)


                        # Start battle loop.
                        if len(spots) == 2:
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

                            break



    def darken_screen(self):
        if self.transition_time <= 5:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            self.display_surface.blit(overlay, (0, 0))
            self.transition_time += 0.1
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

    def find_battle_spot(self, player_rect, spot_size = (900, 50), search_radius = 100, step = 20):
        "Find a nearby unobstructed rectangular area for battle."

        spot_size = (500, 10)

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

                    pygame.draw.rect(self.display_surface, (255, 0,0), candidate)

                    return                     candidate


        return None




