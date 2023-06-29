import pygame.draw
from pygame.sprite import Sprite


class TestSprite(Sprite):

    def __init__(self, x: int, y: int, r: int):
        super(TestSprite, self).__init__()

        self.image = pygame.image.load("resources/images/test.png").convert()
        self.rect = pygame.Rect(x, y, r * 2, r * 2)
