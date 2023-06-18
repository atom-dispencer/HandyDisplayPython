from enum import Enum


class MirrorType(Enum):
    NO_MIRROR = 0
    TFT_LCD_XPT2046_ILI9486 = 1


MINIMUM_ARGS = 2


class Options:
    def __init__(self, argv):
        argv += [''] * (1 + MINIMUM_ARGS - len(argv))

        # Screen type
        st = argv[1].strip()
        if st == "no_mirror":
            self.screen_type = MirrorType.NO_MIRROR
        elif st == "TFT_LCD_XPT2046_ILI9486":
            self.screen_type = MirrorType.TFT_LCD_XPT2046_ILI9486
        else:
            raise Exception("Argument 1 must be [no_mirror/TFT_LCD_XPT2046_ILI9486]. Got: " + st)
        print("Screen: " + str(self.screen_type))

        # Headless mode
        headless = argv[2].strip()
        if headless == "headless":
            self.headless = True
        elif headless == "headful":
            self.headless = False
        else:
            raise Exception("Argument 2 must be [headless/headful]. Got: " + headless)
        print("Headless: " + str(self.headless))
