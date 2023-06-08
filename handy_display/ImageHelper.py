import pygame

search_dir = "resources/images/"


def get_scaled(path: str, w: int, h: int) -> pygame.Surface:
    img = pygame.image.load(search_dir + path)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return pygame.transform.scale(img, (w, h), surf)
