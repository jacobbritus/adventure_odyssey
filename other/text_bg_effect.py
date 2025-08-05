import pygame


def text_bg_effect(text, font, pos, window):
    text: pygame.Surface = font.render(text, True, (81, 57, 44))

    box_size = (max(text.get_width() - 8, 1), max(text.get_height()  - 10, 1))
    box_surf = pygame.Surface(box_size, pygame.SRCALPHA)  # Support transparency
    box_surf.fill((81, 57, 44, 255))  # Light translucent background


    if window:
        window.blit(text, pos + (2, 0))
        window.blit(text, pos + (2, 2))
        window.blit(box_surf, pos + (4, 8))
        return None
    else:
        return [(text, pos + (2,0)), (text, pos + (2, 2)), (box_surf, pos + (4, 8))]