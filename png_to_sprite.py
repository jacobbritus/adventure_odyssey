import pygame

pygame.init()


def sprite_converter(sprite_file: str, row: int, sprites_amount: int, sprite_width: int, sprite_height: int,
                     flip: bool) -> list:
    sprite_file = pygame.image.load(sprite_file)

    sprites = []
    x = 0
    y = row * sprite_height

    for i in range(sprites_amount):
        # get a cut based on the column (y) and the row (x)
        rect = pygame.Rect(x, y, sprite_width, sprite_height)
        image = sprite_file.subsurface(rect).copy()
        if flip:
            image = pygame.transform.flip(image, True, False)

        pygame.transform.flip(image, True, False)
        sprites.append(image)

        x += sprite_width

    return sprites


player_sprites = {
    "running":
        {
            "down": sprite_converter("sprites/characters/me.png", 3, 6, 48, 48, False),
            "right": sprite_converter("sprites/characters/me.png", 4, 6, 48, 48, False),
            "left": sprite_converter("sprites/characters/me.png", 4, 6, 48, 48, True),
            "up": sprite_converter("sprites/characters/me.png", 5, 6, 48, 48, False)},
    "idle":
        {
            "down": sprite_converter("sprites/characters/me.png", 0, 6, 48, 48, False),
            "right": sprite_converter("sprites/characters/me.png", 1, 6, 48, 48, False),
            "left": sprite_converter("sprites/characters/me.png", 1, 6, 48, 48, True),
            "up": sprite_converter("sprites/characters/me.png", 2, 6, 48, 48, False)}

}
