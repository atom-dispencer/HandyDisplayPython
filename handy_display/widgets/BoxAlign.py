from enum import Enum

import numpy
import pygame
from pygame import Surface


class Origin(Enum):
    TOP_LEFT = 0
    TOP_CENTRE = 1
    TOP_RIGHT = 2
    CENTRE_LEFT = 3
    CENTRE = 4
    CENTRE_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTRE = 7
    BOTTOM_RIGHT = 8


def get_local_box_origin_point(dimensions: tuple[float, float], origin: Origin):
    w, h = dimensions
    match origin:
        case Origin.TOP_LEFT:
            return 0, 0
        case Origin.TOP_CENTRE:
            return w / 2, 0
        case Origin.TOP_RIGHT:
            return w, 0

        case Origin.CENTRE_LEFT:
            return 0, h / 2
        case Origin.CENTRE:
            return w / 2, h / 2
        case Origin.CENTRE_RIGHT:
            return w, h / 2

        case Origin.BOTTOM_LEFT:
            return 0, h
        case Origin.BOTTOM_CENTRE:
            return w / 2, h
        case Origin.BOTTOM_CENTRE:
            return w, h


class BoxAlign:
    """Class for aligning boxes on the screen.
    Uses a 'builder' pattern and methods are chainable for ease-of-use.
    """

    def __init__(self,
                 container: tuple[float, float, float, float],
                 local_origin=Origin.TOP_LEFT,
                 global_origin=(0, 0),
                 transform=(0, 0)):
        """Create a new box alignment.
        Only the container (X,Y,W,H) is required here,
        e.g. to centre on 0,0: `(0, 0) + (width, height)` or `(0, 0, width, height)`
        Best practise is to call chainable methods for configuration."""
        self._container = None
        self._local_origin = None
        self._global_origin = None
        self._transform = None
        self._last_rect = None
        self.container(container)
        self.local_origin(local_origin)
        self.global_origin(global_origin)
        self.transform(transform)

    @property
    def last_rect(self) -> pygame.Rect:
        return self._last_rect

    def container(self, container: tuple[float, float, float, float]):
        """Set the container within which objects can be aligned"""
        self._container = container
        return self

    def local_origin(self, origin: Origin):
        """Set the origin point (the point to be considered as the 'centre')
        of objects which will be aligned."""
        self._local_origin = origin
        return self

    def global_origin(self, origin: Origin | tuple[float, float]):
        """Set the world origin, from which all transformations are calculated."""
        self._global_origin = origin
        return self

    def transform(self, vector: tuple[float, float]):
        """Transform the box by the given vector"""
        self._transform = vector
        return self

    def apply_to(self, box: Surface | tuple[float, float]) -> tuple[float, float]:
        """Apply this alignment.
        :param box: The box to align
        :return: The X,Y position the box should be moved to, to be correctly aligned.
        """
        if isinstance(box, Surface):
            box = box.get_size()

        global_origin_point = self._global_origin
        if global_origin_point in Origin:
            global_origin_point = get_local_box_origin_point(self._container[-2:], global_origin_point)

        relative = numpy.multiply(-1, get_local_box_origin_point(box, self._local_origin))
        combined = [
            self._container[:2],
            global_origin_point,
            self._transform,
            relative
        ]
        pos = numpy.sum(combined, axis=0)

        self._last_rect = pygame.Rect(pos, box)
        return tuple(pos)
