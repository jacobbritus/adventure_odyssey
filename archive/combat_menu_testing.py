from classes.UI import CombatMenu
from other.settings import *


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

def attack(name):
    print(name)
#
attacks = ["sword_slash", "fire_ball", "punch"]

combat_menu = CombatMenu(attacks, [attack, two, one])

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    combat_menu.draw(window, 5)

    clock.tick(120)
    pygame.display.update()