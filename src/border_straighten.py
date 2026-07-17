import numpy as np
from collections import defaultdict

from config import MAX_DEVIATION, MIN_BOUNDARY_LENGTH

def _fit_and_snap(points, span_axis):
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


def straighten_borders(labels, max_deviation=MAX_DEVIATION, min_boundary_length=MIN_BOUNDARY_LENGTH):
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