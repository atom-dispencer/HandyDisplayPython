import os
import pygame
from pygame import Surface

from handy_display import Options
from handy_display.widgets.IWidget import IWidget


class PygameGUI:

    # noinspection PyTypeChecker
    def __init__(self, mirror_in, options: Options):
        print("Creating PygameGUI with mirror " + str(mirror_in))

        # Configure drivers
        if options.headless:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'

        # Setup instance variables
        self.mirror = mirror_in
        self.running: bool = False
        self.screen_surface: Surface = None  # The pygame surface backing the GUI
        self.widgets = {}
        self.current_widget_name = None
        self.next_widget_name = None
        self.running = True

        self.mirror.add_touch_callback("PygameGUI_default", lambda x, y: self.click_event(x, y))

        # Initialise pygame
        try:
            pygame.init()
            self.screen_surface = pygame.display.set_mode((self.mirror.width, self.mirror.height))
            pygame.display.set_caption("Handy Display (PygameGUI)")
        except Exception as ex:
            print()
            print("An error occurred while setting up the pygame GUI.")
            print()
            print(ex)
            print()
            print("If you are running in a headless environment, "
                  "make sure you specified the 'headless' option to __main__.py")
            quit(-100)

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
                print("Swapping widget '{old}' for '{new}'".format(old=self.current_widget_name,
                                                                   new=self.next_widget_name))

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

        if self.mirror.ready_for_next_frame():
            # Copy the pixels to a new buffer to avoid race conditions!
            array3d = pygame.surfarray.array3d(self.screen_surface)
            self.mirror.next_frame(array3d)
        self.mirror.process_events()

        # Flip the display buffers (or something like that)
        pygame.display.flip()

    def draw_overlay(self):
        pygame.draw.rect(self.screen_surface, (0, 0, 0), (0, 50, 50, 50))

    def shutdown(self):
        print("Killing PygameGUI")
        self.running = False

        if self.mirror is not None:
            self.mirror.shutdown()
        pygame.quit()
