import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from PIL import ImageStat
from sklearn.cluster import KMeans
from lab12_scalable_pipeline.backend.eo_enhancer import enhance_image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(BASE_DIR, "storage", "eo_metadata.json")
LOG_PATH = os.path.join(BASE_DIR, "logs", "pipeline.log")


def setup_logging():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_PATH, mode="w")
        ]
    )


def log(msg):
    logging.info(msg)


def load_metadata(path):
    with open(path, "r") as f:
        return json.load(f)


def split_into_batches(data, batch_size):
    return [data[i:i + batch_size] for i in range(0, len(data), batch_size)]


def process_eo_product(item):
    image_path = os.path.join(BASE_DIR, item["image_path"])
    eo_id = item["eo_product_id"]
    enhanced_path = os.path.join(BASE_DIR, "storage", "object_store", "enhanced", f"{eo_id}-enhanced.png")

    os.makedirs(os.path.dirname(enhanced_path), exist_ok=True)
    enhanced = enhance_image(image_path, enhanced_path)

    stat = ImageStat.Stat(enhanced)
    brightness = stat.mean[0] / 255.0
    contrast = stat.stddev[0] / 255.0
    quality_score = (brightness + contrast) / 2

    item["enhanced_path"] = enhanced_path
    item["brightness"] = brightness
    item["contrast"] = contrast
    item["quality_score"] = quality_score
    item["is_visible"] = quality_score > 0.2
    return item


def assign_priority(item):
    score = item["quality_score"]
    if score > 0.4:
        item["priority"] = 1
    elif score > 0.3:
        item["priority"] = 2
    else:
        item["priority"] = 3
    return item


def process_batch(batch, batch_number):
    log(f"Batch {batch_number} start ({len(batch)} products)")
    log("-" * 60)
    processed = []
    for item in batch:
        item = process_eo_product(item)
        item = assign_priority(item)
        line = (
            f"{item['eo_product_id']} | "
            f"score={round(item['quality_score'], 4)} | "
            f"brightness={round(item['brightness'], 4)} | "
            f"contrast={round(item['contrast'], 4)}"
        )
        log(line)
        processed.append(item)
    log(f"Batch {batch_number} end")
    log("-" * 60)
    return processed


def run_clustering(data, k):
    features = np.array([[item["brightness"], item["contrast"]] for item in data])
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(features)
    for i, item in enumerate(data):
        item["cluster"] = int(labels[i])
    return data


def run_pipeline(batch_size, k):
    setup_logging()

    data = load_metadata(METADATA_PATH)

    log("Lab 12C - Clustering-Based EO Pipeline")
    log("=" * 60)
    log(f"Total EO products: {len(data)}")
    log(f"Batch size: {batch_size}")

    batches = split_into_batches(data, batch_size)
    log(f"Number of batches: {len(batches)}")
    log("-" * 60)

    all_results = []
    for batch_number, batch in enumerate(batches, start=1):
        processed = process_batch(batch, batch_number)
        all_results.extend(processed)

    all_results = run_clustering(all_results, k)

    with open(METADATA_PATH, "w") as f:
        json.dump(all_results, f, indent=2)

    log("Clustering and batch processing completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    run_pipeline(args.batch_size, args.k)