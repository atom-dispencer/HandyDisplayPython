from __future__ import annotations

from abc import abstractmethod
from pygame import Surface


class IWidget:

    def __init__(self, gui):
        self.gui = gui

    @abstractmethod
    def on_show(self):
        pass

    @abstractmethod
    def draw(self, screen_surface: Surface):
        pass

    @abstractmethod
    def on_hide(self):
        pass

    @abstractmethod
    def click_event(self, x: int, y: int):
        pass
