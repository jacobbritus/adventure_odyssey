from other.png_to_sprite import *
import os


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites

def get_file_location(file_location: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_dir, "..", file_location)



