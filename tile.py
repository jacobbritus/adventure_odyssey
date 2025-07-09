import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf: pygame.Surface, groups: pygame.sprite.Group) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)  # pos must be a tuple of (x, y)
