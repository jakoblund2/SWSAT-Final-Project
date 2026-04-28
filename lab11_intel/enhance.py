import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

# TODO: load data

IMAGE_DIR = Path("lab11_intel/images")

# TODO: LOAD IMAGE
image = Image.open(IMAGE_DIR / "EO-S1A-2026-03-24-001.png")

# TODO: ENHANCE IMAGE
enhancer = ImageEnhance.Brightness(image)
image = enhancer.enhance(1.5)

# TODO: SAVE IMAGE
image.save(IMAGE_DIR / "EO-S1A-2026-03-24-001_enhanced.png")



