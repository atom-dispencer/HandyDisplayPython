import os
import time

import PIL.Image
import pygame
from pygame import Surface

from handy_display import Options
from handy_display.mirrors.IMirror import IMirror
from handy_display.widgets.IWidget import IWidget


class PygameGUI:
    def __init__(self, mirror_in, options: Options):
        print("Creating PygameGUI with mirror " + str(mirror_in))

        # Configure drivers
        if options.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

        # Setup instance variables
        self.mirror: IMirror = mirror_in
        self._running: bool = False
        # The pygame surface backing the GUI
        self.screen_surface: Surface = None
        self._widgets: dict[str, IWidget] = {}
        self._current_widget_name = None
        self.next_widget_name = None
        self._running = True
        self.overlay_dirty = True

        self.last_refresh_time = 0.0
        self.last_refresh_length = 0.0
        self.last_draw_length = 0.0

        self.last_touch_epoch_secs = 0
        self.touch_timeout_secs = 0.5

        self._dirty = True

        # Initialise pygame
        try:
            pygame.init()
            self.screen_surface = pygame.display.set_mode(
                (self.mirror.width, self.mirror.height)
            )
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

    @property
    def current_widget_name(self):
        return self._current_widget_name

    @property
    def widgets(self):
        return self._widgets

    def add_widget(self, name: str, widget: IWidget):
        self._widgets[name] = widget

    def request_widget(self, name: str):
        f"""
        Queue the given {IWidget} for display.
        The widget will change at the start of the next PygameGUI refresh.
        :param name: The name of the widget in {self._widgets} to switch to
        :return:
        """
        self.next_widget_name = name

    def get_current_widget(self) -> IWidget:
        f"""
        Get the currently displayed {IWidget}.
        """
        return (
            self._widgets[self._current_widget_name]
            if self._current_widget_name is not None
            else None
        )

    def make_dirty(self):
        f"""
        Notify the PygameGUI that the screen must be redrawn.
        Mostly called by {IWidget}s when their contents change.
        Cannot be uncalled, and {self._dirty} is NOT for widgets to set directly.
        
        :return: Nothing.
        """
        self._dirty = True

    def refresh(self):
        """
        Do the next update and rendering cycle.
        Very complicated method.
        Updates refresh length with the maximum value of each seen in the
        last second.

        1) Switch in the next queued widget
        2) Handle events in the GUI itself
        3) Handle events in the overlay, then current widget
        4) Draw the current widget, then the overlay over it
        5) Send the screen to the mirror
        :return: Nothing.
        """
        refresh_start = time.time()
        if not self._running:
            return

        #
        # Switch in the next queued widget
        #
        if self.next_widget_name is not None:
            if self.next_widget_name in self._widgets.keys():
                print("Swapping widget '{old}' for '{new}'"
                      .format(old=self._current_widget_name, new=self.next_widget_name))

                old = self.get_current_widget()
                if old is not None:
                    old.on_hide()
                self._current_widget_name = self.next_widget_name

                new = self.get_current_widget()
                new.on_show()
                self.next_widget_name = None
            else:
                print("No known widget of name {w}".format(w=self.next_widget_name))
                self.next_widget_name = None

        #
        # Handle events
        #
        events: list[pygame.event.Event] = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                self.shutdown()
                return  # Prevent further pygame calls

        #
        # Update the GUI
        #
        self._widgets["overlay"].handle_events(events)
        self.get_current_widget().handle_events(events)
        if self._dirty:
            self.get_current_widget().draw(self.screen_surface)
            self._widgets["overlay"].draw(self.screen_surface)

        #
        # Send the new screen to the mirror
        #
        if self.mirror.ready_for_next_frame():
            draw_start = time.time()

            # Copy the pixels to a new buffer to avoid race conditions!
            img_bytes = pygame.image.tobytes(self.screen_surface, "RGB")
            pil_img = PIL.Image.frombytes(
                "RGB", (self.mirror.width, self.mirror.height), img_bytes
            )
            self.mirror.next_frame(pil_img)

            self.last_draw_length = time.time() - draw_start
        self.mirror.process_events()

        # Flip the display buffers (or something like that)
        pygame.display.flip()

        length = time.time() - refresh_start
        if length > self.last_refresh_length or time.time() - self.last_refresh_time > 1:
            self.last_refresh_time = time.time()
            self.last_refresh_length = length

    def shutdown(self):
        """
        Close up shop and take out the trash.
        :return: Nothing.
        """
        print("Killing PygameGUI")
        self._running = False

        if self.mirror is not None:
            self.mirror.shutdown()
        pygame.quit()
