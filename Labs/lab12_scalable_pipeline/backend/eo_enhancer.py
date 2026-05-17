from PIL import Image, ImageEnhance


def enhance_image(image_path, enhanced_path):
    image = Image.open(image_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(3.0)
    image.save(enhanced_path)
    return image