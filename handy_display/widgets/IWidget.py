from __future__ import annotations

from abc import abstractmethod
from enum import Enum
import numpy

import pygame.event


def relative(pos: tuple[int, int], to: tuple[int, int]):
    return tuple(numpy.add(pos, to))


def centred(on_pos: tuple[int, int], dimensions: tuple[int, int]):
    dimensions = numpy.floor_divide(dimensions, 2)
    return tuple(numpy.subtract(on_pos, dimensions))


def anchorpoint(anchor: Anchor, dimensions: tuple[int, int]) -> tuple[int, int]:
    w, h = dimensions
    match anchor:
        case Anchor.TOP_LEFT:
            return 0, 0
        case Anchor.TOP_CENTRE:
            return w // 2, 0
        case Anchor.TOP_RIGHT:
            return w, 0

        case Anchor.CENTRE_LEFT:
            return 0, h // 2
        case Anchor.CENTRE:
            return w // 2, h // 2
        case Anchor.CENTRE_RIGHT:
            return w, h // 2

        case Anchor.BOTTOM_LEFT:
            return 0, h
        case Anchor.BOTTOM_CENTRE:
            return w // 2, h
        case Anchor.BOTTOM_CENTRE:
            return w, h


class IWidget:

    def __init__(self, gui):
        self.gui = gui

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
