import pygame
from png_to_sprite import player_sprites
from player import Player

window_width = 640
window_height = 480

pygame.init()
window = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()

player = Player(
    spawn_coordinates=(320, 160),
    sprite_dict = player_sprites,
    direction = "down"
)

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    player.draw(window)

    clock.tick(60)
    pygame.display.update()