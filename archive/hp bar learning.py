import pygame

from classes.UI import *
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

button = Button(buttons_group, "no parameter", one, "ATTACK", "small", ((WINDOW_WIDTH // 2) - pygame.image.load(BUTTON_TWO_NORMAL).get_width() , WINDOW_HEIGHT // 1.25))
button_two = Button(buttons_group, "no parameter", one, "RUN", "small", ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 5 , WINDOW_HEIGHT // 1.25))

skills = pygame.image.load(LARGE_BACKGROUND_BOX)

def attack(name):
    print(name)

attacks = ["SWORD SLASH", "BALLS", "FORTNITE"]

combat_menu = CombatMenu(attacks, [attack, two, one])

combat_menu.state = "main_menu"
while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                combat_menu.state = "end_screen"
                combat_menu.buttons_group = pygame.sprite.Group()

            if event.key == pygame.K_r:
                combat_menu.state = "main_menu"


    # player_hp_bar.draw(window)
    # enemy_hp_bar.draw(window)
    # button.draw(window)
    # button.update()
    # button_two.draw(window)
    # button_two.update()

    combat_menu.draw(window)

    clock.tick(60)
    pygame.display.update()
