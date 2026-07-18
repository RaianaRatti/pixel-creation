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
from light_extract import extract_light_variation, resize_light_diff, reapply_light_variation


def run_pipeline(
    image,
    width,
    height,
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
    max_deviation,
    min_boundary_length,
    dither,
    dither_strength,
    scale,
    blur_radius,
    light_strength,
    reapply_strength,
    preset=None,
):
    image, light_diff = extract_light_variation(image, blur_radius=blur_radius, strength=light_strength) # light

    labels_full = segment_image(
        image,
        segmentation_max_dimension=segmentation_max_dimension,
        spatial_radius=spatial_radius,
        color_radius=color_radius,
    )

    block_image = downscale_image(image, width, height)
    block_light_diff = resize_light_diff(light_diff, width, height) # light

    block_labels = resize_labels(labels_full, width, height)
    block_labels = cleanup_small_regions(np.array(block_image), block_labels, min_region_size)
    block_labels = straighten_borders(block_labels, max_deviation=max_deviation, min_boundary_length=min_boundary_length)

    budgets = allocate_color_budget(
        np.array(block_image),
        block_labels,
        min_colors_per_region=min_colors_per_region,
        max_colors_per_region=max_colors_per_region,
    )

    pixel_image = quantize_regions(np.array(block_image), block_labels, budgets)
    pixel_image = Image.fromarray(pixel_image)
    pixel_image = reapply_light_variation(pixel_image, block_light_diff, strength=reapply_strength) # light

    pixel_image = boost_colors(pixel_image, saturation=saturation, contrast=contrast)

    if dither:
        pixel_image = ordered_dither(pixel_image, strength=dither_strength)

    pixel_image = upscale_image(pixel_image, scale)

    if borders:
        pixel_image = draw_region_borders(
            pixel_image,
            block_labels,
            scale=scale,
            border_size=border_size,
            border_color=border_color,
        )

    return pixel_image