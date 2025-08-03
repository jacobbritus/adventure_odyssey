from other.settings import *
import random

def play_sound(sound_category, name, number=None):
    channel = pygame.mixer.find_channel()
    if not channel:
        return

    try:
        sounds = SOUND_EFFECTS[sound_category][name]

        # If it's a list
        if isinstance(sounds, list):
            if number == "random":
                channel.play(random.choice(sounds))
            elif isinstance(number, int) and 0 <= number < len(sounds):
                channel.play(sounds[number])
            else:
                # Default: play first if no valid index is provided
                channel.play(sounds[0])
        else:
            # It's a single Sound object
            channel.play(sounds)

    except KeyError:
        print(f"Sound '{name}' in category '{sound_category}' not found.")

