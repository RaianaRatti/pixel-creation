# Pixel Room Converter - Project Plan

## Goal

- Take a real photo of a room, bedroom, or location and turn it into pixel art with a strong retro arcade or video game look, similar to Undertale rooms
- User picks the pixel grid dimensions (for example 32x24 or 64x48 blocks)
- Colors are chosen per object, not globally, so a busy object like a sofa does not eat up most of the color budget and end up looking noisy instead of flat and blocky
- Optional black borders drawn around each detected object, not a uniform grid. Two objects sitting next to each other share a single border line, not two
- Bright, saturated, "popping" colors
- Everything runs locally with plain code, using well established local libraries. No external APIs, no paid services, no network calls, no downloaded ML models

## Core Idea

- Segmentation needs to be reliable, so instead of a hand written region merging algorithm, this uses OpenCV's built in classical segmentation tools. These are not machine learning models, they are standard, decades old computer vision algorithms shipped inside the `cv2` library, and they run entirely on your machine
- Segmentation also needs to happen on the real photo before it gets shrunk down to the tiny block grid, since a 48x32 block grid is too coarse to find clean object edges. The block grid is built afterward from the full resolution segmentation result
- Pipeline order:
  - Load the input image
  - Run segmentation on the full resolution photo using `cv2.pyrMeanShiftFiltering` followed by `cv2.connectedComponents`, producing a full resolution region label map
  - Downscale the color image to the target block grid size using area averaging, and separately downscale the label map to the same grid size using a majority vote per block, since labels cannot be averaged like colors
  - For each region, measure its internal color variation and assign it a share of the total color budget
  - Quantize each region independently, using only that region's own pixels and its own assigned color count
  - Reassemble the full block grid from all the quantized regions
  - Boost saturation and contrast so colors look vivid
  - Optionally apply dithering for a more textured retro shading look
  - Upscale back up using nearest neighbor scaling to keep hard pixel edges
  - Optionally draw a black border at the region boundaries already found during segmentation
  - Save the final image

## Tech Stack

- Python 3.10+
- Pillow, for image loading, resizing, saving, drawing borders, and per-region color quantization
- NumPy, for array based pixel manipulation, majority vote downscaling of the label map, and color variation math
- OpenCV (`opencv-python` package, imported as `cv2`), for reliable segmentation using `cv2.pyrMeanShiftFiltering` and `cv2.connectedComponents`. Pillow has no segmentation tools of its own, this is why OpenCV is needed specifically for this step
- No API keys, no internet access required at runtime, no model weight downloads

## Project Structure

```
pixel-room-converter/
  PLAN.md
  README.md
  requirements.txt
  src/
    main.py              entry point, handles CLI arguments
    pipeline.py          runs the full conversion pipeline in order
    resize.py            downscale/upscale logic, uses Pillow's Image.resize and Image.NEAREST
    segmentation.py      full resolution segmentation, uses cv2.pyrMeanShiftFiltering and cv2.connectedComponents
    label_resize.py      majority vote downscaling of the label map to block grid resolution, uses NumPy
    color_budget.py      decides how many colors each region gets based on its internal variation
    palette.py           quantizes each region independently, uses Image.quantize per region crop
    color_boost.py       saturation/contrast adjustment, uses Image.convert("HSV") and ImageEnhance.Contrast
    dither.py            ordered (Bayer) dithering implementation, NumPy only
    borders.py           draws borders at region boundaries, uses ImageDraw
    presets.py           predefined style presets (see below)
  examples/
    input/               sample room photos for testing
    output/               generated results for comparison
  tests/
    test_resize.py
    test_segmentation.py
    test_label_resize.py
    test_color_budget.py
    test_palette.py
    test_pipeline.py
```

## CLI Design

- Basic usage:
```
python src/main.py --input room.jpg --output room_pixel.png --width 48 --height 32
```
- `--input` : path to source image (required)
- `--output` : path to save result (required)
- `--width`, `--height` : number of pixel blocks across and down (required)
- `--colors` : total color budget shared across the whole image, default 16
- `--min-colors-per-region` : smallest number of colors any single region can be assigned, default 1
- `--max-colors-per-region` : largest number of colors any single region can be assigned, default 6, so no single busy object can eat the entire budget
- `--spatial-radius` : passed directly to `cv2.pyrMeanShiftFiltering` as `sp`, controls how far apart in the image two pixels can be and still merge, default 12
- `--color-radius` : passed directly to `cv2.pyrMeanShiftFiltering` as `sr`, controls how different two colors can be and still merge, default 20
- `--min-region-size` : minimum block count a region must have after downscaling to the block grid before it is merged into its closest neighbor by color distance, default 2, filters out single stray pixel blocks
- `--saturation` : multiplier for color saturation boost, default 1.4
- `--contrast` : multiplier for contrast boost, default 1.2
- `--borders` : on/off flag to enable region borders, default off
- `--border-size` : thickness in final pixels of the border lines, default 2
- `--border-color` : color of the border lines, default black
- `--dither` : on/off flag to enable ordered dithering, default off
- `--scale` : final output size multiplier per block, default 16
- `--segmentation-max-dimension` : the working photo gets resized so its longest side does not exceed this value before running `cv2.pyrMeanShiftFiltering`, default 500, purely for speed since mean shift filtering is slow on large images and the result gets downscaled to the block grid anyway
- `--preset` : optional named preset that sets several of the above at once

## Step Details

- **1. Full Resolution Segmentation** (`segmentation.py`)
  - Resize the input photo so its longest side is `--segmentation-max-dimension` pixels, using `Image.resize` with `Image.LANCZOS`, purely for speed
  - Convert the resized image from a Pillow RGB array to OpenCV's expected format with `cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)`, since OpenCV expects BGR channel order, not RGB
  - Call `cv2.pyrMeanShiftFiltering(src, sp=spatial_radius, sr=color_radius)`. This flattens the image so that pixels close together in both position and color become one exact matching color, effectively pre-grouping the photo into flat colored blobs
  - Find every unique color left in the flattened result with `np.unique(flattened.reshape(-1, 3), axis=0)`
  - For each unique color, build a binary mask with `np.all(flattened == color, axis=-1).astype(np.uint8)`, then run `cv2.connectedComponents(mask, connectivity=4)` on that mask. This splits any same colored but spatially separate areas into distinct labeled regions, so two different colored pillows do not merge just because a third same colored object exists elsewhere in the room
  - Combine the results from every unique color into one master label array, offsetting the label numbers from each call so they stay unique across the whole image
  - The output is a single full resolution 2D NumPy array of integer labels, one label per pixel, matching the resized working image

- **2. Downscaling** (`resize.py`, `label_resize.py`)
  - Downscale the original full color photo to `width x height` blocks using `Image.resize` with `Image.BOX` or `Image.LANCZOS`, same as before, this defines the final block colors
  - Separately downscale the full resolution label map from step 1 to the same `width x height` grid. Since labels are category numbers, not values that can be blended, this cannot use normal image resizing. Instead, for each output block, gather the label map pixels that fall inside that block's region and take the most common label using `np.bincount(block_labels.ravel()).argmax()`
  - The result is a `width x height` grid of region labels lined up one to one with the block grid of colors

- **3. Small Region Cleanup**
  - Count how many blocks belong to each label using `np.bincount` on the flattened label grid
  - Any region with a count below `--min-region-size` gets reassigned to the label of its closest neighboring region by average color distance, so tiny leftover slivers from the mean shift step do not become their own object with their own tiny border

- **4. Color Budget Allocation** (`color_budget.py`)
  - For each region, measure its internal color variation using the standard deviation of the original, non quantized block colors that belong to that region
  - Flat, low variation regions (a plain wall, a single colored cushion) get a color count close to `--min-colors-per-region`
  - Higher variation regions (a patterned rug, a shadowed corner) get more colors, up to `--max-colors-per-region`
  - Distribute the total `--colors` budget across all regions proportionally to their variation and their size, so the sum stays close to the requested total instead of ballooning

- **5. Per-Region Quantization** (`palette.py`)
  - For each region, collect only the block colors belonging to that region, wrap them into a small temporary Pillow image, and call `Image.quantize(colors=assigned_count, method=Image.MEDIANCUT)` on just that temporary image
  - Map the resulting reduced colors back onto that region's blocks in the main block grid
  - This is the key improvement: a busy sofa with only 2 assigned colors gets those colors chosen specifically to represent the sofa's own limited color range, not competing with the rest of the room for shared palette slots

- **6. Reassembly**
  - Walk the block grid and replace each block's color with its region's quantized result from step 5
  - The output at this point is still at block grid resolution with per-region flattened colors

- **7. Saturation and Contrast Boost** (`color_boost.py`)
  - Convert to HSV with `image.convert("HSV")`, split channels, multiply the S channel by `--saturation`, clip to valid range, merge, convert back to RGB
  - Apply `ImageEnhance.Contrast(image).enhance(--contrast)` afterward

- **8. Dithering (optional)** (`dither.py`)
  - Apply an ordered Bayer matrix dither as a NumPy operation, either before or blended into the per-region quantization step in step 5
  - Adds a textured, retro shading look to color transitions inside a region instead of perfectly flat blocks

- **9. Upscaling** (`resize.py`)
  - Scale the block grid back up using `Image.resize` with `Image.NEAREST` only, since any other resampling method blurs the hard pixel edges

- **10. Border Drawing (optional)** (`borders.py`)
  - Reuse the region label grid already computed in steps 1 to 3, no need to redetect boundaries after quantization
  - For every block, compare its region label to the block directly to its right and the block directly below it
  - If the labels differ, record that edge as a border
  - After upscaling, convert each recorded boundary into pixel coordinates and draw it once with `ImageDraw.Draw(image).line(...)`, using `--border-size` and `--border-color`
  - Since each boundary is only checked once, right and down, not all four directions, two touching objects share exactly one line, never a doubled line
  - Controlled by `--borders`. With it off, the pipeline produces plain per-region colored blocks with no outlines

## Presets

- `undertale` : dark background palette, 16 total colors, low max colors per region, region borders on, high saturation on accent colors
- `gameboy` : 4 shade green monochrome palette, 1 color per region, region borders off
- `nes` : 32 total colors, moderate max colors per region, no dithering, region borders on
- `arcade-bright` : 24 total colors, high saturation, region borders on with a thin border size, no dithering

## Testing Plan

- Unit tests for each module in isolation:
  - resize produces correct output dimensions
  - segmentation gives a known flat colored test image exactly one label, and a test image with two clearly different colored halves exactly two labels
  - label_resize picks the correct majority label for a block that straddles two labeled regions
  - color budget allocation gives flat test regions the minimum color count and high variation test regions a higher count, and the total stays close to the requested budget
  - per-region quantization only uses colors that appear within that region's own pixels
  - borders appear only at recorded region boundaries and never as a full grid
- A small set of sample room photos in `examples/input/` used to visually check output quality after each pipeline change
- Manual visual comparison against real Undertale room screenshots to judge style accuracy, kept manual since this part is subjective

## Milestones (Current Status)

1. ✅ Basic pipeline working end to end: input photo to blocky pixel image, one shared color count, no segmentation, no borders
2. ✅ Add full resolution segmentation with cv2.pyrMeanShiftFiltering and cv2.connectedComponents
3. ✅ Add label map downscaling to block grid resolution using majority vote
4. ✅ Add small region cleanup
5. ✅ Add color budget allocation based on per-region variation
6. ✅ Add per-region quantization and reassembly
7. ✅ Add saturation and contrast boost
8. ✅ Add border drawing using the stored region label grid
9. ✅ Add dithering option
10. ✅ Add presets framework (CLI support, implementation pending)
11. ✅ Write README with usage instructions
12. ✅ Add border straightening with line fitting algorithm
13. ⚠️ Add light extraction (experimental, needs tuning - "looks worse" per recent commit)

## Implementation Notes

### Completed Features

**Border Straightening** (`border_straighten.py`)
- Implements least-squares line fitting to straighten jagged region boundaries
- Fits lines to detected boundaries in both vertical and horizontal directions
- Canonical ordering ensures consistent boundary detection even with small notches
- Configurability via `--max-deviation` and `--min-boundary-length`
- Snap points to fitted line within `max_deviation` pixels

**Light Extraction** (`light_extract.py`)
- Extracts luminance patterns from original image using Gaussian blur
- Separates lighting from object color, preserving hue and saturation
- Can be disabled by setting `--light-strength 0`
- ⚠️ May reduce fine detail visibility; currently experimental
- Controlled by `--blur-radius`, `--light-strength`, and `--reapply-strength`

**Color Boosting** (`color_boost.py`)
- Converts to HSV color space and multiplies saturation channel
- Applies contrast enhancement afterward
- Configurable via `--saturation` and `--contrast`

**Dithering** (`dither.py`)
- Ordered Bayer matrix dithering implementation
- Provides textured retro shading effect
- Configurable strength via `--dither-strength`

**CLI & Configuration** (`main.py`, `config.py`)
- Full argument parsing for all pipeline parameters
- Centralized default configuration in `config.py`
- Auto-height calculation from width to preserve aspect ratio
- Support for all pipeline features

### Known Issues

1. **Light Extraction Degradation**: Recent commit "added light extraction but just looks worse" - the feature extracts luminance but may reduce detail visibility. Set `--light-strength 0` to disable.

2. **Requirements Missing**: `requirements.txt` is missing `opencv-python` which is required for segmentation. Should be added.

3. **Presets Not Implemented**: Framework exists in CLI, but preset definitions are not yet implemented in code.

### Architecture Notes

- **Majority Vote Label Downscaling**: Ensures labels remain discrete during downscaling (can't average category IDs)
- **Per-Region Color Budgeting**: Prevents large regions from consuming all colors based on variation metrics
- **Regional Quantization**: Each region quantizes independently, avoiding global palette conflicts
- **Boundary Post-Processing**: Border straightening happens after label downscaling, not before, for better results
- **Two-Phase Lighting**: Light extraction before segmentation preserves segmentation quality; reapplication happens after upscaling

## Next Steps for v1.0 Release

1. **Fix Missing Dependency**: Add `opencv-python` to `requirements.txt`
2. **Implement Presets**: Add preset definitions (Undertale dark, Gameboy monochrome, NES 8-bit, Arcade bright) to CLI
3. **Test & Validate**: Run end-to-end tests on sample images to verify all features work
4. **Light Extraction Tuning**: Either improve the light extraction algorithm to preserve more detail, or document when to disable it
5. **Example Images**: Add before/after examples to the repository for demonstration

## Possible Future Extensions (not required for v1)

- Simple GUI (Tkinter) instead of CLI only, still no external services
- Batch mode to convert a whole folder of photos at once
- Palette lock to a specific existing image so multiple outputs share one consistent look
- Try `cv2.watershed` with markers as an alternative segmentation backend for cases where two touching objects share nearly identical colors and mean shift filtering merges them into one region
- Let the user manually nudge region boundaries or manually merge two regions, for cases where automatic segmentation splits or merges objects in a way that does not match what the user actually wants
- Interactive UI to preview parameter changes before final export