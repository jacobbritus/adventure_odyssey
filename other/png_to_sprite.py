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
            "down": sprite_converter("sprites/characters/jacob.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/jacob.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/jacob.png", 2, 6, 96, 80, False),
        },
        "sound": get_file_location("sounds/sword_slash"),
        "impact_frame": None

    },
    "running": {
        "sprites": {
            "down": sprite_converter("sprites/characters/jacob.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/jacob.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/jacob.png", 5, 6, 96, 80, False),
        },
        "sound": "sounds/footsteps.wav"
    },
    "sword_slash": {
        "sprites": {
            "right": sprite_converter("sprites/characters/jacob.png", 7, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 7, 4, 96, 80, True),
        },
        "sound": get_file_location("sounds/sword_slash.wav"),
        "impact_frame": 2


    },

    "punch": {
            "sprites": {
                "right": sprite_converter("sprites/characters/jacob.png", 11, 4, 96, 80, False),
                "left": sprite_converter("sprites/characters/jacob.png", 11, 4, 96, 80, True),
            },
            "sound": get_file_location("sounds/sword_slash.wav"),
            "impact_frame": 2},
    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/jacob.png", 9, 3, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 9, 3, 96, 80, True),
        },
        "sound": "sounds/death.wav"
    },
"cast": {
        "sprites": {
            "right": sprite_converter("sprites/characters/jacob.png", 10, 5, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 10, 5, 96, 80, True),
        },
        "sound": "sounds/skeleton_death.wav",
        "impact_frame": None},
    "blocking": {
        "sprites": {
            "right": sprite_converter("sprites/characters/jacob.png", 12, 1, 96, 80, False),
                "left": sprite_converter("sprites/characters/jacob.png", 12, 1, 96, 80, True),
        }
    },
    "item_use":{
        "sprites": {
"down": sprite_converter("sprites/characters/jacob.png", 13, 1, 96, 80, False),
                "right": sprite_converter("sprites/characters/jacob.png", 14, 1, 96, 80, False),
            "left": sprite_converter("sprites/characters/jacob.png", 14, 1, 96, 80, True),
            "up": sprite_converter("sprites/characters/jacob.png", 15, 1, 96, 80, True),

        }
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
        "impact_frame": 4
    },
    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 12, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 12, 4, 96, 80, True),
        },
        "sound": "sounds/skeleton_death.wav",
        "impact_frame": None
    },
    "blocking": {
        "sprites": {
            "right": sprite_converter("sprites/characters/skeleton_swordless2.png", 13, 1, 96, 80, False),
                "left": sprite_converter("sprites/characters/skeleton_swordless2.png", 13, 1, 96, 80, True),
        }}

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
                 "impact_frame": None},



    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/slime.png", 12, 4, 64, 64, False),
            "left": sprite_converter("sprites/characters/slime.png", 12, 4, 64, 64, True),
        },
        "sound": "sounds/skeleton_death.wav",
        "impact_frame": None

}}

fireball_sprites = {
        "sprites": {
                "right": sprite_converter("sprites/particles/fireball.png", 0, 4, 96, 128, False),
                "righ1": sprite_converter("sprites/particles/fireball.png", 1, 4, 96, 128, False),
                "right1": sprite_converter("sprites/particles/fireball.png", 2, 4, 96, 128, False),
                "right4": sprite_converter("sprites/particles/fireball.png", 2, 4, 96, 128, False),
            "explosion": sprite_converter("sprites/particles/explosion.png", 0, 7, 128, 144, False),

            "left": sprite_converter("sprites/particles/fireball.png", 0, 4, 96, 96, True),
            "left2": sprite_converter("sprites/particles/fireball.png", 1, 4, 96, 96, True),
                "left3": sprite_converter("sprites/particles/fireball.png", 2, 4, 96, 96, True),
                "left4": sprite_converter("sprites/particles/fireball.png", 2, 4, 96, 96, True),

            "hit": sprite_converter("sprites/particles/fire_hit.png", 0, 4, 80, 80, False)}
                ,

        "sound": [get_file_location("sounds/effects/fire_woosh.mp3"), get_file_location("sounds/effects/fire_impact.mp3")],


                    }

# heal_sprites = {
#     "sprites": {
#         "right": sprite_converter("sprites/particles/heal.png", 0, 4, 96, 90, False),
#
#     }
# }

heal_sprites = sprite_converter("sprites/particles/heal.png", 0, 4, 96, 90, False)

goblin_sprites = {
    "idle": {
        "sprites": {
            "down": sprite_converter("sprites/characters/goblin.png", 0, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/goblin.png", 1, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/goblin.png", 1, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/goblin.png", 2, 6, 96, 80, False),
        },
        "sound": get_file_location("sounds/sword_slash"),
        "impact_frame": None

    },
    "running": {
        "sprites": {
            "down": sprite_converter("sprites/characters/goblin.png", 3, 6, 96, 80, False),
            "right": sprite_converter("sprites/characters/goblin.png", 4, 6, 96, 80, False),
            "left": sprite_converter("sprites/characters/goblin.png", 4, 6, 96, 80, True),
            "up": sprite_converter("sprites/characters/goblin.png", 5, 6, 96, 80, False),
        },
        "sound": "sounds/footsteps.wav"
    },
    "sword_slash": {
        "sprites": {
            "right": sprite_converter("sprites/characters/goblin.png", 6, 4, 96, 80, False),
            "left": sprite_converter("sprites/characters/goblin.png", 6, 4, 96, 80, True),
        },
        "sound": get_file_location("sounds/sword_slash.wav"),
        "impact_frame": 2
    },

    "death": {
        "sprites": {
            "right": sprite_converter("sprites/characters/goblin.png", 7, 3, 96, 80, False),
            "left": sprite_converter("sprites/characters/goblin.png", 7, 3, 96, 80, True),
        },
        "sound": "sounds/death.wav"
},
"blocking": {
        "sprites": {
            "right": sprite_converter("sprites/characters/goblin.png", 8, 1, 96, 80, False),
                "left": sprite_converter("sprites/characters/goblin.png", 8, 1, 96, 80, True),
        }}


}

lightning_sprites = sprite_converter("sprites/particles/lightning.png", 0, 10, 128, 256, False)


book_sprites = {
    "open_book": sprite_converter("sprites/UI/book/open_book.png", 0, 8, 512, 480, False),
    "close_book": sprite_converter("sprites/UI/book/close_book.png", 0, 8, 512, 480, False),
    "next_page": sprite_converter("sprites/UI/book/next_page.png", 0, 8, 512, 352, False),
    "previous_page": sprite_converter("sprites/UI/book/previous_page.png", 0, 8, 512, 352, False),
}

for images in book_sprites.values():
    for image in images:
        image.set_alpha(200)


level_up_sprites = sprite_converter("sprites/particles/level_up.png", 0, 16, 96, 514, False)



block_shield_sprites = {
"sprites": {
        "right": sprite_converter("sprites/particles/shield_block.png", 0, 5, 32, 96, False),
    "left": sprite_converter("sprites/particles/shield_block.png", 0, 5, 32, 96, True),

}}

item_drop = sprite_converter("sprites/items/item_drop.png", 0, 4, 32, 32, False)

