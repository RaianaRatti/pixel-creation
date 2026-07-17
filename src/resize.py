from PIL import Image

def downscale_image(image, width: int, height: int, method: str = "box") -> Image.Image:
    if method.lower() == "lanczos":
        return image.resize((width, height), Image.Resampling.LANCZOS)
    else:
        return image.resize((width, height), Image.Resampling.BOX)

def upscale_image(image, scale: int):
    new_width = image.width * scale
    new_height = image.height * scale

    return image.resize((new_width, new_height), Image.Resampling.NEAREST)