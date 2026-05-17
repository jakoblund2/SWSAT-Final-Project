import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

# TODO: load data

IMAGE_DIR = Path(__file__).parent / "Input_Image"

# TODO: LOAD IMAGE, ENHANCE IMAGE, FILTER IMAGE, SAVE IMAGE
for image_path in IMAGE_DIR.glob("*.png"):
    if "_enhanced" in image_path.name:
        continue
    image = Image.open(image_path)
    image = ImageEnhance.Contrast(image).enhance(3.0)
    #image = image.filter(ImageFilter.FIND_EDGES)
    image.save(IMAGE_DIR / f"{image_path.stem}_enhanced.png")



