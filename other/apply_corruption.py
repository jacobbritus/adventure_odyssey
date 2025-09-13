import pygame

from other.settings import *


def apply_corruption(image, tint_color=(127, 0, 255), intensity=0.3):
    """
    Modify the image pixels by blending each pixel with the tint color.
    - image: Pygame Surface with per-pixel alpha.
    - tint_color: RGB tuple of the tint.
    - intensity: How strong the tint is (0 to 1).
    Returns a new Surface with the tint applied.
    """
    # Make a copy so you don't modify the original
    tinted_image = image.copy().convert_alpha()

    # Lock the surface for pixel access
    tinted_image.lock()

    width, height = tinted_image.get_size()

    for x in range(width):
        for y in range(height):
            r, g, b, a = tinted_image.get_at((x, y))

            # Blend each channel with the tint color
            new_r = int(r * (1 - intensity) + tint_color[0] * intensity)
            new_g = int(g * (1 - intensity) + tint_color[1] * intensity)
            new_b = int(b * (1 - intensity) + tint_color[2] * intensity)

            tinted_image.set_at((x, y), (new_r, new_g, new_b, a))

    tinted_image.unlock()
    return tinted_image

# Usage example:


dark_purple = (48, 25, 52)


