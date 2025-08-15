import os

import pygame.mixer

from classes.states import StatusEffects

pygame.mixer.init()
pygame.mixer.set_num_channels(32)

from other.png_to_sprite import *

SCALE = 2
MUSIC_VOLUME = 0.5
EFFECT_VOLUME = 1
UI_OPACITY = 225

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

FPS = 60
TILE_SIZE = 32

# === animated sprites ===
fireball_sprites = fireball_sprites
level_up_sprites = level_up_sprites

player_sprites = player_sprites
sprite_dust = sprite_dust
skeleton_sprites = skeleton_sprites
block_shield_sprites = block_shield_sprites

item_drop = item_drop

# === moves info ===
SKILLS = {
    "fire_ball": {
        "base_damage": 6,
        "multiplier": 0.5,
        "stat": "magic",
        "type": "special",
        "mana": 3,
        "status_effect": StatusEffects.BURNED,

        "sound": [get_file_location("sounds/effects/fire_woosh.mp3"),get_file_location("sounds/effects/fire_impact.mp3")],
        "description": "A conjured flame hurled to deal magic damage to one enemy."
    },
    "sword_slash": {
        "base_damage": 2,
        "multiplier": 0.5,
        "stat": "strength",
        "type": "physical",
        "mana": 0,
        "sound": [get_file_location("sounds/effects/sword_slash.wav")],
        "description": "A precise sword strike that deals physical damage to one enemy."


    },
    "punch": {
        "base_damage": 1,
        "multiplier": 0.25,
        "stat": "strength",
        "type": "physical",
        "mana": 0,
        "sound": [get_file_location("sounds/effects/punch.mp3")],
        "description": "A close-range blow that deals physical damage to one enemy."
    },
    "heal": {
        "hp": 5,
        "type": "buff",
        "mana": 2,
        "sound": get_file_location("sounds/effects/heal.mp3"),
        "description": "A restoring spell that replenishes HP for one ally."
    },
    "lightning_strike": {
        "base_damage": 60,
        "multiplier": 0.25,
        "stat": "strength",
        "type": "special",
        "mana": 5,
        "sound": [get_file_location("sounds/effects/lightning_strike.mp3")],
        "description": "A surge of lightning that deals magic damage to one enemy."
    },
    "poison_stab": {
            "base_damage": 2,
            "multiplier": 0.25,
            "stat": "strength",
            "type": "physical",
            "mana": 2,
            "status_effect": StatusEffects.POISONED,
            "sound": [get_file_location("sounds/effects/sword_slash.mp3")],
            "description": "A close-range blow that deals physical damage to one enemy."}
}

# === items ===
# types = consumable,
ITEMS = {
    "small_health_potion": {
        "type": "consumable",
        "image": pygame.image.load(get_file_location("sprites/items/small_health_potion.png")),
        "stat": "hp",
        "effect": +5, # get attr(player, stat) += effect
        "description": "A basic potion that restores a small amount of health.",
        "inventory_desc": "Restores 5 HP"
    },
"small_mana_potion": {
        "type": "consumable",
        "image": pygame.image.load(get_file_location("sprites/items/small_mana_potion.png")),
        "stat": "mana",
        "effect": +5, # get attr(player, stat) += effect
        "description": "A basic potion that restores a small amount of health.",
        "inventory_desc": "Restores 5 SP"

}
}

ITEM_SHADOW = pygame.image.load(get_file_location("sprites/items/shadow.png"))

# === maps ===
FOREST_MAP = get_file_location("tmx/untitled.tmx")

# === background music and sounds ===
FOREST_MUSIC = get_file_location("sounds/background/forest_theme.mp3")

BATTLE_MUSIC = [get_file_location("sounds/background/10-Fight.mp3"),
                get_file_location("sounds/background/11-Fight2.mp3"),
                get_file_location("sounds/background/12-Fight3.mp3")]

VICTORY_MUSIC =  [get_file_location("sounds/background/victory1.wav"),
        get_file_location("sounds/background/victory2.wav"),
        get_file_location("sounds/background/victory3.wav")]


# === sound effects ===
SOUND_EFFECTS = {
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
        "victory": [pygame.mixer.Sound(get_file_location("sounds/background/victory1.wav")),
        pygame.mixer.Sound(get_file_location("sounds/background/victory2.wav")),
        pygame.mixer.Sound(get_file_location("sounds/background/victory3.wav")),],
        "poisoned": pygame.mixer.Sound(get_file_location("sounds/effects/poisoned.mp3")),
        "burned": pygame.mixer.Sound(get_file_location("sounds/effects/burned.mp3"))

    }
}

# === set volume to all effects ===
for category in SOUND_EFFECTS.values():
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


# === load UI ===
UI_directory = get_file_location("sprites/UI")
UI_directories = [directory for directory in os.listdir(UI_directory)
                  if os.path.isdir(os.path.join(UI_directory, directory))]

UI = {}
for directory in UI_directories:

    images_dict = {}
    for image in os.listdir(get_file_location(os.path.join(UI_directory, directory))):
        png_image = pygame.image.load(get_file_location(os.path.join(UI_directory, directory, image)))
        png_image.set_alpha(UI_OPACITY)
        key_name = image[:-4]
        images_dict[key_name] = png_image

    UI[directory] = images_dict


# ___hp bar___
EXCLAMATION_MARK = get_file_location(f"sprites/UI/exclamation_mark.png")

# ___fonts___
FONT_ONE = get_file_location("sprites/fonts/FantasyRPGtext.ttf")
FONT_TWO = get_file_location("sprites/fonts/FantasyRPGtitle.ttf")


