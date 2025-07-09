import pygame

from player import Player
from tile import Tile
from pytmx.util_pygame import load_pygame


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.tmx_data = load_pygame("/Users/jacobbritus/Downloads/tmx/untitled.tmx")
        self.ground_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        self.create_map()

        self.player = Player(
            spawn_coordinates=(320, 160),
            direction="down",
            obstacle_sprites = self.obstacle_sprites
        )

    def create_map(self):
        for layer in self.tmx_data.layers:
            if hasattr(layer, "data"):
                for x, y, surface in layer.tiles():
                    position = (int(x * 32), int(y * 32))  # Ensure position is a tuple
                    Tile(pos=position, surf=surface, groups=self.ground_sprites)

        for obj in self.tmx_data.objects:
            pos = (obj.x, obj.y)  # Ensure position is a tuple
            if obj.image:
                Tile(pos=pos, surf=obj.image, groups=self.obstacle_sprites)

    def run(self):
        self.ground_sprites.draw(self.display_surface)

        self.player.draw(self.display_surface)

        self.obstacle_sprites.draw(self.display_surface)