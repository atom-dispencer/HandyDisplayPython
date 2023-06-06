# https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
try:
    from RPi import GPIO
except ImportError:
    print("SPI - Failed to import RPi.GPIO")
    exit(-11)
except RuntimeError:
    print("SPI - Failed to initialise RPi.GPIO")
    exit(-12)


async def transfer(data, gpio_clk, gpio_mosi, gpio_miso):
    reply = bytearray(len(data))
    pass
