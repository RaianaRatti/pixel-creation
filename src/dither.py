# Note: dithering will be done per region (in main) to avoid noisy borders

import numpy as np
from config import STRENGTH

BAYER4 = np.array([
    [0, 8, 2,10],
    [12,4,14,6],
    [3,11,1,9],
    [15,7,13,5]
], dtype=np.float32)

# normalizing classic bayer matrix to give values between 0.03 and 0.97
BAYER4 = (BAYER4 + 0.5) / 16.0


def ordered_dither(image, strength=STRENGTH):
    image = image.astype(np.float32)

    h, w, _ = image.shape

    # repeats bayer matrix to be >= image size and then crops created matrix
    tiled = np.tile(BAYER4, ((h + 3) // 4, (w + 3) // 4))[:h, :w]

    adjustment = (tiled[:, :, None] - 0.5) * 255 * strength

    image += adjustment
    image = np.clip(image, 0, 255)

    return image.astype(np.uint8)