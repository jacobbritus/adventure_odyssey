# 1. player.inventory = Inventory()
import math
import random

import pygame

# 2. player.inventory.add_item(item_name, quantity)

# 3. enemy.drop = Item(sword, None, 1)

from other.settings import *
class Item(pygame.sprite.Sprite):
    def __init__(self, group, name, quantity, pos):
        super().__init__(group)

        self.name = name
        self.image = ITEMS[name]["image"].copy()
        self.image.set_alpha(0)
        self.quantity = quantity

        if pos:
            self.pos = pos
            self.rect = self.image.get_rect(topleft = pos)
            self.t = 0

            self.life_time = pygame.time.get_ticks() + 5000
            self.fade_time = pygame.time.get_ticks() + 1500
            self.opacity = 0

            self.shadow = ITEM_SHADOW



    def draw(self, window, pos, cycle):
        self.pos = pos
        float_offset = math.sin(self.t) * 5  # 5 pixels up/down

        y = self.pos.y + float_offset

        self.t += 0.05
        window.blit(self.image, (self.pos.x, y))

        if cycle:
            self.handle_life_time()
        else:
            window.blit(self.shadow, self.pos + (0, 16))
            self.opacity = 255
            self.image.set_alpha(self.opacity)


    def handle_life_time(self):

        if pygame.time.get_ticks() >= self.fade_time and self.opacity == 0:
            self.kill()
        elif pygame.time.get_ticks() >= self.fade_time:
            self.opacity = max(self.opacity - 10, 0)
            self.image.set_alpha(self.opacity)
        else:
            self.opacity = min(self.opacity + 10, 255)
            self.image.set_alpha(self.opacity)




    def animations(self):
        self.pos += (60, 0)


class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item):
        if item.name in self.items.keys():
            self.items[item.name] += item.quantity
        else:
            self.items[item.name] = item.quantity