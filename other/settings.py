
from other.png_to_sprite import *


SCALE = 2


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360

FPS = 120
TILE_SIZE = 32


# Sprites
fireball_sprites = fireball_sprites

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites

# moves
moves = {"fire_ball": {"dmg": 7, "type": "special", "mana": 5, "sound": [get_file_location("sounds/effects/fire_woosh.mp3"), get_file_location("sounds/effects/fire_impact.mp3")]},
         "sword_slash": {"dmg": 5, "type": "physical", "mana": 1, "sound": [get_file_location("sounds/sword_slash.wav")]},
         "punch": {"dmg": 10, "type": "physical", "mana": 0, "sound": [get_file_location("sounds/effects/punch.mp3")]},
         "heal": {"hp": 5, "type": "buff", "mana": 2, "sound": get_file_location("sounds/effects/heal.mp3")},
        "lightning_strike": {"dmg": 7, "type": "special", "mana": 5, "sound": [get_file_location("sounds/effects/lightning_strike.mp3")]},

         }

# maps
FOREST_MAP = get_file_location("tmx/untitled.tmx")

# background music and sounds
FOREST_MUSIC = get_file_location("sounds/background/forest_theme.mp3")
BATTLE_MUSIC_1 = get_file_location("sounds/background/12-Fight3.mp3")

HOVER_SOUND = get_file_location("sounds/hover.wav")
PRESS_SOUND = get_file_location("sounds/click.wav")
DISABLED_SOUND = get_file_location("sounds/disabled.wav")
ENEMY_ALERT = get_file_location("sounds/effects/enemy_alert.mp3")
PERFECT_BLOCK = get_file_location("sounds/effects/perfect_block_2.mp3")
CRITICAL_HIT = get_file_location("sounds/effects/critical_hit_3.mp3")


GRASS_FOOTSTEP = get_file_location("sounds/Walk/Grass/GRASS - Walk 7.wav")

# UI
BACKGROUND_BOX = get_file_location(f"sprites/UI/background_box.png")
TITLE_BOX = get_file_location(f"sprites/UI/title_box.png")
HP_BOX = get_file_location(f"sprites/UI/hp_box.png")
LEVEL_BOX = get_file_location(f"sprites/UI/level_box.png")
MANA_BOX = get_file_location(f"sprites/UI/mana_box.png")
HP_BAR = get_file_location(f"sprites/UI/hp_bar.png")
HP_ICON = get_file_location(f"sprites/UI/heart_icon.png")

BOOK = get_file_location("sprites/UI/book_stuff/book.png")


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

