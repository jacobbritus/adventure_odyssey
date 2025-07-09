import pygame

class Tile(pygame.sprite.Sprite):
    """A class to initialize and manage a tile in the game."""
    def __init__(self, pos, surf: pygame.Surface, group, tile_type: str) -> None:
        super().__init__(group)
        self.image: pygame.surface = surf
        self.rect: pygame.Rect = self.image.get_rect(topleft = pos)  # pos must be a tuple of (x, y)
        self.type: str = tile_type
        self.hitbox: pygame.Rect = (self.rect.inflate(-32, -32) if tile_type == "tree" else self.rect)




    def update(self):
        ...