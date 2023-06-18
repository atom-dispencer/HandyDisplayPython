from __future__ import annotations

from abc import abstractmethod

import pygame.event


class IWidget:

    def __init__(self, gui):
        self.gui = gui

    @abstractmethod
    def on_show(self):
        pass

    @abstractmethod
    def update(self, events: list[pygame.event.Event]):
        pass

    @abstractmethod
    def on_hide(self):
        pass
