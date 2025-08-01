import pygame

from classes.UI import MenuBook, HpBar
from classes.player import Player
from other.settings import *


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

buttons_group = pygame.sprite.Group()

group = pygame.sprite.Group()


player = Player(
                        group= group,
                        spawn_coordinates= (0, 0),
                        direction="down",
                        obstacle_sprites = group,
                        dust_particles = group,
                    )

player_hp_bar = HpBar(
            owner = player,
            side = "left",
            y_offset = 0)


skills = pygame.image.load(LARGE_BACKGROUND_BOX)

def attack(name):
    print(name)
#
attacks = ["SWORD SLASH", "BALLS", "FORTNITE"]

# combat_menu = CombatMenu(attacks, [attack, two, one])
hp = 20
mana = 5

# combat_menu.state = "main_menu"

# menu_book = MenuBook()
while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                player.hp -= 5
                player.mana += 5
                player.hp = max(player.hp, 0)

                # combat_menu.state = "end_screen"
                # combat_menu.buttons_group = pygame.sprite.Group()

            if event.key == pygame.K_a:
                player.mana -= 1

            if event.key == pygame.K_r:
                player.hp += 5
                player.hp = min(player.hp, player.max_hp)

    #     menu_book.keybinds(event)
    #
    #
    # menu_book.draw(window)


    # player_hp_bar.set_hp(hp)
    # player_hp_bar.update()
    player_hp_bar.draw(window, None)
    #
    # enemy.draw(window)

    # enemy.draw(window)


    # button.draw(window)
    # button.update()
    # button_two.draw(window)
    # button_two.update()

    # combat_menu.draw(window)

    clock.tick(120)
    pygame.display.update()
