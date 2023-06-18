import os
import time

import PIL.Image
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
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

        # Setup instance variables
        self.mirror = mirror_in
        self.running: bool = False
        # The pygame surface backing the GUI
        self.screen_surface: Surface = None
        self.widgets = {}
        self.current_widget_name = None
        self.next_widget_name = None
        self.running = True

        self.last_touch_epoch_secs = 0
        self.touch_timeout_secs = 0.5

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

    def request_widget(self, name: str):
        self.next_widget_name = name

    def get_current_widget(self) -> IWidget:
        return (
            self.widgets[self.current_widget_name]
            if self.current_widget_name is not None
            else None
        )

    def refresh(self):
        if not self.running:
            return

        #
        # Switch in the next queued widget
        #
        if self.next_widget_name is not None:
            if self.next_widget_name in self.widgets.keys():
                print("Swapping widget '{old}' for '{new}'"
                      .format(old=self.current_widget_name, new=self.next_widget_name))

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

        #
        # Handle events
        #
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                events.remove(ev)
                self.shutdown()
                return  # Prevent further pygame calls

            elif ev.type == pygame.KEYDOWN:
                events.remove(ev)

                if ev.key == pygame.K_SPACE:
                    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                               button=1,
                                               pos=(self.mirror.width / 2, self.mirror.height / 2)
                                               )
                    pygame.event.post(event)

                    event = pygame.event.Event(pygame.MOUSEBUTTONUP,
                                               button=1,
                                               pos=(self.mirror.width / 2, self.mirror.height / 2)
                                               )
                    pygame.event.post(event)

        #
        # Update the GUI
        #
        self.get_current_widget().update(events)
        self.draw_overlay()

        #
        # Send the new screen to the mirror
        #
        if self.mirror.ready_for_next_frame():
            # Copy the pixels to a new buffer to avoid race conditions!
            img_bytes = pygame.image.tobytes(self.screen_surface, "RGB")
            pil_img = PIL.Image.frombytes(
                "RGB", (self.mirror.width, self.mirror.height), img_bytes
            )
            self.mirror.next_frame(pil_img)
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
