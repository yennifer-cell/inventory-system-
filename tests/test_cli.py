
import cli


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_request_json_get(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(200, [{"id": 1, "name": "Milk"}]),
    )

    status, data = cli.request_json("GET", "/inventory")
    assert status == 200
    assert data[0]["name"] == "Milk"


def test_request_json_post(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(201, {"id": 3, "name": "New Item"}),
    )

    status, data = cli.request_json("POST", "/inventory", {"name": "New Item", "quantity": 5, "price": 2.0})
    assert status == 201
    assert data["name"] == "New Item"


def test_request_json_patch(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(200, {"id": 1, "name": "Updated", "quantity": 10}),
    )

    status, data = cli.request_json("PATCH", "/inventory/1", {"name": "Updated", "quantity": 10})
    assert status == 200
    assert data["name"] == "Updated"
    assert data["quantity"] == 10


def test_request_json_delete(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(204, None),
    )

    status, data = cli.request_json("DELETE", "/inventory/1")
    assert status == 204
    assert data is None


def test_request_json_error_response(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(404, {"error": "Item not found"}),
    )

    status, data = cli.request_json("GET", "/inventory/999")
    assert status == 404
    assert data["error"] == "Item not found"


def test_request_json_external_barcode(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(200, {"name": "Product", "barcode": "12345"}),
    )

    status, data = cli.request_json("GET", "/external/barcode/12345")
    assert status == 200
    assert data["barcode"] == "12345"


def test_request_json_external_search(monkeypatch):
    monkeypatch.setattr(
        cli.requests,
        "request",
        lambda *args, **kwargs: DummyResponse(200, {"name": "Searched Product"}),
    )

    status, data = cli.request_json("GET", "/external/search?name=test")
    assert status == 200
    assert data["name"] == "Searched Product"


def test_print_menu(capsys):
    cli.print_menu()
    captured = capsys.readouterr()
    assert "Inventory CLI" in captured.out
    assert "List inventory" in captured.out
    assert "Update item" in captured.out
    assert "Find external product by barcode" in captured.out
    assert "Find external product by name" in captured.out
    assert "Add product from barcode" in captured.out
    assert "Exit" in captured.out
