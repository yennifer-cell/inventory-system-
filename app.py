import datetime
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "barcode": "0787678161065",
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
        "quantity": 20,
        "price": 3.99,
        "categories": "Beverages",
        "country": "USA",
        "last_updated": "2026-07-05T00:00:00Z",
    },
    {
        "id": 2,
        "barcode": "5000159402543",
        "name": "Chocolate Hazelnut Spread",
        "brand": "Nutella",
        "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder",
        "quantity": 12,
        "price": 4.50,
        "categories": "Spreads",
        "country": "France",
        "last_updated": "2026-07-05T00:00:00Z",
    },
]


def _next_item_id():
    return max((item["id"] for item in inventory), default=0) + 1


def _now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _extract_product(product):
    return {
        "name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
        "brand": product.get("brands") or "Unknown Brand",
        "ingredients_text": product.get("ingredients_text", ""),
        "barcode": product.get("code", ""),
        "categories": product.get("categories", ""),
        "country": product.get("countries", ""),
    }


def fetch_product_details(barcode=None, name=None):
    if barcode:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 1:
            raise ValueError(f"Product not found for barcode: {barcode}")
        return _extract_product(data["product"])

    if name:
        search_url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": name,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1,
        }
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        if not products:
            raise ValueError(f"No matching product found for name: {name}")
        return _extract_product(products[0])

    raise ValueError("Please provide a barcode or product name to search.")


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found."}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json(force=True)
    if not data or not data.get("name"):
        return jsonify({"error": "The field 'name' is required."}), 400

    item = {
        "id": _next_item_id(),
        "name": data["name"],
        "barcode": data.get("barcode", ""),
        "brand": data.get("brand", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "quantity": int(data.get("quantity", 0)),
        "price": float(data.get("price", 0.0)),
        "categories": data.get("categories", ""),
        "country": data.get("country", ""),
        "last_updated": _now_iso(),
    }

    if item["barcode"] and not item["brand"]:
        try:
            details = fetch_product_details(barcode=item["barcode"])
            item.update({k: v for k, v in details.items() if v})
        except (ValueError, requests.RequestException):
            pass

    inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found."}), 404

    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No update payload provided."}), 400

    for field in ["name", "barcode", "brand", "ingredients_text", "categories", "country"]:
        if field in data:
            item[field] = data[field]
    if "quantity" in data:
        item["quantity"] = int(data["quantity"])
    if "price" in data:
        item["price"] = float(data["price"])

    item["last_updated"] = _now_iso()
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found."}), 404
    inventory.remove(item)
    return jsonify({"message": "Item deleted successfully."}), 200


@app.route("/inventory/find", methods=["GET"])
def find_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    try:
        found = fetch_product_details(barcode=barcode, name=name)
        return jsonify(found), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except requests.RequestException:
        return jsonify({"error": "External API request failed."}), 502


if __name__ == "__main__":
    app.run(debug=True)
