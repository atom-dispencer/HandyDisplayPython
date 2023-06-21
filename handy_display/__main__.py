import cProfile
import platform
import sys

from handy_display.Options import Options, MirrorType
from handy_display.PygameGUI import PygameGUI
from handy_display.widgets.OverlayWidget import *
from handy_display.widgets.TestWidget import *
from handy_display.widgets.WeatherWidget import *

#
def get_relevant_mirror(mirror_type):
    if mirror_type == MirrorType.NO_MIRROR:
        print("Using PygameOnlyMirror...")
        import handy_display.mirrors.PygameOnlyMirror

        return handy_display.mirrors.PygameOnlyMirror.PygameOnlyMirror()
    if mirror_type == MirrorType.TFT_LCD_XPT2046_ILI9486:
        print("Using TFT_LCD_XPT2046_ILI9486_Mirror...")
        import handy_display.mirrors.Elegoo35.Elegoo35Mirror

        return handy_display.mirrors.Elegoo35.Elegoo35Mirror.Elegoo35Mirror(480, 320)


# Main loop
def start():
    print("")
    print("Starting up handy display...")
    print("Running on platform: " + str(platform.platform()))
    print("")

    options = Options(sys.argv)

    mirror = get_relevant_mirror(options.screen_type)
    gui = PygameGUI(mirror, options)

    gui.add_widget(OverlayWidget.NAME, OverlayWidget(gui))
    gui.add_widget(TestWidget.NAME, TestWidget(gui))
    gui.add_widget(WeatherWidget.NAME, WeatherWidget(gui))

    gui.request_widget("test")

    # https://stackoverflow.com/questions/6087484/how-to-capture-pygame-screen
    # https://realpython.com/pygame-a-primer/
    # https://stackoverflow.com/questions/34347973/run-pygame-without-a-window-gui

    print("Startup done!")
    print("")

    try:
        while gui._running:
            gui.refresh()
    except KeyboardInterrupt:
        print("Interrupted by keyboard. Shutting down...")
    finally:
        mirror.shutdown()

    print("Exited")


# Start execution
if __name__ == "__main__":
    try:
        # cProfile.run('start()')
        start()
    except KeyboardInterrupt:
        print("")
        print("Interrupted. Shutting down.")
else:
    print("The HandyDisplay is not being run as __main__ (not starting)")
