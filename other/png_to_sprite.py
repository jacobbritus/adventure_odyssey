import pygame
import os

pygame.init()


def sprite_converter(sprite_file: str, row: int, sprites_amount: int, sprite_width: int, sprite_height: int,
                     flip: bool) -> list:

    project_root = os.path.dirname(os.path.dirname(__file__))
    sprite_path = os.path.join(project_root, sprite_file)


    sprite_file = pygame.image.load(sprite_path)

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
            "down": sprite_converter("sprites/characters/me2.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/me2.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/me2.png", 5, 6, 96, 80, False)},
    "idle":
        {
            "down": sprite_converter("sprites/characters/me2.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/me2.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/me2.png", 2, 6, 96, 80, False)},
    # "punch": {
    #         "right": sprite_converter("sprites/characters/punch.png", 0, 5, 80, 80, False)},

    "sword_slash": {
        "right": sprite_converter("sprites/characters/me2.png", 7, 4, 96, 80, False),
        "left": sprite_converter("sprites/characters/me2.png", 7, 4, 96, 80, True)

    }
}

sprite_dust = sprite_converter("sprites/particles/dust.png", 0, 4, 24, 24, False)

skeleton_sprites = {
    "running":
        {
            "down": sprite_converter("sprites/characters/skeleton_swordless2.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/skeleton_swordless2.png", 5, 6, 96, 80, False)},
    "idle":
        {
            "down": sprite_converter("sprites/characters/skeleton_swordless2.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/skeleton_swordless2.png", 2, 6, 96, 80, False)},

    "sword_slash": {
        "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 7, 4, 96, 80, False),
        "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 7, 4, 96, 80, True)},

    "death": {
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 14, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 14, 4, 96, 80, True)}

}