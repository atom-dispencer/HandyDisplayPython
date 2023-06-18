import numbers
import threading
import time

import pygame
from PIL import Image

from handy_display.mirrors.Elegoo35.ILI9486 import ILI9486
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

MAX_XPT_RTN: int = 0xFFF  # 4095
HEIGHT_PX: int = 320
WIDTH_PX: int = 480
X_SCALE: float = WIDTH_PX / MAX_XPT_RTN
Y_SCALE: float = WIDTH_PX / MAX_XPT_RTN
X_OFFSET: int = 0
Y_OFFSET: int = 0


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
        GPIO.setup(Pins.LCD_RS, GPIO.OUT)

        print("Starting SpiDev")
        self.tp_spi = SpiDev()
        self.tp_spi.open(Devices.LCD_TP_BUS, Devices.TP_DEVICE)
        self.tp_spi.max_speed_hz = 2_000_000  # 2MHz (max 2.5MHz)

        self.last_touch_nanos = 0
        self.touch_timeout_nanos = 0.5e9

        lcd_spi = SpiDev()
        self.tp_spi.open(Devices.LCD_TP_BUS, Devices.TP_DEVICE)
        self.tp_spi.max_speed_hz = 2_000_000  # 2MHz (max 2.5MHz)
        self.lcd = ILI9486(data_cmd=Pins.LCD_RS, spi=lcd_spi, rst=Pins.RST)
        self.lcd.send_init_sequence()

    # --------------------------------------------- IScreen stuff ---------------------------------------------

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    def process_events(self):
        if self.touched():
            pos = self.get_touch_position()
            event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
            pygame.event.post(event)

    def ready_for_next_frame(self):
        return self.spi_thread is None or not self.spi_thread.is_alive()

    def next_frame(self, pixel_array_3d):
        if self.ready_for_next_frame():
            self.spi_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.push_pixels_spi(pixel_array_3d))
            self.spi_thread.start()

    def shutdown(self):
        print("Shutting down Elegoo35...")
        # TODO Correct XPT/LCD/E35 mirror shutdown
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

    #
    # Reply is of format 00000000 0....... .....000 and has 12 relevant bits
    #
    def get_touch_position(self):

        if self.touched():
            # For each, concatenate the two significant reply bytes, subtract an offset and scale the result, and clamp

            reply = self.tp_spi.xfer2([0b11010000, 0b00000000, 0b00000000])
            y = int(((reply[1] << 5 | reply[2] >> 3) * Y_SCALE) - Y_OFFSET)
            if y < 0:
                y = 0
            if y > HEIGHT_PX:
                y = HEIGHT_PX
            print("ReplyY", reply)

            reply = self.tp_spi.xfer2([0b10010000, 0b00000000, 0b00000000])
            x = int(((reply[1] << 5 | reply[2] >> 3) * X_SCALE) - X_OFFSET)
            if x < 0:
                x = 0
            if x > WIDTH_PX:
                x = WIDTH_PX
            print("ReplyX", reply)
        else:
            x = 0
            y = 0
        print(x, y)
        return x, y

    # --------------------------------------------- SPI things ---------------------------------------------

    def reset(self):
        for i in range(2):
            GPIO.output(Pins.RST, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(Pins.RST, GPIO.LOW)
            time.sleep(0.05)

    def push_pixels_spi(self, pil_img):
        print("Pushing pixels: ", str(pil_img))
        try:

            GPIO.output(Pins.LCD_RS, GPIO.LOW)
            self.lcd.display_pil(pil_img)
            GPIO.output(Pins.LCD_RS, GPIO.HIGH)
            print("Done!!")

        except RuntimeError as re:
            print("Error while pushing pixels!")
            print(re)
        pass
