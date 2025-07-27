"""
Item-related models for Zoho Books MCP Integration Server.

This module contains Pydantic models for item operations (products and services).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

from .base import BaseResponse


class ItemInput(BaseModel):
    """Model for creating or updating an item."""
    name: str = Field(..., description="Name of the item")
    description: Optional[str] = Field(None, description="Description of the item")
    rate: float = Field(..., description="Price/rate of the item")

    # Item type and attributes
    item_type: Literal["service", "goods", "inventory"] = Field(
        "service", description="Type of item (service, goods, inventory)"
    )
    sku: Optional[str] = Field(None, description="Stock Keeping Unit (SKU)")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., pcs, hrs)")

    # Inventory specific
    initial_stock: Optional[float] = Field(None, ge=0, description="Initial stock quantity")
    initial_stock_rate: Optional[float] = Field(None, gt=0, description="Initial stock rate/cost")

    # Account mapping
    purchase_account_id: Optional[str] = Field(None, description="ID of the purchase account")
    inventory_account_id: Optional[str] = Field(None, description="ID of the inventory account")
    sales_account_id: Optional[str] = Field(None, description="ID of the sales account")
    purchase_description: Optional[str] = Field(None, description="Description for purchases")

    # Tax information
    tax_id: Optional[str] = Field(None, description="ID of the tax")
    tax_name: Optional[str] = Field(None, description="Name of the tax (if tax_id not provided)")
    tax_percentage: Optional[float] = Field(None, ge=0, description="Tax percentage")

    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom field values"
    )

    @model_validator(mode='after')
    def validate_item(self) -> 'ItemInput':
        """Validate the item data."""
        # Validate inventory items
        if self.item_type == "inventory":
            if self.initial_stock is None:
                raise ValueError("initial_stock is required for inventory items")
            if self.initial_stock_rate is None:
                raise ValueError("initial_stock_rate is required for inventory items")
            if self.inventory_account_id is None:
                raise ValueError("inventory_account_id is required for inventory items")

        # Validate tax information
        if self.tax_id and (self.tax_name or self.tax_percentage is not None):
            raise ValueError("Cannot specify both tax_id and tax_name/tax_percentage")
        if self.tax_name and self.tax_percentage is None:
            raise ValueError("tax_percentage is required when tax_name is provided")

        return self


class GetItemInput(BaseModel):
    """Model for retrieving an item."""
    item_id: str = Field(..., description="ID of the item to retrieve")


class ListItemsInput(BaseModel):
    """Model for listing items."""
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination")
    item_type: Optional[Literal["service", "goods", "inventory", "all"]] = Field(
        None, description="Filter by item type"
    )
    search_text: Optional[str] = Field(None, description="Search text")
    status: Optional[Literal["active", "inactive"]] = Field(
        None, description="Filter by item status"
    )


class ItemResponse(BaseResponse):
    """Model for item API responses."""
    item: Optional[Dict] = Field(None, description="Item details")


class ItemsListResponse(BaseResponse):
    """Model for list items API response."""
    items: Optional[List[Dict]] = Field(None, description="List of items")
