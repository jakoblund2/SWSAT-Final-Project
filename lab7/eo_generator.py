import numpy as np
from PIL import Image
from pathlib import Path


def generate_eo_image(pass_id, date_str, index):
    rng = np.random.default_rng(seed=index)

    img = np.zeros((256, 256), dtype=np.float32)

    # Water (left side, dark) — varying width
    water_width = rng.integers(60, 120)
    img[:, :water_width] = rng.uniform(10, 40, (256, water_width))

    # Land (right side, brighter)
    img[:, water_width:] = rng.uniform(60, 120, (256, 256 - water_width))

    # Farmland stripes — varying position and count
    stripe_start = rng.integers(50, 100)
    for r in range(stripe_start, 220, rng.integers(15, 30)):
        img[r:r+rng.integers(5, 12), water_width:] = rng.uniform(130, 180)

    # Urban blocks — random positions and sizes
    for _ in range(rng.integers(2, 5)):
        r = rng.integers(20, 200)
        c = rng.integers(water_width, 230)
        h = min(rng.integers(20, 50), 256 - r)
        w = min(rng.integers(20, 50), 256 - c)
        img[r:r+h, c:c+w] = rng.uniform(190, 240, (h, w))

    # Road / river — varying curve
    amplitude = rng.uniform(10, 30)
    center = rng.integers(water_width + 20, 220)
    for row in range(256):
        col = min(int(center + amplitude * np.sin(row / rng.uniform(20, 40))), 254)
        img[row, col:col+2] = 220

    # Speckle noise
    img = img * rng.gamma(shape=4.0, scale=0.25, size=(256, 256))
    img = np.clip(img, 0, 255).astype(np.uint8)

    year, month, day = date_str.split("-")
    out_dir = Path(f"storage/object_store/{year}/{month}/{day}")
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"EO-Sen1A-AARHUS-{date_str}-{index:03d}.png"
    Image.fromarray(img, mode="L").save(path)
    return path
