import numpy as np

from config import MIN_REGION_SIZE


# Takes labels (segmented image) array and downscales it
def resize_labels(labels: np.ndarray, width: int, height: int) -> np.ndarray:
    input_height, input_width = labels.shape
    output = np.zeros((height, width), dtype=np.int32)

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
def cleanup_small_regions(image, labels, min_region_size=MIN_REGION_SIZE):
    changed = True
    while changed:
        changed = False
        counts = np.bincount(labels.ravel())
        region_colors = {}
        for label in range(len(counts)):
            if counts[label] == 0:
                continue
            region_colors[label] = image[labels == label].mean(axis=0)

        for label in range(1, len(counts)):
            if counts[label] == 0 or counts[label] >= min_region_size:
                continue

            region_pixels = np.argwhere(labels == label)
            neighbor_labels = set()
            for y, x in region_pixels:
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < labels.shape[0] and 0 <= nx < labels.shape[1]:
                        neighbor = labels[ny, nx]
                        if neighbor != label:
                            neighbor_labels.add(neighbor)

            if not neighbor_labels:
                continue

            source_color = region_colors[label]
            best_label = min(neighbor_labels, key=lambda n: np.linalg.norm(source_color - region_colors[n]))
            labels[labels == label] = best_label
            changed = True  # re-scan, since counts are now stale

    return labels