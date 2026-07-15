from PIL import Image
import argparse
from resize import upscale, downscale

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--colors", type=int, default=16)
    parser.add_argument("--saturation", type=float, default=1.0)
    parser.add_argument("--contrast", type=float, default=1.0)
    parser.add_argument("--border-size", type=int, default=0)
    parser.add_argument("--border-color", default="black")
    parser.add_argument("--dither", action="store_true")
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--preset")

    args = parser.parse_args()

    image = Image.open(args.input)
    image_pixelated = upscale(downscale(image, 32, 48), 40) # 40x downscale & upscale

    image_pixelated.save(args.output)

if __name__ == "__main__":
    main()