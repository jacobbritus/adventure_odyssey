import pygame

from classes.UI import Hpbar, Button


def one():
    print("yess")

def two():
    print("noooo")

pygame.init()
window = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

buttons_group = pygame.sprite.Group()

window_center_x = window.get_width() // 2
window_center_y = window.get_height() // 2

player_hp_bar = Hpbar((window.get_size()), "left", 20, 20)
enemy_hp_bar = Hpbar((window.get_size()), "right", 20, 20)


while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    player_hp_bar.draw(window)
    enemy_hp_bar.draw(window)

    clock.tick(60)
    pygame.display.update()
