import json
import shutil
import time
import os
from pathlib import Path

# =============================
# CONFIG
# =============================

BASE_DIR = Path(__file__).parent / "data"
INCOMING_DIR = BASE_DIR / "incoming"
PROCESSED_DIR = BASE_DIR / "processed"
ARCHIVE_DIR = BASE_DIR / "archive"
METADATA_DIR = BASE_DIR / "metadata"
CATALOG_DIR = BASE_DIR / "catalog"

PROCESSING_DELAY = 1


# =============================
# SETUP
# =============================

def setup():
    """
    Create the required folder structure.

    This version does NOT delete the workspace.
    Students can place files into incoming/ before running.
    """
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)


# =============================
# AREA MAPPING
# =============================

def get_area_name_from_filename(file_name):
    """
    Return a meaningful area name based on the provided file name.
    """
    area_map = {
        "EO-AARHUS-001.png": "Aarhus Harbor",
        "EO-AARHUS-002.png": "Aarhus University",
        "EO-AARHUS-003.png": "Den Permanente",
        "EO-AARHUS-004.png": "Marselisborg Harbor",
        "EO-AARHUS-005.png": "Hørret",
        "EO-AARHUS-006.png": "Ajstrup Strand",
        "EO-AARHUS-007.png": "Egå",
        "EO-AARHUS-008.png": "Aarhus Center",
    }

    return area_map.get(file_name, "Aarhus, Denmark")


# =============================
# TASK 1: PREPARE EO PRODUCTS
# =============================

def load_initial_products():
    """
    Scan files in incoming/ and create EO product records.

    TODO:
    - Read all files from incoming/
    - Create one product dictionary per file
    - Use get_area_name_from_filename(...)
    - Start each product in state GENERATED
    """
    products = []

    for i, file_path in enumerate(sorted(INCOMING_DIR.glob("*")), start=1):
        if file_path.is_file():
            eo_id = f"EO-S1A-2026-03-24-{i:03d}"

            product = {
                "eo_product_id": eo_id,
                "satellite_id": "Sentinel-1A",
                "area_name": get_area_name_from_filename(file_path.name),
                "timestamp": "2026-03-24T10:25:00Z",
                "file_name": file_path.name,
                "processing_state": "GENERATED"
            }

            products.append(product)

    return products


def save_metadata(product):
    """
    Save metadata JSON for one EO product.

    TODO:
    - Save product as JSON in metadata/
    - File name should be:
      <eo_product_id>.json
    """
    metadata_path = METADATA_DIR / f"{product['eo_product_id']}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(product, f, indent=2)


# =============================
# TASK 2: INGEST EO PRODUCTS
# =============================

def ingest(products, queue):
    """
    Add EO products to the queue.

    TODO:
    - Change state to QUEUED
    - Save updated metadata
    - Append product to queue
    - Print log output
    """
    for product in products:
        product["processing_state"] = "QUEUED"
        save_metadata(product)
        queue.append(product)
        print(f"[INGEST] {product['eo_product_id']} -> QUEUED")

    print(f"Queue length: {len(queue)}")


# =============================
# TASK 3: PROCESS EO PRODUCTS
# =============================

def process_product(product):
    """
    Process one EO product.

    TODO:
    - Change state to PROCESSING
    - Save metadata
    - Simulate delay
    - Move file from incoming/ to processed/
    - Change state to COMPLETED
    - Save metadata
    """
    product["processing_state"] = "PROCESSING"
    save_metadata(product)
    print(f"[PROCESS] {product['eo_product_id']} -> PROCESSING")

    time.sleep(PROCESSING_DELAY)

    src = INCOMING_DIR / product["file_name"]
    dst = PROCESSED_DIR / product["file_name"]
    shutil.move(src, dst)

    product["processing_state"] = "COMPLETED"
    save_metadata(product)
    print(f"[PROCESS] {product['eo_product_id']} -> COMPLETED")


# =============================
# TASK 4: ARCHIVE EO PRODUCTS
# =============================

def build_archive_folder(product):
    """
    Build the archive folder path.

    Required structure:
    archive/
      satellite=<satellite_id>/
        area=<area_name>/
          date=<YYYY-MM-DD>/

    TODO:
    - Extract date from timestamp
    - Clean area_name for safe folder names
    - Return the full Path object
    """
    
    # Hint:
    date_str = product["timestamp"][:10]
    safe_area = product["area_name"].replace(" ", "_").replace(",", "")
    
    folder = (
        ARCHIVE_DIR / f"satellite={product['satellite_id']}" / f"area={safe_area}" / f"date={date_str}"
    )
    
    return folder


def archive_product(product):
    """
    Move processed file into archive.

    TODO:
    
    - Build archive folder
    - Create archive folder if needed
    - Move file from processed/ to archive/
    - Return final archive file path
    """
    archive_folder = build_archive_folder(product)
    os.makedirs(archive_folder, exist_ok=True)
    shutil.move(PROCESSED_DIR / product["file_name"], archive_folder / product["file_name"])
    return archive_folder / product["file_name"]


# =============================
# TASK 5: CREATE CATALOG RECORDS
# =============================

def create_catalog_record(product, archive_path):
    """
    Create one catalog record for one EO product.

    TODO:
    - Create a dictionary containing:
        eo_product_id
        satellite_id
        area_name
        timestamp
        archive_path
    - Save it in catalog/
    - File name should be:
        <eo_product_id>.catalog.json
    """
    Cata_dic = {
        "eo_product_id": product["eo_product_id"],
        "satellite_id": product["satellite_id"],
        "area_name": product["area_name"],
        "timestamp": product["timestamp"],
        "archive_path": str(archive_path)
    }
    catalog_path = CATALOG_DIR / f"{product['eo_product_id']}.catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(Cata_dic, f, indent=2)
    


# =============================
# TASK 6: QUERY SYSTEM
# =============================

def load_catalog():
    """
    Load all catalog records.

    TODO:
    - Read all *.catalog.json files from catalog/
    - Return them as a list
    """
    records = []
    for filename in CATALOG_DIR.glob("*.catalog.json"):
        with open(filename, "r", encoding="utf-8") as f:
            catalog_record = json.load(f)
            records.append(catalog_record)
    return records


def query_by_area(area_name):
    """
    Return all catalog records matching area_name.

    TODO:
    - Load catalog
    - Filter by area_name
    """
    
    results = []

    for record in load_catalog():
        if record["area_name"] == area_name:
            results.append(record)

    return results


def print_results(results):
    """
    Print query results in a readable way.
    """
    print(f"\nFound {len(results)} results:\n")
    for record in results:
        print(f"{record['eo_product_id']} -> {record['archive_path']}")


# =============================
# PIPELINE
# =============================

def run_pipeline(products):
    """
    Main Week 9 pipeline.

    TODO:
    - Create empty queue
    - Ingest all products first
    - Process queue in FIFO order
    - Archive each product
    - Create catalog record for each product
    """
    queue = []

    ingest(products, queue)

    print("\n--- START PROCESSING ---\n")

    while queue:
        product = queue.pop(0)

        process_product(product)

        # TODO:
        archive_path = archive_product(product)
        create_catalog_record(product, archive_path)

        print(f"Queue length: {len(queue)}")


# =============================
# MAIN
# =============================

def main():
    setup()

    products = load_initial_products()

    if not products:
        print("No EO files found in lab9/data/incoming/")
        print("Please place your EO image files there before running.")
        return

    for product in products:
        save_metadata(product)

    run_pipeline(products)

    print("\n--- QUERY TEST ---")
    results = query_by_area("Aarhus Harbor")
    print_results(results)


if __name__ == "__main__":
    main()