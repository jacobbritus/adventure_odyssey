import pygame.mouse

from other.settings import UI


class Mouse:
    def __init__(self):
        self.image = UI["cursors"]["blue_cursor"]

    def draw(self, window):
        mouse_pos = pygame.mouse.get_pos()
        updated_pos = pygame.Vector2(mouse_pos) - (12, 12)
        window.blit(self.image, updated_pos)