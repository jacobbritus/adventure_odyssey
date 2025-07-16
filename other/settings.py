
from other.png_to_sprite import *
import os


SCALE = 2


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360

FPS = 60
TILE_SIZE = 32

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites

# maps
FOREST_MAP = get_file_location("tmx/untitled.tmx")

# background music and sounds
FOREST_MUSIC = get_file_location("sounds/background/forest_theme.mp3")
BATTLE_MUSIC_1 = get_file_location("sounds/background/12-Fight3.mp3")

HOVER_SOUND = get_file_location("sounds/hover.wav")
PRESS_SOUND = get_file_location("sounds/click.wav")
ENEMY_ALERT = get_file_location("sounds/effects/enemy_alert.mp3")
PERFECT_BLOCK = get_file_location("sounds/effects/perfect_block.wav")
CRITICAL_HIT = get_file_location("sounds/effects/critical_hit.mp3")


GRASS_FOOTSTEP = get_file_location("sounds/Walk/Grass/GRASS - Walk 7.wav")

# UI
BACKGROUND_BOX = get_file_location(f"sprites/UI/{str(SCALE)}x/background_box.png")
TITLE_BOX = get_file_location(f"sprites/UI/{str(SCALE)}x/title_box.png")
HP_BOX = get_file_location(f"sprites/UI/{str(SCALE)}x/hp_box.png")
HP_BAR = get_file_location(f"sprites/UI/{str(SCALE)}x/hp_bar.png")

TIME_BACKGROUND = get_file_location(f"sprites/UI/{str(SCALE)}x/time_background.png")

LARGE_BACKGROUND_BOX = get_file_location(f"sprites/UI/{str(SCALE)}x/large_background_box.png")
SKILLS_TITLE = get_file_location(f"sprites/UI/{str(SCALE)}x/skills_title.png")




HP_ICON = get_file_location(f"sprites/UI/{str(SCALE)}x/heart_icon.png")
EXCLAMATION_MARK = get_file_location(f"sprites/UI/{str(SCALE)}x/exclamation_mark.png")


BUTTON_NORMAL = get_file_location(f"sprites/UI/{str(SCALE)}x/button_one_normal.png")
BUTTON_SELECTED = get_file_location(f"sprites/UI/{str(SCALE)}x/button_one_selected.png")
BUTTON_PRESSED = get_file_location(f"sprites/UI/{str(SCALE)}x/button_one_pressed.png")

BUTTON_TWO_NORMAL = get_file_location(f"sprites/UI/{str(SCALE)}x/button_two_normal.png")
BUTTON_TWO_SELECTED = get_file_location(f"sprites/UI/{str(SCALE)}x/button_two_selected.png")
BUTTON_TWO_PRESSED = get_file_location(f"sprites/UI/{str(SCALE)}x/button_two_pressed.png")


LARGE_BUTTON_NORMAL = get_file_location(f"sprites/UI/{str(SCALE)}x/large_button_normal.png")
LARGE_BUTTON_SELECTED = get_file_location(f"sprites/UI/{str(SCALE)}x/large_button_selected.png")
LARGE_BUTTON_PRESSED = get_file_location(f"sprites/UI/{str(SCALE)}x/large_button_pressed.png")

TEXT_ONE = get_file_location("sprites/fonts/FantasyRPGtext.ttf")
TEXT_TWO = get_file_location("sprites/fonts/FantasyRPGtitle.ttf")

