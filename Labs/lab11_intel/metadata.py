import json
from pathlib import Path
from PIL import Image, ImageStat

IMAGE_DIR = Path(__file__).parent / "Input_Image"
METADATA_PATH = Path(__file__).parent / "metadata_json" / "metadata.json"

records = []

for image_path in sorted(IMAGE_DIR.glob("*.png")):
    if "_enhanced" in image_path.name:
        continue

    image = Image.open(image_path)
    stat = ImageStat.Stat(image)

    brightness = round(stat.mean[0] / 255, 3)
    contrast = round(stat.stddev[0] / 255, 3)
    quality_score = round((brightness + contrast) / 2, 3)
    is_visible = brightness > 0.1
    is_anomaly = contrast > 0.8
    priority = 1 if quality_score > 0.5 else (2 if quality_score > 0.2 else 3)

    enhanced_path = IMAGE_DIR / f"{image_path.stem}_enhanced.png"

    records.append({
        "eo_product_id": image_path.stem,
        "image_path": str(image_path),
        "quality_score": quality_score,
        "brightness": brightness,
        "contrast": contrast,
        "is_visible": is_visible,
        "is_anomaly": is_anomaly,
        "priority": priority,
        "enhanced_path": str(enhanced_path)
    })

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(f"Saved metadata for {len(records)} products to {METADATA_PATH}")



