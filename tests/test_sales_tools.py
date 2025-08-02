"""
Tests for the Sales Order Management Tools.

This module contains tests for the Zoho Books sales order management tools.
"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import date

from zoho_mcp.tools.sales import (
    list_sales_orders,
    create_sales_order,
    get_sales_order,
    update_sales_order,
    convert_to_invoice,
)


# Sample test data
SAMPLE_SALES_ORDER = {
    "salesorder_id": "12345",
    "customer_id": "67890",
    "customer_name": "Test Customer",
    "salesorder_number": "SO-001",
    "date": "2023-05-01",
    "status": "open",
    "total": 1000.00,
    "line_items": [
        {
            "item_id": "item001",
            "name": "Test Item",
            "rate": 100.00,
            "quantity": 10,
        }
    ]
}

SAMPLE_SALES_ORDERS_RESPONSE = {
    "code": 0,
    "message": "success",
    "salesorders": [SAMPLE_SALES_ORDER],
    "page_context": {
        "page": 1,
        "per_page": 25,
        "has_more_page": False,
        "total": 1
    }
}

SAMPLE_SALES_ORDER_RESPONSE = {
    "code": 0,
    "message": "success",
    "salesorder": SAMPLE_SALES_ORDER
}


class TestListSalesOrders:
    """Tests for the list_sales_orders function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_list_sales_orders_success(self, mock_api_request):
        """Test successful listing of sales orders."""
        mock_api_request.return_value = SAMPLE_SALES_ORDERS_RESPONSE
        
        result = await list_sales_orders()
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "GET"
        assert args[1] == "/salesorders"
        assert kwargs["params"]["page"] == 1
        assert kwargs["params"]["per_page"] == 25
        
        assert "sales_orders" in result
        assert len(result["sales_orders"]) == 1
        assert result["total"] == 1

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_list_sales_orders_with_date_range(self, mock_api_request):
        """Test listing sales orders with date range."""
        mock_api_request.return_value = SAMPLE_SALES_ORDERS_RESPONSE
        
        result = await list_sales_orders(
            status="open",
            date_range_start="2023-01-01",
            date_range_end="2023-12-31"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert kwargs["params"]["filter_by"] == "open"
        assert kwargs["params"]["date_start"] == "2023-01-01"
        assert kwargs["params"]["date_end"] == "2023-12-31"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_list_sales_orders_error(self, mock_api_request):
        """Test error handling in list_sales_orders."""
        mock_api_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await list_sales_orders()


class TestCreateSalesOrder:
    """Tests for the create_sales_order function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_create_sales_order_success(self, mock_api_request):
        """Test successful creation of a sales order."""
        mock_api_request.return_value = SAMPLE_SALES_ORDER_RESPONSE
        
        result = await create_sales_order(
            customer_id="67890",
            date="2023-05-01",
            line_items=[
                {
                    "item_id": "item001",
                    "rate": 100.00,
                    "quantity": 10,
                }
            ]
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "POST"
        assert args[1] == "/salesorders"
        
        data = kwargs["json_data"]
        assert data["customer_id"] == "67890"
        assert data["date"] == "2023-05-01"
        assert len(data["line_items"]) == 1
        
        assert result["salesorder"]["salesorder_id"] == "12345"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_create_sales_order_validation_error(self, mock_api_request):
        """Test validation error in create_sales_order."""
        with pytest.raises(ValueError):
            await create_sales_order(
                customer_id="",  # Empty customer_id should fail
                date="2023-05-01",
                line_items=[]
            )

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_create_sales_order_api_error(self, mock_api_request):
        """Test API error handling in create_sales_order."""
        mock_api_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await create_sales_order(
                customer_id="67890",
                line_items=[{"item_id": "item001", "rate": 100.00, "quantity": 10}]
            )

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_create_sales_order_with_all_fields(self, mock_api_request):
        """Test creating sales order with all fields."""
        mock_api_request.return_value = SAMPLE_SALES_ORDER_RESPONSE
        
        result = await create_sales_order(
            customer_id="67890",
            line_items=[{"item_id": "item001", "rate": 100.00, "quantity": 10}],
            reference_number="REF-001",
            notes="Test notes",
            terms="Test terms"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        data = kwargs["json_data"]
        assert data["reference_number"] == "REF-001"
        assert data["notes"] == "Test notes"
        assert data["terms"] == "Test terms"


class TestGetSalesOrder:
    """Tests for the get_sales_order function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_get_sales_order_success(self, mock_api_request):
        """Test successful retrieval of a sales order."""
        mock_api_request.return_value = SAMPLE_SALES_ORDER_RESPONSE
        
        result = await get_sales_order("12345")
        
        mock_api_request.assert_called_once_with("GET", "/salesorders/12345")
        assert result["salesorder"]["salesorder_id"] == "12345"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_get_sales_order_not_found(self, mock_api_request):
        """Test getting a sales order that doesn't exist."""
        mock_api_request.return_value = {
            "salesorder": None,
            "message": "Sales order not found"
        }
        
        result = await get_sales_order("nonexistent")
        
        mock_api_request.assert_called_once_with("GET", "/salesorders/nonexistent")
        assert result["salesorder"] is None

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_get_sales_order_invalid_id(self, mock_api_request):
        """Test getting sales order with invalid ID."""
        with pytest.raises(ValueError):
            await get_sales_order("")  # Empty ID should raise ValueError

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_get_sales_order_api_error(self, mock_api_request):
        """Test API error handling in get_sales_order."""
        mock_api_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await get_sales_order("12345")


class TestUpdateSalesOrder:
    """Tests for the update_sales_order function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_update_sales_order_success(self, mock_api_request):
        """Test successful update of a sales order."""
        # Mock update response
        updated_order = {**SAMPLE_SALES_ORDER, "notes": "Updated notes"}
        mock_api_request.return_value = {
            "salesorder": updated_order,
            "message": "Success"
        }
        
        result = await update_sales_order(
            salesorder_id="12345",
            notes="Updated notes"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "PUT"
        assert args[1] == "/salesorders/12345"
        
        data = kwargs["json_data"]
        assert data["notes"] == "Updated notes"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_update_sales_order_no_fields(self, mock_api_request):
        """Test updating sales order with no fields provided."""
        with pytest.raises(ValueError, match="At least one field must be provided"):
            await update_sales_order(salesorder_id="12345")

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_update_sales_order_invalid_id(self, mock_api_request):
        """Test updating sales order with invalid ID."""
        with pytest.raises(ValueError):
            await update_sales_order(salesorder_id="")

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_update_sales_order_line_items(self, mock_api_request):
        """Test updating sales order with line items."""
        updated_order = {**SAMPLE_SALES_ORDER, "line_items": [{"item_id": "item002", "rate": 200.00, "quantity": 5}]}
        mock_api_request.return_value = {
            "salesorder": updated_order,
            "message": "Success"
        }
        
        result = await update_sales_order(
            salesorder_id="12345",
            line_items=[{"item_id": "item002", "rate": 200.00, "quantity": 5}]
        )
        
        data = mock_api_request.call_args[1]["json_data"]
        assert len(data["line_items"]) == 1
        assert data["line_items"][0]["item_id"] == "item002"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_update_sales_order_api_error(self, mock_api_request):
        """Test API error handling in update_sales_order."""
        mock_api_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await update_sales_order(salesorder_id="12345", notes="Updated notes")


class TestConvertToInvoice:
    """Tests for the convert_to_invoice function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_convert_to_invoice_success(self, mock_api_request):
        """Test successful conversion of sales order to invoice."""
        mock_api_request.return_value = {
            "invoice": {
                "invoice_id": "INV-001",
                "invoice_number": "INV-2023-001",
                "total": 1000.00
            },
            "message": "Success"
        }
        
        result = await convert_to_invoice("12345")
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "POST"
        assert args[1] == "/salesorders/12345/convert"
        
        assert result["invoice"]["invoice_id"] == "INV-001"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_convert_validation_error(self, mock_api_request):
        """Test validation error in convert_to_invoice."""
        with pytest.raises(ValueError):
            await convert_to_invoice("")  # Empty ID should fail

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_convert_with_custom_invoice_number(self, mock_api_request):
        """Test converting with custom invoice number."""
        mock_api_request.return_value = {
            "invoice": {
                "invoice_id": "INV-002",
                "invoice_number": "CUSTOM-001",
                "total": 1000.00
            },
            "message": "Success"
        }
        
        result = await convert_to_invoice(
            salesorder_id="12345",
            invoice_number="CUSTOM-001"
        )
        
        data = mock_api_request.call_args[1]["json_data"]
        assert data["invoice_number"] == "CUSTOM-001"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.sales.zoho_api_request_async")
    async def test_convert_api_error(self, mock_api_request):
        """Test API error handling in convert_to_invoice."""
        mock_api_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await convert_to_invoice("12345")