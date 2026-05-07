import json
from pathlib import Path
from flask import Flask, render_template, request, send_file, abort

app = Flask(__name__)

# TODO:
# Update these paths to match your Lab 9 folders
CATALOG_DIR = Path("lab9/data/catalog")
ARCHIVE_DIR = Path("lab9/data/archive")


# =========================
# TASK 1: LOAD CATALOG from Lab 9
# =========================
def load_catalog():
    """
    Read all catalog JSON files and return a list of EO products.
    """
    products = []
    
   

    # TODO:
    # Loop through all *.catalog.json files
    # Open each file
    # Load JSON
    # Append to products list
    for file_path in sorted(CATALOG_DIR.glob("*.catalog.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            products.append(json.load(f))
    

    return products


# =========================
# TASK 2: FILTERING
# =========================
def apply_filters(products, area_name="", satellite_id="", date=""):
    filtered = products

    # TODO:
    # Filter by area_name (if provided)
    if area_name:
        filtered = [p for p in filtered if area_name.lower() in p["area_name"].lower()]

    # TODO:
    # Filter by satellite_id (if provided)
    if satellite_id:
        filtered = [p for p in filtered if satellite_id.lower() in p["satellite_id"].lower()]

    # TODO:
    # Filter by date (match timestamp prefix)
    if date:
        filtered = [p for p in filtered if p["timestamp"].startswith(date)]

    return filtered


# =========================
# TASK 3: SELECT PRODUCT
# =========================
def get_selected_product(products, selected_id):
    # TODO:
    # If selected_id exists:
    #   find and return matching product information from metadata (catalog)
    if selected_id:
        for product in products:
            if product["eo_product_id"] == selected_id:
                return product

    # TODO:
    # Otherwise return first product if list is not empty
    if len(products) > 0:
        return products[0]

    return None


# =========================
# TASK 4: MAIN DASHBOARD
# =========================
@app.route("/") #API endpoint mapping
def index():

    all_products = load_catalog()
    total = len(all_products)
    latest_timestamp = max((p["timestamp"] for p in all_products))

    # Read filters from URL
    area_name = request.args.get("area_name", "").strip()
    satellite_id = request.args.get("satellite_id", "").strip()
    date = request.args.get("date", "").strip()
    selected_id = request.args.get("selected_id", "").strip()

    # TODO:
    # Apply filtering
    products = apply_filters(all_products, area_name, satellite_id, date)

    # TODO:
    # Get selected product
    selected_product = get_selected_product(products, selected_id)

    return render_template(
        "index.html",
        products=products,
        selected_product=selected_product,
        area_name=area_name,
        satellite_id=satellite_id,
        date=date,
        total_products=total,
        filtered_products=len(products),
        latest_timestamp=latest_timestamp,
    )


# =========================
# TASK 5: IMAGE ENDPOINT
# =========================
@app.route("/image/<eo_product_id>") #API endpoint mapping
def serve_image(eo_product_id):

    products = load_catalog()

    # TODO:
    # Find product by eo_product_id
    for product in products:
        if product["eo_product_id"] == eo_product_id:
            
    

    # TODO:
    # Get archive_path from product
            archive_path = Path(product["archive_path"]).resolve()
    # TODO:
    # Convert to Path and check if file exists
            if archive_path.is_file():
                
    # TODO:
    # Return image using send_file()
                return send_file(archive_path, mimetype="image/png")

    abort(404)


# =========================
# OPTIONAL: SIMPLE API
# =========================
@app.route("/api/products") #API endpoint mapping
def api_products():
    """
    Optional: return JSON data
    """
    products = load_catalog()
    return products


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)