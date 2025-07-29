import os

import pygame.mixer

pygame.mixer.init()

from other.png_to_sprite import *

SCALE = 2
MUSIC_VOLUME = 0.2
EFFECT_VOLUME = 0.2

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

FPS = 60
TILE_SIZE = 32

# Sprites
fireball_sprites = fireball_sprites
level_up_sprites = level_up_sprites

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites
block_shield_sprites = block_shield_sprites

# moves
moves = {
    "fire_ball": {
        "base_damage": 10,
        "multiplier": 0.5,
        "stat": "magic",
        "type": "special",
        "mana": 3,
        "sound": [get_file_location("sounds/effects/fire_woosh.mp3"),get_file_location("sounds/effects/fire_impact.mp3")]
    },
    "sword_slash": {
        "base_damage": 3,
        "multiplier": 0.25,
        "stat": "strength",
        "type": "physical",
        "mana": 1,
        "sound": [get_file_location("sounds/sword_slash.wav")]
    },
    "punch": {
        "base_damage": 50,
        "multiplier": 0.25,
        "stat": "strength",
        "type": "physical",
        "mana": 0,
        "sound": [get_file_location("sounds/effects/punch.mp3")]
    },
    "heal": {
        "hp": 5,
        "type": "buff",
        "mana": 2,
        "sound": get_file_location("sounds/effects/heal.mp3")
    },
    "lightning_strike": {
        "base_damage": 7,
        "multiplier": 0.25,
        "stat": "strength",
        "type": "special",
        "mana": 5,
        "sound": [get_file_location("sounds/effects/lightning_strike.mp3")]},
}

# maps
FOREST_MAP = get_file_location("tmx/untitled.tmx")

# background music and sounds
FOREST_MUSIC = get_file_location("sounds/background/forest_theme.mp3")
BATTLE_MUSIC_1 = get_file_location("sounds/background/10-Fight.mp3")
BATTLE_MUSIC_2 = get_file_location("sounds/background/11-Fight2.mp3")
BATTLE_MUSIC_3 = get_file_location("sounds/background/12-Fight3.mp3")


# === Load and Categorize ===
sound_effects = {
    "moves": {
        "fire_ball": [pygame.mixer.Sound(get_file_location("sounds/effects/fire_woosh.mp3")), pygame.mixer.Sound(get_file_location("sounds/effects/fire_impact.mp3"))],
        "sword_slash": pygame.mixer.Sound(get_file_location("sounds/sword_slash.wav")),
        "punch": pygame.mixer.Sound(get_file_location("sounds/effects/punch.mp3")),
        "heal": pygame.mixer.Sound(get_file_location("sounds/effects/heal.mp3")),
        "lightning_strike": pygame.mixer.Sound(get_file_location("sounds/effects/lightning_strike.mp3"))

    },

    "ui": {
        "hover": pygame.mixer.Sound(get_file_location("sounds/hover.wav")),
        "press": pygame.mixer.Sound(get_file_location("sounds/click.wav")),
        "disabled": pygame.mixer.Sound(get_file_location("sounds/disabled.wav")),
    },
    "gameplay": {
        "enemy_alert": pygame.mixer.Sound(get_file_location("sounds/effects/enemy_alert.mp3")),
        "perfect_block": pygame.mixer.Sound(get_file_location("sounds/effects/perfect_block_2.mp3")),
        "critical_hit": pygame.mixer.Sound(get_file_location("sounds/effects/critical_hit_3.mp3")),
        "level_up": pygame.mixer.Sound(get_file_location("sounds/effects/level_up_sound.mp3")),
    }
}

# === Set volume for all effects ===
for category in sound_effects.values():
    for effect in category.values():
        sounds = effect if isinstance(effect, list) else [effect]
        for sound in sounds:
            sound.set_volume(EFFECT_VOLUME)



GRASS_FOOTSTEPS = []
grass_footsteps_dir = get_file_location("sounds/footsteps/grass")
for file in os.listdir(grass_footsteps_dir):
    if file.endswith(".wav"):
        full_path = get_file_location(os.path.join(grass_footsteps_dir, file))
        sound = pygame.mixer.Sound(full_path)
        sound.set_volume(EFFECT_VOLUME)
        GRASS_FOOTSTEPS.append(sound)

# UI
BACKGROUND_BOX = get_file_location(f"sprites/UI/background_box.png")
TITLE_BOX = get_file_location(f"sprites/UI/title_box.png")
HP_BOX = get_file_location(f"sprites/UI/hp_box.png")
LEVEL_BOX = get_file_location(f"sprites/UI/level_box.png")
MANA_BOX = get_file_location(f"sprites/UI/mana_box.png")
HP_BAR = get_file_location(f"sprites/UI/hp_bar.png")
HP_ICON = get_file_location(f"sprites/UI/heart_icon.png")

### book
BOOK = get_file_location("sprites/UI/book_stuff/book.png")
DIVIDER = get_file_location("sprites/UI/divider.png")
INFO_TITLE = get_file_location("sprites/UI/book_stuff/info_title.png")
INFO_PAGE = get_file_location("sprites/UI/book_stuff/info_page.png")
BOOK_SKILLS_TITLE = get_file_location("sprites/UI/book_stuff/skills_title.png")

# ___hp bar___
BACKGROUND_BOX2 = get_file_location(f"sprites/UI/background_box2.png")
BACKGROUND_BOX3 = get_file_location(f"sprites/UI/background_box3.png")
ENEMY_BACKGROUND_BOX = get_file_location(f"sprites/UI/enemy_background_box.png")
HP_MANA_BOX = get_file_location(f"sprites/UI/hp_box2.png")
STAT_BOX = get_file_location(f"sprites/UI/stat_bar.png")
HP_BAR2 = get_file_location(f"sprites/UI/hp_bar2.png")
HP_BAR3 = get_file_location(f"sprites/UI/hp_bar3.png")
MANA_BAR = get_file_location(f"sprites/UI/mana_bar.png")

TIME_BACKGROUND = get_file_location(f"sprites/UI/time_background.png")

LARGE_BACKGROUND_BOX = get_file_location(f"sprites/UI/large_background_box.png")
SKILLS_TITLE = get_file_location(f"sprites/UI/skills_title.png")

EXCLAMATION_MARK = get_file_location(f"sprites/UI/exclamation_mark.png")

# ___buttons___
BUTTON_SMALL_NORMAL = pygame.image.load(get_file_location("sprites/UI/button_small.png"))
BUTTON_SMALL_SELECTED = pygame.image.load(get_file_location("sprites/UI/button_small_selected.png"))
BUTTON_SMALL_PRESSED = pygame.image.load(get_file_location("sprites/UI/button_small_pressed.png"))


BUTTON_NORMAL = get_file_location(f"sprites/UI/button_one_normal.png")
BUTTON_SELECTED = get_file_location(f"sprites/UI/button_one_selected.png")
BUTTON_PRESSED = get_file_location(f"sprites/UI/button_one_pressed.png")

BUTTON_TWO_NORMAL = get_file_location(f"sprites/UI/button_two_normal.png")
BUTTON_TWO_SELECTED = get_file_location(f"sprites/UI/button_two_selected.png")
BUTTON_TWO_PRESSED = get_file_location(f"sprites/UI/button_two_pressed.png")

LARGE_BUTTON_NORMAL = get_file_location(f"sprites/UI/large_button_normal.png")
LARGE_BUTTON_SELECTED = get_file_location(f"sprites/UI/large_button_selected.png")
LARGE_BUTTON_PRESSED = get_file_location(f"sprites/UI/large_button_pressed.png")

# ___fonts___
FONT_ONE = get_file_location("sprites/fonts/FantasyRPGtext.ttf")
FONT_TWO = get_file_location("sprites/fonts/FantasyRPGtitle.ttf")
