import platform
import sys

from Options import Options, MirrorType
from PygameGUI import PygameGUI
from widgets.TestWidget import TestWidget
from widgets.WeatherWidget import WeatherWidget


#
def get_relevant_mirror(mirror_type):
    if mirror_type == MirrorType.NO_MIRROR:
        from mirrors.PygameOnlyMirror import PygameOnlyMirror
        print("Using PygameOnlyMirror...")
        return PygameOnlyMirror()
    if mirror_type == MirrorType.TFT_LCD_XPT2046_ILI9486:
        from mirrors.TFT_LCD_XPT2046_ILI9486_Mirror import Mirror
        print("Using TFT_LCD_XPT2046_ILI9486_Mirror...")
        return Mirror(0, 0, 480, 320)


# Main loop
def start():
    print("")
    print("Starting up handy display...")
    print("Running on platform: " + str(platform.platform()))
    print("")

    options = Options(sys.argv)
    mirror = get_relevant_mirror(options.screen_type)

    gui = PygameGUI(mirror, options)

    gui.widgets["test"] = TestWidget(gui)
    gui.widgets["weather"] = WeatherWidget(gui)

    gui.request_widget("test")

    # https://stackoverflow.com/questions/6087484/how-to-capture-pygame-screen
    # https://realpython.com/pygame-a-primer/
    # https://stackoverflow.com/questions/34347973/run-pygame-without-a-window-gui

    print("Startup done!")
    print("")
    while gui.running:
        gui.refresh()

    print("Exited")


# Start execution
if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        print("")
        print("Interrupted. Shutting down.")
else:
    print("The HandyDisplay is not being run as __main__ (not starting)")
