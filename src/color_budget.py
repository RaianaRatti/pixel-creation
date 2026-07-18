import numpy as np

def allocate_color_budget(
        image,
        labels,
        min_colors_per_region,
        max_colors_per_region
):
    counts = np.bincount(labels.ravel())
    variation_scores = {}

    for label in range(1, len(counts)):
        if counts[label] == 0:
            continue

        pixels = image[labels == label]
        variation = pixels.std(axis=0).mean()
        variation_scores[label] = variation

    if not variation_scores:
        return {}

    # Normalize variation to [0, 1] range
    min_var = min(variation_scores.values())
    max_var = max(variation_scores.values())

    budgets = {}
    for label, variation in variation_scores.items():
        if max_var == min_var:
            normalized = 0.5
        else:
            normalized = (variation - min_var) / (max_var - min_var)

        # Map normalized variation to color range [min_colors_per_region, max_colors_per_region]
        n_colors = round(min_colors_per_region + normalized * (max_colors_per_region - min_colors_per_region))
        budgets[label] = n_colors

    return budgets