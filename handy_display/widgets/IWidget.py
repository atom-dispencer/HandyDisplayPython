from abc import abstractmethod
from enum import Enum

import pygame.event

from handy_display.widgets.Config import Config


class IWidget:

    def __init__(self, gui, name: str, default_config: dict[str, object]):
        self.gui = gui
        self.name: str = name
        self.config: Config = Config(name, default_config)

    @abstractmethod
    def on_show(self):
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]):
        pass

    @abstractmethod
    def draw(self, screen_surface: pygame.surface.Surface):
        pass

    @abstractmethod
    def on_hide(self):
        pass


class Anchor(Enum):
    TOP_LEFT = 0
    TOP_CENTRE = 1
    TOP_RIGHT = 2
    CENTRE_LEFT = 3
    CENTRE = 4
    CENTRE_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTRE = 7
    BOTTOM_RIGHT = 8
