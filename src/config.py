# main.py ---------------------------------------
SCALE = 16
TOTAL_COLORS = 20

# segmentation.py ---------------------------------------
SPATIAL_RADIUS = 10
COLOR_RADIUS = 20

# label_resize.py ---------------------------------------
MIN_REGION_SIZE = 2

# color_budget.py ---------------------------------------
MIN_COLORS_PER_REGION = 1
MAX_COLORS_PER_REGION = 4

# color_boost.py ---------------------------------------
SATURATION = 1.5
CONTRAST = 1.3

# dither.py ---------------------------------------
STRENGTH = 0.08

# borders.py ---------------------------------------
BORDER_SIZE = 2
BORDER_COLOR = "black"

# border_straighten.py ---------------------------------------
MAX_DEVIATION = 2
MIN_BOUNDARY_LENGTH = 4

# light_extract.py ---------------------------------------
BLUR_RADIUS = 31
LIGHT_STRENGTH = 1.0
REAPPLY_STRENGTH = 0.4

# preset.py ---------------------------------------
PRESET = None