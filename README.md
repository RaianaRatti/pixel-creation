# Pixel Room Converter

Convert real photos of rooms into pixel art with a strong retro arcade or video game look, similar to Undertale rooms.

## Features

- **Smart Segmentation**: Uses OpenCV's classical computer vision algorithms to detect objects/regions reliably
- **Per-Region Color Quantization**: Each region gets its own color palette based on its internal variation, preventing busy objects from consuming the entire color budget
- **Customizable Pixel Grid**: Specify any grid dimensions (e.g., 32×24 or 64×48 blocks)
- **Optional Borders**: Draw clean borders around detected regions with no duplicates where regions touch
- **Border Straightening**: Automatically straighten jagged region boundaries using least-squares line fitting
- **Dithering Support**: Optional ordered (Bayer) dithering for a more textured retro look
- **Light Preservation**: Extract and optionally reapply luminance variations from the original photo
- **Color Boosting**: Enhance saturation and contrast for vibrant, popping colors
- **Local Processing**: No external APIs, no network calls, no ML models—everything runs entirely on your machine

## Tech Stack

- **Python 3.10+**
- **Pillow**: Image loading, resizing, saving, and drawing
- **NumPy**: Array-based pixel manipulation and color analysis
- **OpenCV** (`opencv-python`): Segmentation with `cv2.pyrMeanShiftFiltering` and `cv2.connectedComponents`

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pixel-creation

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start with Presets

Use a named preset to instantly apply a complete visual style:

```bash
# List all available presets
python src/main.py --list-presets

# Use a preset
python src/main.py --input room.jpg --output output.png --preset arcade
```

### Basic Usage

```bash
python src/main.py \
  --input room.jpg \
  --output room_pixel.png \
  --width 48 \
  --height 32
```

### Common Options

```bash
python src/main.py \
  --input room.jpg \
  --output room_pixel.png \
  --width 48 \
  --height 32 \
  --colors 20 \
  --borders \
  --dither \
  --scale 16
```

### All CLI Arguments

#### Required
- `--input` : Path to source image
- `--output` : Path to save result
- `--width` : Number of pixel blocks across

#### Image Grid
- `--height` : Number of pixel blocks down (default: auto-calculated from width to maintain aspect ratio)
- `--scale` : Final output size multiplier per block (default: 16)

#### Color Budget
- `--colors` : Total color budget across the whole image (default: 20)
- `--min-colors-per-region` : Minimum colors any single region can use (default: 1)
- `--max-colors-per-region` : Maximum colors any single region can use (default: 4)

#### Segmentation
- `--spatial-radius` : How far apart pixels can be and still merge in `cv2.pyrMeanShiftFiltering` (default: 10)
- `--color-radius` : How different colors can be and still merge (default: 20)
- `--segmentation-max-dimension` : Resize working photo's longest side before segmentation for speed (default: 500)
- `--min-region-size` : Minimum block count before small regions are merged (default: 2)

#### Borders
- `--borders` : Enable region borders (boolean flag, default: off)
- `--border-size` : Thickness of border lines in final pixels (default: 2)
- `--border-color` : Color of border lines (default: black)
- `--max-deviation` : Maximum pixel distance for border straightening (default: 2)
- `--min-boundary-length` : Minimum length to straighten a boundary (default: 4)

#### Color Adjustment
- `--saturation` : Multiplier for color saturation boost (default: 1.5)
- `--contrast` : Multiplier for contrast boost (default: 1.3)

#### Dithering
- `--dither` : Enable ordered dithering (boolean flag, default: off)
- `--dither-strength` : Strength of dithering effect (default: 0.08)

#### Light Extraction (Experimental)
- `--blur-radius` : Radius for extracting lighting patterns (default: 10)
- `--light-strength` : How much of the lighting pattern to remove (default: 1.0)
- `--reapply-strength` : How much of the lighting pattern to reapply to final image (default: 1.0)

### Preset Workflows

Presets provide ready-to-use style configurations. Use `--list-presets` to see all options.

#### Arcade Preset
Bright, saturated look with vibrant colors perfect for arcade-style games.
```bash
python src/main.py --input room.jpg --output output.png --preset arcade
```
Equivalent to: `--width 48 --height 32 --max-colors-per-region 6 --saturation 1.8 --contrast 1.5 --borders --border-size 2`

#### Undertale Preset
Dark, restrained style with muted colors and clean borders.
```bash
python src/main.py --input room.jpg --output output.png --preset undertale
```
Equivalent to: `--width 48 --height 32 --max-colors-per-region 4 --saturation 1.4 --contrast 1.2 --borders --border-color black`

#### Gameboy Preset
Monochrome Gameboy-style output with minimal colors.
```bash
python src/main.py --input room.jpg --output output.png --preset gameboy
```
Equivalent to: `--width 48 --height 32 --max-colors-per-region 1 --saturation 0.0`

#### Dithered Preset
Textured retro look with dithering for added detail.
```bash
python src/main.py --input room.jpg --output output.png --preset dithered
```
Equivalent to: `--width 48 --height 32 --max-colors-per-region 3 --dither --dither-strength 0.12 --borders`

### Custom Workflows

Override preset values or customize from scratch:

```bash
python src/main.py \
  --input room.jpg \
  --output output.png \
  --preset arcade \
  --border-color red \
  --width 64
```

Presets are a good starting point—feel free to tweak any parameter to suit your image.

## Pipeline Overview

The conversion pipeline processes images through the following stages:

1. **Light Extraction** (optional): Extract luminance variations from the original photo to preserve subtle lighting
2. **Full Resolution Segmentation**: Use `cv2.pyrMeanShiftFiltering` to flatten the image into color regions, then `cv2.connectedComponents` to label each distinct region
3. **Downscaling**: Scale the color image and label map to the target block grid size (using area averaging for colors, majority vote for labels)
4. **Small Region Cleanup**: Merge tiny leftover regions into neighboring regions to avoid noise
5. **Border Straightening**: Fit lines to region boundaries and snap them straight using least-squares line fitting
6. **Color Budget Allocation**: Decide how many colors each region deserves based on its internal color variation
7. **Per-Region Quantization**: Quantize colors for each region independently using only that region's own pixel colors
8. **Color Boosting**: Enhance saturation and contrast to make colors vibrant and vivid
9. **Dithering** (optional): Apply ordered Bayer matrix dithering for a textured retro look
10. **Upscaling**: Scale back up using nearest-neighbor interpolation to preserve hard pixel edges
11. **Border Drawing** (optional): Draw clean borders around region boundaries

## Module Structure

```
src/
├── main.py              Entry point, CLI argument parsing
├── pipeline.py          Orchestrates the full conversion pipeline
├── config.py            Default configuration values
├── segmentation.py      Full resolution segmentation using OpenCV
├── resize.py            Downscale/upscale image using Pillow
├── label_resize.py      Downscale label map using majority vote
├── color_budget.py      Allocate per-region color counts based on variation
├── palette.py           Per-region color quantization using Pillow's quantize
├── border_straighten.py Line fitting algorithm to straighten boundaries
├── color_boost.py       Saturation/contrast adjustment using HSV
├── dither.py            Ordered Bayer matrix dithering
├── borders.py           Draw borders at region boundaries
└── light_extract.py     Extract and reapply luminance variations
```

## Known Issues & Experimental Features

- **Light Extraction**: The light extraction feature (flags: `--light-strength`, `--reapply-strength`) is experimental. It can reduce visibility of fine details by removing luminance information. Use `--light-strength 0` to disable it (set to 0.0).
- **Border Straightening**: Works well for most cases, but may over-straighten complex curved boundaries. Adjust `--max-deviation` and `--min-boundary-length` if needed.
```

## Project Status

- ✅ Full resolution segmentation
- ✅ Label downscaling with majority vote
- ✅ Small region cleanup
- ✅ Border straightening with line fitting
- ✅ Per-region color quantization
- ✅ Color boosting
- ✅ Dithering support
- ✅ Border drawing
- ✅ Presets (Arcade, Undertale, Gameboy, Dithered)
- ⚠️ Light extraction (experimental, may need tuning)

## Future Extensions

- Named presets for common styles (Undertale dark, Gameboy monochrome, NES 8-bit, Arcade bright)
- Batch mode to convert multiple photos at once
- Simple GUI (Tkinter) as an alternative to CLI
- Palette locking to keep consistent colors across multiple images
- Alternative segmentation backends (`cv2.watershed`) for challenging cases
- Interactive boundary editor to manually adjust regions

## License

This project is provided as-is for personal and educational use.
