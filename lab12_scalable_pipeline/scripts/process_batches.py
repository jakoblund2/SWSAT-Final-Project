import json
import os
from PIL import Image, ImageEnhance, ImageStat

def load_metadata(metadata_path):
    """
    Load EO product metadata from a JSON file.
    Each item should contain at least:
    - eo_product_id
    - image_path
    """

    # TODO: open the JSON file
    with open(metadata_path, "r") as f:
        data = json.load(f)
    # TODO: load the data
    # TODO: return the data

    return data

def split_into_batches(data, batch_size):
    """
    Split the full dataset into smaller groups.
    Each group is one batch.
    """

    batches = []

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        batches.append(batch)

    return batches

def enhance_image(image_path, enhanced_path):
    image = Image.open(image_path).convert("L")
    image = ImageEnhance.Contrast(image).enhance(3.0)
    image.save(enhanced_path)
    return image


def process_eo_product(item):
    """
    Process one EO product inside a batch.
    """

    # 1. Get image path from metadata
    image_path = item["image_path"]

    # 2. Create output path for enhanced image
    eo_id = item["eo_product_id"]
    enhanced_path = f"storage/object_store/enhanced/{eo_id}-enhanced.png"

    # 3. Apply enhancement
    # TODO: call enhancement function (e.g., your ML logic from Lab11)
    # example idea:
    # enhance_image(image_path, enhanced_path)
    os.makedirs("storage/object_store/enhanced", exist_ok=True)
    enhanced = enhance_image(image_path, enhanced_path)


    # 4. Compute features from enhanced image (example enhance features)
    # TODO: compute brightness
    # How to:
    # this is from lab11 , calculate brightsness of image
    # think, brightness = average pixel value
    # example logic can be (or you use your own way from your lab11:
    #      stat = ImageStat.Stat(img)
    #      brightness = stat.mean[0] / 255.0
    stat = ImageStat.Stat(enhanced)
    brightness = stat.mean[0] / 255.0

    # TODO: compute contrast
    # HowTo: think,  Contrast = variation of pixel values
    # example: contrast = stat.stddev[0] / 255.0
    contrast = stat.stddev[0] / 255.0

    # 5. Calculate quality score
    # Hint: use brightness and contrast
    # example: calculate quality score with brigtness and contrast
    # most simple way:  quality_score = (brightness + contrast) / 2
    quality_score = (brightness + contrast) / 2

    # 6. Store results in metadata
    item["enhanced_path"] = enhanced_path
    item["brightness"] = brightness
    item["contrast"] = contrast
    item["quality_score"] = quality_score
    item["is_visible"] = quality_score > 0.2

    return item

def assign_priority(item):
    """
    Assign priority based on quality score.
    """

    score = item["quality_score"]

    #these scores are example, 
    #you can adjust the score as quality threshold (rule-based)
    if score > 0.4:
        priority = 1
    elif score > 0.3:
        priority = 2
    else:
        priority = 3

    item["priority"] = priority

    return item

def process_batch(batch, batch_number):
    """
    Process all EO products inside one batch.
    """

    # TODO: print or log batch number
    print(f"Batch {batch_number}")

    processed_batch = []

    for item in batch:
        # TODO: process one EO product
        item = process_eo_product(item)

        # TODO: assign priority based on score
        item = assign_priority(item)

        # TODO: log result for this EO product
        # Example format:
        # EO-001 | score=... | priority=...

        print(
            f"{item['eo_product_id']} | "
            f"score={item['quality_score']} | "
            f"priority={item['priority']}"
        )

        # TODO: add processed item to batch result
        processed_batch.append(item)

    return processed_batch

def run_pipeline():
    """
    Main pipeline for Lab 12.
    """

    metadata_path = "storage/eo_metadata.json"

    # 1. Load all EO products
    data = load_metadata(metadata_path)

    # 2. Choose batch size
    batch_size = 5

    # 3. Split into batches
    batches = split_into_batches(data, batch_size)

    all_results = []

    # 4. Process batch by batch
    for batch_number, batch in enumerate(batches, start=1):
        processed_batch = process_batch(batch, batch_number)
        all_results.extend(processed_batch)

    # 5. Save updated metadata
    # TODO: save all_results back to metadata file
    with open(metadata_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print("Batch processing completed.")

