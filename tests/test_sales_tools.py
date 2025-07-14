"""
Tests for the Sales Order Management Tools.

This module contains tests for the Zoho Books sales order management tools.
"""

import unittest
from unittest.mock import patch, Mock, ANY
from datetime import date

from zoho_mcp.tools.sales import (
    list_sales_orders,
    create_sales_order,
    get_sales_order,
    update_sales_order,
    convert_to_invoice,
)
from zoho_mcp.tools.api import ZohoAPIError


class TestListSalesOrders(unittest.TestCase):
    """Tests for the list_sales_orders function."""
    
    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_list_sales_orders_success(self, mock_api_request):
        """Test successful listing of sales orders."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "success",
            "salesorders": [
                {
                    "salesorder_id": "12345",
                    "customer_id": "67890",
                    "customer_name": "Test Customer",
                    "salesorder_number": "SO-001",
                    "date": "2023-05-01",
                    "status": "open",
                    "total": 1000.00,
                },
                {
                    "salesorder_id": "12346",
                    "customer_id": "67891",
                    "customer_name": "Another Customer",
                    "salesorder_number": "SO-002",
                    "date": "2023-05-02",
                    "status": "draft",
                    "total": 2000.00,
                },
            ],
            "page_context": {
                "page": 1,
                "per_page": 25,
                "has_more_page": False,
                "total": 2,
            },
        }
        
        # Call the function
        result = list_sales_orders(
            page=1,
            page_size=25,
            status="all",
            customer_id=None,
            sort_column="date",
            sort_order="descending",
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once_with(
            "GET",
            "/salesorders",
            params={
                "page": 1,
                "per_page": 25,
                "filter_by": "all",
                "sort_column": "date",
                "sort_order": "D",
            },
        )
        
        # Assert the result is formatted correctly
        self.assertEqual(len(result["sales_orders"]), 2)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["page_size"], 25)
        self.assertEqual(result["message"], "success")
        self.assertEqual(result["total"], 2)
        self.assertFalse(result["has_more_page"])

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_list_sales_orders_with_date_range(self, mock_api_request):
        """Test listing sales orders with date range filters."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "success",
            "salesorders": [],
            "page_context": {"page": 1, "per_page": 25, "has_more_page": False, "total": 0},
        }
        
        # Call the function with date range
        result = list_sales_orders(
            date_range_start=date(2023, 5, 1),
            date_range_end="2023-05-31",
        )
        
        # Assert the API was called correctly with date range parameters
        mock_api_request.assert_called_once()
        call_args = mock_api_request.call_args[1]
        self.assertEqual(call_args["params"]["date_start"], "2023-05-01")
        self.assertEqual(call_args["params"]["date_end"], "2023-05-31")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_list_sales_orders_error(self, mock_api_request):
        """Test handling of API errors when listing sales orders."""
        # Mock API error
        mock_api_request.side_effect = ZohoAPIError(400, "Invalid request")
        
        # Assert the error is propagated
        with self.assertRaises(ZohoAPIError):
            list_sales_orders()


class TestCreateSalesOrder(unittest.TestCase):
    """Tests for the create_sales_order function."""
    
    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_create_sales_order_success(self, mock_api_request):
        """Test successful creation of a sales order."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Sales order created successfully",
            "salesorder": {
                "salesorder_id": "12345",
                "customer_id": "67890",
                "customer_name": "Test Customer",
                "salesorder_number": "SO-001",
                "date": "2023-05-01",
                "status": "draft",
                "total": 1000.00,
            },
        }
        
        # Sample line items
        line_items = [
            {
                "item_id": "item1",
                "name": "Product 1",
                "description": "Test product",
                "rate": 100.00,
                "quantity": 2,
            },
            {
                "item_id": "item2",
                "name": "Product 2",
                "description": "Another test product",
                "rate": 200.00,
                "quantity": 4,
            },
        ]
        
        # Call the function
        result = create_sales_order(
            customer_id="67890",
            line_items=line_items,
            date="2023-05-01",
            notes="Test sales order",
            terms="Net 30",
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once()
        self.assertEqual(mock_api_request.call_args[0][0], "POST")
        self.assertEqual(mock_api_request.call_args[0][1], "/salesorders")
        
        # Check JSON payload
        json_data = mock_api_request.call_args[1]["json"]
        self.assertEqual(json_data["customer_id"], "67890")
        self.assertEqual(len(json_data["line_items"]), 2)
        self.assertEqual(json_data["date"], "2023-05-01")
        self.assertEqual(json_data["notes"], "Test sales order")
        self.assertEqual(json_data["terms"], "Net 30")
        
        # Assert the result is formatted correctly
        self.assertEqual(result["salesorder"]["salesorder_id"], "12345")
        self.assertEqual(result["message"], "Sales order created successfully")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_create_sales_order_with_all_fields(self, mock_api_request):
        """Test creation of a sales order with all optional fields."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Sales order created successfully",
            "salesorder": {"salesorder_id": "12345"},
        }
        
        # Call the function with all fields
        result = create_sales_order(
            customer_id="67890",
            line_items=[{"item_id": "item1", "name": "Product 1", "rate": 100.00, "quantity": 2}],
            date="2023-05-01",
            salesorder_number="SO-CUSTOM-001",
            reference_number="REF-001",
            shipment_date="2023-05-15",
            notes="Test sales order",
            terms="Net 30",
            contact_persons=["contact1", "contact2"],
            currency_id="USD",
            is_inclusive_tax=False,
            discount="10%",
            is_discount_before_tax=True,
            discount_type="entity_level",
            shipping_charge=50.00,
            adjustment=10.00,
            adjustment_description="Rounding adjustment",
            billing_address={"address": "123 Main St", "city": "Anytown", "state": "CA"},
            shipping_address={"address": "456 Oak St", "city": "Anytown", "state": "CA"},
            custom_fields={"field1": "value1"},
            salesperson_id="sales1",
            salesperson_name="John Doe",
            template_id="template1",
            location_id="location1",
        )
        
        # Assert the API was called with all fields
        mock_api_request.assert_called_once()
        json_data = mock_api_request.call_args[1]["json"]
        
        # Check a few key fields
        self.assertEqual(json_data["customer_id"], "67890")
        self.assertEqual(json_data["salesorder_number"], "SO-CUSTOM-001")
        self.assertEqual(json_data["shipment_date"], "2023-05-15")
        self.assertEqual(json_data["discount"], "10%")
        self.assertTrue(json_data["is_discount_before_tax"])
        self.assertEqual(json_data["shipping_charge"], 50.00)
        self.assertEqual(json_data["salesperson_name"], "John Doe")
        
        # Assert the result is returned properly
        self.assertEqual(result["salesorder"]["salesorder_id"], "12345")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_create_sales_order_validation_error(self, mock_api_request):
        """Test validation error when creating a sales order."""
        # Try to create a sales order without required fields
        with self.assertRaises(ValueError):
            create_sales_order(
                customer_id="67890",
                line_items=[{"description": "Invalid line item without rate or quantity"}],
            )
        
        # Assert the API was not called
        mock_api_request.assert_not_called()

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_create_sales_order_api_error(self, mock_api_request):
        """Test handling of API errors when creating a sales order."""
        # Mock API error
        mock_api_request.side_effect = ZohoAPIError(400, "Invalid request")
        
        # Attempt to create a sales order
        with self.assertRaises(ZohoAPIError):
            create_sales_order(
                customer_id="67890",
                line_items=[{"item_id": "item1", "rate": 100.00, "quantity": 2}],
            )


class TestGetSalesOrder(unittest.TestCase):
    """Tests for the get_sales_order function."""
    
    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_get_sales_order_success(self, mock_api_request):
        """Test successful retrieval of a sales order."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "success",
            "salesorder": {
                "salesorder_id": "12345",
                "customer_id": "67890",
                "customer_name": "Test Customer",
                "salesorder_number": "SO-001",
                "date": "2023-05-01",
                "status": "draft",
                "line_items": [
                    {"item_id": "item1", "name": "Product 1", "quantity": 2, "rate": 100.00},
                ],
                "total": 200.00,
            },
        }
        
        # Call the function
        result = get_sales_order("12345")
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once_with("GET", "/salesorders/12345")
        
        # Assert the result is formatted correctly
        self.assertEqual(result["salesorder"]["salesorder_id"], "12345")
        self.assertEqual(result["salesorder"]["customer_name"], "Test Customer")
        self.assertEqual(len(result["salesorder"]["line_items"]), 1)

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_get_sales_order_not_found(self, mock_api_request):
        """Test retrieval of a non-existent sales order."""
        # Mock API response for not found
        mock_api_request.return_value = {
            "code": 0,
            "message": "No data available",
            "salesorder": None,
        }
        
        # Call the function
        result = get_sales_order("nonexistent")
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once_with("GET", "/salesorders/nonexistent")
        
        # Assert the result indicates not found
        self.assertIsNone(result["salesorder"])
        self.assertEqual(result["message"], "Sales order not found")

    def test_get_sales_order_invalid_id(self):
        """Test retrieval with an invalid sales order ID."""
        # Test with None
        with self.assertRaises(ValueError):
            get_sales_order(None)
        
        # Test with empty string
        with self.assertRaises(ValueError):
            get_sales_order("")
        
        # Test with non-string
        with self.assertRaises(ValueError):
            get_sales_order(12345)

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_get_sales_order_api_error(self, mock_api_request):
        """Test handling of API errors when retrieving a sales order."""
        # Mock API error
        mock_api_request.side_effect = ZohoAPIError(404, "Sales order not found")
        
        # Attempt to get a sales order
        with self.assertRaises(ZohoAPIError):
            get_sales_order("12345")


class TestUpdateSalesOrder(unittest.TestCase):
    """Tests for the update_sales_order function."""
    
    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_update_sales_order_success(self, mock_api_request):
        """Test successful update of a sales order."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Sales order updated successfully",
            "salesorder": {
                "salesorder_id": "12345",
                "customer_id": "67890",
                "notes": "Updated notes",
                "total": 200.00,
            },
        }
        
        # Call the function
        result = update_sales_order(
            salesorder_id="12345",
            notes="Updated notes",
            shipment_date="2023-06-01",
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once()
        self.assertEqual(mock_api_request.call_args[0][0], "PUT")
        self.assertEqual(mock_api_request.call_args[0][1], "/salesorders/12345")
        
        # Check JSON payload
        json_data = mock_api_request.call_args[1]["json"]
        self.assertEqual(json_data["notes"], "Updated notes")
        self.assertEqual(json_data["shipment_date"], "2023-06-01")
        
        # Assert the result is formatted correctly
        self.assertEqual(result["salesorder"]["salesorder_id"], "12345")
        self.assertEqual(result["message"], "Sales order updated successfully")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_update_sales_order_line_items(self, mock_api_request):
        """Test updating sales order line items."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Sales order updated successfully",
            "salesorder": {"salesorder_id": "12345"},
        }
        
        # Updated line items
        line_items = [
            {
                "line_item_id": "line1",  # Existing line item
                "quantity": 3,  # Updated quantity
            },
            {
                "item_id": "item2",  # New line item
                "name": "New Product",
                "rate": 150.00,
                "quantity": 1,
            },
        ]
        
        # Call the function
        result = update_sales_order(
            salesorder_id="12345",
            line_items=line_items,
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once()
        
        # Check JSON payload
        json_data = mock_api_request.call_args[1]["json"]
        self.assertEqual(len(json_data["line_items"]), 2)
        self.assertEqual(json_data["line_items"][0]["line_item_id"], "line1")
        self.assertEqual(json_data["line_items"][0]["quantity"], 3)
        self.assertEqual(json_data["line_items"][1]["item_id"], "item2")
        self.assertEqual(json_data["line_items"][1]["name"], "New Product")

    def test_update_sales_order_no_fields(self):
        """Test update with no fields to update."""
        # Try to update without providing any fields
        with self.assertRaises(ValueError):
            update_sales_order(salesorder_id="12345")

    def test_update_sales_order_invalid_id(self):
        """Test update with an invalid sales order ID."""
        # Test with None
        with self.assertRaises(ValueError):
            update_sales_order(salesorder_id=None, notes="Test")
        
        # Test with empty string
        with self.assertRaises(ValueError):
            update_sales_order(salesorder_id="", notes="Test")
        
        # Test with non-string
        with self.assertRaises(ValueError):
            update_sales_order(salesorder_id=12345, notes="Test")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_update_sales_order_api_error(self, mock_api_request):
        """Test handling of API errors when updating a sales order."""
        # Mock API error
        mock_api_request.side_effect = ZohoAPIError(404, "Sales order not found")
        
        # Attempt to update a sales order
        with self.assertRaises(ZohoAPIError):
            update_sales_order(
                salesorder_id="12345",
                notes="Updated notes",
            )


class TestConvertToInvoice(unittest.TestCase):
    """Tests for the convert_to_invoice function."""
    
    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_convert_to_invoice_success(self, mock_api_request):
        """Test successful conversion of a sales order to an invoice."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Sales order converted to invoice successfully",
            "invoice": {
                "invoice_id": "INV-001",
                "salesorder_id": "12345",
                "customer_id": "67890",
                "invoice_number": "INV-001",
                "status": "draft",
                "total": 200.00,
            },
        }
        
        # Call the function
        result = convert_to_invoice(
            salesorder_id="12345",
            date="2023-06-01",
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once()
        self.assertEqual(mock_api_request.call_args[0][0], "POST")
        self.assertEqual(mock_api_request.call_args[0][1], "/salesorders/12345/convert")
        
        # Check JSON payload
        json_data = mock_api_request.call_args[1]["json"]
        self.assertEqual(json_data["salesorder_id"], "12345")
        self.assertEqual(json_data["date"], "2023-06-01")
        
        # Assert the result is formatted correctly
        self.assertEqual(result["invoice"]["invoice_id"], "INV-001")
        self.assertEqual(result["invoice"]["salesorder_id"], "12345")
        self.assertEqual(result["message"], "Sales order converted to invoice successfully")

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_convert_with_custom_invoice_number(self, mock_api_request):
        """Test conversion with a custom invoice number."""
        # Mock API response
        mock_api_request.return_value = {
            "code": 0,
            "message": "Success",
            "invoice": {"invoice_id": "INV-CUSTOM-001"},
        }
        
        # Call the function
        result = convert_to_invoice(
            salesorder_id="12345",
            ignore_auto_number_generation=True,
            invoice_number="INV-CUSTOM-001",
        )
        
        # Assert the API was called correctly
        mock_api_request.assert_called_once()
        
        # Check JSON payload
        json_data = mock_api_request.call_args[1]["json"]
        self.assertEqual(json_data["salesorder_id"], "12345")
        self.assertEqual(json_data["ignore_auto_number_generation"], True)
        self.assertEqual(json_data["invoice_number"], "INV-CUSTOM-001")
        
        # Check query parameters
        params = mock_api_request.call_args[1]["params"]
        self.assertEqual(params["ignore_auto_number_generation"], "true")

    def test_convert_validation_error(self):
        """Test validation errors when converting to invoice."""
        # Test with ignore_auto_number_generation=True but no invoice_number
        with self.assertRaises(ValueError):
            convert_to_invoice(
                salesorder_id="12345",
                ignore_auto_number_generation=True,
            )

    @patch("zoho_mcp.tools.sales.zoho_api_request")
    def test_convert_api_error(self, mock_api_request):
        """Test handling of API errors when converting to invoice."""
        # Mock API error
        mock_api_request.side_effect = ZohoAPIError(400, "Invalid request")
        
        # Attempt to convert a sales order
        with self.assertRaises(ZohoAPIError):
            convert_to_invoice(salesorder_id="12345")


if __name__ == "__main__":
    unittest.main()