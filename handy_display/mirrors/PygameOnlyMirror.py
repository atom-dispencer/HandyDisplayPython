from handy_display.mirrors.IMirror import IMirror


class PygameOnlyMirror(IMirror):

    def __init__(self, gui):
        super().__init__(480, 320, gui)

    def refresh(self, pixels3d):
        pass

    def shutdown(self):
        pass

    def __str__(self):
        return "PygameOnlyMirror(" + str((480, 320)) + ")"
