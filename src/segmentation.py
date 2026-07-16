from PIL import Image
import cv2
import numpy as np

from config import SPATIAL_RADIUS, COLOR_RADIUS

def segment_image(
        image: Image.image,
        segmentation_max_dimension: int,
        spatial_radius: int = SPATIAL_RADIUS,
        color_radius: int = COLOR_RADIUS
):
    # 1. Resize image so longest side is segmentation_max_dimension
    width, height = image.size
    longest_side = max(width, height)

    if longest_side > segmentation_max_dimension:
        scale = segmentation_max_dimension / longest_side
        new_width = int(width * scale)
        new_height = int(width * scale)

        image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 2. Convert RGB to BGR
    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 3. Combines pixels that are close and same color
    flattened = cv2.pyrMeanShiftFiltering(image_bgr, sp=spatial_radius, sr=color_radius)

    # 4. Find unique colors remaining in flattened image
    unique_colors = np.unique(flattened.reshape(-1, 3), axis=0)

    # 5. Binary mask for every unique color
    height, width = flattened[:2]

    labels = np.zeroes((height, width), dtype=np.int32)
    next_label = 1

    for color in unique_colors:
        mask = np.all(flattened == color, axis=-1).astype(np.uint8)
        num_components, component_labels = cv2.connectedComponents(mask, connectivity=4)
        
        for component_id in range(1, num_components):
            labels[component_id == component_labels] = next_label
            next_label += 1
    
    return labels