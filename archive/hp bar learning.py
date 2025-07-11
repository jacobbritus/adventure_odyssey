import pygame

from classes.hpbar import Hpbar

pygame.init()
window = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
box = pygame.image.load("../sprites/UI/Slider01_Box.png")
box_position = (100, 300) # change based on the sprites position


bar = pygame.image.load("../sprites/UI/Slider01_Bar02.png")
bar_location = box_position

crop_width_by = 0

hpbar = Hpbar((10, 10), 20)

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_a and not new_size >= 96:
        #         new_size += 4
        #     if event.key == pygame.K_d and not new_size <= 0:
        #         new_size -= 4

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and not crop_width_by >= 96:
            crop_width_by += 4
        if keys[pygame.K_d] and not crop_width_by <= 0:
            crop_width_by -= 4


    crop = pygame.Rect(0, 0, bar.get_size()[0] - crop_width_by, bar.get_size()[1])


    # print(bar_rect)
    # print(crop)

    cropped_image = bar.subsurface(crop).copy()

    hpbar.draw(window)
    window.blit(box, box_position)

    window.blit(cropped_image, bar_location)


    clock.tick(60)
    pygame.display.update()
