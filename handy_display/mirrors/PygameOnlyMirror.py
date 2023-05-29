from handy_display.mirrors.IMirror import IMirror


class PygameOnlyMirror(IMirror):

    requesting_frame = False

    def __init__(self):
        super().__init__(480, 320)

    def push_frame_data(self, pixels3d):
        pass

    def shutdown(self):
        pass

    def __str__(self):
        return "PygameOnlyMirror(" + str((480, 320)) + ")"
