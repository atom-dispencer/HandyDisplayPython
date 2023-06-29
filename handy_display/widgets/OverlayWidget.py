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
        "datetime_format": "%a %d/%m/%y - %H:%M:%S",
        "widget_order": ["test", "weather"]
    }

    def __init__(self, gui):
        super().__init__(gui, self.INTERNAL_NAME, self.DISPLAY_NAME, self.DEFAULT_CONFIG)
        self.verify_order()

        self.display_datetime = "??:?? - ??/??/??"

    def verify_order(self):
        lst = self.config["widget_order"]
        adj = [lst[x] for x in range(len(lst) - 1) if lst[x] == lst[x + 1]]
        if len(adj) > 0 or lst[0] == lst[len(lst) - 1]:
            raise Exception("The given widget order contains neighboring duplicate elements. "
                            "This may cause unexpected behaviour. "
                            "For example: ['test', 'weather', 'weather'], or ['test', 'weather', 'test']")

    def on_show(self):
        pass

    def handle_events(self, events: list[pygame.event.Event]):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.check_clicks(ev.pos)

        datetime_str = datetime.datetime.now().strftime(self.config["datetime_format"])
        if not self.display_datetime == datetime_str:
            self.display_datetime = datetime_str
            self.gui.make_dirty()

    def check_clicks(self, pos):
        x, y = pos
        last_rect_left = align_left_toggle.last_rect
        last_rect_right = align_right_toggle.last_rect
        if last_rect_left is not None and last_rect_left.collidepoint(x, y):
            self.next_widget(forwards=False)
        elif last_rect_right is not None and last_rect_right.collidepoint(x, y):
            self.next_widget(forwards=True)

    def next_widget(self, forwards: bool = True):
        current = self.gui.current_widget_name

        order: list = self.config["widget_order"]

        target_index = 0
        if current in order:
            target_index = order.index(current) + (1 if forwards else -1)

        if target_index >= len(order):
            target_index = 0
        elif target_index < 0:
            target_index = len(order) - 1

        next_name = order[target_index]
        self.gui.request_widget(next_name)

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
