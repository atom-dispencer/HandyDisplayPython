import threading

from handy_display.mirrors.IMirror import IMirror

# https://pinout.xyz/pinout/spi
# https://pypi.org/project/spidev/
try:
    from spidev import SpiDev

    print("Successfully imported spidev: " + str(SpiDev))
except ImportError:
    print("Cannot use physical mirrors because spidev is not present!")
    exit(-10)

# https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
try:
    from RPi import GPIO

    print("Successfully imported RPi: " + str(GPIO))
except ImportError:
    print("Failed to import RPi.GPIO")
    exit(-11)
except RuntimeError:
    print("Failed to initialise RPi.GPIO")
    exit(-12)

# The pi has 1 bus (#0) and 2 devices (CE0 and CE1)

# GPIO pin 22 is the TP_IRQ (Touch Panel Interrupt)
TP_IRQ = 22

THREAD_NAME = "tft_lcd_spi_thread"


class Mirror(IMirror):

    def __init__(self, width, height, gui):
        print("Creating physical mirrors " + str(width) + "x" + str(height))
        super().__init__(width, height, gui)

        self.pushing = False
        self.spi_thread = None

        print("Setting up GPIO")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TP_IRQ, GPIO.IN)
        GPIO.add_event_detect(TP_IRQ, GPIO.RISING, bouncetime=500)

        print("Testing SpiDev")
        self.spi = SpiDev()
        self.spi.open(0, 0)
        message = [0x00]
        self.spi.xfer(message)

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    def refresh(self, pixels3d):
        if GPIO.event_detected(TP_IRQ):
            self.gui.click_event(0, 0)

        # If the thread is None, or is not alive (has died or finished)
        if self.spi_thread is None or not self.spi_thread.is_alive():
            self.spi_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.push_pixels_spi(pixels3d))
            self.spi_thread.start()

    def push_pixels_spi(self, pixels3d):
        print("Pushing pixels: " + pixels3d)

    def shutdown(self):
        print("Shutting down physical mirrors...")

    def click_callback(self, click_event):
        self.screen_touched(click_event.x, click_event.y)
