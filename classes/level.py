import pygame

from classes.enemy import Enemy
from classes.player import Player, DustParticle
from classes.tile import Tile, AnimatedTile, ActionTile
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

        self.player = None
        self.create_map()

    def create_map(self):

        for layer in self.tmx_data.layers:
            if layer.name == "Ground":
                for x, y, gid in layer:


                    props = self.tmx_data.get_tile_properties_by_gid(gid)

                    # Check if the tile has animations.
                    if props and props["frames"]:

                        frames = props["frames"]

                        frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                        position = (int(x * TILE_SIZE), int(y * TILE_SIZE))

                        AnimatedTile(pos=position, frames = frame_surfaces, group = (self.obstacle_sprites, self.visible_sprites), tile_type = "water", animation_speed = 0.1)


                    else:
                        surface = self.tmx_data.get_tile_image_by_gid(gid)
                        position = (int(x * TILE_SIZE), int(y * TILE_SIZE))
                        Tile(pos=position, surf=surface, group = (self.ground_sprites, self.visible_sprites), tile_type = "ground")


        for obj in self.tmx_data.get_layer_by_name("Enemies"):
            pos = (obj.x, obj.y)
            Enemy(surf = obj.image, pos = pos, monster_name = obj.name, group = (self.enemies, self.visible_sprites), obstacle_sprites = self.obstacle_sprites)



        for obj in self.tmx_data.get_layer_by_name("Obstacles"):
            pos = (obj.x, obj.y)
            props = self.tmx_data.get_tile_properties_by_gid(obj.gid)




            if obj.image:
                if props and props["frames"]:
                    frames = props["frames"]
                    frame_surfaces = [self.tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]

                    AnimatedTile(pos=pos, frames = frame_surfaces, group = (self.obstacle_sprites, self.visible_sprites), tile_type = "tree", animation_speed = 0.1)
                else:

                    Tile(pos=pos, surf=obj.image, group = (self.obstacle_sprites, self.visible_sprites), tile_type = "tree")
            if obj.name == "Spawn":

                self.player = Player(
                    group = self.visible_sprites,
                    spawn_coordinates=pos,
                    direction="down",
                    obstacle_sprites=self.obstacle_sprites,
                    dust_particles = self.dust_particle,
                    enemy_sprites= self.enemies
                )

            if obj.name == "battle_spot":
                ActionTile(pos=pos, size = (obj.width, obj.height), group = (self.obstacle_sprites, self.visible_sprites), tile_type = "battle_spot")

    def run(self):
        if self.visible_sprites.state == "OVERWORLD":
            self.run_overworld()
        else:
            self.run_battle()

    def run_overworld(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()  # get the actual locations
        self.visible_sprites.update_enemy(self.player)
        self.visible_sprites.simple_initiate_combat(self.player)
        if self.visible_sprites.transition: self.visible_sprites.darken_screen()


    def run_battle(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()  # get the actual locations
        self.visible_sprites.update_enemy(self.player)
        if self.player.run: self.visible_sprites.end_battle()
        if self.visible_sprites.transition: self.visible_sprites.darken_screen()



    def dust_particle(self):
        DustParticle(self.player, self.visible_sprites)


class YSortCameraGroup(pygame.sprite.Group):
    """A custom sprite group that draws sprites with a camera offset, so the player stays centered."""
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.display_rect = self.display_surface.get_rect()

        # Calculate the center of the screen.
        self.screen_center_x = self.display_surface.get_width() // 2
        self.screen_center_y = self.display_surface.get_height() // 2

        # Used to track how far the player has moved from the center.
        self.offset = pygame.math.Vector2()

        self.enemy_sprites = None

        # Screen transition into battle.
        self.transition_time = 0
        self.transition_speed = 0.1
        self.transition = False

        # Game state
        self.state = "OVERWORLD"
        self.battle_participants = None


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
        self.offset.x = player.rect.centerx - self.screen_center_x # Move all sprite
        self.offset.y = player.rect.centery - self.screen_center_y

        if self.state == "BATTLE": self.offset.x += 150

        # If the camera / player.x increases, all the sprite's x positions decrease
        # If player move right all sprites move left

        # Draw all the ground sprites.
        ground_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type and sprite.type in ["ground", "water"]]
        for sprite in ground_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # Draw the other sprites with overlapping.
        other_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type in ["player", "tree", "enemy", "battle_spot"]]
        for sprite in sorted(other_sprites, key=lambda sprite: sprite.rect.centery + (32 if sprite.type == "tree" else 0)):
            offset_pos = sprite.rect.topleft - self.offset # draw all the elements in a different spot
            if hasattr(sprite, "image"): self.display_surface.blit(sprite.image, offset_pos)

        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]

    def update_enemy(self, player):
        """Updates all of the enemy sprites based on the player's position."""
        self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]
        for sprite in self.enemy_sprites:
            sprite.enemy_update(player)

    def simple_initiate_combat(self, player):
        if self.state == "OVERWORLD":

            self.enemy_sprites = [sprite for sprite in self.get_visible_sprites() if sprite.type == "enemy"]
            battle_spots = [sprite for sprite in self.get_visible_sprites() if sprite.type == "battle_spot"]

            for enemy in self.enemy_sprites:
                if player.hitbox.colliderect(enemy.rect.inflate(32,32)):
                    self.state = "BATTLE"
                    self.battle_participants = [player, enemy]
                    spots = player.find_two_closest_battle_spots(battle_spots)

                    if len(spots) == 2:
                        self.transition = True
                        enemy.in_battle_position = True
                        player.in_battle_position = True

                        player.teleport_to_spot(spots[0])
                        enemy.teleport_to_spot(spots[1])

                        player.face_target(enemy)
                        enemy.face_target(player)

                        break





    def darken_screen(self):
        if self.transition_time <= 30:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            self.display_surface.blit(overlay, (0, 0))
            self.transition_time += 1
        else:
            self.transition = False  # Transition finished
            self.transition_time = 0

    def end_battle(self):
        self.state = "OVERWORLD"
        player, enemy = self.battle_participants
        player.in_battle_position = False
        enemy.in_battle_position = False
        self.battle_participants = None
        player.run = False
        self.transition = True

