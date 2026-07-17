from PIL import ImageDraw


def draw_region_borders(image, labels, scale, border_size=2, border_color="black"):
    draw = ImageDraw.Draw(image)
    height, width = labels.shape
    half = border_size / 2

    for y in range(height):
        for x in range(width):
            label = labels[y, x]

            # right neighbor
            if x + 1 < width and labels[y, x + 1] != label:
                bx = (x + 1) * scale
                y0 = y * scale
                y1 = (y + 1) * scale
                draw.line(
                    [(bx, y0), (bx, y1)],
                    fill=border_color,
                    width=border_size,
                )

            # bottom neighbor
            if y + 1 < height and labels[y + 1, x] != label:
                by = (y + 1) * scale
                x0 = x * scale
                x1 = (x + 1) * scale
                draw.line(
                    [(x0, by), (x1, by)],
                    fill=border_color,
                    width=border_size,
                )

    return image