
import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.inventory[:] = [
        {
            "id": 1,
            "name": "Milk",
            "brand": "Brand A",
            "quantity": 4,
            "price": 2.5,
            "barcode": "111",
        },
        {
            "id": 2,
            "name": "Bread",
            "brand": "Brand B",
            "quantity": 7,
            "price": 1.8,
            "barcode": "222",
        },
    ]
    return app_module.app.test_client()


# --- GET Tests ---

def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Milk"
    assert data["id"] == 1


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found"


# --- POST Tests ---

def test_create_inventory_item(client):
    payload = {"name": "Eggs", "brand": "Farm", "quantity": 12, "price": 4.2}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    assert response.get_json()["name"] == "Eggs"


def test_create_inventory_item_missing_name(client):
    payload = {"quantity": 10, "price": 5.0}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 400
    assert "name" in response.get_json()["error"]


def test_create_inventory_item_missing_quantity(client):
    payload = {"name": "Juice", "price": 3.0}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 400
    assert "quantity" in response.get_json()["error"]


def test_create_inventory_item_invalid_quantity(client):
    payload = {"name": "Juice", "quantity": -5, "price": 3.0}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 400
    assert "quantity" in response.get_json()["error"]


def test_create_inventory_item_invalid_price(client):
    payload = {"name": "Juice", "quantity": 5, "price": -10}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 400
    assert "price" in response.get_json()["error"]


# --- PATCH Tests ---

def test_patch_inventory_item(client):
    response = client.patch("/inventory/1", json={"quantity": 10})
    assert response.status_code == 200
    assert response.get_json()["quantity"] == 10


def test_patch_inventory_item_multiple_fields(client):
    response = client.patch("/inventory/1", json={
        "name": "Whole Milk",
        "brand": "Dairy Fresh",
        "quantity": 20,
        "price": 3.99
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Whole Milk"
    assert data["brand"] == "Dairy Fresh"
    assert data["quantity"] == 20
    assert data["price"] == 3.99


def test_patch_inventory_item_not_found(client):
    response = client.patch("/inventory/999", json={"quantity": 10})
    assert response.status_code == 404


def test_patch_inventory_item_no_fields(client):
    response = client.patch("/inventory/1", json={})
    assert response.status_code == 400
    assert "No fields" in response.get_json()["error"]


def test_patch_inventory_item_invalid_field(client):
    response = client.patch("/inventory/1", json={"invalid_field": "value"})
    assert response.status_code == 400
    assert "Invalid fields" in response.get_json()["error"]


def test_patch_inventory_item_invalid_quantity(client):
    response = client.patch("/inventory/1", json={"quantity": -5})
    assert response.status_code == 400
    assert "quantity" in response.get_json()["error"]


# --- DELETE Tests ---

def test_delete_inventory_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 204


def test_delete_inventory_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


# --- External API Route Tests ---

def test_barcode_lookup_route(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_barcode",
        lambda barcode: {"name": "Mock Product", "barcode": barcode},
    )

    response = client.get("/external/barcode/12345")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Mock Product"


def test_barcode_lookup_route_not_found(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_barcode",
        lambda barcode: None,
    )

    response = client.get("/external/barcode/00000")
    assert response.status_code == 404


def test_search_by_name_route(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_name",
        lambda name: {"name": "Searched Product", "brand": "Test"},
    )

    response = client.get("/external/search?name=test")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Searched Product"


def test_search_by_name_route_missing_param(client):
    response = client.get("/external/search")
    assert response.status_code == 400
    assert "name" in response.get_json()["error"]


def test_search_by_name_route_not_found(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_name",
        lambda name: None,
    )

    response = client.get("/external/search?name=nonexistent")
    assert response.status_code == 404


# --- Create from Barcode Tests ---

def test_create_from_barcode(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_barcode",
        lambda barcode: {
            "name": "External Product",
            "brand": "External Brand",
            "barcode": barcode,
            "ingredients": "water, sugar",
        },
    )

    response = client.post("/inventory/from-barcode/12345", json={"quantity": 5})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "External Product"
    assert data["quantity"] == 5
    assert data["barcode"] == "12345"


def test_create_from_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_barcode",
        lambda barcode: None,
    )

    response = client.post("/inventory/from-barcode/00000", json={"quantity": 5})
    assert response.status_code == 404


def test_create_from_barcode_invalid_quantity(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "fetch_product_by_barcode",
        lambda barcode: {"name": "Product", "barcode": barcode},
    )

    response = client.post("/inventory/from-barcode/12345", json={"quantity": -1})
    assert response.status_code == 400
    assert "quantity" in response.get_json()["error"]


# --- Home Route Test ---

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.get_json()["message"].lower()
