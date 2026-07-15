# Pixel Room Converter - Implementation Steps

Step by step build order. Each stage produces something testable before moving to the next.

## Stage 1: Project setup

1. Create the folder structure from PLAN.md (`src/`, `examples/input/`, `examples/output/`, `tests/`).
2. Set up a virtual environment and `requirements.txt` with `Pillow` and `numpy`.
3. Drop 2-3 real room photos into `examples/input/` for testing throughout.
4. Write a minimal `main.py` that just loads an image and saves it back out unchanged. This confirms your environment and paths work before any real logic exists.

## Stage 2: Downscaling (the core pixelation step)

1. In `resize.py`, write `downscale(image, width, height)` that resizes the source image to the target block grid using `Image.BOX` or `Image.LANCZOS`.
2. Write `upscale(image, scale)` that resizes back up using `Image.NEAREST` only. Do not build this to accept other resampling modes, since anything else will blur the blocks.
3. Test by running downscale then upscale immediately with no other processing. You should already see a basic pixelated version of the room. This is your baseline before color work starts.

## Stage 3: Color quantization

1. In `palette.py`, write `quantize(image, num_colors)` using `Image.quantize(colors=num_colors, method=Image.MEDIANCUT)`.
2. Run it on the downscaled image (before upscaling) and check the result. Try a few values like 8, 16, 32 to see how the room reads at each level.
3. If Pillow's built in quantizer gives poor results on your test photos, this is the point to swap in a custom k-means version using NumPy instead. Do not build the custom version first. Try the simple option and only replace it if needed.

## Stage 4: Saturation and contrast boost

1. In `color_boost.py`, write `boost_saturation(image, factor)`. Convert the image to HSV with `image.convert("HSV")`, split channels, multiply the S channel by `factor`, clip to valid range, merge, convert back to RGB.
2. Write `boost_contrast(image, factor)` using `ImageEnhance.Contrast`.
3. Apply these right after quantization, before upscaling. Compare before and after on your test photos to confirm colors look more vivid and less like a plain photo.

## Stage 5: Borders

1. In `borders.py`, write `draw_grid(image, block_size, border_size, border_color)`.
2. This runs after upscaling. Use `ImageDraw` to draw horizontal and vertical lines every `block_size` pixels across the full image.
3. Test on the upscaled output from Stage 4. At this point the image should already look close to the final Undertale style tile look.

## Stage 6: Dithering (optional, do this after everything else works)

1. In `dither.py`, implement a Bayer matrix (start with 4x4) as a NumPy array.
2. Write `ordered_dither(image, matrix)` that applies the threshold pattern to each color channel before or during quantization.
3. Add this as an optional step so you can turn it on and off and compare. Some rooms will look better with it, some without.

## Stage 7: Wire it into one pipeline

1. In `pipeline.py`, write a single `run_pipeline(image, config)` function that calls the steps in order: downscale, quantize, boost saturation, boost contrast, optional dither, upscale, draw grid.
2. `config` should be a simple dataclass or dict holding all the parameters (width, height, colors, saturation, contrast, border size, border color, dither on/off, scale).
3. Test the full pipeline on all your sample photos in one run.

## Stage 8: CLI

1. In `main.py`, use `argparse` to expose all the parameters from PLAN.md's CLI design.
2. Parse arguments, build the `config`, load the input image, call `run_pipeline`, save to the output path.
3. Run it a few times with different flag combinations to confirm every argument actually changes the output.

## Stage 9: Presets

1. In `presets.py`, define a dictionary of named presets (`undertale`, `gameboy`, `nes`, `arcade-bright`), each mapping to a config.
2. Add a `--preset` flag to `main.py` that loads a preset's values as defaults, still overridable by explicit flags.

## Stage 10: Tests and polish

1. Write the unit tests listed in PLAN.md: confirm `downscale` returns the exact requested dimensions, confirm `quantize` returns exactly N colors, confirm grid lines appear at the correct pixel offsets.
2. Run the full pipeline on all sample photos, save results in `examples/output/`, and do a visual pass comparing against real Undertale screenshots.
3. Write the README with usage instructions and a couple of before/after image pairs.