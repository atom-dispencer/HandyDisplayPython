import pygame
from pygame import Surface

from handy_display.widgets.WeatherWidget import WeatherWidget
from widgets.IWidget import IWidget
from widgets.TestWidget import TestWidget


class PygameGUI:

    # noinspection PyTypeChecker
    def __init__(self, mirror_in):
        print("Creating PygameGUI with mirror " + str(mirror_in))

        self.mirror = mirror_in
        self.running: bool = False
        self.screen_surface: Surface = None  # The pygame surface backing the GUI
        self.widgets = {}
        self.current_widget_name = None
        self.next_widget_name = None

        self.mirror.add_touch_callback("PygameGUI_default", lambda x, y: self.click_event(x, y))

        pygame.init()
        self.screen_surface = pygame.display.set_mode((self.mirror.width, self.mirror.height))
        pygame.display.set_caption("Handy Display (PygameGUI)")

        self.next_widget_name = None
        self.running = True

    def click_event(self, x: int, y: int):
        # Check overlay collisions first
        self.get_current_widget().click_event(x, y)

    def request_widget(self, name: str):
        self.next_widget_name = name

    def get_current_widget(self) -> IWidget:
        return self.widgets[self.current_widget_name] if self.current_widget_name is not None else None

    def refresh(self):
        if not self.running:
            return

        # Switch in the next queued widget
        if self.next_widget_name is not None:
            if self.next_widget_name in self.widgets.keys():
                print("Swapping widget '{old}' for '{new}'".format(old=self.current_widget_name, new=self.next_widget_name))

                old = self.get_current_widget()
                if old is not None:
                    old.on_hide()
                self.current_widget_name = self.next_widget_name

                new = self.get_current_widget()
                new.on_show()
                self.next_widget_name = None
            else:
                print("No known widget of name {w}".format(w=self.next_widget_name))
                self.next_widget_name = None

        # Respond to events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.shutdown()
                return  # Prevent further pygame calls
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                self.click_event(position[0], position[1])

        self.get_current_widget().draw(self.screen_surface)
        self.draw_overlay()

        # Flip the display buffers (or something like that)
        pygame.display.flip()

        # Push to the mirror
        if self.mirror.requesting_frame:
            pixels3d = pygame.surfarray.pixels3d(self.screen_surface)
            self.mirror.push_frame_data(pixels3d)

    def draw_overlay(self):
        pygame.draw.rect(self.screen_surface, (0, 0, 0), (0, 50, 50, 50))

    def shutdown(self):
        print("Killing PygameGUI")
        self.running = False

        if self.mirror is not None:
            self.mirror.shutdown()
        pygame.quit()
