import argparse
import json
import requests
import sys

DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def request_api(method, path, base_url, json_payload=None, params=None):
    url = f"{base_url}{path}"
    response = requests.request(method, url=url, json=json_payload, params=params, timeout=5)
    try:
        result = response.json()
    except ValueError:
        response.raise_for_status()
    if not response.ok:
        raise requests.HTTPError(f"{response.status_code} {response.text}")
    return result


def print_item(item):
    print(json.dumps(item, indent=2, sort_keys=True))


def list_items(args):
    items = request_api("GET", "/inventory", args.base_url)
    for item in items:
        print_item(item)


def get_item(args):
    item = request_api("GET", f"/inventory/{args.id}", args.base_url)
    print_item(item)


def add_item(args):
    payload = {
        "name": args.name,
        "barcode": args.barcode,
        "quantity": args.quantity,
        "price": args.price,
    }
    item = request_api("POST", "/inventory", args.base_url, json_payload=payload)
    print("Created item:")
    print_item(item)


def update_item(args):
    payload = {}
    if args.name:
        payload["name"] = args.name
    if args.barcode:
        payload["barcode"] = args.barcode
    if args.quantity is not None:
        payload["quantity"] = args.quantity
    if args.price is not None:
        payload["price"] = args.price
    if not payload:
        print("No update fields provided.")
        return
    item = request_api("PATCH", f"/inventory/{args.id}", args.base_url, json_payload=payload)
    print("Updated item:")
    print_item(item)


def delete_item(args):
    result = request_api("DELETE", f"/inventory/{args.id}", args.base_url)
    print(result.get("message", "Deleted."))


def find_item(args):
    params = {}
    if args.barcode:
        params["barcode"] = args.barcode
    elif args.name:
        params["name"] = args.name
    else:
        print("Provide either --barcode or --name to find an item.")
        return

    item = request_api("GET", "/inventory/find", args.base_url, params=params)
    print("External product result:")
    print_item(item)


def run_server(args):
    from app import app

    app.run(debug=True)


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all inventory items")

    get_parser = subparsers.add_parser("get", help="Fetch a single inventory item")
    get_parser.add_argument("id", type=int, help="Item ID")

    add_parser = subparsers.add_parser("add", help="Add a new inventory item")
    add_parser.add_argument("name", help="Item name")
    add_parser.add_argument("--barcode", default="", help="Product barcode")
    add_parser.add_argument("--quantity", type=int, default=0, help="Stock quantity")
    add_parser.add_argument("--price", type=float, default=0.0, help="Unit price")

    update_parser = subparsers.add_parser("update", help="Update an existing inventory item")
    update_parser.add_argument("id", type=int, help="Item ID")
    update_parser.add_argument("--name", help="New item name")
    update_parser.add_argument("--barcode", help="New barcode")
    update_parser.add_argument("--quantity", type=int, help="New stock quantity")
    update_parser.add_argument("--price", type=float, help="New price")

    delete_parser = subparsers.add_parser("delete", help="Delete an inventory item")
    delete_parser.add_argument("id", type=int, help="Item ID")

    find_parser = subparsers.add_parser("find", help="Find product details from external API")
    find_group = find_parser.add_mutually_exclusive_group(required=True)
    find_group.add_argument("--barcode", help="Product barcode")
    find_group.add_argument("--name", help="Product name")

    subparsers.add_parser("runserver", help="Start the Flask API server")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "list":
            list_items(args)
        elif args.command == "get":
            get_item(args)
        elif args.command == "add":
            add_item(args)
        elif args.command == "update":
            update_item(args)
        elif args.command == "delete":
            delete_item(args)
        elif args.command == "find":
            find_item(args)
        elif args.command == "runserver":
            run_server(args)
        else:
            raise ValueError("Unknown command")
    except requests.HTTPError as exc:
        print(f"Request failed: {exc}")
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Network error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
