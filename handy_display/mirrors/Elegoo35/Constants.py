# How do I give NeilAlexanderHiggins a medal? https://forums.raspberrypi.com/viewtopic.php?t=330844
# The pi has 1 bus (#0) and 2 devices (CE0 and CE1)


class Channels:
    X_POS = 0b0_101_0000
    Y_POS = 0b0_001_0000
    Z1_POS = 0b0_011_0000
    Z2_POS = 0b0_100_0000
    TEMP_0 = 0b0_000_0000
    TEMP_1 = 0b0_111_0000
    BAT_V = 0b0_001_0000
    AUX = 0b0_110_0000


class Conversions:
    BIT_12 = 0b0000_0_000
    BIT_8 = 0b0000_1_000


class ReferenceInput:
    SINGLE = 0b00000_1_00
    DIFFERENTIAL = 0b00000_0_00


class PowerMode:
    POWER_DOWN_BETWEEN = 0b000000_00
    # I don't know exactly what these do, but they stop touch interrupts, so I don't like them
    __UNSAFE__REF_OFF_ADC_ON = 0b000000_10
    __UNSAFE__REF_ON_ADC_OFF = 0b000000_01
    __UNSAFE__ALWAYS_POWERED = 0b000000_11


def get_control_byte(channel, conversion, reference_input, power_mode) -> int:
    return 0b_1_000_0000 | channel | conversion | reference_input | power_mode


class Devices:
    LCD_TP_BUS = 0
    LCD_DEVICE = 0
    TP_DEVICE = 1


class Pins:
    # Using the XPT2046 touch panel (TP) and the ILI9486 LCD chip (LCD)
    TP_IRQ = 17  # SPI1 CE1  # TP touch interrupt
    LCD_RS = 24  # -         # LCD instruction control (Instruction/Data register select)
    LCD_TP_SI = 10  # SPI0 MOSI # SPI data into TP (MOSI) and LCD
    RST = 25  # -         # Reset
    TP_SO = 9  # SPI0 MISO # SPI data out (MISO) of the TP
    LCD_CS = 8  # SPI0 CE0  # Chip select (enable) for the LCD
    LCD_TP_SCK = 11  # SPI0 SCLK # Clock for SPI interface
    TP_CS = 7  # SPI0 CE1  # Chip select (enable) for the TP


class Commands:
    NOP = 0x00
    SOFT_RESET = 0x01
    READ_DISPLAY_IDENTIFICATION_INFORMATION = 0x04
    READ_NUMBER_OF_THE_ERRORS_ON_DSI = 0x05
    READ_DISPLAY_STATUS = 0x09
    READ_DISPLAY_POWER_MODE = 0x0A
    READ_DISPLAY_MADCTL = 0x0B
    READ_PIXEL_FORMAT = 0x0C
    READ_DISPLAY_IMAGE_MODE = 0x0D
    READ_DISPLAY_SIGNAL_MODE = 0x0E
    READ_DISPLAY_SELF_DIAGNOSTIC_RESULT = 0x0F
    SLEEP_IN = 0x10
    SLEEP_OUT = 0x11
    PARTIAL_MODE_ON = 0x12
    NORMAL_DISPLAY_MODE_ON = 0x13
    DISPLAY_INVERSION_OFF = 0x20
    DISPLAY_INVERSION_ON = 0x21
    DISPLAY_OFF = 0x28
    DISPLAY_ON = 0x29
    COLUMN_ADDRESS_SET = 0x2A
    PAGE_ADDRESS_SET = 0x2B
    MEMORY_WRITE = 0x2C
    MEMORY_READ = 0x2E
    PARTIAL_AREA = 0x30
    VERTICAL_SCROLLING_DEFINITION = 0x33
    TEARING_EFFECT_LINE_OFF = 0x34
    TEARING_EFFECT_LINE_ON = 0x35
    MEMORY_ACCESS_CONTROL = 0x36
    VERTICAL_SCROLLING_START_ADDRESS = 0x37
    IDLE_MODE_OFF = 0x38
    IDLE_MODE_ON = 0x39
    INTERFACE_PIXEL_FORMAT = 0x3A
    MEMORY_WRITE_CONTINUE = 0x3C
    MEMORY_READ_CONTINUE = 0x3E
    WRITE_TEAR_SCAN_LINE = 0x44
    READ_TEAR_SCAN_LINE = 0x45
    WRITE_DISPLAY_BRIGHTNESS_VALUE = 0x51
    READ_DISPLAY_BRIGHTNESS_VALUE = 0x52
    WRITE_CTRL_DISPLAY_VALUE = 0x53
    READ_CTRL_DISPLAY_VALUE = 0x54
    WRITE_CONTENT_ADAPTIVE_BRIGHTNESS_CONTROL_VALUE = 0x55
    READ_CONTENT_ADAPTIVE_BRIGHTNESS_CONTROL_VALUE = 0x56
    WRITE_CABC_MINIMUM_BRIGHTNESS_ = 0x5E
    READ_CABC_MINIMUM_BRIGHTNESS = 0x5F
    READ_FIRST_CHECKSUM = 0xAA
    READ_CONTINUE_CHECKSUM = 0xAF
    READ_ID1 = 0xDA
    READ_ID2 = 0xDB
    READ_ID3 = 0xDC
