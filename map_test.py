import pygame
from pytmx.util_pygame import load_pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf: pygame.Surface, groups: pygame.sprite.Group) -> None:
        super().__init__(groups)
        self.image = surf
        print(pygame.Surface.get_size(self.image))
        self.rect = self.image.get_rect(topleft = pos)  # pos must be a tuple of (x, y)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
tmx_data = load_pygame("/Users/jacobbritus/Downloads/tmx/untitled.tmx")
sprite_group = pygame.sprite.Group()

# cycle through all layers
for layer in tmx_data.layers:
    if hasattr(layer, "data"):
        for x, y, surface in layer.tiles():
            position = (int(x * 32), int(y * 32))  # Ensure position is a tuple
            Tile(pos=position, surf=surface, groups=sprite_group)



for obj in tmx_data.objects:
    pos = (obj.x, obj.y)  # Ensure position is a tuple
    if obj.image:
        Tile(pos=pos, surf= obj.image, groups=sprite_group)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()

    screen.fill('black')
    sprite_group.draw(screen)
    pygame.display.update()
    clock.tick(60)