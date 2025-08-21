import math

import pygame

from other.settings import *

class Pointer:
    def __init__(self):
        self.image = UI["cursors"]["tick_pointer_right"]
        self.pos = None
        self.x_float = 5


    def draw(self, window, pos, direction):
        x_offset = (-2, 30) if direction == "right" else (64, 30)
        self.pos = pos + x_offset

        self.image = UI["cursors"][f"hand_pointer_{direction}"]
        float_offset = math.sin(self.x_float) * 5

        x = self.pos.x + float_offset

        self.x_float -= 0.1

        window.blit(self.image, (x, self.pos.y))