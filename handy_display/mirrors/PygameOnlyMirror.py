from handy_display.mirrors.IMirror import IMirror


class PygameOnlyMirror(IMirror):

    def __init__(self):
        super().__init__(480, 320)
        self.needs_new_pixels = False

    def process_events(self):
        pass

    def ready_for_next_frame(self) -> bool:
        return False

    def next_frame(self, pixel_array_3d):
        pass

    def shutdown(self):
        pass

    def __str__(self):
        return "PygameOnlyMirror(" + str((480, 320)) + ")"
