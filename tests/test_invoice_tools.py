"""
Unit tests for the invoice management tools.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from zoho_mcp.tools.invoices import (
    list_invoices,
    create_invoice,
    get_invoice,
    email_invoice,
    mark_invoice_as_sent,
    void_invoice,
)


def test_list_invoices_default_params():
    """Test list_invoices with default parameters."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "invoices": [
                {"invoice_id": "123", "customer_name": "Test Customer", "total": 100.0},
                {"invoice_id": "456", "customer_name": "Another Customer", "total": 200.0},
            ],
            "page_context": {"page": 1, "per_page": 25, "has_more_page": False, "total": 2},
            "message": "2 invoices found",
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = list_invoices()
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with(
            "GET", 
            "/invoices", 
            params={
                "page": 1,
                "per_page": 25,
                "sort_column": "created_time",
                "sort_order": "D",
            }
        )
        
        # Check the result
        assert result["page"] == 1
        assert result["page_size"] == 25
        assert result["has_more_page"] is False
        assert len(result["invoices"]) == 2
        assert result["message"] == "2 invoices found"


def test_list_invoices_with_filters():
    """Test list_invoices with filters."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "invoices": [
                {"invoice_id": "123", "customer_name": "Test Customer", "total": 100.0, "status": "draft"},
            ],
            "page_context": {"page": 1, "per_page": 10, "has_more_page": False, "total": 1},
            "message": "1 invoice found",
        }
        mock_request.return_value = mock_response
        
        # Call the function with filters
        result = list_invoices(
            page=1,
            page_size=10,
            status="draft",
            customer_id="CUST-123",
            date_range_start="2023-01-01",
            date_range_end="2023-12-31",
            search_text="Test",
            sort_column="date",
            sort_order="ascending",
        )
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with(
            "GET", 
            "/invoices", 
            params={
                "page": 1,
                "per_page": 10,
                "status": "draft",
                "customer_id": "CUST-123",
                "date_start": "2023-01-01",
                "date_end": "2023-12-31",
                "search_text": "Test",
                "sort_column": "date",
                "sort_order": "A",
            }
        )
        
        # Check the result
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert len(result["invoices"]) == 1
        assert result["message"] == "1 invoice found"


def test_create_invoice_success():
    """Test create_invoice success case."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "invoice": {
                "invoice_id": "INV-123",
                "invoice_number": "INV-2023-001",
                "customer_id": "CUST-123",
                "customer_name": "Test Customer",
                "total": 150.0,
                "status": "draft",
            },
            "message": "Invoice created successfully",
        }
        mock_request.return_value = mock_response
        
        # Invoice data to create
        invoice_data = {
            "customer_id": "CUST-123",
            "invoice_date": "2023-01-15",
            "due_date": "2023-02-15",
            "line_items": [
                {
                    "name": "Test Item",
                    "description": "A test item",
                    "rate": 50.0,
                    "quantity": 3,
                }
            ],
            "notes": "Test invoice",
            "terms": "Payment due within 30 days",
        }
        
        # Call the function
        result = create_invoice(**invoice_data)
        
        # Check the API was called with correct parameters
        # Note: We don't check the exact json argument because the Pydantic model adds defaults
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/invoices"
        assert "json" in call_args[1]
        
        # Check that all our original data is in the request
        sent_data = call_args[1]["json"]
        assert sent_data["customer_id"] == "CUST-123"
        assert sent_data["invoice_date"] == "2023-01-15"
        assert sent_data["due_date"] == "2023-02-15"
        assert len(sent_data["line_items"]) == 1
        assert sent_data["line_items"][0]["name"] == "Test Item"
        assert sent_data["line_items"][0]["description"] == "A test item"
        assert sent_data["line_items"][0]["rate"] == 50.0
        assert sent_data["line_items"][0]["quantity"] == 3.0  # Note: may be converted to float
        assert sent_data["notes"] == "Test invoice"
        assert sent_data["terms"] == "Payment due within 30 days"
        
        # Check the result
        assert result["invoice"]["invoice_id"] == "INV-123"
        assert result["invoice"]["customer_id"] == "CUST-123"
        assert result["message"] == "Invoice created successfully"


def test_create_invoice_validation_error():
    """Test create_invoice validation error case."""
    # Invoice data with missing required field (customer_id)
    invoice_data = {
        "invoice_date": "2023-01-15",
        "line_items": [
            {
                "name": "Test Item",
                "rate": 50.0,
                "quantity": 3,
            }
        ],
    }
    
    # Check that validation error is raised
    with pytest.raises(ValueError):
        create_invoice(**invoice_data)


def test_create_invoice_line_item_validation_error():
    """Test create_invoice line item validation error case."""
    # Invoice data with invalid line item (negative rate)
    invoice_data = {
        "customer_id": "CUST-123",
        "line_items": [
            {
                "name": "Test Item",
                "rate": -50.0,  # Negative rate is invalid
                "quantity": 3,
            }
        ],
    }
    
    # Check that validation error is raised
    with pytest.raises(ValueError):
        create_invoice(**invoice_data)


def test_get_invoice_success():
    """Test get_invoice success case."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "invoice": {
                "invoice_id": "INV-123",
                "invoice_number": "INV-2023-001",
                "customer_id": "CUST-123",
                "customer_name": "Test Customer",
                "total": 150.0,
                "status": "draft",
                "line_items": [
                    {
                        "line_item_id": "LI-123",
                        "name": "Test Item",
                        "description": "A test item",
                        "rate": 50.0,
                        "quantity": 3,
                    }
                ],
            },
            "message": "Invoice details fetched successfully",
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = get_invoice("INV-123")
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with("GET", "/invoices/INV-123")
        
        # Check the result
        assert result["invoice"]["invoice_id"] == "INV-123"
        assert result["invoice"]["customer_id"] == "CUST-123"
        assert len(result["invoice"]["line_items"]) == 1
        assert result["message"] == "Invoice details fetched successfully"


def test_get_invoice_not_found():
    """Test get_invoice when invoice is not found."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API for not found case
        mock_response = {
            "message": "Invoice not found",
            "invoice": None,
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = get_invoice("INV-999")
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with("GET", "/invoices/INV-999")
        
        # Check the result
        assert result["invoice"] is None
        assert result["message"] == "Invoice not found"


def test_email_invoice_success():
    """Test email_invoice success case."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "message": "Invoice has been emailed successfully",
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = email_invoice(
            invoice_id="INV-123",
            to_email=["customer@example.com"],
            subject="Your Invoice",
            body="Please find your invoice attached",
            cc_email=["accounting@example.com"],
        )
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with(
            "POST",
            "/invoices/INV-123/email",
            json={
                "to_mail": ["customer@example.com"],
                "subject": "Your Invoice",
                "body": "Please find your invoice attached",
                "cc_mail": ["accounting@example.com"],
                "send_customer_statement": False,
                "send_attachment": True,
            }
        )
        
        # Check the result
        assert result["success"] is True
        assert result["message"] == "Invoice has been emailed successfully"
        assert result["invoice_id"] == "INV-123"


def test_mark_invoice_as_sent_success():
    """Test mark_invoice_as_sent success case."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "message": "Invoice marked as sent",
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = mark_invoice_as_sent("INV-123")
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with("POST", "/invoices/INV-123/status/sent")
        
        # Check the result
        assert result["success"] is True
        assert result["message"] == "Invoice marked as sent"
        assert result["invoice_id"] == "INV-123"


def test_void_invoice_success():
    """Test void_invoice success case."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock response from the API
        mock_response = {
            "message": "Invoice has been voided successfully",
        }
        mock_request.return_value = mock_response
        
        # Call the function
        result = void_invoice("INV-123")
        
        # Check the API was called with correct parameters
        mock_request.assert_called_once_with("POST", "/invoices/INV-123/status/void")
        
        # Check the result
        assert result["success"] is True
        assert result["message"] == "Invoice has been voided successfully"
        assert result["invoice_id"] == "INV-123"


def test_invoice_api_error_handling():
    """Test error handling in invoice tools."""
    with patch("zoho_mcp.tools.invoices.zoho_api_request") as mock_request:
        # Mock API error
        mock_request.side_effect = Exception("API error occurred")
        
        # Check that the error is propagated
        with pytest.raises(Exception, match="API error occurred"):
            list_invoices()
            
        with pytest.raises(Exception, match="API error occurred"):
            get_invoice("INV-123")
            
        with pytest.raises(Exception, match="API error occurred"):
            void_invoice("INV-123")