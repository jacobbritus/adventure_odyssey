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

        self.player = None
        self.create_map()

    def create_map(self):
        for layer in self.tmx_data.layers:
            if hasattr(layer, "data"):
                for x, y, surface in layer.tiles():
                    position = (int(x * 32), int(y * 32))
                    Tile(pos=position, surf=surface, groups=self.ground_sprites)

        for obj in self.tmx_data.objects:
            pos = (obj.x, obj.y)
            if obj.image:
                Tile(pos=pos, surf=obj.image, groups=self.obstacle_sprites)
            if obj.name == "Spawn":
                self.player = Player(
                    spawn_coordinates=pos,
                    direction="down",
                    obstacle_sprites=self.obstacle_sprites
                )

    def get_camera_offset(self):
        screen_center_x = self.display_surface.get_width() // 2
        screen_center_y = self.display_surface.get_height() // 2
        offset_x = self.player.rect.centerx - screen_center_x
        offset_y = self.player.rect.centery - screen_center_y
        return offset_x, offset_y

    def run(self):
        offset_x, offset_y = self.get_camera_offset()
        screen_rect = pygame.Rect(offset_x, offset_y, self.display_surface.get_width(),
                                  self.display_surface.get_height())

        # Draw visible ground tiles
        visible_ground = [sprite for sprite in self.ground_sprites if sprite.rect.colliderect(screen_rect)]
        for sprite in visible_ground:
            pos = (sprite.rect.x - offset_x, sprite.rect.y - offset_y)
            self.display_surface.blit(sprite.image, pos)

        # Player is always visible, draw with offset
        player_pos = (self.player.rect.x - offset_x, self.player.rect.y - offset_y)
        self.display_surface.blit(self.player.image, player_pos)

        self.player.update()

        # Similarly for obstacles and player
        visible_obstacles = [sprite for sprite in self.obstacle_sprites if sprite.rect.colliderect(screen_rect)]
        for sprite in visible_obstacles:
            pos = (sprite.rect.x - offset_x, sprite.rect.y - offset_y)
            self.display_surface.blit(sprite.image, pos)
