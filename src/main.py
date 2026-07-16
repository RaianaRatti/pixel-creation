from PIL import Image
import argparse

from resize import upscale, downscale
from palette import quantize
from config import SCALE, NUM_COLORS

def main():

    # OBTAINING ARGUMENTS
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)

    args = parser.parse_args()

    image = Image.open(args.input)

    # IMAGES THROUGH PROCESS
    new_width = image.width // SCALE
    new_height = image.height // SCALE

    image_downscaled = downscale(image, new_width, new_height) # 40x downscale & upscale
    image_quantized = quantize(image_downscaled, NUM_COLORS)
    image_upscaled = upscale(image_quantized, SCALE)

    image_upscaled.save(args.output)

if __name__ == "__main__":
    main()