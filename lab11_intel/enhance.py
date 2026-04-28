import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

# TODO: load data

IMAGE_DIR = Path(__file__).parent / "Input_Image"

# TODO: LOAD IMAGE
image = Image.open(IMAGE_DIR / "EO-002.png")

# TODO: ENHANCE IMAGE
image = ImageEnhance.Contrast(image).enhance(3.0)

# TODO: FILTER IMAGE
image = image.filter(ImageFilter.FIND_EDGES)

# TODO: SAVE IMAGE
image.save(IMAGE_DIR / "EO-002_enhanced.png")



