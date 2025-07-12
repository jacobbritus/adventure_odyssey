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

button1 = Button(buttons_group, (window_center_x, window_center_y), one, "Attack")
button2 = Button(buttons_group, (100, 200), two, "Run")

while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()



    for button in buttons_group:
        button.draw(window)
        button.update()
        if button.delete:
            for buttons in buttons_group:
                buttons.kill()


    clock.tick(60)
    pygame.display.update()
