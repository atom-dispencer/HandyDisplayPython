import time

import datetime

import pygame.surface

from handy_display.widgets.IWidget import IWidget
from handy_display.PygameLoaderHelper import *

ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)


class OverlayWidget(IWidget):

    def __init__(self, gui):
        super().__init__(gui)

        self.display_datetime = "??:?? - ??/??/??"

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):

        datetime_str = datetime.datetime.now().strftime("%a %d/%m/%y - %H:%M:%S")
        if not self.display_datetime == datetime_str:
            self.display_datetime = datetime_str
            self.gui.make_dirty()

    def draw(self, surf: pygame.surface.Surface):
        time_render = ROBOTO_16.render(self.display_datetime, True, (0, 0, 0))
        surf.blit(time_render, (0, 0))

    def on_hide(self):
        pass