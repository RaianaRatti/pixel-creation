# main.py ---------------------------------------
SCALE = 16 # scale to downscale image
TOTAL_COLORS = 20 # number of colors to allow in quantization

# segmentation.py ---------------------------------------
SPATIAL_RADIUS = 10 # similar regions closer than this found in segmentation are grouped together
COLOR_RADIUS = 20 # similar regions closer in color than this found in segmentation are grouped together

# label_resize.py ---------------------------------------
MIN_REGION_SIZE = 2 # regions found in segmentation smaller than this get merged with closest larger region

# color_budget.py ---------------------------------------
MIN_COLORS_PER_REGION = 1 # min colors per region in segmented region
MAX_COLORS_PER_REGION = 4 # max colors per region in segmented region

# color_boost.py ---------------------------------------
SATURATION = 1.5
CONTRAST = 1.3

# dither.py ---------------------------------------
STRENGTH = 0.08

# borders.py ---------------------------------------
BORDER_SIZE = 2
BORDER_COLOR = "black"

# preset.py ---------------------------------------
PRESET = None