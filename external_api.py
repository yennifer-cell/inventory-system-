import requests

PRODUCT_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# Required headers for OpenFoodFacts API
HEADERS = {
    "User-Agent": "InventoryManagementSystem/1.0 (https://github.com/yennifer-cell/summative-inventory-api)"
}


def _normalize_product(product):
    return {
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
        "barcode": product.get("code", ""),
    }


def fetch_product_by_barcode(barcode):
    try:
        response = requests.get(
            PRODUCT_URL.format(barcode=barcode),
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    if payload.get("status") != 1:
        return None

    product = payload.get("product", {})
    return _normalize_product(product)


def fetch_product_by_name(name):
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }

    try:
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    products = payload.get("products", [])
    if not products:
        return None

    return _normalize_product(products[0])
