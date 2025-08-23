import math

from other.settings import *

class Pointer:
    def __init__(self, variant = "tick_pointer", direction = "right", color = "blue"):
        if variant == "tick_pointer":
            self.image = UI["cursors"][f"{color}_{variant}_{direction}"]
        else:
            self.image = UI["cursors"][f"{variant}_{direction}"]
        self.variant = variant
        self.direction = direction
        self.pos = None
        self.float = 5

    def draw(self, window, pos, direction, **kwargs):
        if kwargs.get("color"):
            self.image = UI["cursors"][f"{kwargs.get("color")}_{self.variant}_{direction}"]
        else:
            self.image = UI["cursors"][f"{self.variant}_{direction}"]

        self.pos = pygame.Vector2(pos)

        float_offset = math.sin(self.float) * 5

        if direction in ["left", "right"]:
            x = self.pos.x + float_offset
            self.float -= 0.1
            window.blit(self.image, (x, self.pos.y))
        else:
            y = self.pos.y + float_offset
            self.float -= 0.1
            window.blit(self.image, (self.pos.x, y))
