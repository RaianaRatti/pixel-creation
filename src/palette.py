from PIL import Image
import numpy as np

def quantize_regions(image, labels, budgets):
    output = image.copy()

    for label, n_colors in budgets.items():
        pixels = image[labels == label] # gets pixels where label = current label
 
        if len(pixels) == 0: # safety check
            continue

        temp = pixels.reshape((-1,1,3)) # reshape so one pixel per row (that's what PIL accepts)
        temp_img = Image.fromarray(temp.astype(np.uint8), mode="RGB")

        quantized = temp_img.quantize(colors=n_colors, method=Image.MEDIANCUT).convert("RGB")
        quantized_pixels = np.array(quantized).reshape((-1, 3)) # reshape back so 3 values (RGB) per row

        output[labels == label] = quantized_pixels # change value of pixels in output (which was image.copy)
    
    return output