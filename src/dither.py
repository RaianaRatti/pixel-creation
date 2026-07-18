# Note: dithering will be done per region (in main) to avoid noisy borders

import numpy as np
from PIL import Image

BAYER4 = np.array([
    [0, 8, 2,10],
    [12,4,14,6],
    [3,11,1,9],
    [15,7,13,5]
], dtype=np.float32)

# normalizing classic bayer matrix to give values between 0.03 and 0.97
BAYER4 = (BAYER4 + 0.5) / 16.0


def ordered_dither(image, strength):
    image_array = np.array(image).astype(np.float32)

    h, w, _ = image_array.shape

    # repeats bayer matrix to be >= image size and then crops created matrix
    tiled = np.tile(BAYER4, ((h + 3) // 4, (w + 3) // 4))[:h, :w]

    adjustment = (tiled[:, :, None] - 0.5) * 255 * strength

    image_array += adjustment
    image_array = np.clip(image_array, 0, 255)

    return Image.fromarray(image_array.astype(np.uint8))