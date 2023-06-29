import datetime

import numpy

from handy_display.PygameLoaderHelper import *
from handy_display.widgets.BoxAlign import BoxAlign, Origin
from handy_display.widgets.IWidget import IWidget

ROBOTO_16 = font("Roboto/Roboto-Black.ttf", 16)

BAR_BOX = image("overlay/bar_box.bmp", 480, 28)
align_bar_time: BoxAlign = BoxAlign(
    container=(0, 0) + BAR_BOX.get_size(),
    local_origin=Origin.CENTRE_LEFT,
    global_origin=Origin.CENTRE_LEFT,
    transform=(5, 0)
)
align_bar_spf: BoxAlign = BoxAlign(
    container=(0, 0) + BAR_BOX.get_size(),
    local_origin=Origin.CENTRE_RIGHT,
    global_origin=Origin.CENTRE_RIGHT,
    transform=(-5, 0)
)
align_bar_name: BoxAlign = BoxAlign(
    container=(0, 0) + BAR_BOX.get_size(),
    local_origin=Origin.CENTRE,
    global_origin=Origin.CENTRE,
    transform=(0, 0)
)

RIGHT_TOGGLE = image("overlay/right_toggle.bmp", 40, 74)
align_right_toggle: BoxAlign = BoxAlign(
    container=(0, 0, 0, 0),
    local_origin=Origin.CENTRE_RIGHT,
    global_origin=Origin.CENTRE_RIGHT
)

LEFT_TOGGLE = image("overlay/left_toggle.bmp", 40, 74)
align_left_toggle: BoxAlign = BoxAlign(
    container=(0, 0, 0, 0),
    local_origin=Origin.CENTRE_LEFT,
    global_origin=Origin.CENTRE_LEFT
)


class OverlayWidget(IWidget):
    INTERNAL_NAME = "overlay"
    DISPLAY_NAME = "Overlay"
    DEFAULT_CONFIG = {
        "datetime_format": "%a %d/%m/%y - %H:%M:%S"
    }

    def __init__(self, gui):
        super().__init__(gui, self.INTERNAL_NAME, self.DISPLAY_NAME, self.DEFAULT_CONFIG)

        self.display_datetime = "??:?? - ??/??/??"

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        datetime_str = datetime.datetime.now().strftime(self.config["datetime_format"])
        if not self.display_datetime == datetime_str:
            self.display_datetime = datetime_str
            self.gui.make_dirty()

    def draw(self, surf: pygame.surface.Surface):

        # Top bar
        surf.blit(BAR_BOX, (0, 0))

        text_render = ROBOTO_16.render(self.display_datetime, True, (0, 0, 0))
        pos = align_bar_time.apply_to(text_render)
        surf.blit(text_render, pos)

        text_render = ROBOTO_16.render("0.00011"[:5], True, (0, 0, 0))
        pos = align_bar_spf.apply_to(text_render)
        surf.blit(text_render, pos)

        name = self.gui.get_current_widget().display_name
        text_render = ROBOTO_16.render(name, True, (0, 0, 0))
        pos = align_bar_name.apply_to(text_render)
        surf.blit(text_render, pos)

        # Toggles
        left_pos = align_left_toggle.container((0, 0) + surf.get_size()).apply_to(LEFT_TOGGLE.get_size())
        surf.blit(LEFT_TOGGLE, left_pos)
        right_pos = align_right_toggle.container((0, 0) + surf.get_size()).apply_to(RIGHT_TOGGLE.get_size())
        surf.blit(RIGHT_TOGGLE, right_pos)

    def on_hide(self):
        pass
