# src/main.py

import argparse
from pathlib import Path
from PIL import Image

from pipeline import run_pipeline

from config import SCALE, TOTAL_COLORS, SPATIAL_RADIUS, COLOR_RADIUS, MIN_REGION_SIZE, MIN_COLORS_PER_REGION, MAX_COLORS_PER_REGION, SATURATION, CONTRAST, STRENGTH, BORDER_COLOR, BORDER_SIZE, PRESET


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert real photos into pixel art"
    )

    # Required arguments
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input image"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output image"
    )

    parser.add_argument(
        "--width",
        required=True,
        type=int,
        help="Number of horizontal pixel blocks"
    )

    parser.add_argument(
        "--height",
        type=int,
        help="Number of vertical pixel blocks"
    )


    # Color settings
    parser.add_argument(
        "--colors",
        type=int,
        default=TOTAL_COLORS,
        help="Total color budget"
    )

    parser.add_argument(
        "--min-colors-per-region",
        type=int,
        default=MIN_COLORS_PER_REGION
    )

    parser.add_argument(
        "--max-colors-per-region",
        type=int,
        default=MAX_COLORS_PER_REGION
    )


    # Segmentation settings
    parser.add_argument(
        "--spatial-radius",
        type=int,
        default=SPATIAL_RADIUS
    )

    parser.add_argument(
        "--color-radius",
        type=int,
        default=COLOR_RADIUS
    )

    parser.add_argument(
        "--segmentation-max-dimension",
        type=int,
        default=500
    )

    parser.add_argument(
        "--min-region-size",
        type=int,
        default=MIN_REGION_SIZE
    )


    # Color enhancement
    parser.add_argument(
        "--saturation",
        type=float,
        default=SATURATION
    )

    parser.add_argument(
        "--contrast",
        type=float,
        default=CONTRAST
    )


    # Borders
    parser.add_argument(
        "--borders",
        action="store_true",
        help="Enable region borders"
    )

    parser.add_argument(
        "--border-size",
        type=int,
        default=BORDER_SIZE
    )

    parser.add_argument(
        "--border-color",
        default=BORDER_COLOR
    )


    # Dithering
    parser.add_argument(
        "--dither",
        action="store_true",
        help="Enable Bayer dithering"
    )


    # Output scaling
    parser.add_argument(
        "--scale",
        type=int,
        default=SCALE,
        help="Final pixel scale multiplier"
    )


    # Presets
    parser.add_argument(
        "--preset",
        default=PRESET,
        help="Optional style preset"
    )


    return parser.parse_args()



def main():

    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)


    if not input_path.exists():
        raise FileNotFoundError(
            f"Input image does not exist: {input_path}"
        )


    # Load image
    image = Image.open(input_path).convert("RGB")


    # Run complete pipeline
    result = run_pipeline(
        image=image,

        width=args.width,
        height=int(image.height * (args.width / image.width)),

        colors=args.colors,
        min_colors_per_region=args.min_colors_per_region,
        max_colors_per_region=args.max_colors_per_region,

        spatial_radius=args.spatial_radius,
        color_radius=args.color_radius,
        segmentation_max_dimension=args.segmentation_max_dimension,

        min_region_size=args.min_region_size,

        saturation=args.saturation,
        contrast=args.contrast,

        borders=args.borders,
        border_size=args.border_size,
        border_color=args.border_color,

        dither=args.dither,

        scale=args.scale,

        preset=args.preset,
    )


    # Ensure output directory exists
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # Save result
    result.save(output_path)

    print(
        f"Saved pixel art image to {output_path}"
    )


if __name__ == "__main__":
    main()