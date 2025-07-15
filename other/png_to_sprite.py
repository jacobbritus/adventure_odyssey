import os
import pygame

def get_file_location(file_location: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_dir, "..", file_location)

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
    "idle": {
        "sprites": {
            "down": sprite_converter("sprites/characters/me2.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/me2.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/me2.png", 2, 6, 96, 80, False),
        },
        "sound": get_file_location("sounds/sword_slash")
    },
    "running": {
        "sprites": {
            "down": sprite_converter("sprites/characters/me2.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/me2.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/me2.png", 5, 6, 96, 80, False),
        },
        "sound": "sounds/footsteps.wav"
    },
    "sword_slash": {
        "sprites": {
            "right": sprite_converter("sprites/characters/me2.png", 7, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 7, 4, 96, 80, True),
        },
        "sound": get_file_location("sounds/sword_slash.wav"),
        "impact_frame": 2


    },

    "punch": {
            "sprites": {
                "right": sprite_converter("sprites/characters/me2.png", 11, 4, 96, 80, False),
                "left": sprite_converter("sprites/characters/me2.png", 11, 4, 96, 80, True),
            },
            "sound": get_file_location("sounds/sword_slash.wav"),
            "impact_frame": 2},
    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/me2.png", 9, 3, 96, 80, False),
            "left": sprite_converter("sprites/characters/me2.png", 9, 3, 96, 80, True),
        },
        "sound": "sounds/death.wav"
    }
}


sprite_dust = sprite_converter("sprites/particles/dust.png", 0, 4, 24, 24, False)

skeleton_sprites = {
    "idle": {
        "sprites": {
            "down": sprite_converter("sprites/characters/skeleton_swordless2.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/skeleton_swordless2.png", 2, 6, 96, 80, False),
        },
        "sound": None,
        "impact_frame": None
    },
    "running": {
        "sprites": {
            "down": sprite_converter("sprites/characters/skeleton_swordless2.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/skeleton_swordless2.png", 5, 6, 96, 80, False),
        },
        "sound": "sounds/skeleton_run.wav",
                 "impact_frame": None
},
    "sword_slash": {
        "sprites": {
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 7, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 7, 6, 96, 80, True),
        },
        "sound": get_file_location("sounds/sword_slash.wav"),
        "impact_frame": 3
    },
    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 12, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 12, 4, 96, 80, True),
        },
        "sound": "sounds/skeleton_death.wav",
        "impact_frame": None

    }
}


slime_sprites = {
    "idle": {
        "sprites": {
            "down": sprite_converter("sprites/characters/slime.png", 0, 4, 64, 64, False),
            "right": sprite_converter("sprites/characters/slime.png", 1, 4, 64, 64, False),
            "left": sprite_converter("sprites/characters/slime.png", 1, 4, 64, 64, True),
            "up": sprite_converter("sprites/characters/slime.png", 2, 4, 64, 64, False),
        },
        "sound": None,
        "impact_frame": None
    },
    "running": {
        "sprites": {
            "down": sprite_converter("sprites/characters/slime.png", 3, 6, 64, 64, False),
            "right": sprite_converter("sprites/characters/slime.png", 4, 6, 64, 64, False),
            "left": sprite_converter("sprites/characters/slime.png", 4, 6, 64, 64, True),
            "up": sprite_converter("sprites/characters/slime.png", 5, 6, 64, 64, False),
        },
        "sound": "sounds/skeleton_run.wav",
                 "impact_frame": None}}