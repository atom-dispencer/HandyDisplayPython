import datetime

from handy_display.PygameLoaderHelper import *
from handy_display.widgets.IWidget import IWidget

ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)


class OverlayWidget(IWidget):
    NAME = "overlay"
    DEFAULT_CONFIG = {
        "datetime_format": "%a %d/%m/%y - %H:%M:%S"
    }

    def __init__(self, gui):
        super().__init__(gui, self.NAME, self.DEFAULT_CONFIG)

        self.display_datetime = "??:?? - ??/??/??"

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        datetime_str = datetime.datetime.now().strftime(self.config["datetime_format"])
        if not self.display_datetime == datetime_str:
            self.display_datetime = datetime_str
            self.gui.make_dirty()

    def draw(self, surf: pygame.surface.Surface):
        time_render = ROBOTO_16.render(self.display_datetime, True, (0, 0, 0))
        surf.blit(time_render, (0, 0))

    def on_hide(self):
        pass
