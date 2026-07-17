"""
Snaps noisy, jagged region boundaries (from segmentation + majority-vote
downscaling) to the nearest consistent straight or uniform-slope diagonal
line, so borders read as clean architectural lines instead of stray
one-pixel zig-zags.

The key idea: a "real" straight or diagonal boundary shows up as a set of
transition points that are almost collinear when you plot them. We fit a
line to those points and re-assign only the few blocks that don't already
sit on that line -- blocks far from the original boundary are never
touched, so this can't leak into the interior of a region.
"""

import numpy as np
from collections import defaultdict


def _fit_and_snap(points, span_axis):
    """
    points: list of (independent, dependent) coordinate pairs describing
            where a boundary crosses, e.g. (row, col) for a boundary that
            is mostly vertical (col varies slowly as row increases).
    span_axis: dict mapping each independent coordinate -> list of observed
               dependent coordinates (there can be more than one crossing
               per row/col if the boundary is not simple).
    Returns: dict {independent_coord: snapped_dependent_coord}, using a
             least-squares line fit through the observed points, rounded
             to the nearest integer so the result is a real uniform
             staircase (e.g. slope 2/3 -> 2 pixels, then 1, then 2, ...)
             rather than a fractional line.
    """
    pts = np.array(points, dtype=np.float64)
    x = pts[:, 0]
    y = pts[:, 1]

    A = np.vstack([x, np.ones_like(x)]).T
    # Least squares line fit: y = m*x + b
    m, b = np.linalg.lstsq(A, y, rcond=None)[0]

    snapped = {}
    for xv in span_axis:
        snapped[xv] = int(round(m * xv + b))
    return snapped


def _boundary_points(labels, vertical):
    """
    Collect boundary crossing points between every pair of adjacent
    regions.

    vertical=True:  scans left/right neighbors -> boundaries that run
                    roughly top-to-bottom (col is a function of row).
    vertical=False: scans up/down neighbors -> boundaries that run
                    roughly left-to-right (row is a function of col).

    Returns dict keyed by (left_or_top_label, right_or_bottom_label) in
    the *actual* orientation seen at that point (not sorted), each value a
    list of (independent_coord, dependent_coord) pairs plus a running vote
    for canonical orientation.
    """
    h, w = labels.shape
    raw = defaultdict(list)  # frozenset({a,b}) -> list of (indep, dep, a, b)

    if vertical:
        # boundary is col = f(row): indep=row, dep=col
        for y in range(h):
            for x in range(w - 1):
                a, b = int(labels[y, x]), int(labels[y, x + 1])
                if a != b:
                    raw[frozenset((a, b))].append((y, x, a, b))
    else:
        # boundary is row = f(col): indep=col, dep=row
        for y in range(h - 1):
            for x in range(w):
                a, b = int(labels[y, x]), int(labels[y + 1, x])
                if a != b:
                    raw[frozenset((a, b))].append((x, y, a, b))

    return raw


def straighten_borders(labels, max_deviation=2, min_boundary_length=4):
    """
    labels: 2D int array of block-level region labels.
    max_deviation: how many blocks a boundary crossing may move from its
                   original position. Keeps the effect local -- it can
                   straighten a jitter, it can't redraw a whole region.
    min_boundary_length: boundaries shorter than this are left alone,
                   there aren't enough points to trust a line fit.

    Returns a new label array with straightened boundaries.
    """
    out = labels.copy()
    h, w = labels.shape

    for vertical in (True, False):
        raw = _boundary_points(out, vertical=vertical)

        for pair, occurrences in raw.items():
            if len(occurrences) < min_boundary_length:
                continue

            # Canonical orientation: which label is more often on the
            # left/top across this whole boundary. Points where the local
            # order is flipped (a small notch) get re-expressed in the
            # canonical order so the line fit sees one consistent boundary,
            # not two interleaved ones.
            a, b = tuple(pair)
            votes_a_first = sum(1 for (_, _, la, lb) in occurrences if la == a)
            canon_left, canon_right = (a, b) if votes_a_first >= len(occurrences) / 2 else (b, a)

            indep_coords = defaultdict(list)
            fit_points = []
            for (indep, dep, la, lb) in occurrences:
                # dep = column index of the LEFT/TOP block of the crossing.
                # If locally flipped, the crossing for canon_left is one
                # step later.
                if la == canon_left:
                    crossing = dep
                else:
                    crossing = dep - 1
                fit_points.append((indep, crossing))
                indep_coords[indep].append(crossing)

            unique_indep = sorted(indep_coords)
            if len(unique_indep) < min_boundary_length:
                continue

            snapped = _fit_and_snap(fit_points, unique_indep)

            for indep in unique_indep:
                orig_crossings = indep_coords[indep]
                target = snapped[indep]

                for orig in orig_crossings:
                    if abs(target - orig) > max_deviation:
                        continue  # too far off the real boundary, skip

                    lo, hi = sorted((orig, target))
                    for pos in range(lo, hi + 1):
                        if vertical:
                            row, col = indep, pos
                        else:
                            row, col = pos, indep

                        if row < 0 or row + 1 >= h or col < 0 or col + 1 >= w:
                            continue  # out of grid bounds (line fit extrapolated past the edge)

                        if vertical:
                            cur, nxt = out[row, col], out[row, col + 1]
                        else:
                            cur, nxt = out[row, col], out[row + 1, col]

                        if cur not in (canon_left, canon_right) and nxt not in (canon_left, canon_right):
                            continue  # this cell belongs to some other region entirely, don't touch it

                        new_label = canon_left if pos <= target else canon_right
                        out[row, col] = new_label

    return out