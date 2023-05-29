from abc import abstractmethod

from pygame import Surface


class IWidget:

    @abstractmethod
    def draw(self, screen_surface: Surface):
        pass

    @abstractmethod
    def click_event(self, x: int, y: int):
        pass
