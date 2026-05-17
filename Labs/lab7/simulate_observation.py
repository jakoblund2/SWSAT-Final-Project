import json
from datetime import datetime, timezone
from eo_generator import generate_eo_image

SCHEDULE_FILE = "storage/sampleschedule.json"
METADATA_FILE = "storage/eo_metadata.json"

with open(SCHEDULE_FILE) as f:
    schedule = json.load(f)

schedule_id = schedule["schedule_id"]
satellite_id = schedule["satellite_id"]
selected_passes = schedule["selected_passes"]

print(f"Loaded schedule {schedule_id}")
print(f"Selected passes: {len(selected_passes)}")

records = []

for index, p in enumerate(selected_passes, start=1):
    pass_id = p["pass_id"]
    date_str = p["start_time"][:10]

    print(f"\nGenerating EO product for pass {pass_id}")

    image_path = generate_eo_image(pass_id, date_str, index)

    print(f"Saved image: {image_path}")

    records.append({
        "eo_product_id": f"EO-Sen1A-AARHUS-{date_str}-{index:03d}",
        "schedule_id": schedule_id,
        "pass_id": pass_id,
        "satellite_id": satellite_id,
        "area_name": "Aarhus, Denmark",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "image_path": str(image_path),
        "image_width": 256,
        "image_height": 256,
        "processing_state": "GENERATED"
    })

with open(METADATA_FILE, "w") as f:
    json.dump(records, f, indent=2)

print(f"\nSaved EO metadata records: {len(records)}")
