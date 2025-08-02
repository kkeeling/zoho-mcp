"""
Unit tests for expense management tools in Zoho Books MCP Integration Server.
"""

import pytest
from datetime import date
from unittest.mock import patch, AsyncMock

from zoho_mcp.tools.expenses import (
    list_expenses,
    create_expense,
    get_expense,
    update_expense,
)


# Test fixtures
MOCK_EXPENSE_ID = "123456789"
MOCK_EXPENSE = {
    "expense_id": MOCK_EXPENSE_ID,
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

MOCK_EXPENSES_LIST = {
    "expenses": [MOCK_EXPENSE, {
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


class TestExpenseTools:
    """Test cases for expense management tools."""

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_list_expenses_success(self, mock_api_request):
        """Test listing expenses with default parameters."""
        mock_api_request.return_value = MOCK_EXPENSES_LIST
        
        result = await list_expenses()
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "GET"
        assert args[1] == "/expenses"
        assert kwargs["params"]["page"] == 1
        assert kwargs["params"]["per_page"] == 25
        
        assert len(result["expenses"]) == 2
        assert result["total"] == 2
        assert result["page"] == 1
        assert result["page_size"] == 25
        assert result["has_more_page"] is False
        assert result["message"] == "Expenses retrieved successfully"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_list_expenses_with_filters(self, mock_api_request):
        """Test listing expenses with filters."""
        filtered_response = {
            **MOCK_EXPENSES_LIST,
            "expenses": [MOCK_EXPENSE],
            "page_context": {**MOCK_EXPENSES_LIST["page_context"], "total": 1}
        }
        mock_api_request.return_value = filtered_response
        
        result = await list_expenses(
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
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "GET"
        assert args[1] == "/expenses"
        assert kwargs["params"]["page"] == 2
        assert kwargs["params"]["per_page"] == 10
        assert kwargs["params"]["status"] == "unbilled"
        assert kwargs["params"]["vendor_id"] == "vendor123"
        assert kwargs["params"]["date.from"] == "2025-01-01"
        assert kwargs["params"]["date.to"] == "2025-01-31"
        assert kwargs["params"]["search_text"] == "office"
        assert kwargs["params"]["sort_column"] == "date"
        assert kwargs["params"]["sort_order"] == "ascending"
        
        assert len(result["expenses"]) == 1

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_list_expenses_with_date_objects(self, mock_api_request):
        """Test listing expenses with date objects."""
        mock_api_request.return_value = MOCK_EXPENSES_LIST
        
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = await list_expenses(
            date_range_start=start_date,
            date_range_end=end_date
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert kwargs["params"]["date.from"] == "2025-01-01"
        assert kwargs["params"]["date.to"] == "2025-01-31"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_list_expenses_error(self, mock_api_request):
        """Test error handling in list_expenses."""
        mock_api_request.side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="API error"):
            await list_expenses()

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_create_expense_success(self, mock_api_request):
        """Test creating an expense successfully."""
        create_response = {
            "expense": MOCK_EXPENSE,
            "message": "Expense created successfully",
            "code": 0,
        }
        mock_api_request.return_value = create_response
        
        result = await create_expense(
            account_id="account123",
            paid_through_account_id="paid_account123",
            date="2025-01-15",
            amount=500.50,
            vendor_id="vendor123",
            description="Office supplies"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "POST"
        assert args[1] == "/expenses"
        assert "json_data" in kwargs
        
        expense_data = kwargs["json_data"]
        assert expense_data["account_id"] == "account123"
        assert expense_data["amount"] == 500.50
        assert expense_data["description"] == "Office supplies"
        
        assert result["expense"]["expense_id"] == MOCK_EXPENSE_ID
        assert result["message"] == "Expense created successfully"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_create_expense_with_date_object(self, mock_api_request):
        """Test creating an expense with date object."""
        create_response = {
            "expense": MOCK_EXPENSE,
            "message": "Expense created successfully",
            "code": 0,
        }
        mock_api_request.return_value = create_response
        
        expense_date = date(2025, 1, 15)
        
        result = await create_expense(
            account_id="account123",
            paid_through_account_id="paid_account123",
            date=expense_date,
            amount=500.50,
            vendor_id="vendor123"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        expense_data = kwargs["json_data"]
        assert expense_data["date"] == "2025-01-15"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_create_expense_error(self, mock_api_request):
        """Test error handling in create_expense."""
        mock_api_request.side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="API error"):
            await create_expense(
                account_id="account123",
                paid_through_account_id="paid_account123",
                date="2025-01-15",
                amount=500.50,
                vendor_id="vendor123"
            )

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_get_expense_success(self, mock_api_request):
        """Test getting an expense successfully."""
        get_response = {
            "expense": MOCK_EXPENSE,
            "message": "Expense retrieved successfully",
            "code": 0,
        }
        mock_api_request.return_value = get_response
        
        result = await get_expense(MOCK_EXPENSE_ID)
        
        mock_api_request.assert_called_once_with("GET", f"/expenses/{MOCK_EXPENSE_ID}")
        assert result["expense"]["expense_id"] == MOCK_EXPENSE_ID
        assert result["message"] == "Expense retrieved successfully"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_get_expense_not_found(self, mock_api_request):
        """Test getting an expense that doesn't exist."""
        get_response = {
            "message": "Expense not found",
            "expense": None,
        }
        mock_api_request.return_value = get_response
        
        result = await get_expense("nonexistent")
        
        mock_api_request.assert_called_once_with("GET", "/expenses/nonexistent")
        assert result["expense"] is None
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_get_expense_error(self, mock_api_request):
        """Test error handling in get_expense."""
        mock_api_request.side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="API error"):
            await get_expense(MOCK_EXPENSE_ID)

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_update_expense_success(self, mock_api_request):
        """Test updating an expense successfully."""
        # Mock the update response
        update_response = {
            "expense": {
                **MOCK_EXPENSE,
                "amount": 600.75,
                "description": "Updated office supplies"
            },
            "message": "Expense updated successfully",
            "code": 0,
        }
        mock_api_request.return_value = update_response
        
        result = await update_expense(
            MOCK_EXPENSE_ID,
            amount=600.75,
            description="Updated office supplies"
        )
        
        mock_api_request.assert_called_once()
        args, kwargs = mock_api_request.call_args
        assert args[0] == "PUT"
        assert args[1] == f"/expenses/{MOCK_EXPENSE_ID}"
        assert "json_data" in kwargs
        
        expense_data = kwargs["json_data"]
        assert expense_data["amount"] == 600.75
        assert expense_data["description"] == "Updated office supplies"
        
        assert result["expense"]["amount"] == 600.75
        assert result["message"] == "Expense updated successfully"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_update_expense_not_found(self, mock_api_request):
        """Test updating an expense that doesn't exist."""
        from zoho_mcp.errors import ResourceNotFoundError
        
        mock_api_request.side_effect = ResourceNotFoundError("expenses", "nonexistent", "Invalid URL Passed")
        
        with pytest.raises(ResourceNotFoundError):
            await update_expense("nonexistent", amount=100.0)

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.expenses.zoho_api_request_async")
    async def test_update_expense_error(self, mock_api_request):
        """Test error handling in update_expense."""
        mock_api_request.side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="API error"):
            await update_expense(MOCK_EXPENSE_ID, amount=600.75)