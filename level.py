import pygame
from player import Player
from tile import Tile
from pytmx.util_pygame import load_pygame

from settings import *


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.tmx_data = load_pygame("/Users/jacobbritus/Downloads/tmx/untitled.tmx")
        self.ground_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.visible_sprites = YSortCameraGroup()

        self.player = None
        self.create_map()

    def create_map(self):
        for layer in self.tmx_data.layers:
            if hasattr(layer, "data"):
                for x, y, surface in layer.tiles():
                    position = (int(x * TILE_SIZE), int(y * TILE_SIZE))
                    Tile(pos=position, surf=surface, group = (self.ground_sprites, self.visible_sprites), tile_type = "ground")

        for obj in self.tmx_data.objects:
            pos = (obj.x, obj.y)
            if obj.image:
                Tile(pos=pos, surf=obj.image, group = (self.obstacle_sprites, self.visible_sprites), tile_type = "tree")
            if obj.name == "Spawn":
                self.player = Player(
                    group = self.visible_sprites,
                    spawn_coordinates=pos,
                    direction="down",
                    obstacle_sprites=self.obstacle_sprites
                )


    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update() # get the actual locations


class YSortCameraGroup(pygame.sprite.Group):
    """A custom sprite group that draws sprites with a camera offset, so the player stays centered."""
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # Calculate the center of the screen.
        self.screen_center_x = self.display_surface.get_width() // 2
        self.screen_center_y = self.display_surface.get_height() // 2

        # Used to track how far the player has moved from the center.
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # Get how far the player is from the screen center (1000 - 600 = 300, move everything by this amount)
        # Move all sprites by the offset calculated here
        self.offset.x = player.rect.centerx - self.screen_center_x # Move all sprite
        self.offset.y = player.rect.centery - self.screen_center_y

        # If the camera / player.x increases, all the sprite's x positions decrease
        # If player move right all sprites move left

        # Draw all the ground sprites.
        ground_sprites = [sprite for sprite in self.sprites() if sprite.type == "ground"]
        for sprite in ground_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # Draw the other sprites with overlapping.
        other_sprites = [sprite for sprite in self.sprites() if sprite.type != "ground"]
        for sprite in sorted(other_sprites, key=lambda sprite: sprite.rect.centery + (32 if sprite.type == "tree" else 0)):
            offset_pos = sprite.rect.topleft - self.offset # draw all the elements in a different spot
            self.display_surface.blit(sprite.image, offset_pos)

