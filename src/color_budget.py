import numpy as np

from config import TOTAL_COLORS, MIN_COLORS_PER_REGION, MAX_COLORS_PER_REGION

def allocate_color_budget(
        image, 
        labels, 
        total_colors = TOTAL_COLORS, 
        min_colors_per_region = MIN_COLORS_PER_REGION, 
        max_colors_per_region = MAX_COLORS_PER_REGION
):
    counts = np.bincount(labels.ravel())
    variation_scores = {}

    for label in range(1,len(counts)):
        if counts[label] == 0:
            continue

        pixels = image[labels == label]

        variation = pixels.std(axis=0).mean()
        size = counts[label]

        # number of colors region gets depends on 1. variation of color in region 2. size of region
        variation_scores[label] = variation * size

    budgets = {
        label: min_colors_per_region for label in variation_scores
    }

    remaining = total_colors - len(budgets) * min_colors_per_region
    total_score = sum(variation_scores.values()) # sum of all variations

    # finds region that needs variation most and adds to their budget
    for label in budgets:
        if total_score > 0:
            # divides variation into percentage, cumulative variation of all regions = 100%
            extra = round(remaining * variation_scores[label] / total_score)
        else:
            extra = 0

        budgets[label] += extra
        budgets[label] = max(1, min(budgets[label], max_colors_per_region))

    return budgets