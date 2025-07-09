import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf: pygame.Surface, group, tile_type) -> None:
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)  # pos must be a tuple of (x, y)
        self.type = tile_type
        self.hitbox = (self.rect.inflate(-32, -32) if tile_type == "tree" else self.rect)




    def update(self):
        ...