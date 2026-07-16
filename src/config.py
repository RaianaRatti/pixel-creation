# main.py ---------------------------------------
SCALE = 5 # scale to downscale image
NUM_COLORS = 16 # number of colors to allow in quantization

# segmentation.py ---------------------------------------
SPATIAL_RADIUS = 1 # similar regions closer than this found in segmentation are grouped together
COLOR_RADIUS = 1 # similar regions closer in color than this found in segmentation are grouped together

# label_resize.py ---------------------------------------
MIN_REGION_SIZE = 1 # regions found in segmentation smaller than this get merged with closest larger region