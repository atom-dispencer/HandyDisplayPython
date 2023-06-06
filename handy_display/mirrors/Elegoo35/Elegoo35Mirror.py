import threading
import time

from handy_display.mirrors.IMirror import IMirror
from handy_display.mirrors.Elegoo35.Constants import *

# https://pinout.xyz/pinout/spi
# https://pypi.org/project/spidev/
try:
    # from spidev import SpiDev
    import Adafruit_PureIO.spi

    print("Elegoo35 - Successfully imported spidev: " + str(Adafruit_PureIO.spi))
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
CLK_HZ = int(1e6)  # 1MHz


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

        GPIO.setup(Pins.LCD_TP_SCK, GPIO.OUT)
        GPIO.setup(Pins.LCD_TP_SI, GPIO.OUT)
        GPIO.setup(Pins.TP_SO, GPIO.IN)
        GPIO.setup(Pins.LCD_CS, GPIO.OUT)
        GPIO.setup(Pins.TP_CS, GPIO.OUT)

        GPIO.output(Pins.LCD_CS, GPIO.HIGH)
        GPIO.output(Pins.TP_CS, GPIO.HIGH)

        print("Starting SpiDev")
        self.touch_panel_spi = Adafruit_PureIO.spi.SPI(
            device=(Devices.LCD_TP_BUS, Devices.TP_DEVICE),
            max_speed_hz=CLK_HZ,
            bits_per_word=8
        )

        # Reset the screen to a functional state in case I screw something up
        ctrl_byte = bytearray()
        ctrl_byte.append(
            get_control_byte(
                Channels.X_POS,
                Conversions.BIT_12,
                ReferenceInput.DIFFERENTIAL,
                PowerMode.POWER_DOWN_BETWEEN
            )
        )
        self.touch_panel_spi.writebytes(ctrl_byte)

    # --------------------------------------------- IScreen stuff ---------------------------------------------

    def get_dimensions(self) -> (int, int):
        return self.width, self.height

    def process_events(self):
        if GPIO.event_detected(Pins.TP_IRQ):
            self.process_tft_touch()

    def ready_for_next_frame(self):
        return self.spi_thread is None or not self.spi_thread.is_alive()

    def next_frame(self, pixel_array_3d):
        if self.ready_for_next_frame():
            self.spi_thread = threading.Thread(name=THREAD_NAME, target=lambda: self.push_pixels_spi(pixel_array_3d))
            # self.spi_thread.start()

    def shutdown(self):
        print("Shutting down Elegoo35...")
        GPIO.cleanup()

    def process_tft_touch(self):
        samples = []
        start = time.time()
        while time.time() - start < 0.25:
            sample = self.get_tft_sample()
            samples += sample if sample is not None else []
        print("Samples:", samples)

    def get_tft_sample(self):
        ctrl_byte = bytearray()
        ctrl_byte.append(
            get_control_byte(
                Channels.X_POS,
                Conversions.BIT_12,
                ReferenceInput.DIFFERENTIAL,
                PowerMode.POWER_DOWN_BETWEEN
            )
        )  # Control byte
        ctrl_byte.append(0)
        ctrl_byte.append(0)
        ctrl_byte.append(0)

        mask = 0b1000_0000
        GPIO.output(Pins.TP_CS, GPIO.LOW)
        sample = None
        attempt = 0
        while sample is None and attempt < 25:
            out_arr = []
            for byte in ctrl_byte:
                out_byte = 0x00
                for i in range(8):

                    # Serial output
                    if byte & mask == 0:
                        GPIO.output(Pins.LCD_TP_SI, GPIO.LOW)
                    else:
                        GPIO.output(Pins.LCD_TP_SI, GPIO.HIGH)
                    byte <<= 1

                    # Clock pulse (The timing helps a lot!)
                    GPIO.output(Pins.LCD_TP_SCK, GPIO.HIGH)
                    time.sleep(0.001)
                    GPIO.output(Pins.LCD_TP_SCK, GPIO.LOW)
                    time.sleep(0.001)

                    # Serial input
                    if GPIO.input(Pins.TP_SO):
                        out_byte |= 0b0000_0001
                    if i < 7:
                        out_byte <<= 1

                out_arr.append(out_byte)

            if not all(v == 0 for v in out_arr):
                sample = out_arr
            attempt += 1
        GPIO.output(Pins.TP_CS, GPIO.HIGH)

        if sample is None:
            print("Failed to get touch in {attempt} attempts".format(attempt=attempt))
        else:
            print("Got sample " + str(sample) + " in " + str(attempt) + " attempts")

        return sample

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
