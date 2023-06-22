import pygame

pygame.init()


def font(name: str, size: int):
    path = "resources/fonts/" + name
    return pygame.font.Font(path, size)


def image(path: str, w: int, h: int) -> pygame.Surface:
    img = pygame.image.load("resources/images/" + path)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return pygame.transform.scale(img, (w, h), surf)


def smooth_image(path: str, w: int, h: int) -> pygame.Surface:
    img = pygame.image.load("resources/images/" + path)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return pygame.transform.smoothscale(img, (w, h), surf)
