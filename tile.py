import pygame

class Tile(pygame.sprite.Sprite):
    """A class to initialize and manage a tile in the game."""
    def __init__(self, pos, surf: pygame.Surface, group, tile_type: str) -> None:
        super().__init__(group)
        self.image = surf
        self.rect: pygame.Rect = self.image.get_rect(topleft = pos)  # pos must be a tuple of (x, y)
        self.type: str = tile_type
        self.hitbox: pygame.Rect = (self.rect.inflate(-32, -32) if tile_type == "tree" else self.rect)




class AnimatedTile(pygame.sprite.Sprite):
    """A class to initialize and manage a tile with animations."""
    def __init__(self, pos, frames: list, group, tile_type) -> None:
        super().__init__(group)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect: pygame.Rect = self.image.get_rect(topleft = pos)
        self.type = tile_type

    def update(self):
        self.frame_index += 0.1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

