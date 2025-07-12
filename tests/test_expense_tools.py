"""
Unit tests for expense management tools in Zoho Books MCP Integration Server.
"""

import json
import unittest
from datetime import date
from unittest.mock import patch, MagicMock

from zoho_mcp.tools.expenses import (
    list_expenses,
    create_expense,
    get_expense,
    update_expense,
)


class TestExpenseTools(unittest.TestCase):
    """Test cases for expense management tools."""

    def setUp(self):
        """Set up test fixtures."""
        # Common test data
        self.mock_expense_id = "123456789"
        self.mock_expense = {
            "expense_id": self.mock_expense_id,
            "account_id": "account123",
            "paid_through_account_id": "paid_account123",
            "date": "2025-01-15",
            "amount": 500.50,
            "vendor_name": "ABC Supplies",
            "vendor_id": "vendor123",
            "is_billable": False,
            "reference_number": "REF-001",
            "description": "Office supplies",
            "status": "unbilled",
        }
        
        # Mock expense list response
        self.mock_expenses_list = {
            "expenses": [self.mock_expense, {
                "expense_id": "987654321",
                "account_id": "account456",
                "paid_through_account_id": "paid_account456",
                "date": "2025-01-20",
                "amount": 1000.00,
                "vendor_name": "XYZ Services",
                "vendor_id": "vendor456",
                "is_billable": True,
                "customer_id": "customer123",
                "reference_number": "REF-002",
                "description": "Consulting services",
                "status": "invoiced",
            }],
            "page_context": {
                "page": 1,
                "per_page": 25,
                "has_more_page": False,
                "report_name": "Expenses",
                "applied_filter": "All Expenses",
                "sort_column": "created_time",
                "sort_order": "D",
                "total": 2
            },
            "message": "Expenses retrieved successfully",
            "code": 0,
        }
        
        # Mock create expense response
        self.mock_create_response = {
            "expense": self.mock_expense,
            "message": "Expense created successfully",
            "code": 0,
        }
        
        # Mock get expense response
        self.mock_get_response = {
            "expense": self.mock_expense,
            "message": "Expense retrieved successfully",
            "code": 0,
        }
        
        # Mock update expense response
        self.mock_update_response = {
            "expense": {
                **self.mock_expense,
                "amount": 600.75,
                "description": "Updated office supplies"
            },
            "message": "Expense updated successfully",
            "code": 0,
        }

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_list_expenses_success(self, mock_api_request):
        """Test listing expenses with default parameters."""
        # Set up the mock
        mock_api_request.return_value = self.mock_expenses_list
        
        # Call the function
        result = list_expenses()
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "/expenses")
        self.assertEqual(kwargs["params"]["page"], 1)
        self.assertEqual(kwargs["params"]["per_page"], 25)
        
        # Verify the result
        self.assertEqual(len(result["expenses"]), 2)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["page_size"], 25)
        self.assertEqual(result["has_more_page"], False)
        self.assertEqual(result["message"], "Expenses retrieved successfully")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_list_expenses_with_filters(self, mock_api_request):
        """Test listing expenses with filters."""
        # Set up the mock
        mock_api_request.return_value = {
            **self.mock_expenses_list,
            "expenses": [self.mock_expense],
            "page_context": {**self.mock_expenses_list["page_context"], "total": 1}
        }
        
        # Call the function with filters
        result = list_expenses(
            page=2,
            page_size=10,
            status="unbilled",
            vendor_id="vendor123",
            date_range_start="2025-01-01",
            date_range_end="2025-01-31",
            search_text="office",
            sort_column="date",
            sort_order="ascending"
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "/expenses")
        self.assertEqual(kwargs["params"]["page"], 2)
        self.assertEqual(kwargs["params"]["per_page"], 10)
        self.assertEqual(kwargs["params"]["status"], "unbilled")
        self.assertEqual(kwargs["params"]["vendor_id"], "vendor123")
        self.assertEqual(kwargs["params"]["date.from"], "2025-01-01")
        self.assertEqual(kwargs["params"]["date.to"], "2025-01-31")
        self.assertEqual(kwargs["params"]["search_text"], "office")
        self.assertEqual(kwargs["params"]["sort_column"], "date")
        self.assertEqual(kwargs["params"]["sort_order"], "A")
        
        # Verify the result
        self.assertEqual(len(result["expenses"]), 1)
        self.assertEqual(result["expenses"][0]["vendor_id"], "vendor123")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_list_expenses_with_date_objects(self, mock_api_request):
        """Test listing expenses with date objects."""
        # Set up the mock
        mock_api_request.return_value = self.mock_expenses_list
        
        # Call the function with date objects
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        result = list_expenses(
            date_range_start=start_date,
            date_range_end=end_date
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(kwargs["params"]["date.from"], "2025-01-01")
        self.assertEqual(kwargs["params"]["date.to"], "2025-01-31")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_list_expenses_error(self, mock_api_request):
        """Test error handling when listing expenses."""
        # Set up the mock to raise an exception
        mock_api_request.side_effect = Exception("API error")
        
        # Verify the exception is raised
        with self.assertRaises(Exception) as context:
            list_expenses()
        
        self.assertIn("API error", str(context.exception))

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_create_expense_success(self, mock_api_request):
        """Test creating an expense successfully."""
        # Set up the mock
        mock_api_request.return_value = self.mock_create_response
        
        # Call the function
        result = create_expense(
            account_id="account123",
            date="2025-01-15",
            amount=500.50,
            paid_through_account_id="paid_account123",
            vendor_id="vendor123",
            is_billable=False,
            reference_number="REF-001",
            description="Office supplies"
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "/expenses")
        self.assertEqual(kwargs["json"]["account_id"], "account123")
        self.assertEqual(kwargs["json"]["date"], "2025-01-15")
        self.assertEqual(kwargs["json"]["amount"], 500.50)
        self.assertEqual(kwargs["json"]["paid_through_account_id"], "paid_account123")
        self.assertEqual(kwargs["json"]["vendor_id"], "vendor123")
        self.assertEqual(kwargs["json"]["is_billable"], False)
        self.assertEqual(kwargs["json"]["reference_number"], "REF-001")
        self.assertEqual(kwargs["json"]["description"], "Office supplies")
        
        # Verify the result
        self.assertEqual(result["expense"]["expense_id"], self.mock_expense_id)
        self.assertEqual(result["message"], "Expense created successfully")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_create_expense_with_date_object(self, mock_api_request):
        """Test creating an expense with a date object."""
        # Set up the mock
        mock_api_request.return_value = self.mock_create_response
        
        # Call the function with a date object
        expense_date = date(2025, 1, 15)
        result = create_expense(
            account_id="account123",
            date=expense_date,
            amount=500.50,
            paid_through_account_id="paid_account123"
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(kwargs["json"]["date"], "2025-01-15")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_create_expense_with_line_items(self, mock_api_request):
        """Test creating an expense with line items."""
        # Set up the mock
        mock_response = {
            **self.mock_create_response,
            "expense": {
                **self.mock_expense,
                "line_items": [
                    {
                        "line_item_id": "item1",
                        "account_id": "account123",
                        "amount": 300.50,
                        "description": "Paper supplies"
                    },
                    {
                        "line_item_id": "item2",
                        "account_id": "account123",
                        "amount": 200.00,
                        "description": "Printer ink"
                    }
                ]
            }
        }
        mock_api_request.return_value = mock_response
        
        # Line items to include
        line_items = [
            {
                "account_id": "account123",
                "amount": 300.50,
                "description": "Paper supplies"
            },
            {
                "account_id": "account123",
                "amount": 200.00,
                "description": "Printer ink"
            }
        ]
        
        # Call the function
        result = create_expense(
            account_id="account123",
            date="2025-01-15",
            amount=500.50,
            paid_through_account_id="paid_account123",
            line_items=line_items
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(len(kwargs["json"]["line_items"]), 2)
        self.assertEqual(kwargs["json"]["line_items"][0]["amount"], 300.50)
        self.assertEqual(kwargs["json"]["line_items"][1]["description"], "Printer ink")
        
        # Verify the result
        self.assertEqual(len(result["expense"]["line_items"]), 2)
        self.assertEqual(result["expense"]["line_items"][0]["line_item_id"], "item1")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_create_expense_with_invalid_line_item(self, mock_api_request):
        """Test error handling when creating an expense with invalid line items."""
        # Invalid line item (missing required account_id)
        line_items = [
            {
                "amount": 300.50,
                "description": "Paper supplies"
            }
        ]
        
        # Verify the exception is raised
        with self.assertRaises(ValueError) as context:
            create_expense(
                account_id="account123",
                date="2025-01-15",
                amount=500.50,
                paid_through_account_id="paid_account123",
                line_items=line_items
            )
        
        # The validation error should mention the missing account_id
        self.assertIn("account_id", str(context.exception))
        
        # Verify API was not called
        mock_api_request.assert_not_called()

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_create_expense_error(self, mock_api_request):
        """Test error handling when creating an expense."""
        # Set up the mock to raise an exception
        mock_api_request.side_effect = Exception("API error")
        
        # Verify the exception is raised
        with self.assertRaises(Exception) as context:
            create_expense(
                account_id="account123",
                date="2025-01-15",
                amount=500.50,
                paid_through_account_id="paid_account123"
            )
        
        self.assertIn("API error", str(context.exception))

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_get_expense_success(self, mock_api_request):
        """Test getting an expense successfully."""
        # Set up the mock
        mock_api_request.return_value = self.mock_get_response
        
        # Call the function
        result = get_expense(expense_id=self.mock_expense_id)
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], f"/expenses/{self.mock_expense_id}")
        
        # Verify the result
        self.assertEqual(result["expense"]["expense_id"], self.mock_expense_id)
        self.assertEqual(result["message"], "Expense retrieved successfully")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_get_expense_not_found(self, mock_api_request):
        """Test getting a non-existent expense."""
        # Set up the mock to return a response without an expense
        mock_api_request.return_value = {
            "message": "Expense not found",
            "code": 0,
        }
        
        # Call the function
        result = get_expense(expense_id="nonexistent")
        
        # Verify the result
        self.assertIsNone(result["expense"])
        self.assertEqual(result["message"], "Expense not found")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_get_expense_invalid_id(self, mock_api_request):
        """Test error handling when getting an expense with invalid ID."""
        # Verify the exception is raised with an empty expense_id
        with self.assertRaises(ValueError) as context:
            get_expense(expense_id="")
        
        self.assertIn("Invalid expense ID", str(context.exception))
        
        # Verify API was not called
        mock_api_request.assert_not_called()

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    def test_get_expense_error(self, mock_api_request):
        """Test error handling when getting an expense."""
        # Set up the mock to raise an exception
        mock_api_request.side_effect = Exception("API error")
        
        # Verify the exception is raised
        with self.assertRaises(Exception) as context:
            get_expense(expense_id=self.mock_expense_id)
        
        self.assertIn("API error", str(context.exception))

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    @patch("zoho_mcp.tools.expenses.get_expense")
    def test_update_expense_success(self, mock_get_expense, mock_api_request):
        """Test updating an expense successfully."""
        # Set up the mocks
        mock_get_expense.return_value = {"expense": self.mock_expense}
        mock_api_request.return_value = self.mock_update_response
        
        # Call the function
        result = update_expense(
            expense_id=self.mock_expense_id,
            amount=600.75,
            description="Updated office supplies"
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(args[0], "PUT")
        self.assertEqual(args[1], f"/expenses/{self.mock_expense_id}")
        self.assertEqual(kwargs["json"]["expense_id"], self.mock_expense_id)
        self.assertEqual(kwargs["json"]["amount"], 600.75)
        self.assertEqual(kwargs["json"]["description"], "Updated office supplies")
        
        # Verify unchanged fields are preserved
        self.assertEqual(kwargs["json"]["account_id"], "account123")
        self.assertEqual(kwargs["json"]["date"], "2025-01-15")
        
        # Verify the result
        self.assertEqual(result["expense"]["amount"], 600.75)
        self.assertEqual(result["expense"]["description"], "Updated office supplies")
        self.assertEqual(result["message"], "Expense updated successfully")

    @patch("zoho_mcp.tools.expenses.get_expense")
    def test_update_expense_not_found(self, mock_get_expense):
        """Test updating a non-existent expense."""
        # Set up the mock to return an empty response
        mock_get_expense.return_value = {"expense": None}
        
        # Verify the exception is raised
        with self.assertRaises(ValueError) as context:
            update_expense(
                expense_id="nonexistent",
                amount=600.75
            )
        
        self.assertIn("not found", str(context.exception))

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    @patch("zoho_mcp.tools.expenses.get_expense")
    def test_update_expense_with_date_object(self, mock_get_expense, mock_api_request):
        """Test updating an expense with a date object."""
        # Set up the mocks
        mock_get_expense.return_value = {"expense": self.mock_expense}
        mock_api_request.return_value = {
            **self.mock_update_response,
            "expense": {
                **self.mock_update_response["expense"],
                "date": "2025-02-15"
            }
        }
        
        # Call the function with a date object
        expense_date = date(2025, 2, 15)
        result = update_expense(
            expense_id=self.mock_expense_id,
            date=expense_date
        )
        
        # Verify the API request
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        self.assertEqual(kwargs["json"]["date"], "2025-02-15")
        
        # Verify the result
        self.assertEqual(result["expense"]["date"], "2025-02-15")

    @patch("zoho_mcp.tools.expenses.zoho_api_request")
    @patch("zoho_mcp.tools.expenses.get_expense")
    def test_update_expense_error(self, mock_get_expense, mock_api_request):
        """Test error handling when updating an expense."""
        # Set up the mocks
        mock_get_expense.return_value = {"expense": self.mock_expense}
        mock_api_request.side_effect = Exception("API error")
        
        # Verify the exception is raised
        with self.assertRaises(Exception) as context:
            update_expense(
                expense_id=self.mock_expense_id,
                amount=600.75
            )
        
        self.assertIn("API error", str(context.exception))


if __name__ == "__main__":
    unittest.main()