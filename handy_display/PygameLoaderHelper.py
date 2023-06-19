import pygame

pygame.init()


def font(name: str, size: int):
    path = "resources/fonts/" + name
    return pygame.font.Font(path, size)


def image(path: str, w: int, h: int) -> pygame.Surface:
    if not pygame.get_init():
        raise Exception("Pygame must be initialised before using ImageHelper.get_scaled(...)")

    img = pygame.image.load("resources/images/" + path)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return pygame.transform.scale(img, (w, h), surf)
