import random

import pygame.event
from pygame.sprite import Group

from handy_display.sprite.TestSprite import TestSprite
from handy_display.widgets.IWidget import IWidget


class TestWidget(IWidget):
    INTERNAL_NAME = "test"
    DISPLAY_NAME = "Test"
    DEFAULT_CONFIG = {
        "": ""
    }

    def __init__(self, gui):
        super().__init__(gui, self.INTERNAL_NAME, self.DISPLAY_NAME , self.DEFAULT_CONFIG)
        self.bg_color = (255, 255, 255)

        self.group = Group()
        self.test = TestSprite(50, 50, 50)
        self.group.add(self.test)

    def on_show(self):
        print("Showing test widget!")

    def handle_events(self, events: list[pygame.event.Event]):

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.change_to_weather(ev.pos)

        return

    def draw(self, screen_surface: pygame.surface.Surface):
        self.gui.screen_surface.fill(self.bg_color)
        self.group.draw(self.gui.screen_surface)

    def on_hide(self):
        print("Removing test widget")

    def change_to_weather(self, pos: tuple[int, int]):
        (x, y) = pos
        print("TestWidget clicked at ({x},{y})".format(x=x, y=y))
        if self.test.rect.collidepoint(x, y):
            print("Switching to Weather!")
            self.bg_color = tuple(random.randint(0, 255) for _ in range(3))
            self.test.rect.x = random.randint(50, 150)
            self.test.rect.y = random.randint(50, 150)
            self.test.rect.w = random.randint(50, 150)
            self.test.rect.h = random.randint(50, 100)
            self.gui.request_widget("weather")
        return
