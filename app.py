from flask import Flask, jsonify, request

from external_api import fetch_product_by_barcode, fetch_product_by_name

app = Flask(__name__)


# In-memory inventory store for this lab.
inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "quantity": 10,
        "price": 3.99,
        "barcode": "737628064502",
    },
    {
        "id": 2,
        "name": "Whole Wheat Bread",
        "brand": "Nature's Own",
        "quantity": 15,
        "price": 2.49,
        "barcode": "072250013494",
    },
]


def get_next_id():
    if not inventory:
        return 1
    return max(item["id"] for item in inventory) + 1


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def validate_create_payload(data):
    required = ["name", "quantity", "price"]
    for field in required:
        if field not in data:
            return f"Missing required field: {field}"

    if not isinstance(data["name"], str) or not data["name"].strip():
        return "name must be a non-empty string"

    if not isinstance(data["quantity"], int) or data["quantity"] < 0:
        return "quantity must be a non-negative integer"

    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return "price must be a non-negative number"

    return None


def validate_patch_payload(data):
    allowed = {"name", "brand", "quantity", "price", "barcode", "ingredients"}
    invalid = [key for key in data.keys() if key not in allowed]
    if invalid:
        return f"Invalid fields: {', '.join(invalid)}"

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "name must be a non-empty string"

    if "quantity" in data:
        if not isinstance(data["quantity"], int) or data["quantity"] < 0:
            return "quantity must be a non-negative integer"

    if "price" in data:
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            return "price must be a non-negative number"

    return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Inventory Management API is running"}), 200


@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json(silent=True) or {}

    error = validate_create_payload(data)
    if error:
        return jsonify({"error": error}), 400

    new_item = {
        "id": get_next_id(),
        "name": data["name"].strip(),
        "brand": data.get("brand", ""),
        "quantity": data["quantity"],
        "price": float(data["price"]),
        "barcode": data.get("barcode", ""),
        "ingredients": data.get("ingredients", ""),
    }
    inventory.append(new_item)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No fields provided"}), 400

    error = validate_patch_payload(data)
    if error:
        return jsonify({"error": error}), 400

    for key, value in data.items():
        if key == "name" and isinstance(value, str):
            item[key] = value.strip()
        elif key == "price":
            item[key] = float(value)
        else:
            item[key] = value

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return "", 204


@app.route("/external/barcode/<barcode>", methods=["GET"])
def lookup_barcode(barcode):
    product = fetch_product_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found in external API"}), 404
    return jsonify(product), 200


@app.route("/external/search", methods=["GET"])
def lookup_name():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "name query parameter is required"}), 400

    product = fetch_product_by_name(name)
    if product is None:
        return jsonify({"error": "Product not found in external API"}), 404
    return jsonify(product), 200


@app.route("/inventory/from-barcode/<barcode>", methods=["POST"])
def create_from_barcode(barcode):
    product = fetch_product_by_barcode(barcode)
    if product is None:
        return jsonify({"error": "Product not found in external API"}), 404

    quantity = (request.get_json(silent=True) or {}).get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "quantity must be a non-negative integer"}), 400

    new_item = {
        "id": get_next_id(),
        "name": product.get("name", "Unknown Product"),
        "brand": product.get("brand", ""),
        "quantity": quantity,
        "price": 0.0,
        "barcode": product.get("barcode", barcode),
        "ingredients": product.get("ingredients", ""),
    }
    inventory.append(new_item)
    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True, port=8000)
