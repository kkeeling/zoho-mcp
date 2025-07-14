"""
Item Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing items (products and services) in Zoho Books.
"""

import logging
from typing import Any, Dict, Literal, Optional, TYPE_CHECKING

# Only used for type checking
if TYPE_CHECKING:
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from zoho_mcp.models.items import (
    ItemInput,
    ListItemsInput,
    ItemResponse,
    ItemsListResponse,
)
from zoho_mcp.tools.api import zoho_api_request_async

logger = logging.getLogger(__name__)


async def list_items(
    page: int = 1,
    page_size: int = 25,
    item_type: Optional[Literal["service", "goods", "inventory", "all"]] = None,
    search_text: Optional[str] = None,
    status: Optional[Literal["active", "inactive"]] = None,
    sort_column: str = "name",
    sort_order: str = "ascending",
) -> Dict[str, Any]:
    """
    List items (products and services) in Zoho Books with pagination and filtering.
    
    Args:
        page: Page number for pagination
        page_size: Number of items per page
        item_type: Filter by item type (service, goods, inventory, or all)
        search_text: Search text to filter items by name or description
        status: Filter items by status (active or inactive)
        sort_column: Column to sort by (name, created_time, last_modified_time)
        sort_order: Sort order (ascending or descending)
        
    Returns:
        A paginated list of items matching the filters
    """
    logger.info(
        f"Listing items with page={page}, item_type={item_type or 'None'}, "
        f"status={status or 'None'}, search_text={search_text or 'None'}"
    )
    
    # Validate inputs using the Pydantic model
    try:
        ListItemsInput(
            page=page,
            item_type=item_type,
            search_text=search_text,
            status=status,
        )
    except Exception as e:
        logger.error(f"Validation error listing items: {str(e)}")
        raise ValueError(f"Invalid list items parameters: {str(e)}")
    
    # Build query parameters
    params = {
        "page": page,
        "per_page": page_size,
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
    
    # Add optional filters if provided
    if item_type and item_type != "all":
        params["filter_by"] = f"ItemType.{item_type}"
    if status:
        params["status"] = status
    if search_text:
        params["search_text"] = search_text
    
    try:
        response = await zoho_api_request_async("GET", "/items", params=params)
        
        # Parse the response
        items_response = ItemsListResponse.model_validate(response)
        
        # Construct paginated response
        result = {
            "page": page,
            "page_size": page_size,
            "has_more_page": response.get("page_context", {}).get("has_more_page", False),
            "items": items_response.items or [],
            "message": items_response.message,
        }
        
        # Add total count if available
        if "page_context" in response and "total" in response["page_context"]:
            result["total"] = response["page_context"]["total"]
            
        logger.info(f"Retrieved {len(result['items'])} items")
        return result
        
    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        raise


async def create_item(
    name: str,
    rate: float,
    description: Optional[str] = None,
    item_type: Literal["service", "goods", "inventory"] = "service",
    sku: Optional[str] = None,
    unit: Optional[str] = None,
    initial_stock: Optional[float] = None,
    initial_stock_rate: Optional[float] = None,
    purchase_account_id: Optional[str] = None,
    inventory_account_id: Optional[str] = None,
    sales_account_id: Optional[str] = None,
    purchase_description: Optional[str] = None,
    tax_id: Optional[str] = None,
    tax_name: Optional[str] = None,
    tax_percentage: Optional[float] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new item in Zoho Books.
    
    Args:
        name: Name of the item (required)
        rate: Price/rate of the item (required)
        description: Description of the item
        item_type: Type of item (service, goods, inventory), defaults to service
        sku: Stock Keeping Unit (SKU)
        unit: Unit of measurement (e.g., pcs, hrs)
        initial_stock: Initial stock quantity (required for inventory items)
        initial_stock_rate: Initial stock rate/cost (required for inventory items)
        purchase_account_id: ID of the purchase account
        inventory_account_id: ID of the inventory account (required for inventory items)
        sales_account_id: ID of the sales account
        purchase_description: Description for purchases
        tax_id: ID of the tax
        tax_name: Name of the tax (only if tax_id not provided)
        tax_percentage: Tax percentage (required if tax_name is provided)
        custom_fields: Custom field values
        
    Returns:
        The created item details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating item with name: {name}, type: {item_type}")
    
    # Combine all parameters into a dictionary for validation
    item_data = {
        "name": name,
        "rate": rate,
        "description": description,
        "item_type": item_type,
        "sku": sku,
        "unit": unit,
        "initial_stock": initial_stock,
        "initial_stock_rate": initial_stock_rate,
        "purchase_account_id": purchase_account_id,
        "inventory_account_id": inventory_account_id,
        "sales_account_id": sales_account_id,
        "purchase_description": purchase_description,
        "tax_id": tax_id,
        "tax_name": tax_name,
        "tax_percentage": tax_percentage,
        "custom_fields": custom_fields,
    }
    
    # Validate using the ItemInput model
    try:
        validated_item = ItemInput.model_validate(item_data)
    except Exception as e:
        logger.error(f"Validation error creating item: {str(e)}")
        raise ValueError(f"Invalid item data: {str(e)}")
    
    # Prepare data for API request
    data = validated_item.model_dump(exclude_none=True)
    
    try:
        response = await zoho_api_request_async("POST", "/items", json_data=data)
        
        # Parse the response
        item_response = ItemResponse.model_validate(response)
        
        logger.info(f"Item created successfully: {item_response.item.get('item_id') if item_response.item else 'Unknown ID'}")
        
        return {
            "item": item_response.item,
            "message": item_response.message or "Item created successfully",
        }
        
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise


async def get_item(item_id: str) -> Dict[str, Any]:
    """
    Get an item by ID from Zoho Books.
    
    Args:
        item_id: ID of the item to retrieve
        
    Returns:
        The item details
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Getting item with ID: {item_id}")
    
    # Validate item_id - simple string validation
    if not item_id or not isinstance(item_id, str):
        logger.error("Invalid item ID: Item ID cannot be empty")
        raise ValueError("Invalid item ID: Item ID cannot be empty")
    
    try:
        response = await zoho_api_request_async("GET", f"/items/{item_id}")
        
        # Parse the response
        item_response = ItemResponse.model_validate(response)
        
        if not item_response.item:
            logger.warning(f"Item not found: {item_id}")
            return {
                "message": "Item not found",
                "item": None,
            }
        
        logger.info(f"Item retrieved successfully: {item_id}")
        
        return {
            "item": item_response.item,
            "message": item_response.message or "Item retrieved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error getting item: {str(e)}")
        raise


async def update_item(
    item_id: str,
    name: Optional[str] = None,
    rate: Optional[float] = None,
    description: Optional[str] = None,
    sku: Optional[str] = None,
    unit: Optional[str] = None,
    tax_id: Optional[str] = None,
    tax_name: Optional[str] = None,
    tax_percentage: Optional[float] = None,
    purchase_account_id: Optional[str] = None,
    inventory_account_id: Optional[str] = None,
    sales_account_id: Optional[str] = None,
    purchase_description: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update an existing item in Zoho Books.
    
    Args:
        item_id: ID of the item to update (required)
        name: Updated name of the item
        rate: Updated price/rate of the item
        description: Updated description of the item
        sku: Updated Stock Keeping Unit (SKU)
        unit: Updated unit of measurement (e.g., pcs, hrs)
        tax_id: Updated ID of the tax
        tax_name: Updated name of the tax (only if tax_id not provided)
        tax_percentage: Updated tax percentage (required if tax_name is provided)
        purchase_account_id: Updated ID of the purchase account
        inventory_account_id: Updated ID of the inventory account
        sales_account_id: Updated ID of the sales account
        purchase_description: Updated description for purchases
        custom_fields: Updated custom field values
        
    Returns:
        The updated item details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Updating item with ID: {item_id}")
    
    # First, get the current item to update only the provided fields
    try:
        current_item = await get_item(item_id)
        if not current_item["item"]:
            raise ValueError(f"Item with ID {item_id} not found")
        
        # Extract the current data
        current_data = current_item["item"]
        
        # Prepare the update data with current values for required fields
        update_data = {
            "name": name if name is not None else current_data.get("name"),
            "rate": rate if rate is not None else current_data.get("rate"),
        }
        
        # Add optional fields only if provided
        if description is not None:
            update_data["description"] = description
        if sku is not None:
            update_data["sku"] = sku
        if unit is not None:
            update_data["unit"] = unit
        if tax_id is not None:
            update_data["tax_id"] = tax_id
        if tax_name is not None:
            update_data["tax_name"] = tax_name
        if tax_percentage is not None:
            update_data["tax_percentage"] = tax_percentage
        if purchase_account_id is not None:
            update_data["purchase_account_id"] = purchase_account_id
        if inventory_account_id is not None:
            update_data["inventory_account_id"] = inventory_account_id
        if sales_account_id is not None:
            update_data["sales_account_id"] = sales_account_id
        if purchase_description is not None:
            update_data["purchase_description"] = purchase_description
        if custom_fields is not None:
            update_data["custom_fields"] = custom_fields
        
        # We don't need full validation since we're updating an existing item
        # But we can still use the model for basic type checking
        try:
            validated_data = ItemInput.model_validate(update_data)
            data = validated_data.model_dump(exclude_none=True)
        except Exception as e:
            logger.error(f"Validation error updating item: {str(e)}")
            raise ValueError(f"Invalid update data: {str(e)}")
        
        # Make the API request
        response = await zoho_api_request_async("PUT", f"/items/{item_id}", json_data=data)
        
        # Parse the response
        item_response = ItemResponse.model_validate(response)
        
        logger.info(f"Item updated successfully: {item_id}")
        
        return {
            "item": item_response.item,
            "message": item_response.message or "Item updated successfully",
        }
        
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        raise


# Define metadata for tools that can be used by the MCP server
list_items.name = "list_items"  # type: ignore
list_items.description = "List items (products and services) in Zoho Books with pagination and filtering"  # type: ignore
list_items.parameters = {  # type: ignore
    "page": {
        "type": "integer",
        "description": "Page number for pagination",
        "default": 1,
    },
    "page_size": {
        "type": "integer",
        "description": "Number of items per page",
        "default": 25,
    },
    "item_type": {
        "type": "string",
        "enum": ["service", "goods", "inventory", "all"],
        "description": "Filter by item type (service, goods, inventory, or all)",
        "optional": True,
    },
    "search_text": {
        "type": "string",
        "description": "Search text to filter items by name or description",
        "optional": True,
    },
    "status": {
        "type": "string",
        "enum": ["active", "inactive"],
        "description": "Filter items by status (active or inactive)",
        "optional": True,
    },
    "sort_column": {
        "type": "string",
        "description": "Column to sort by",
        "default": "name",
        "optional": True,
    },
    "sort_order": {
        "type": "string",
        "description": "Sort order (ascending or descending)",
        "enum": ["ascending", "descending"],
        "default": "ascending",
        "optional": True,
    },
}

create_item.name = "create_item"  # type: ignore
create_item.description = "Create a new item in Zoho Books"  # type: ignore
create_item.parameters = {  # type: ignore
    "name": {
        "type": "string",
        "description": "Name of the item (required)",
    },
    "rate": {
        "type": "number",
        "description": "Price/rate of the item (required)",
    },
    "description": {
        "type": "string",
        "description": "Description of the item",
        "optional": True,
    },
    "item_type": {
        "type": "string",
        "enum": ["service", "goods", "inventory"],
        "description": "Type of item (service, goods, inventory)",
        "default": "service",
        "optional": True,
    },
    "sku": {
        "type": "string",
        "description": "Stock Keeping Unit (SKU)",
        "optional": True,
    },
    "unit": {
        "type": "string",
        "description": "Unit of measurement (e.g., pcs, hrs)",
        "optional": True,
    },
    "initial_stock": {
        "type": "number",
        "description": "Initial stock quantity (required for inventory items)",
        "optional": True,
    },
    "initial_stock_rate": {
        "type": "number",
        "description": "Initial stock rate/cost (required for inventory items)",
        "optional": True,
    },
    "purchase_account_id": {
        "type": "string",
        "description": "ID of the purchase account",
        "optional": True,
    },
    "inventory_account_id": {
        "type": "string",
        "description": "ID of the inventory account (required for inventory items)",
        "optional": True,
    },
    "sales_account_id": {
        "type": "string",
        "description": "ID of the sales account",
        "optional": True,
    },
    "purchase_description": {
        "type": "string",
        "description": "Description for purchases",
        "optional": True,
    },
    "tax_id": {
        "type": "string",
        "description": "ID of the tax",
        "optional": True,
    },
    "tax_name": {
        "type": "string",
        "description": "Name of the tax (only if tax_id not provided)",
        "optional": True,
    },
    "tax_percentage": {
        "type": "number",
        "description": "Tax percentage (required if tax_name is provided)",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}

get_item.name = "get_item"  # type: ignore
get_item.description = "Get an item by ID from Zoho Books"  # type: ignore
get_item.parameters = {  # type: ignore
    "item_id": {
        "type": "string",
        "description": "ID of the item to retrieve",
    },
}

update_item.name = "update_item"  # type: ignore
update_item.description = "Update an existing item in Zoho Books"  # type: ignore
update_item.parameters = {  # type: ignore
    "item_id": {
        "type": "string",
        "description": "ID of the item to update (required)",
    },
    "name": {
        "type": "string",
        "description": "Updated name of the item",
        "optional": True,
    },
    "rate": {
        "type": "number",
        "description": "Updated price/rate of the item",
        "optional": True,
    },
    "description": {
        "type": "string",
        "description": "Updated description of the item",
        "optional": True,
    },
    "sku": {
        "type": "string",
        "description": "Updated Stock Keeping Unit (SKU)",
        "optional": True,
    },
    "unit": {
        "type": "string",
        "description": "Updated unit of measurement (e.g., pcs, hrs)",
        "optional": True,
    },
    "tax_id": {
        "type": "string",
        "description": "Updated ID of the tax",
        "optional": True,
    },
    "tax_name": {
        "type": "string",
        "description": "Updated name of the tax (only if tax_id not provided)",
        "optional": True,
    },
    "tax_percentage": {
        "type": "number",
        "description": "Updated tax percentage (required if tax_name is provided)",
        "optional": True,
    },
    "purchase_account_id": {
        "type": "string",
        "description": "Updated ID of the purchase account",
        "optional": True,
    },
    "inventory_account_id": {
        "type": "string",
        "description": "Updated ID of the inventory account",
        "optional": True,
    },
    "sales_account_id": {
        "type": "string",
        "description": "Updated ID of the sales account",
        "optional": True,
    },
    "purchase_description": {
        "type": "string",
        "description": "Updated description for purchases",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Updated custom field values",
        "optional": True,
    },
}
