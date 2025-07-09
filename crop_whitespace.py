import pygame
import sys

def crop_whitespace(image: pygame.Surface) -> pygame.Surface:
    # Get smallest rect containing all non-transparent pixels
    rect = image.get_bounding_rect()
    cropped = pygame.Surface(rect.size, pygame.SRCALPHA)
    cropped.blit(image, (0, 0), rect)
    return cropped

def main():
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Load your original image (replace with your actual path)
    original_image = pygame.image.load("sprites/characters/me2.png").convert_alpha()

    # Crop transparent whitespace
    cropped_image = crop_whitespace(original_image)

    # Save cropped image
    pygame.image.save(cropped_image, "sprites/characters/cropped_player_sprite.png")
    print("Saved cropped image as cropped_player_sprite.png")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
