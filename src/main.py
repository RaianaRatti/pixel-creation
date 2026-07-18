import argparse
from pathlib import Path
from PIL import Image

from pipeline import run_pipeline
from presets import get_preset, list_presets

from config import (
    SCALE,
    SPATIAL_RADIUS, COLOR_RADIUS,
    MIN_REGION_SIZE,
    MIN_COLORS_PER_REGION, MAX_COLORS_PER_REGION,
    SATURATION, CONTRAST,
    STRENGTH,
    BORDER_SIZE, BORDER_COLOR,
    MAX_DEVIATION, MIN_BOUNDARY_LENGTH,
    BLUR_RADIUS, LIGHT_STRENGTH, REAPPLY_STRENGTH,
    PRESET,
)


def parse_args():
    # Check for --list-presets first to avoid required arg errors
    import sys
    if "--list-presets" in sys.argv:
        print("Available Presets:\n")
        for name, description in list_presets():
            print(f"  {name:12} - {description}")
        exit(0)

    parser = argparse.ArgumentParser(description="Convert real photos into pixel art")

    parser.add_argument("--preset", default=None, help="Use a named preset (see --list-presets)")

    # Positional/required
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", type=int, default=None)

    # Optional with config defaults
    parser.add_argument("--min-colors-per-region", type=int, default=MIN_COLORS_PER_REGION)
    parser.add_argument("--max-colors-per-region", type=int, default=MAX_COLORS_PER_REGION)
    parser.add_argument("--spatial-radius", type=int, default=SPATIAL_RADIUS)
    parser.add_argument("--color-radius", type=int, default=COLOR_RADIUS)
    parser.add_argument("--segmentation-max-dimension", type=int, default=500)
    parser.add_argument("--min-region-size", type=int, default=MIN_REGION_SIZE)
    parser.add_argument("--saturation", type=float, default=SATURATION)
    parser.add_argument("--contrast", type=float, default=CONTRAST)
    parser.add_argument("--borders", action="store_true")
    parser.add_argument("--border-size", type=int, default=BORDER_SIZE)
    parser.add_argument("--border-color", default=BORDER_COLOR)
    parser.add_argument("--max-deviation", type=int, default=MAX_DEVIATION)
    parser.add_argument("--min-boundary-length", type=int, default=MIN_BOUNDARY_LENGTH)
    parser.add_argument("--dither", action="store_true")
    parser.add_argument("--dither-strength", type=float, default=STRENGTH)
    parser.add_argument("--blur-radius", type=int, default=BLUR_RADIUS)
    parser.add_argument("--light-strength", type=float, default=LIGHT_STRENGTH)
    parser.add_argument("--reapply-strength", type=float, default=REAPPLY_STRENGTH)
    parser.add_argument("--scale", type=int, default=SCALE)

    args = parser.parse_args()

    # Handle preset loading
    if args.preset:
        preset = get_preset(args.preset)
        if not preset:
            print(f"Error: Unknown preset '{args.preset}'")
            print("\nAvailable presets:")
            for name, description in list_presets():
                print(f"  {name:12} - {description}")
            exit(1)
        # Apply preset values to args (only if not explicitly set on command line)
        for key, value in preset.items():
            if key != "description":
                attr = key.replace("-", "_")
                if hasattr(args, attr):
                    setattr(args, attr, value)

    return args


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input image does not exist: {input_path}")

    image = Image.open(input_path).convert("RGB")
    height = args.height if args.height is not None else int(image.height * (args.width / image.width))

    result = run_pipeline(
        image=image,
        width=args.width,
        height=height,
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
        max_deviation=args.max_deviation,
        min_boundary_length=args.min_boundary_length,
        dither=args.dither,
        dither_strength=args.dither_strength,
        scale=args.scale,
        preset=args.preset,
        blur_radius=args.blur_radius,
        light_strength=args.light_strength,
        reapply_strength=args.reapply_strength,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    print(f"Saved pixel art image to {output_path}")


if __name__ == "__main__":
    main()