from PIL import Image, ImageEnhance
import numpy as np

def boost_colors(image, saturation, contrast):
    hsv = image.convert("HSV")
    h, s, v = hsv.split()

    s = np.array(s, dtype=np.float32)
    s *= saturation

    s = np.clip(s, 0, 255) # pixel values must stay between 0 and 255 (may not due to line 11)
    s = Image.fromarray(s.astype(np.uint8)) # convert back to PIL image

    hsv = Image.merge("HSV", (h,s,v))

    image = hsv.convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(contrast)
    
    return image