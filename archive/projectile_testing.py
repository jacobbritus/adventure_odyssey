import pygame

from classes.spells import ProjectileSpell
from other.settings import *

a = 5
b = 5
print(max(a, b))


pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

projectiles = pygame.sprite.Group()

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                ProjectileSpell(projectiles, "lightning_strike", pygame.Vector2(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 1), None, 6)

    projectiles.draw(window)
    projectiles.update((0, WINDOW_HEIGHT // 2))

    for projectile in projectiles:
        if projectile.hit:
            print("hit!")


    clock.tick(60)
    pygame.display.update()
