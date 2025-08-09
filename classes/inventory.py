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
        self.type = "item"
        self.image = ITEMS[name]["image"].copy()
        self.quantity = quantity

        if pos:
            self.pos = pos
            self.rect = self.image.get_rect(topleft = pos)
            self.t = 0

            self.life_time = pygame.time.get_ticks() + 5000
            self.fade_time = pygame.time.get_ticks() + 1500

            self.shadow = ITEM_SHADOW

    def update(self):
        float_offset = math.sin(self.t) * 1  # 5 pixels up/down

        y = round(self.rect.y - float_offset)

        self.t += 0.1

        self.rect.topleft = (self.rect.x, y)


    def draw(self, window, pos, cycle):
        self.pos = pos
        float_offset = math.sin(self.t) * 5  # 5 pixels up/down

        y = self.pos.y + float_offset

        self.t += 0.1
        window.blit(self.image, (self.pos.x, y))

        if cycle:
            self.handle_life_time()
        else:
            window.blit(self.shadow, self.pos + (0, 16))


    def handle_life_time(self):

        if pygame.time.get_ticks() >= self.fade_time:
            print("check")
            self.kill()





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