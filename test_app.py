import json
import pytest
import requests
from unittest.mock import patch

from app import app, inventory, fetch_product_details


@pytest.fixture(autouse=True)
def reset_inventory():
    inventory.clear()
    inventory.extend([
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
        }
    ])


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Organic Almond Milk"


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1


def test_get_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found."


def test_create_inventory_item(client):
    payload = {"name": "Test Product", "quantity": 5, "price": 1.99}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 2
    assert data["name"] == "Test Product"


def test_update_inventory_item(client):
    payload = {"price": 4.50, "quantity": 25}
    response = client.patch("/inventory/1", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["quantity"] == 25
    assert data["price"] == 4.50


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404


def test_delete_inventory_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Item deleted successfully."
    assert len(inventory) == 0


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


@patch("app.requests.get")
def test_find_product_by_barcode(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds",
            "code": "0787678161065",
            "categories": "Beverages",
            "countries": "USA",
        },
    }

    response = client.get("/inventory/find?barcode=0787678161065")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Organic Almond Milk"
    assert data["brand"] == "Silk"


def test_fetch_product_details_requires_input():
    with pytest.raises(ValueError):
        fetch_product_details()


@patch("app.requests.get")
def test_fetch_product_details_by_name(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "products": [
            {
                "product_name": "Organic Almond Milk",
                "brands": "Silk",
                "ingredients_text": "Filtered water, almonds",
                "code": "0787678161065",
                "categories": "Beverages",
                "countries": "USA",
            }
        ]
    }

    details = fetch_product_details(name="Almond Milk")
    assert details["name"] == "Organic Almond Milk"
    assert details["brand"] == "Silk"
