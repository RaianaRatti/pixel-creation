# Pixel Room Converter - Project Plan

## Goal

Build a tool that takes a real photo of a room, bedroom, or location and turns it into a pixel art version with a strong retro arcade or video game look, similar to the style of Undertale rooms. The output should have:

- User-chosen pixel grid dimensions (for example 32x24 or 64x48 blocks)
- Clear, visible borders between pixel blocks
- Bright, saturated, "popping" colors
- A limited color palette, like old game sprites, instead of full photo color range

Everything runs locally with plain code. No external APIs, no paid services, no network calls.

## Core Idea

The pipeline is a sequence of image processing steps, all done with standard image libraries (Pillow, NumPy, and optionally OpenCV). No machine learning model or web service is needed for the base version.

Pipeline order:

1. Load the input image
2. Downscale the image to the target pixel grid size (this is what actually creates the "pixel art" blocks)
3. Reduce the color palette (quantization) to a small fixed number of colors, similar to 8 bit or 16 bit game palettes
4. Boost saturation and contrast so colors look vivid instead of washed out
5. Optionally apply dithering so color transitions look more like retro sprite shading instead of flat blur
6. Upscale back up using nearest neighbor scaling (this keeps hard, blocky pixel edges instead of blur)
7. Draw grid lines / borders between each pixel block to get the clean tile look
8. Save the final image

## Tech Stack

- Python 3.10+
- Pillow for image loading, resizing, saving
- NumPy for array based pixel manipulation (palette mapping, dithering math)
- Optional: OpenCV, only if we need faster color quantization (k-means clustering), otherwise Pillow's built in quantize is enough
- No API keys, no internet access required at runtime

## Project Structure

```
pixel-room-converter/
  PLAN.md
  README.md
  requirements.txt
  src/
    main.py              entry point, handles CLI arguments
    pipeline.py          runs the full conversion pipeline in order
    resize.py            downscale/upscale logic
    palette.py           color quantization logic
    color_boost.py       saturation/contrast adjustment
    dither.py            ordered (Bayer) dithering implementation
    borders.py           draws grid lines between pixel blocks
    presets.py           predefined style presets (see below)
  examples/
    input/               sample room photos for testing
    output/               generated results for comparison
  tests/
    test_resize.py
    test_palette.py
    test_pipeline.py
```

## CLI Design

Basic usage:

```
python src/main.py --input room.jpg --output room_pixel.png --width 48 --height 32
```

Arguments:

- `--input` : path to source image (required)
- `--output` : path to save result (required)
- `--width`, `--height` : number of pixel blocks across and down (required, this is the "pixel dimensions" the user chooses)
- `--colors` : size of the reduced color palette, default 16
- `--saturation` : multiplier for color saturation boost, default 1.4
- `--contrast` : multiplier for contrast boost, default 1.2
- `--border-size` : thickness in final pixels of the grid lines between blocks, default 2
- `--border-color` : color of the grid lines, default black
- `--dither` : on/off flag to enable ordered dithering, default off
- `--scale` : final output size multiplier per block, default 16 (so a 48x32 grid becomes a 768x512 image)
- `--preset` : optional named preset that sets several of the above at once (see Presets)

## Step Details

### 1. Downscaling

Resize the source photo down to `width x height` blocks using area averaging (Pillow's `Image.resize` with `Image.BOX` or `Image.LANCZOS` for the shrink step). Area averaging gives smoother, more representative colors per block than simple nearest neighbor shrink, which matters a lot for how a room reads once pixelated.

### 2. Color Quantization

Reduce the shrunk image to a fixed number of colors using Pillow's `Image.quantize(colors=N, method=Image.MEDIANCUT)` or a custom k-means clustering in NumPy for more control over palette choice. This is the step that gives the "16 color game palette" feel instead of a photographic gradient.

Optional addition later: let the user supply a fixed custom palette file (a small PNG or list of hex colors) so results can match a specific game's palette, such as an Undertale-style dark palette with a few bright accent colors.

### 3. Saturation and Contrast Boost

Convert to HSV, multiply the saturation channel, then convert back to RGB. Apply a simple contrast stretch afterward. This step is what makes colors "pop" instead of looking like a plain downsized photo.

### 4. Dithering (optional)

Implement ordered dithering (Bayer matrix, 4x4 or 8x8) as a NumPy operation applied before or during quantization. This adds a textured, retro look to color transitions instead of flat blocks, similar to older 8 bit console games.

### 5. Upscaling

Scale the quantized, color boosted grid back up using `Image.NEAREST` only. This is critical: any other resampling method will blur the hard pixel edges and ruin the effect.

### 6. Border Drawing

After upscaling, draw grid lines directly using Pillow's `ImageDraw`, placing lines at every block boundary (every `scale` pixels). Border thickness and color are configurable. This is what gives the clean "tile" look seen in games like Undertale, where each pixel block reads as a distinct unit.

## Presets

Ship a few named presets in `presets.py` so the user does not have to tune every parameter manually:

- `undertale` : dark background palette, 16 colors, strong border, high saturation on accent colors
- `gameboy` : 4 shade green monochrome palette
- `nes` : 54 color NES-style palette, no dithering
- `arcade-bright` : 32 colors, high saturation, thin border, no dithering

## Testing Plan

- Unit tests for each module in isolation (resize produces correct output dimensions, palette produces exactly N colors, borders appear at correct pixel offsets)
- A small set of sample room photos in `examples/input/` used to visually check output quality after each pipeline change
- Manual visual comparison against real Undertale room screenshots to judge style accuracy (this part is subjective, so it stays manual rather than automated)

## Milestones

1. Basic pipeline working end to end: input photo to blocky pixel image, no color reduction, no borders
2. Add color quantization and saturation boost
3. Add border drawing
4. Add dithering option
5. Add presets and polish CLI
6. Write README with example before/after images and usage instructions

## Possible Future Extensions (not required for v1)

- Simple GUI (Tkinter) instead of CLI only, still no external services
- Batch mode to convert a whole folder of photos at once
- Palette lock to a specific existing image so multiple outputs share one consistent look
- Edge detection pass to darken structural lines (walls, furniture edges) before pixelation, to make room layouts read more clearly at low pixel counts