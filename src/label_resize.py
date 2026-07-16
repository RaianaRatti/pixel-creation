import numpy as np

from config import MIN_REGION_SIZE


# Takes labels (segmented image) array and downscales it
def resize_labels(labels: np.ndarray, width: int, height: int) -> np.ndarray:
    input_width, input_height = labels.shape
    output = np.zeroes((width, height), dtype=np.int32)

    x_scale = input_width / width
    y_scale = input_height / height

    for y in range(height):
        for x in range(width):
            x_start = int(x * x_scale)
            x_end = int((x+1) * x_scale)

            y_start = int(y * y_scale)
            y_end = int((y+1) * y_scale)

            block_labels = labels[y_start:y_end, x_start:x_end]

            dominant_label = np.bincount(block_labels.ravel()).argmax()
            output[y,x] = dominant_label
    
    return output

# Merges tiny areas (smaller than MIN_REGION_SIZE)
def cleanup_small_regions(image: np.ndarray, labels: np.ndarray, min_region_size: int = MIN_REGION_SIZE):
    counts = np.bincount(labels.ravel()) # map: label (region) -> # of pixels in label
    region_colors = {}

    # Compute average color of each region
    for label in range(len(counts)):
        if counts[label] == 0:
            continue

        pixels = image[labels == label]
        region_colors[label] = pixels.mean(axis=0)

    # Process tiny regions
    for label in range(1, len(counts)):
        if counts[label] >= min_region_size:
            continue

        region_pixels = np.argwhere(labels == label) # coordinates where pixel's label is (current) label
        neighbor_labels = set() # empty set

        for y, x in region_pixels:
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny = y + dy
                nx = x + dx

                if (0 <= ny < labels.shape[0] and 0 <= nx < labels.shape[1]): # make sure in image
                    neighbor = labels[ny, nx]

                    if neighbor != label: # ignore neighboring pixels with same label
                        neighbor_labels.add(neighbor)

            if not neighbor_labels: # set empty- label of pixel does not touch any other label (except 0)
                continue

            source_color = region_colors[label]

            best_label = None
            best_distance = float("inf")

            for neighbor in neighbor_labels:
                dist = np.linalg.norm(source_color - region_colors[neighbor])

                if dist < best_distance:
                    best_distance = dist
                    best_label = neighbor

            labels[labels == label] = best_label
        
        return labels