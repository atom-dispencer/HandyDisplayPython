import numpy as np
from PIL import Image


def pil_to_rgb888(pil_image: Image):
    return np.array(pil_image.convert('RGB'))


def rgb888_to_rgb565(arr_3d) -> []:
    """The original conversion function didn't work at all, so I made this new one"""

    arr_3d = arr_3d.astype('uint16')

    r = (arr_3d[..., 0] & 0xF8) << 8
    g = (arr_3d[..., 1] & 0xFC) << 3
    b = arr_3d[..., 2] >> 3

    return r | g | b


def single_rgb888_to_rgb565(rgb_arr: tuple[int]) -> int:
    # 1F,3F
    return (rgb_arr[0] & 0xF8) << 8 \
        | (rgb_arr[1] & 0xFC) << 3 \
        | (rgb_arr[2] >> 3)
