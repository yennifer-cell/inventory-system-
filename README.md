# Inventory Management System

A Flask-based REST API and CLI tool for managing retail inventory with external product enrichment from OpenFoodFacts.

## Features

- RESTful inventory CRUD endpoints in Flask
- External product searches by barcode or name using OpenFoodFacts
- CLI interface to add, list, update, delete, and find products
- In-memory inventory storage for quick prototyping
- Pytest suite covering API endpoints, CLI commands, and external API integration

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
python app.py
```

The API will start on `http://127.0.0.1:5000`.

## API Endpoints

- `GET /inventory` — list all inventory items
- `GET /inventory/<id>` — get a single item by ID
- `POST /inventory` — add a new item
- `PATCH /inventory/<id>` — update a specific item
- `DELETE /inventory/<id>` — delete a specific item
- `GET /inventory/find?barcode=<barcode>` — fetch product details from OpenFoodFacts
- `GET /inventory/find?name=<name>` — search product details by name

### Example `POST /inventory`

```json
{
  "name": "Organic Almond Milk",
  "barcode": "0787678161065",
  "quantity": 10,
  "price": 3.99
}
```

## CLI Usage

Start the API server first, then run operations from the CLI.

```bash
python cli.py list
python cli.py get 1
python cli.py add "Fresh Oats" --barcode 1234567890123 --quantity 15 --price 2.99
python cli.py update 1 --price 4.25 --quantity 18
python cli.py delete 2
python cli.py find --barcode 0787678161065
python cli.py find --name "Almond Milk"
```

To start the API from the CLI directly:

```bash
python cli.py runserver
```

## Testing

```bash
pytest
```

## Notes

- Inventory is stored in memory for this lab-style project.
- The API enriches items with OpenFoodFacts metadata when a valid barcode is provided.
- Use the CLI commands after starting `app.py` or the `runserver` command.
