# Inventory Management API (Flask)

A Flask-based REST API for inventory management with OpenFoodFacts API integration and a CLI client.

## Features

- Full CRUD operations for inventory items
- External API integration with OpenFoodFacts (search by barcode or product name)
- CLI client for easy interaction with the API
- Comprehensive test suite with pytest

## Project Structure

```
inventory-system-/
├── app.py              # Flask REST API
├── cli.py              # Command-line interface client
├── external_api.py     # OpenFoodFacts API integration
├── tests/
│   ├── test_app.py          # API endpoint tests
│   ├── test_cli.py          # CLI tests
│   └── test_external_api.py # External API tests
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yennifer-cell/inventory-system-.git
cd inventory-system-
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the Flask server:
```bash
python app.py
```

The API runs on `http://127.0.0.1:8000` by default.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/inventory` | List all inventory items |
| GET | `/inventory/<id>` | Get a single item by ID |
| POST | `/inventory` | Create a new item |
| PATCH | `/inventory/<id>` | Update an existing item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/external/barcode/<barcode>` | Lookup product by barcode (OpenFoodFacts) |
| GET | `/external/search?name=<name>` | Search product by name (OpenFoodFacts) |
| POST | `/inventory/from-barcode/<barcode>` | Create item from external product data |

## Sample API Requests

### Create an item
```bash
curl -X POST http://127.0.0.1:8000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Organic Almond Milk", "brand": "Silk", "quantity": 12, "price": 3.99}'
```

### Update multiple fields
```bash
curl -X PATCH http://127.0.0.1:8000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name", "quantity": 20, "price": 4.99}'
```

### Lookup product by barcode
```bash
curl http://127.0.0.1:8000/external/barcode/737628064502
```

### Search product by name
```bash
curl "http://127.0.0.1:8000/external/search?name=almond%20milk"
```

## CLI Usage

In a new terminal (with the venv active and API running):

```bash
python cli.py
```

### CLI Menu Options

```
Inventory CLI
1. List inventory       - View all inventory items
2. View one item        - Get details of a specific item by ID
3. Add item             - Create a new inventory item
4. Update item          - Update one or more fields of an existing item
5. Delete item          - Remove an item from inventory
6. Find external product by barcode - Search OpenFoodFacts by barcode
7. Find external product by name    - Search OpenFoodFacts by product name
8. Add product from barcode         - Create inventory item from external data
9. Exit                 - Close the CLI
```

### CLI Examples

**List all inventory:**
```
Choose an option: 1
200 [{'id': 1, 'name': 'Organic Almond Milk', 'brand': 'Silk', ...}]
```

**Add a new item:**
```
Choose an option: 3
Name: Orange Juice
Brand: Tropicana
Quantity: 24
Price: 5.99
Barcode (optional): 048500202661
201 {'id': 3, 'name': 'Orange Juice', 'brand': 'Tropicana', ...}
```

**Update multiple fields:**
```
Choose an option: 4
Item id: 1
Enter new values (leave blank to skip a field):
Name: Premium Almond Milk
Brand:
Quantity: 15
Price: 4.49
Barcode:
Ingredients:
200 {'id': 1, 'name': 'Premium Almond Milk', 'quantity': 15, 'price': 4.49, ...}
```

**Search by product name:**
```
Choose an option: 7
Product name to search: nutella
200 {'name': 'Nutella', 'brand': 'Ferrero', 'ingredients': '...', 'barcode': '...'}
```

**Add product from barcode:**
```
Choose an option: 8
Barcode: 737628064502
Quantity to add: 10
201 {'id': 4, 'name': 'Thai peanut noodle kit...', 'quantity': 10, ...}
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_app.py -v
```

## Technologies Used

- Python 3.12
- Flask - Web framework
- Requests - HTTP library for external API calls
- Pytest - Testing framework

## License

This project is for educational purposes as part of the Moringa School Software Engineering program.
