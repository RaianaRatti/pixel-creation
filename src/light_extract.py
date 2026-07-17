import numpy as np
import cv2
from PIL import Image

from config import BLUR_RADIUS, STRENGTH


def extract_light_variation(image: Image.Image, blur_radius: int = BLUR_RADIUS, strength: float = STRENGTH):
    rgb = np.asarray(image, dtype=np.float32)

    # Standard luminance weights (matches how the eye perceives brightness)
    luminance = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114

    # Large blur = estimate of the ambient lighting pattern only, real
    # object edges are too high-frequency to survive a blur this big
    ksize = blur_radius * 2 + 1  # cv2 wants an odd kernel size, not a radius
    base_luminance = cv2.GaussianBlur(luminance, (ksize, ksize), 0)

    light_diff = (luminance - base_luminance) * strength

    # Remove the light difference from every channel equally, so hue and
    # saturation are preserved -- only the brightness gradient is flattened
    flattened = rgb - light_diff[..., None]
    flattened = np.clip(flattened, 0, 255).astype(np.uint8)

    return Image.fromarray(flattened, mode="RGB"), light_diff

def resize_light_diff(light_diff: np.ndarray, width: int, height: int) -> np.ndarray:
    return cv2.resize(light_diff.astype(np.float32), (width, height), interpolation=cv2.INTER_AREA)


def reapply_light_variation(image: Image.Image, light_diff: np.ndarray, strength: float = 1.0):
    rgb = np.asarray(image, dtype=np.float32)
    result = rgb + (light_diff[..., None] * strength)
    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")