"""
Unit tests for item management tools.

Tests for listing, creating, retrieving, and updating items in Zoho Books.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from zoho_mcp.tools.items import list_items, create_item, get_item, update_item
from zoho_mcp.tools.api import ZohoRequestError


# Sample item data for testing
SAMPLE_ITEM = {
    "item_id": "123456789",
    "name": "Test Item",
    "description": "Test item description",
    "item_type": "service",
    "rate": 100.0,
    "status": "active",
    "sku": "TST-001",
    "tax_id": "1234",
}

SAMPLE_ITEM_LIST = {
    "items": [SAMPLE_ITEM],
    "page_context": {
        "page": 1,
        "per_page": 25,
        "has_more_page": False,
        "total": 1
    }
}

SAMPLE_ITEM_RESPONSE = {
    "item": SAMPLE_ITEM,
    "code": 0,
    "message": "Success"
}


class TestListItems:
    """Tests for list_items function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_list_items_default(self, mock_api):
        """Test listing items with default parameters."""
        # Setup mock response
        mock_api.return_value = SAMPLE_ITEM_LIST
        
        # Call the function
        result = await list_items()
        
        # Verify API call
        mock_api.assert_called_once()
        args, kwargs = mock_api.call_args
        assert args[0] == "GET"
        assert args[1] == "/items"
        assert kwargs["params"]["page"] == 1
        assert kwargs["params"]["per_page"] == 25
        assert kwargs["params"]["sort_column"] == "name"
        assert kwargs["params"]["sort_order"] == "ascending"
        
        # Verify result structure
        assert "items" in result
        assert "page" in result
        assert "page_size" in result
        assert "has_more_page" in result
        assert "total" in result

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_list_items_with_filters(self, mock_api):
        """Test listing items with filters."""
        # Setup mock response
        filtered_response = {
            "items": [SAMPLE_ITEM],
            "page_context": {
                "page": 2,
                "per_page": 10,
                "has_more_page": False,
                "total": 1
            }
        }
        mock_api.return_value = filtered_response
        
        # Call the function with filters
        result = await list_items(
            page=2,
            page_size=10,
            item_type="service",
            status="active",
            search_text="test",
            sort_column="name",
            sort_order="ascending"
        )
        
        # Verify API call with filters
        mock_api.assert_called_once()
        args, kwargs = mock_api.call_args
        assert args[0] == "GET"
        assert args[1] == "/items"
        assert kwargs["params"]["page"] == 2
        assert kwargs["params"]["per_page"] == 10
        assert kwargs["params"]["filter_by"] == "ItemType.service"
        assert kwargs["params"]["status"] == "active"
        assert kwargs["params"]["search_text"] == "test"
        assert kwargs["params"]["sort_column"] == "name"
        assert kwargs["params"]["sort_order"] == "ascending"
        
        # Verify result
        assert result["page"] == 2
        assert result["page_size"] == 10

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_list_items_error(self, mock_api):
        """Test error handling in list_items."""
        # Setup mock to raise an exception
        mock_api.side_effect = ZohoRequestError(500, "Internal Server Error")
        
        # Call the function and expect an exception
        with pytest.raises(ZohoRequestError):
            await list_items()


class TestCreateItem:
    """Tests for create_item function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_create_item_minimal(self, mock_api):
        """Test creating an item with minimal required fields."""
        # Setup mock response
        mock_api.return_value = SAMPLE_ITEM_RESPONSE
        
        # Call the function
        result = await create_item(
            name="Test Item",
            rate=100.0
        )
        
        # Verify API call
        mock_api.assert_called_once_with(
            "POST",
            "/items",
            json_data={
                "name": "Test Item",
                "rate": 100.0,
                "item_type": "service"
            }
        )
        
        # Verify result
        assert "item" in result
        assert result["item"]["name"] == "Test Item"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_create_item_complete(self, mock_api):
        """Test creating an item with all fields."""
        # Setup mock response
        mock_api.return_value = SAMPLE_ITEM_RESPONSE
        
        # Call the function with all fields
        result = await create_item(
            name="Complete Item",
            description="A complete test item",
            item_type="service",
            rate=150.0,
            sku="CMP-001",
            unit="hours"
        )
        
        # Verify API call
        mock_api.assert_called_once()
        args, kwargs = mock_api.call_args
        assert args[0] == "POST"
        assert args[1] == "/items"
        
        # Verify the data sent
        data = kwargs["json_data"]
        assert data["name"] == "Complete Item"
        assert data["description"] == "A complete test item"
        assert data["item_type"] == "service"
        assert data["rate"] == 150.0
        assert data["sku"] == "CMP-001"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_create_item_validation_error(self, mock_api):
        """Test create_item with validation error."""
        # Don't need to set up mock since validation should fail before API call
        
        # Call the function with invalid data (missing required fields)
        with pytest.raises(TypeError):
            await create_item()  # Missing required name and rate

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_create_item_api_error(self, mock_api):
        """Test API error handling in create_item."""
        # Setup mock to raise an exception
        mock_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        # Call the function and expect an exception
        with pytest.raises(ZohoRequestError):
            await create_item(
                name="Test Item",
                rate=100.0
            )


class TestGetItem:
    """Tests for get_item function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_get_item_success(self, mock_api):
        """Test successfully getting an item."""
        # Setup mock response
        mock_api.return_value = SAMPLE_ITEM_RESPONSE
        
        # Call the function
        result = await get_item("123456789")
        
        # Verify API call
        mock_api.assert_called_once_with("GET", "/items/123456789")
        
        # Verify result
        assert "item" in result
        assert result["item"]["item_id"] == "123456789"

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_get_item_not_found(self, mock_api):
        """Test getting an item that doesn't exist."""
        # Setup mock response for not found
        mock_api.return_value = {
            "item": None,
            "message": "Item not found"
        }
        
        # Call the function
        result = await get_item("nonexistent")
        
        # Verify API call
        mock_api.assert_called_once_with("GET", "/items/nonexistent")
        
        # Verify result
        assert result["item"] is None
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_get_item_invalid_id(self, mock_api):
        """Test getting an item with invalid ID."""
        # Call the function with invalid ID
        with pytest.raises(ValueError):
            await get_item("")  # Empty ID should raise ValueError

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_get_item_api_error(self, mock_api):
        """Test API error handling in get_item."""
        # Setup mock to raise an exception
        mock_api.side_effect = ZohoRequestError(500, "Internal Server Error")
        
        # Call the function and expect an exception
        with pytest.raises(ZohoRequestError):
            await get_item("123456789")


class TestUpdateItem:
    """Tests for update_item function."""
    
    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.get_item")
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_update_item_partial(self, mock_api, mock_get_item):
        """Test updating an item with partial data."""
        # Mock get_item response
        mock_get_item.return_value = {
            "item": SAMPLE_ITEM,
            "message": "Item retrieved successfully"
        }
        
        # Setup mock response for update
        updated_item = {**SAMPLE_ITEM, "name": "Updated Item", "rate": 200.0}
        mock_response = {
            "item": updated_item,
            "code": 0,
            "message": "Success"
        }
        mock_api.return_value = mock_response
        
        # Call the function
        result = await update_item(
            item_id="123456789",
            name="Updated Item",
            rate=200.0
        )
        
        # Verify get_item was called first
        mock_get_item.assert_called_once_with("123456789")
        
        # Verify API call
        mock_api.assert_called_once()
        args, kwargs = mock_api.call_args
        assert args[0] == "PUT"
        assert args[1] == "/items/123456789"
        
        # Verify the data sent
        data = kwargs["json_data"]
        assert data["name"] == "Updated Item"
        assert data["rate"] == 200.0
        
        # Verify result
        assert result["item"]["name"] == "Updated Item"
        assert result["item"]["rate"] == 200.0

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_update_item_not_found(self, mock_api):
        """Test updating an item that doesn't exist."""
        from zoho_mcp.errors import ResourceNotFoundError
        
        # Setup mock to raise not found error
        mock_api.side_effect = ResourceNotFoundError("items", "nonexistent", "Item not found")
        
        # Call the function and expect an exception
        with pytest.raises(ResourceNotFoundError):
            await update_item(
                item_id="nonexistent",
                name="Updated Item"
            )

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.get_item")
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_update_item_all_fields(self, mock_api, mock_get_item):
        """Test updating an item with all fields."""
        # Mock get_item response
        mock_get_item.return_value = {
            "item": SAMPLE_ITEM,
            "message": "Item retrieved successfully"
        }
        
        # Setup mock response
        updated_item = {
            **SAMPLE_ITEM,
            "name": "Fully Updated Item",
            "description": "Updated description",
            "rate": 300.0,
            "status": "inactive"
        }
        mock_response = {
            "item": updated_item,
            "code": 0,
            "message": "Success"
        }
        mock_api.return_value = mock_response
        
        # Call the function with all fields
        result = await update_item(
            item_id="123456789",
            name="Fully Updated Item",
            description="Updated description",
            rate=300.0,
            sku="UPD-001",
            unit="pieces"
        )
        
        # Verify the result
        assert result["item"]["name"] == "Fully Updated Item"
        assert result["item"]["description"] == "Updated description"
        assert result["item"]["rate"] == 300.0

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_update_item_validation_error(self, mock_api):
        """Test update_item with validation error."""
        # Call the function with invalid item_id
        with pytest.raises(ValueError):
            await update_item(item_id="")  # Empty item_id should raise ValueError

    @pytest.mark.asyncio
    @patch("zoho_mcp.tools.items.zoho_api_request_async")
    async def test_update_item_api_error(self, mock_api):
        """Test API error handling in update_item."""
        # Setup mock to raise an exception
        mock_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        # Call the function and expect an exception
        with pytest.raises(ZohoRequestError):
            await update_item(
                item_id="123456789",
                name="Updated Item"
            )