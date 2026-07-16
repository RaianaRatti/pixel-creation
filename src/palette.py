from PIL import Image
import numpy as np

def quantize_regions(image, labels, budgets):
    output = image.copy()

    for label, n_colors in budgets.items():
        pixels = image[labels == label]
 
        if len(pixels) == 0:
            continue

        temp = pixels.reshape((-1,1,3))
        temp_img = Image.fromarray(temp.astype(np.uint8), mode="RGB")

        quantized = temp_img.quantize(colors=n_colors, method=Image.MEDIANCUT).convert("RGB")
        quantized_pixels = np.array(quantized).reshape((-1, 3))

        output[labels == label] = quantized_pixels
    
    return output