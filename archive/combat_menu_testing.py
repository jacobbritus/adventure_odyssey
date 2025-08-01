import pygame

from classes.UI import CombatMenu
from classes.states import CombatMenuState
from other.settings import *


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

def attack(name):
    ...
        #
attacks = ["sword_slash", "fire_ball", "punch"]

combat_menu = CombatMenu(attacks, [attack, two, one])


bg = SKILLS_MENU_BG
pos = pygame.Vector2(WINDOW_WIDTH // 2 - SKILLS_MENU_BG.get_width() // 2, WINDOW_HEIGHT // 2 - SKILLS_MENU_BG.get_height() // 2)




print(bg.get_size())
rect = pygame.Rect(0, 88, bg.get_width(), 24)

image = bg.subsurface(rect).copy()

mask = pygame.mask.from_surface(image).to_surface(setcolor=(0, 255, 255, 100),
                                                                       unsetcolor=(0, 0, 0, 0))

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    combat_menu.draw(window, 5)


    window.blit(NEW_HP_BG, (10, 30))

    # window.blit(SKILLS_MENU_BG, pos)
    # window.blit(mask, pos + rect.topleft)

    clock.tick(120)
    pygame.display.update()