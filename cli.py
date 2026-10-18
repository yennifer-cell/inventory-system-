
import os

import requests

BASE_URL = os.getenv("INVENTORY_API_URL", "http://127.0.0.1:5000")


def request_json(method, path, payload=None):
    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, json=payload, timeout=10)

    if response.status_code == 204:
        return response.status_code, None

    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"raw": response.text}


def print_menu():
    print("\nInventory CLI")
    print("1. List inventory")
    print("2. View one item")
    print("3. Add item")
    print("4. Update item")
    print("5. Delete item")
    print("6. Find external product by barcode")
    print("7. Find external product by name")
    print("8. Add product from barcode")
    print("9. Exit")


def run_cli():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                status, data = request_json("GET", "/inventory")
                print(status, data)

            elif choice == "2":
                item_id = int(input("Item id: ").strip())
                status, data = request_json("GET", f"/inventory/{item_id}")
                print(status, data)

            elif choice == "3":
                name = input("Name: ").strip()
                brand = input("Brand: ").strip()
                quantity = int(input("Quantity: ").strip())
                price = float(input("Price: ").strip())
                barcode = input("Barcode (optional): ").strip()
                payload = {
                    "name": name,
                    "brand": brand,
                    "quantity": quantity,
                    "price": price,
                    "barcode": barcode,
                }
                status, data = request_json("POST", "/inventory", payload)
                print(status, data)

            elif choice == "4":
                item_id = int(input("Item id: ").strip())
                print("Enter new values (leave blank to skip a field):")

                payload = {}

                name = input("Name: ").strip()
                if name:
                    payload["name"] = name

                brand = input("Brand: ").strip()
                if brand:
                    payload["brand"] = brand

                quantity_str = input("Quantity: ").strip()
                if quantity_str:
                    payload["quantity"] = int(quantity_str)

                price_str = input("Price: ").strip()
                if price_str:
                    payload["price"] = float(price_str)

                barcode = input("Barcode: ").strip()
                if barcode:
                    payload["barcode"] = barcode

                ingredients = input("Ingredients: ").strip()
                if ingredients:
                    payload["ingredients"] = ingredients

                if not payload:
                    print("No fields to update.")
                else:
                    status, data = request_json("PATCH", f"/inventory/{item_id}", payload)
                    print(status, data)

            elif choice == "5":
                item_id = int(input("Item id: ").strip())
                status, _ = request_json("DELETE", f"/inventory/{item_id}")
                print(status)

            elif choice == "6":
                barcode = input("Barcode: ").strip()
                status, data = request_json("GET", f"/external/barcode/{barcode}")
                print(status, data)

            elif choice == "7":
                name = input("Product name to search: ").strip()
                if not name:
                    print("Name cannot be empty.")
                else:
                    status, data = request_json("GET", f"/external/search?name={name}")
                    print(status, data)

            elif choice == "8":
                barcode = input("Barcode: ").strip()
                quantity = int(input("Quantity to add: ").strip())
                status, data = request_json("POST", f"/inventory/from-barcode/{barcode}", {"quantity": quantity})
                print(status, data)

            elif choice == "9":
                print("Goodbye")
                break

            else:
                print("Invalid choice. Try again.")

        except ValueError:
            print("Invalid input type. Try again.")
        except requests.RequestException:
            print("Request failed. Is the Flask API running?")


if __name__ == "__main__":
    run_cli()
