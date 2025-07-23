import pygame

from other.settings import *


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

buttons_group = pygame.sprite.Group()
#
# player_hp_bar = Hpbar("left", 67, 20, 20, 5,
#                            "PLAYER")  # enemy.name in the future
#
# enemy = Hpbar("right", 5, 20, 20, 5,
#                            "SKELETON")  # enemy.name in the future

# button = Button(buttons_group, "no parameter", one, "ATTACK", "small", ((WINDOW_WIDTH // 2) - pygame.image.load(BUTTON_TWO_NORMAL).get_width() , WINDOW_HEIGHT // 1.25))
# button_two = Button(buttons_group, "no parameter", one, "RUN", "small", ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 5 , WINDOW_HEIGHT // 1.25))

skills = pygame.image.load(LARGE_BACKGROUND_BOX)

def attack(name):
    print(name)
#
attacks = ["SWORD SLASH", "BALLS", "FORTNITE"]

# combat_menu = CombatMenu(attacks, [attack, two, one])
hp = 20
mana = 5

# combat_menu.state = "main_menu"
while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                hp -= 5
                # combat_menu.state = "end_screen"
                # combat_menu.buttons_group = pygame.sprite.Group()

            if event.key == pygame.K_a:
                mana -= 1

            if event.key == pygame.K_r:
                hp += 5

                # combat_menu.state = "main_menu"


    # player_hp_bar.set_hp(hp)
    # player_hp_bar.update()
    # player_hp_bar.draw(window)
    #
    # enemy.draw(window)

    # enemy.draw(window)
    spellbook = pygame.image.load(BOOK)

    window.blit(spellbook, (WINDOW_WIDTH // 2 - spellbook.get_width()//2, WINDOW_HEIGHT // 2 - spellbook.get_height() // 2))



    # button.draw(window)
    # button.update()
    # button_two.draw(window)
    # button_two.update()

    # combat_menu.draw(window)

    clock.tick(60)
    pygame.display.update()
