import numpy as np
from PIL import Image

from resize import downscale_image, upscale_image
from segmentation import segment_image
from label_resize import resize_labels, cleanup_small_regions
from color_budget import allocate_color_budget
from palette import quantize_regions
from color_boost import boost_colors
from dither import ordered_dither
from border_straighten import straighten_borders
from borders import draw_region_borders
# from borders import draw_region_borders

def run_pipeline(
    image,

    width,
    height,

    colors,
    min_colors_per_region,
    max_colors_per_region,

    spatial_radius,
    color_radius,
    segmentation_max_dimension,

    min_region_size,

    saturation,
    contrast,

    borders,
    border_size,
    border_color,

    dither,

    scale,

    preset=None,
):
    """
    Runs the complete pixel room conversion pipeline.
    """


    # --------------------------------------------------
    # 0. Apply preset (optional)
    # --------------------------------------------------

    # TODO:
    # if preset:
    #     apply_preset(...)


    # --------------------------------------------------
    # 1. Full resolution segmentation
    # --------------------------------------------------

    labels_full = segment_image(
        image,
        segmentation_max_dimension=segmentation_max_dimension,
        spatial_radius=spatial_radius,
        color_radius=color_radius
    )


    # --------------------------------------------------
    # 2. Downscale image into block grid
    # --------------------------------------------------

    block_image = downscale_image(
        image,
        width,
        height
    )


    # --------------------------------------------------
    # 3. Resize label map to block grid
    # --------------------------------------------------

    block_labels = resize_labels(
        labels_full,
        width,
        height
    )


    # --------------------------------------------------
    # 4. Remove tiny regions
    # --------------------------------------------------

    block_labels = cleanup_small_regions(
        np.array(block_image),
        block_labels,
        min_region_size
    )

    block_labels = straighten_borders(block_labels, max_deviation=2, min_boundary_length=4)


    # --------------------------------------------------
    # 5. Allocate color budget
    # --------------------------------------------------

    budgets = allocate_color_budget(
        np.array(block_image),
        block_labels,

        total_colors=colors,
        min_colors_per_region=min_colors_per_region,
        max_colors_per_region=max_colors_per_region
    )


    # --------------------------------------------------
    # 6. Quantize each region independently
    # --------------------------------------------------

    pixel_image = quantize_regions(
        np.array(block_image),
        block_labels,
        budgets
    )

    pixel_image = Image.fromarray(pixel_image)

    # --------------------------------------------------
    # 7. Boost saturation and contrast
    # --------------------------------------------------

    pixel_image = boost_colors(
        pixel_image,
        saturation=saturation,
        contrast=contrast
    )


    # --------------------------------------------------
    # 8. Optional dithering
    # --------------------------------------------------

    if dither:
        pixel_image = ordered_dither(
            pixel_image
        )


    # --------------------------------------------------
    # 9. Upscale with nearest neighbor
    # --------------------------------------------------

    pixel_image = upscale_image(
        pixel_image,
        scale
    )


    # --------------------------------------------------
    # 10. Optional borders
    # --------------------------------------------------

    if borders:
        pixel_image = draw_region_borders(
            pixel_image, block_labels,
            scale=scale, border_size=border_size, border_color=border_color
        )


    return pixel_image