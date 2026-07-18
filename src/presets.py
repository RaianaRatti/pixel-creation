PRESETS = {
    "arcade": {
        "description": "Bright, Saturated Arcade Look",
        "min_colors_per_region": 1,
        "max_colors_per_region": 6,
        "saturation": 1.8,
        "contrast": 1.5,
    },
    "simple": {
        "description": "Dark, Restrained Undertale Style",
        "min_colors_per_region": 1,
        "max_colors_per_region": 4,
        "saturation": 1.4,
        "contrast": 1.2,
    },
    "gameboy": {
        "description": "Monochrome Gameboy Style",
        "min_colors_per_region": 1,
        "max_colors_per_region": 1,
        "saturation": 0.0,
    },
    "dithered": {
        "description": "Textured Retro with Dithering",
        "min_colors_per_region": 1,
        "max_colors_per_region": 3,
        "dither": True,
        "dither_strength": 0.12,
    },
}


def get_preset(name):
    return PRESETS.get(name)


def list_presets():
    return [(name, PRESETS[name]["description"]) for name in PRESETS.keys()]
