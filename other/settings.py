import os

import pygame.mixer

pygame.mixer.init()

from other.png_to_sprite import *

SCALE = 2
MUSIC_VOLUME = 0.0
EFFECT_VOLUME = 0.25

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

FPS = 60
TILE_SIZE = 32

# === animated sprites ===
fireball_sprites = fireball_sprites
level_up_sprites = level_up_sprites

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites
block_shield_sprites = block_shield_sprites

# === moves info ===
MOVES = {
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
        "sound": [get_file_location("sounds/effects/sword_slash.wav")]
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

# === maps ===
FOREST_MAP = get_file_location("tmx/untitled.tmx")

# === background music and sounds ===
FOREST_MUSIC = get_file_location("sounds/background/forest_theme.mp3")
BATTLE_MUSIC_1 = get_file_location("sounds/background/10-Fight.mp3")
BATTLE_MUSIC_2 = get_file_location("sounds/background/11-Fight2.mp3")
BATTLE_MUSIC_3 = get_file_location("sounds/background/12-Fight3.mp3")


# === sound effects ===
sound_effects = {
    "moves": {
        "fire_ball": [pygame.mixer.Sound(get_file_location("sounds/effects/fire_woosh.mp3")), pygame.mixer.Sound(get_file_location("sounds/effects/fire_impact.mp3"))],
        "sword_slash": pygame.mixer.Sound(get_file_location("sounds/effects/sword_slash.wav")),
        "punch": pygame.mixer.Sound(get_file_location("sounds/effects/punch.mp3")),
        "heal": pygame.mixer.Sound(get_file_location("sounds/effects/heal.mp3")),
        "lightning_strike": pygame.mixer.Sound(get_file_location("sounds/effects/lightning_strike.mp3"))
    },
    "ui": {
        "hover": pygame.mixer.Sound(get_file_location("sounds/effects/hover.wav")),
        "press": pygame.mixer.Sound(get_file_location("sounds/effects/click.wav")),
        "disabled": pygame.mixer.Sound(get_file_location("sounds/effects/disabled.wav")),
    },
    "gameplay": {
        "enemy_alert": pygame.mixer.Sound(get_file_location("sounds/effects/enemy_alert.mp3")),
        "perfect_block": pygame.mixer.Sound(get_file_location("sounds/effects/perfect_block_2.mp3")),
        "critical_hit": pygame.mixer.Sound(get_file_location("sounds/effects/critical_hit_3.mp3")),
        "level_up": pygame.mixer.Sound(get_file_location("sounds/effects/level_up_sound.mp3")),
    }
}

# === set volume to all effects ===
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

# === book ===
BOOK_IMAGE = pygame.image.load(get_file_location("sprites/UI/book_stuff/book.png"))
DIVIDER = pygame.image.load(get_file_location("sprites/UI/divider.png"))
INFO_TITLE = pygame.image.load(get_file_location("sprites/UI/book_stuff/info_title.png"))
INFO_PAGE = pygame.image.load(get_file_location("sprites/UI/book_stuff/info_page.png"))
BOOK_SKILLS_TITLE = get_file_location("sprites/UI/book_stuff/skills_title.png") # to be implemented

# ___hp bar___
EXCLAMATION_MARK = get_file_location(f"sprites/UI/exclamation_mark.png")

NEW_HP_BG = pygame.image.load(get_file_location("sprites/UI/new_hp_bar.png"))
NEW_HP_BOX = pygame.image.load(get_file_location("sprites/UI/new_hp_box.png"))
NEW_HP_BAR = pygame.image.load(get_file_location("sprites/UI/new_hp.png"))
NEW_MANA_BAR = pygame.image.load(get_file_location("sprites/UI/new_mana.png"))
BG_BAR = pygame.image.load(get_file_location("sprites/UI/second_bar.png"))

HP_BAR_BG = pygame.image.load(get_file_location("sprites/UI/hp_test.png"))


# === combat menu
COMBAT_MENU_MAIN_BG = pygame.image.load(get_file_location("sprites/UI/combat_menu_bg.png"))
PLAYER_ICON = pygame.image.load(get_file_location("sprites/UI/player_face.png"))
SKILLS_MENU_BG = pygame.image.load(get_file_location("sprites/UI/skills_bg.png"))
VICTORY_TEXT = pygame.image.load(get_file_location("sprites/UI/victory_text.png"))


# ___buttons___
BUTTON_SMALL_NORMAL = pygame.image.load(get_file_location("sprites/UI/button_small.png"))
BUTTON_SMALL_SELECTED = pygame.image.load(get_file_location("sprites/UI/button_small_selected.png"))
BUTTON_SMALL_PRESSED = pygame.image.load(get_file_location("sprites/UI/button_small_pressed.png"))

BUTTON_SIMPLE_NORMAL = pygame.image.load(get_file_location("sprites/UI/simple_button_normal.png"))
BUTTON_SIMPLE_SELECTED = pygame.image.load(get_file_location("sprites/UI/simple_button_selected.png"))
BUTTON_SIMPLE_PRESSED = pygame.image.load(get_file_location("sprites/UI/simple_button_normal.png"))

BUTTON_LARGE_SIMPLE_NORMAL = pygame.image.load(get_file_location("sprites/UI/simple_large_button_normal.png"))
BUTTON_LARGE_SIMPLE_SELECTED = pygame.image.load(get_file_location("sprites/UI/simple_large_button_selected.png"))
BUTTON_LARGE_SIMPLE_PRESSED = pygame.image.load(get_file_location("sprites/UI/simple_large_button_normal.png"))


# ___fonts___
FONT_ONE = get_file_location("sprites/fonts/FantasyRPGtext.ttf")
FONT_TWO = get_file_location("sprites/fonts/FantasyRPGtitle.ttf")
