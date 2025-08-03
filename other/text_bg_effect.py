
def text_bg_effect(text, font, pos, window):
    text = font.render(text, True, (81, 57, 44))
    if window:
        window.blit(text, pos + (2, 0))
        window.blit(text, pos + (2, 2))
        return None
    else:
        return [(text, pos + (2,0)), (text, pos + (2, 2))]



