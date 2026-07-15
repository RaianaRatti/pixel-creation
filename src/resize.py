from PIL import Image

def downscale(image, width: int, height: int):
    return image.resize((width, height), Image.Resampling.BOX)

def upscale(image, scale: int):
    new_width = image.width * scale
    new_height = image.height * scale

    return image.resize((new_width, new_height), Image.Resampling.NEAREST)