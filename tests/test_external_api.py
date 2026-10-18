
import requests

import external_api


class DummyResponse:
    def __init__(self, payload, should_raise=False):
        self.payload = payload
        self.should_raise = should_raise

    def raise_for_status(self):
        if self.should_raise:
            raise requests.RequestException("Mock error")
        return None

    def json(self):
        return self.payload


def test_fetch_product_by_barcode(monkeypatch):
    payload = {
        "status": 1,
        "product": {
            "product_name": "Orange Juice",
            "brands": "Fresh Co",
            "ingredients_text": "orange",
            "code": "123",
        },
    }

    monkeypatch.setattr(external_api.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    product = external_api.fetch_product_by_barcode("123")
    assert product["name"] == "Orange Juice"
    assert product["brand"] == "Fresh Co"
    assert product["ingredients"] == "orange"
    assert product["barcode"] == "123"


def test_fetch_product_by_barcode_not_found(monkeypatch):
    payload = {"status": 0}

    monkeypatch.setattr(external_api.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    product = external_api.fetch_product_by_barcode("000")
    assert product is None


def test_fetch_product_by_barcode_request_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(external_api.requests, "get", mock_get)

    product = external_api.fetch_product_by_barcode("123")
    assert product is None


def test_fetch_product_by_barcode_includes_headers(monkeypatch):
    payload = {
        "status": 1,
        "product": {
            "product_name": "Test",
            "brands": "",
            "ingredients_text": "",
            "code": "123",
        },
    }

    captured_kwargs = {}

    def mock_get(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return DummyResponse(payload)

    monkeypatch.setattr(external_api.requests, "get", mock_get)

    external_api.fetch_product_by_barcode("123")
    assert "headers" in captured_kwargs
    assert "User-Agent" in captured_kwargs["headers"]


def test_fetch_product_by_name(monkeypatch):
    payload = {
        "products": [
            {
                "product_name": "Chocolate",
                "brands": "Sweet",
                "ingredients_text": "cocoa",
                "code": "999",
            }
        ]
    }

    monkeypatch.setattr(external_api.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    product = external_api.fetch_product_by_name("chocolate")
    assert product["name"] == "Chocolate"
    assert product["brand"] == "Sweet"
    assert product["ingredients"] == "cocoa"
    assert product["barcode"] == "999"


def test_fetch_product_by_name_no_results(monkeypatch):
    payload = {"products": []}

    monkeypatch.setattr(external_api.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    product = external_api.fetch_product_by_name("nonexistent")
    assert product is None


def test_fetch_product_by_name_request_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr(external_api.requests, "get", mock_get)

    product = external_api.fetch_product_by_name("test")
    assert product is None


def test_fetch_product_by_name_includes_headers(monkeypatch):
    payload = {"products": [{"product_name": "Test", "brands": "", "ingredients_text": "", "code": "123"}]}

    captured_kwargs = {}

    def mock_get(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return DummyResponse(payload)

    monkeypatch.setattr(external_api.requests, "get", mock_get)

    external_api.fetch_product_by_name("test")
    assert "headers" in captured_kwargs
    assert "User-Agent" in captured_kwargs["headers"]


def test_normalize_product_missing_fields():
    product = external_api._normalize_product({})
    assert product["name"] == ""
    assert product["brand"] == ""
    assert product["ingredients"] == ""
    assert product["barcode"] == ""


def test_normalize_product_partial_fields():
    product = external_api._normalize_product({
        "product_name": "Partial Product",
        "code": "555",
    })
    assert product["name"] == "Partial Product"
    assert product["brand"] == ""
    assert product["ingredients"] == ""
    assert product["barcode"] == "555"
