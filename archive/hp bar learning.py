import pygame

from classes.UI import Hpbar, Button
from other.settings import *


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

buttons_group = pygame.sprite.Group()

player_hp_bar = Hpbar((window.get_size()), "left", 20, 20, "JACOB")
enemy_hp_bar = Hpbar((window.get_size()), "right", 20, 20, "SKELETON")

button = Button(buttons_group, one, "ATTACK", "one")
button_two = Button(buttons_group, one, "RUN", "two")


while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    player_hp_bar.draw(window)
    enemy_hp_bar.draw(window)
    button.draw(window)
    button.update()
    button_two.draw(window)
    button_two.update()

    clock.tick(60)
    pygame.display.update()
