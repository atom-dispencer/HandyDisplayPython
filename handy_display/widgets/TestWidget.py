import random

from pygame import Surface
from pygame.sprite import Group

from handy_display.sprite.TestSprite import TestSprite
from handy_display.widgets.IWidget import IWidget


class TestWidget(IWidget):

    def __init__(self):
        self.bg_color = (255, 255, 255)

        self.group = Group()
        self.test = TestSprite(50, 50, 50)
        self.group.add(self.test)

    def draw(self, screen_surface: Surface):
        screen_surface.fill(self.bg_color)

        self.group.draw(screen_surface)
        return

    def click_event(self, x: int, y: int):
        if self.test.rect.collidepoint(x, y):
            self.bg_color = tuple(random.randint(0, 255) for _ in range(3))
            self.test.rect.x = random.randint(50, 150)
            self.test.rect.y = random.randint(50, 150)
            self.test.rect.w = random.randint(50, 150)
            self.test.rect.h = random.randint(50, 100)
        return
