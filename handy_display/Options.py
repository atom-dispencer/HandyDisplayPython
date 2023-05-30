from enum import Enum


class MirrorType(Enum):
    NO_MIRROR = 0
    TFT_LCD_XPT2046_ILI9486 = 1


class Options:
    def __init__(self, argv):
        if len(argv) < 2:
            raise Exception("Cannot have < 2 arguments, got: ", len(argv))

        st = argv[1].strip()
        if st == "0" or st == "no_mirror":
            self.screen_type = MirrorType.NO_MIRROR
        elif st == "1" or st == "TFT_LCD_XPT2046_ILI9486":
            self.screen_type = MirrorType.TFT_LCD_XPT2046_ILI9486
        else:
            raise Exception("Screen type may only be 0 (no_mirror) or 1 (TFT_LCD_XPT2046_ILI9486), got: " + st)
