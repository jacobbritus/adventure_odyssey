from other.png_to_sprite import *
import os


WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
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


GRASS_FOOTSTEP = get_file_location("sounds/Walk/Grass/GRASS - Walk 7.wav")

# UI
BACKGROUND_BOX = get_file_location("sprites/UI/background_box.png")
TITLE_BOX = get_file_location("sprites/UI/title_box.png")

HP_BOX = get_file_location("sprites/UI/Slider01_Box.png")
HP_BAR = get_file_location("sprites/UI/Slider01_Bar02.png")
HP_ICON = get_file_location("sprites/UI/heart_icon.png")


BUTTON_NORMAL = get_file_location("sprites/UI/Button_01A_Normal.png")
BUTTON_SELECTED = get_file_location("sprites/UI/Button_01A_Selected.png")
BUTTON_PRESSED = get_file_location("sprites/UI/Button_01A_Pressed.png")

RPG_TEXT = get_file_location("sprites/fonts/FantasyRPGtext.ttf")

