from PIL import Image

def quantize(image, num_colors: int):
    image = image.convert("RGB")
    return image.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)