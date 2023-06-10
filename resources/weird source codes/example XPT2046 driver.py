import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image
import numbers
import numpy as np

ILI9341_TFTWIDTH = 240
ILI9341_TFTHEIGHT = 320

ILI9341_NOP = 0x00
ILI9341_SWRESET = 0x01
ILI9341_RDDID = 0x04
ILI9341_RDDST = 0x09

ILI9341_SLPIN = 0x10
ILI9341_SLPOUT = 0x11
ILI9341_PTLON = 0x12
ILI9341_NORON = 0x13

ILI9341_RDMODE = 0x0A
ILI9341_RDMADCTL = 0x0B
ILI9341_RDPIXFMT = 0x0C
ILI9341_RDIMGFMT = 0x0A
ILI9341_RDSELFDIAG = 0x0F

ILI9341_INVOFF = 0x20
ILI9341_INVON = 0x21
ILI9341_GAMMASET = 0x26
ILI9341_DISPOFF = 0x28
ILI9341_DISPON = 0x29

ILI9341_CASET = 0x2A
ILI9341_PASET = 0x2B
ILI9341_RAMWR = 0x2C
ILI9341_RAMRD = 0x2E

ILI9341_PTLAR = 0x30
ILI9341_MADCTL = 0x36
ILI9341_PIXFMT = 0x3A

ILI9341_FRMCTR1 = 0xB1
ILI9341_FRMCTR2 = 0xB2
ILI9341_FRMCTR3 = 0xB3
ILI9341_INVCTR = 0xB4
ILI9341_DFUNCTR = 0xB6

ILI9341_PWCTR1 = 0xC0
ILI9341_PWCTR2 = 0xC1
ILI9341_PWCTR3 = 0xC2
ILI9341_PWCTR4 = 0xC3
ILI9341_PWCTR5 = 0xC4
ILI9341_VMCTR1 = 0xC5
ILI9341_VMCTR2 = 0xC7

ILI9341_RDID1 = 0xDA
ILI9341_RDID2 = 0xDB
ILI9341_RDID3 = 0xDC
ILI9341_RDID4 = 0xDD

ILI9341_GMCTRP1 = 0xE0
ILI9341_GMCTRN1 = 0xE1
ILI9341_PWCTR6 = 0xFC
ILI9341_BLACK = 0x0000
ILI9341_BLUE = 0x001F
ILI9341_RED = 0xF800
ILI9341_GREEN = 0x07E0
ILI9341_CYAN = 0x07FF
ILI9341_MAGENTA = 0xF81F
ILI9341_YELLOW = 0xFFE0
ILI9341_WHITE = 0xFFFF

button_register = [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0),
                   (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 64000000

spi1 = spidev.SpiDev()
spi1.open(0, 1)

DC = 24
RST = 25
LED = 18


class Touch_Screen_320_240:

    def __init__(self):
        global backlight
        global current_screen
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DC, GPIO.OUT)  # DC
        GPIO.setup(RST, GPIO.OUT)  # RST
        GPIO.setup(LED, GPIO.OUT)
        backlight = GPIO.PWM(LED, 200)
        backlight.start(0)
        GPIO.output(RST, True)
        time.sleep(0.005)
        GPIO.output(RST, False)
        time.sleep(0.02)
        GPIO.output(RST, True)
        time.sleep(0.150)
        self.send(0xEF, False)
        self.send(0x03, True)
        self.send(0x80, True)
        self.send(0x02, True)
        self.send(0xCF, False)
        self.send(0x00, True)
        self.send(0XC1, True)
        self.send(0X30, True)
        self.send(0xED, False)
        self.send(0x64, True)
        self.send(0x03, True)
        self.send(0X12, True)
        self.send(0X81, True)
        self.send(0xE8, False)
        self.send(0x85, True)
        self.send(0x00, True)
        self.send(0x78, True)
        self.send(0xCB, False)
        self.send(0x39, True)
        self.send(0x2C, True)
        self.send(0x00, True)
        self.send(0x34, True)
        self.send(0x02, True)
        self.send(0xF7, False)
        self.send(0x20, True)
        self.send(0xEA, False)
        self.send(0x00, True)
        self.send(0x00, True)
        self.send(ILI9341_PWCTR1, False)  # Power control
        self.send(0x23, True)  # VRH[5:0]
        self.send(ILI9341_PWCTR2, False)  # Power control
        self.send(0x10, True)  # SAP[2:0];BT[3:0]
        self.send(ILI9341_VMCTR1, False)  # VCM control
        self.send(0x3e, True)
        self.send(0x28, True)
        self.send(ILI9341_VMCTR2, False)  # VCM control2
        self.send(0x86, True)  # --
        self.send(ILI9341_MADCTL, False)  # Memory Access Control
        self.send(0x48, True)
        self.send(ILI9341_PIXFMT, False)
        self.send(0x55, True)
        self.send(ILI9341_FRMCTR1, False)
        self.send(0x00, True)
        self.send(0x18, True)
        self.send(ILI9341_DFUNCTR, False)  # Display Function Control
        self.send(0x08, True)
        self.send(0x82, True)
        self.send(0x27, True)
        self.send(0xF2, False)  # 3Gamma Function Disable
        self.send(0x00, True)
        self.send(ILI9341_GAMMASET, False)  # Gamma curve selected
        self.send(0x01, True)
        self.send(ILI9341_GMCTRP1, False)  # Set Gamma
        self.send(0x0F, True)
        self.send(0x31, True)
        self.send(0x2B, True)
        self.send(0x0C, True)
        self.send(0x0E, True)
        self.send(0x08, True)
        self.send(0x4E, True)
        self.send(0xF1, True)
        self.send(0x37, True)
        self.send(0x07, True)
        self.send(0x10, True)
        self.send(0x03, True)
        self.send(0x0E, True)
        self.send(0x09, True)
        self.send(0x00, True)
        self.send(ILI9341_GMCTRN1, False)  # Set Gamma
        self.send(0x00, True)
        self.send(0x0E, True)
        self.send(0x14, True)
        self.send(0x03, True)
        self.send(0x11, True)
        self.send(0x07, True)
        self.send(0x31, True)
        self.send(0xC1, True)
        self.send(0x48, True)
        self.send(0x08, True)
        self.send(0x0F, True)
        self.send(0x0C, True)
        self.send(0x31, True)
        self.send(0x36, True)
        self.send(0x0F, True)
        self.send(ILI9341_SLPOUT, False)  # Exit Sleep
        time.sleep(0.120)
        self.send(ILI9341_DISPON, False)  # Display on
        current_screen = [0] * 153600
        self.touch_calibration()
        self.display_background(current_screen)

    # self.touch_calibration()

    def convert_16bit(self, image):
        # convert 24bit colours to 16bit colours code from
        # Keith (https://www.blogger.com/profile/02555547344016007163)
        pb = np.array(image.convert('RGB')).astype('uint16')
        color = ((pb[:, :, 0] & 0xF8) << 8) | ((pb[:, :, 1] & 0xFC) << 3) | (pb[:, :, 2] >> 3)
        return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

    def send(self, data, is_data=True, chunk_size=4096):
        # Set DC low for command, high for data. 			
        GPIO.output(DC, is_data)
        # Convert scalar argument to list so either can be passed as parameter.        
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.		
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            temp_data = spi.xfer(data[start:end])

    def set_window(self, x0=0, y0=0, width=320, height=240):
        x1 = x0 + width - 1
        y1 = y0 + height - 1

        self.send(ILI9341_CASET, False)  # set Column addr command
        self.send(y0 >> 8, True)
        self.send(y0, True)  # x_start
        self.send(y1 >> 8, True)
        self.send(y1, True)  # x_end

        self.send(ILI9341_PASET, False)  # set Row addr command
        self.send(x0 >> 8, True)
        self.send(x0, True)  # y_start
        self.send(x1 >> 8, True)
        self.send(x1, True)  # y_end

        self.send(ILI9341_RAMWR, False)  # set to write to RAM

    def back_light(self, brightness):
        backlight.ChangeDutyCycle(brightness)

    def load_image(self, image_file, xsize, ysize):
        image = Image.open(image_file)
        image = image.rotate(270).resize((ysize, xsize))
        image = list(self.convert_16bit(image))
        return image

    def load_background_image(self, image_file):
        background_image = self.load_image(image_file, 320, 240)
        return background_image

    def load_button_image(self, image_file, xsize, ysize):
        button_image = self.load_image(image_file, xsize, ysize)
        return [xsize, ysize, button_image]

    def display_background(self, image):
        global current_screen
        current_screen = image
        self.set_window()
        self.send(image, True)

    def scroll(self, start):
        while start > 319: start -= 320
        self.send(0x37, False)
        self.send(start >> 8, True)
        self.send(start & 0b0000000011111111, True)

    def touch_calibration(self, touch_xoffset=170, touch_yoffset=280, touch_xscale=10.8, touch_yscale=15):
        global xoffset
        global yoffset
        global xscale
        global yscale
        xoffset = touch_xoffset
        yoffset = touch_yoffset
        xscale = touch_xscale
        yscale = touch_yscale

    def touched(self, touch_sensitivity=245):
        readarry = spi1.xfer2([0b10111000, 0b00000000, 0b00000000])
        z1 = readarry[2] >> 7 | readarry[1] << 1
        readarry = spi1.xfer2([0b11001000, 0b00000000, 0b00000000])
        z2 = readarry[2] >> 7 | readarry[1] << 1
        if z2 - z1 < touch_sensitivity:
            return True
        else:
            return False

    def get_touch_position(self):
        if self.touched():
            readarry = spi1.xfer2([0b11010000, 0b00000000, 0b00000000])
            y = int((4095 - (readarry[1] << 5 | readarry[2] >> 3) - yoffset) // yscale)
            if y < 0: y = 0
            if y > 239: y = 239
            readarry = spi1.xfer2([0b10010000, 0b00000000, 0b00000000])
            x = (((readarry[1] << 5 | readarry[2] >> 3) - xoffset) // xscale)
            x = int(x)
            if x < 0: x = 0
            if x > 319: x = 319
        else:
            x = 0
            y = 0
        return [x, y]

    def get_block(self, x, y, width, height):
        block = []
        for x_pos in range((x) * 480, (x * 480) + ((width) * 480), 480):
            for y_pos in range((y * 2), (y * 2) + (height * 2), 1):
                block.append(current_screen[x_pos + y_pos])
        return block

    def put_button(self, button_data, button_number, x, y):
        if x < 0 or y < 0 or x + button_data[0] > 319 or y + button_data[1] > 239:
            raise "Button outside screen"
        else:
            global button_register
            button_register[button_number] = [x, y, button_data[0], button_data[1], True]
            self.set_window(x, y, button_data[0], button_data[1])
            self.send(button_data[2], True)

    def remove_button(self, button_number):
        button = button_register[button_number]
        self.set_window(button[0], button[1], button[2], button[3])
        blocks = self.get_block(button[0], button[1], button[2], button[3])
        self.send(blocks, True)
        button_register[button_number] = [0, 0, 0, 0, 0]

    def button_pressed(self, button_number):
        if self.touched():
            position = self.get_touch_position()
            button = button_register[button_number]
            if position[0] > button[0] and position[0] < button[0] + button[2] and position[1] > button[1] and position[
                1] < button[1] + button[3]:
                return True
            else:
                return False

    def shutdown(self, GPIO_clean=True):
        self.back_light(0)
        GPIO.output(RST, False)
        GPIO.output(DC, False)
        if GPIO_clean == True: GPIO.cleanup()
