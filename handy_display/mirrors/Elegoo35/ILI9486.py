# https://github.com/ustropo/Python_ILI9486/blob/master/Python_ILI9486/ILI9486.py

# Copyright (c) 2016 myway work
# Author: Liqun Hu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import numbers
import time

from PIL.Image import Image as PILImage
from PIL import ImageDraw

from handy_display import ImageHelper
from handy_display.mirrors.Elegoo35.Constants import Devices

###
#    My additions
###
try:
    from RPi import GPIO
    from spidev import SpiDev
except ImportError as e:
    print("Import error for ILI9486:", e)
    exit(-15)

lcd_spi = SpiDev()
lcd_spi.open(Devices.LCD_TP_BUS, Devices.LCD_DEVICE)
lcd_spi.max_speed_hz = 64_000_000  # 64MHz (max 2.5MHz)
###
###
###

# Constants for interacting with display registers.
ILI9486_TFTWIDTH = 320
ILI9486_TFTHEIGHT = 480

ILI9486_NOP = 0x00
ILI9486_SWRESET = 0x01
ILI9486_RDDID = 0x04
ILI9486_RDDST = 0x09

ILI9486_SLPIN = 0x10
ILI9486_SLPOUT = 0x11
ILI9486_PTLON = 0x12
ILI9486_NORON = 0x13

ILI9486_RDMODE = 0x0A
ILI9486_RDMADCTL = 0x0B
ILI9486_RDPIXFMT = 0x0C
ILI9486_RDIMGFMT = 0x0A
ILI9486_RDSELFDIAG = 0x0F

ILI9486_INVOFF = 0x20
ILI9486_INVON = 0x21
ILI9486_GAMMASET = 0x26
ILI9486_DISPOFF = 0x28
ILI9486_DISPON = 0x29

ILI9486_CASET = 0x2A
ILI9486_PASET = 0x2B
ILI9486_RAMWR = 0x2C
ILI9486_RAMRD = 0x2E

ILI9486_PTLAR = 0x30
ILI9486_MADCTL = 0x36
ILI9486_PIXFMT = 0x3A

ILI9486_FRMCTR1 = 0xB1
ILI9486_FRMCTR2 = 0xB2
ILI9486_FRMCTR3 = 0xB3
ILI9486_INVCTR = 0xB4
ILI9486_DFUNCTR = 0xB6

ILI9486_PWCTR1 = 0xC0
ILI9486_PWCTR2 = 0xC1
ILI9486_PWCTR3 = 0xC2
ILI9486_PWCTR4 = 0xC3
ILI9486_PWCTR5 = 0xC4
ILI9486_VMCTR1 = 0xC5
ILI9486_VMCTR2 = 0xC7

ILI9486_RDID1 = 0xDA
ILI9486_RDID2 = 0xDB
ILI9486_RDID3 = 0xDC
ILI9486_RDID4 = 0xDD

ILI9486_GMCTRP1 = 0xE0
ILI9486_GMCTRN1 = 0xE1

ILI9486_PWCTR6 = 0xFC

ILI9486_BLACK = 0x0000
ILI9486_BLUE = 0x001F
ILI9486_RED = 0xF800
ILI9486_GREEN = 0x07E0
ILI9486_CYAN = 0x07FF
ILI9486_MAGENTA = 0xF81F
ILI9486_YELLOW = 0xFFE0
ILI9486_WHITE = 0xFFFF


class ILI9486(object):
    """Representation of an ILI9486 TFT LCD."""

    def __init__(
        self, data_cmd, spi, rst=None, width=ILI9486_TFTWIDTH, height=ILI9486_TFTHEIGHT
    ):
        """Create an instance of the display using SPI communication.  Must
        provide the GPIO pin number for the D/C pin and the SPI driver.  Can
        optionally provide the GPIO pin number for the reset pin as the rst
        parameter.
        """
        self._data_cmd = data_cmd
        self._rst = rst
        self._spi = spi
        self.width = width
        self.height = height

        GPIO.setup(data_cmd, GPIO.OUT)
        if rst is not None:
            GPIO.setup(rst, GPIO.OUT)

        # Set SPI to mode 0, MSB first.
        self._spi.open(Devices.LCD_TP_BUS, Devices.LCD_DEVICE)
        self._spi.mode = 2  # This was actually 2 before?
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = 64000000  # Is this too high?

        # Create an image buffer.
        self.pil_internal = PILImage.new("RGB", (width, height))

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or
        command data (False).  Chunk_size is an optional size of bytes to write
        in a single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        GPIO.output(self._data_cmd, is_data)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))

            f = open("out/data.txt", "w")
            f.write(str(data))
            f.close()

            self._spi.xfer2(data[start:end])

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            GPIO.output(self._rst, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(self._rst, GPIO.LOW)
            time.sleep(0.02)
            GPIO.output(self._rst, GPIO.HIGH)
            time.sleep(0.150)

    def begin(self):
        """Initialize the display.  Should be called once before other calls
        that interact with the display are called.
        """
        self.reset()
        self.send_init_sequence()

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to 239,319.
        """
        if x1 is None:
            x1 = self.width - 1
        if y1 is None:
            y1 = self.height - 1
        self.command(0x2A)  # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)  # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)  # XEND
        self.command(0x2B)  # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)  # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)  # YEND
        self.command(0x2C)  # write to RAM

    def display_pil(self, pil_img: PILImage):
        """Write the display buffer or provided image to the hardware.  If no
        image parameter is provided the display buffer will be written to the
        hardware.  If an image is provided, it should be RGB format and the
        same dimensions as the display hardware.
        """
        # By default, write the internal buffer to the display.
        if pil_img is None:
            pil_img = self.pil_internal
        # Set address bounds to entire display.
        self.set_window()

        print("Converting...")
        rgb888 = ImageHelper.pil_to_rgb888(pil_img)
        rgb565 = ImageHelper.rgb888_to_rgb565(rgb888)
        data = rgb565.flatten().tolist()

        print("SPI'ing...")
        self.data(data)

    def fill_pil_internal(self, color=(0, 0, 0)):
        """Clear the image buffer to the specified RGB color
        (default black)."""
        width, height = self.pil_internal.size
        self.pil_internal.putdata([color] * (width * height))

    def get_internal_drawer(self):
        """Return a PIL ImageDraw instance for 2D drawing on the
        image buffer."""
        return ImageDraw.Draw(self.pil_internal)

    def send_init_sequence(self):
        # Initialize the display.  Broken out as a separate function so it can
        # be overridden by other displays in the future.
        self.command(0xB0)
        self.data(0x00)
        self.command(0x11)
        time.sleep(0.020)

        self.command(0x3A)
        self.data(0x66)

        self.command(0x0C)
        self.data(0x66)

        # self.command(0xB6)
        # self.data(0x00)
        # self.data(0x42)
        # self.data(0x3B)

        self.command(0xC2)
        self.data(0x44)

        self.command(0xC5)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)

        self.command(0xE0)
        self.data(0x0F)
        self.data(0x1F)
        self.data(0x1C)
        self.data(0x0C)
        self.data(0x0F)
        self.data(0x08)
        self.data(0x48)
        self.data(0x98)
        self.data(0x37)
        self.data(0x0A)
        self.data(0x13)
        self.data(0x04)
        self.data(0x11)
        self.data(0x0D)
        self.data(0x00)

        self.command(0xE1)
        self.data(0x0F)
        self.data(0x32)
        self.data(0x2E)
        self.data(0x0B)
        self.data(0x0D)
        self.data(0x05)
        self.data(0x47)
        self.data(0x75)
        self.data(0x37)
        self.data(0x06)
        self.data(0x10)
        self.data(0x03)
        self.data(0x24)
        self.data(0x20)
        self.data(0x00)

        self.command(0xE2)
        self.data(0x0F)
        self.data(0x32)
        self.data(0x2E)
        self.data(0x0B)
        self.data(0x0D)
        self.data(0x05)
        self.data(0x47)
        self.data(0x75)
        self.data(0x37)
        self.data(0x06)
        self.data(0x10)
        self.data(0x03)
        self.data(0x24)
        self.data(0x20)
        self.data(0x00)

        self.command(0x36)
        self.data(0x88)  # change the direct

        self.command(0x11)
        self.command(0x29)
