from __future__ import annotations

from abc import abstractmethod


class IWidget:

    def __init__(self, gui):
        self.gui = gui

    @abstractmethod
    def on_show(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def on_hide(self):
        pass

    @abstractmethod
    def click_event(self, x: int, y: int):
        pass
