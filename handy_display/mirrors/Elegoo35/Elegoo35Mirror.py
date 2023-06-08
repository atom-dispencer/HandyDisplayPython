import threading
import time

from handy_display.mirrors.IMirror import IMirror
from handy_display.mirrors.Elegoo35.Constants import *

# https://pinout.xyz/pinout/spi
# https://pypi.org/project/spidev/
try:
    from spidev import SpiDev
    # import Adafruit_PureIO.spi

    print("Elegoo35 - Successfully imported spidev: " + str(SpiDev))
except ImportError:
    print("Elegoo35 - Cannot use physical mirrors because spidev is not present!")
    exit(-10)

# https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
try:
    from RPi import GPIO

    print("Elegoo35 - Successfully imported RPi: " + str(GPIO))
except ImportError:
    print("Elegoo35 - Failed to import RPi.GPIO")
    exit(-11)
except RuntimeError:
    print("Elegoo35 - Failed to initialise RPi.GPIO")
    exit(-12)

THREAD_NAME = "tft_lcd_spi_thread"
CLK_HZ = int(125e3)  # 125kHz


class Elegoo35Mirror(IMirror):

    def __init__(self, width, height):
        print("Creating physical mirrors " + str(width) + "x" + str(height))
        super().__init__(width, height)

        self.pushing = False
        self.spi_thread = None

        print("Setting up GPIO")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Pins.TP_IRQ, GPIO.IN)
        GPIO.setup(Pins.RST, GPIO.OUT)
        GPIO.add_event_detect(Pins.TP_IRQ, GPIO.RISING, bouncetime=500)

        print("Starting SpiDev")
        self.lcd_spi = SpiDev()

        self.tp_spi = SpiDev()
        self.tp_spi.open(Devices.LCD_TP_BUS, Devices.TP_DEVICE)
        self.tp_spi.max_speed_hz = 2_000_000  # 2MHz (max 2.5MHz)

        # Reset the screen to a functional state in case I screw something up
        # ctrl_byte = bytearray()
        # ctrl_byte.append(
        #     get_control_byte(
        #         Channels.X_POS,
        #         Conversions.BIT_12,
        #         ReferenceInput.DIFFERENTIAL,
        #         PowerMode.POWER_DOWN_BETWEEN
        #     )
        # )
        # self.touch_panel_spi.writebytes(ctrl_byte)

    # --------------------------------------------- IScreen stuff ---------------------------------------------

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    def process_events(self):
        # if GPIO.event_detected(Pins.TP_IRQ):
           #  self.process_tft_touch()
        if self.touched():
            print(self.get_touch_position())

    def ready_for_next_frame(self):
        return self.spi_thread is None or not self.spi_thread.is_alive()

    def next_frame(self, pixel_array_3d):
        if self.ready_for_next_frame():
            self.spi_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.push_pixels_spi(pixel_array_3d))
            # self.spi_thread.start()

    def shutdown(self):
        print("Shutting down Elegoo35...")
        GPIO.cleanup()

    def touched(self, touch_sensitivity=245):
        reply = self.tp_spi.xfer2([0b10111000, 0b00000000, 0b00000000])
        z1 = reply[2] >> 7 | reply[1] << 1
        reply = self.tp_spi.xfer2([0b11001000, 0b00000000, 0b00000000])
        z2 = reply[2] >> 7 | reply[1] << 1
        if z2 - z1 < touch_sensitivity:
            return True
        else:
            return False

    def get_touch_position(self):

        yoffset = 1
        xoffset = 1
        yscale = 1
        xscale = 1

        if self.touched():
            reply = self.tp_spi.xfer2([0b11010000, 0b00000000, 0b00000000])
            y = int((4095 - (reply[1] << 5 | reply[2] >> 3) - yoffset) // yscale)
            if y < 0:
                y = 0
            if y > 239:
                y = 239
            print("ReplyY", reply)
            reply = self.tp_spi.xfer2([0b10010000, 0b00000000, 0b00000000])
            x = (((reply[1] << 5 | reply[2] >> 3) - xoffset) // xscale)
            x = int(x)
            if x < 0:
                x = 0
            if x > 319:
                x = 319
            print("ReplyX", reply)
        else:
            x = 0
            y = 0
        return [x, y]

    # --------------------------------------------- SPI things ---------------------------------------------

    def reset(self):
        for i in range(2):
            GPIO.output(Pins.RST, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(Pins.RST, GPIO.LOW)
            time.sleep(0.05)

    def push_pixels_spi(self, pixel_array_3d):
        #  print("Pushing pixels!")
        pass
