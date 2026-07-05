import argparse
import json
import pytest
import requests
from unittest.mock import patch

import cli


@patch("cli.requests.request")
def test_list_items(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = [{"id": 1, "name": "Test"}]

    args = argparse.Namespace(command="list", base_url="http://127.0.0.1:5000")
    cli.list_items(args)

    captured = capsys.readouterr()
    assert "Test" in captured.out


@patch("cli.requests.request")
def test_get_item(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = {"id": 1, "name": "Test"}

    args = argparse.Namespace(command="get", base_url="http://127.0.0.1:5000", id=1)
    cli.get_item(args)

    captured = capsys.readouterr()
    assert "Test" in captured.out


@patch("cli.requests.request")
def test_add_item(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = {"id": 2, "name": "New Product"}

    args = argparse.Namespace(command="add", base_url="http://127.0.0.1:5000", name="New Product", barcode="", quantity=5, price=2.99)
    cli.add_item(args)

    captured = capsys.readouterr()
    assert "Created item" in captured.out
    assert "New Product" in captured.out


@patch("cli.requests.request")
def test_update_item(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = {"id": 1, "name": "Updated Product", "price": 4.5}

    args = argparse.Namespace(command="update", base_url="http://127.0.0.1:5000", id=1, name=None, barcode=None, quantity=10, price=4.5)
    cli.update_item(args)

    captured = capsys.readouterr()
    assert "Updated item" in captured.out
    assert "Updated Product" in captured.out


@patch("cli.requests.request")
def test_delete_item(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = {"message": "Deleted."}

    args = argparse.Namespace(command="delete", base_url="http://127.0.0.1:5000", id=1)
    cli.delete_item(args)

    captured = capsys.readouterr()
    assert "Deleted." in captured.out


@patch("cli.requests.request")
def test_find_item(mock_request, capsys):
    mock_request.return_value.ok = True
    mock_request.return_value.json.return_value = {"name": "Test Product"}

    args = argparse.Namespace(command="find", base_url="http://127.0.0.1:5000", barcode="12345", name=None)
    cli.find_item(args)

    captured = capsys.readouterr()
    assert "External product result" in captured.out
    assert "Test Product" in captured.out


def test_parser_builds_subcommands():
    parser = cli.build_parser()
    assert parser.parse_args(["list"]).command == "list"
    assert parser.parse_args(["get", "1"]).command == "get"
    assert parser.parse_args(["add", "Item", "--quantity", "2", "--price", "1.0"]).command == "add"
