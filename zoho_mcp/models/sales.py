"""
Sales order-related models for Zoho Books MCP Integration Server.

This module contains Pydantic models for sales order operations.
"""

from datetime import date as DateType
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

from .base import BaseResponse


class SalesOrderLineItem(BaseModel):
    """Model for a sales order line item."""
    item_id: Optional[str] = Field(None, description="ID of the existing item (from Zoho Books)")
    name: Optional[str] = Field(None, description="Name of the item (if item_id not provided)")
    description: Optional[str] = Field(None, description="Description of the line item")
    rate: float = Field(..., gt=0, description="Unit price of the item")
    quantity: float = Field(..., gt=0, description="Quantity of the item")
    discount: Optional[float] = Field(None, ge=0, description="Discount percentage or amount")
    discount_type: Optional[Literal["percentage", "amount"]] = Field(
        "percentage", description="Type of discount ('percentage' or 'amount')"
    )
    tax_id: Optional[str] = Field(None, description="ID of the tax to apply")
    tax_name: Optional[str] = Field(None, description="Name of the tax (if tax_id not provided)")
    tax_percentage: Optional[float] = Field(None, ge=0, description="Tax percentage")
    line_item_id: Optional[str] = Field(None, description="ID of the line item (for updating)")
    location_id: Optional[str] = Field(None, description="Location ID for inventory management")

    @model_validator(mode='after')
    def validate_item(self) -> 'SalesOrderLineItem':
        """Ensure either item_id or name is provided."""
        if not self.item_id and not self.name:
            raise ValueError("Either item_id or name must be provided")
        return self

    @model_validator(mode='after')
    def validate_tax(self) -> 'SalesOrderLineItem':
        """Ensure tax information is consistent."""
        if self.tax_id and (self.tax_name or self.tax_percentage is not None):
            raise ValueError("Cannot specify both tax_id and tax_name/tax_percentage")
        if self.tax_name and self.tax_percentage is None:
            raise ValueError("tax_percentage is required when tax_name is provided")
        return self


class Address(BaseModel):
    """Model for billing or shipping address."""
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State or province")
    zip: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Country")
    phone: Optional[str] = Field(None, description="Phone number")
    fax: Optional[str] = Field(None, description="Fax number")
    attention: Optional[str] = Field(None, description="Attention to")


class CreateSalesOrderInput(BaseModel):
    """Model for creating a sales order."""
    customer_id: str = Field(..., description="ID of the customer")
    salesorder_number: Optional[str] = Field(None, description="Custom sales order number (system-generated if omitted)")
    reference_number: Optional[str] = Field(None, description="Reference number")
    date: Optional[Union[str, DateType]] = Field(
        None, description="Sales order date (YYYY-MM-DD, default: current date)"
    )
    shipment_date: Optional[Union[str, DateType]] = Field(
        None, description="Expected shipment date (YYYY-MM-DD)"
    )
    line_items: List[SalesOrderLineItem] = Field(
        ..., min_length=1, description="Line items for the sales order"
    )
    notes: Optional[str] = Field(None, description="Notes to be displayed on the sales order")
    terms: Optional[str] = Field(None, description="Terms and conditions")

    # Optional fields
    contact_persons: Optional[List[str]] = Field(None, description="IDs of contact persons")
    currency_id: Optional[str] = Field(None, description="ID of the currency")
    is_inclusive_tax: Optional[bool] = Field(None, description="Whether tax is inclusive in item rate")
    discount: Optional[str] = Field(None, description="Discount applied to the sales order")
    is_discount_before_tax: Optional[bool] = Field(None, description="Whether discount is applied before tax")
    discount_type: Optional[Literal["entity_level", "item_level"]] = Field(
        None, description="How the discount is specified"
    )
    shipping_charge: Optional[float] = Field(None, ge=0, description="Shipping charge")
    adjustment: Optional[float] = Field(None, description="Adjustment amount")
    adjustment_description: Optional[str] = Field(None, description="Description for the adjustment")

    # Address fields
    billing_address: Optional[Address] = Field(None, description="Billing address")
    shipping_address: Optional[Address] = Field(None, description="Shipping address")

    # Other fields
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom field values")
    salesperson_id: Optional[str] = Field(None, description="ID of the salesperson")
    salesperson_name: Optional[str] = Field(None, description="Name of the salesperson")
    template_id: Optional[str] = Field(None, description="ID of the PDF template")
    location_id: Optional[str] = Field(None, description="Location ID for inventory")


class UpdateSalesOrderInput(BaseModel):
    """Model for updating an existing sales order."""
    customer_id: Optional[str] = Field(None, description="ID of the customer")
    salesorder_number: Optional[str] = Field(None, description="Custom sales order number")
    reference_number: Optional[str] = Field(None, description="Reference number")
    date: Optional[Union[str, DateType]] = Field(None, description="Sales order date (YYYY-MM-DD)")
    shipment_date: Optional[Union[str, DateType]] = Field(None, description="Expected shipment date (YYYY-MM-DD)")
    line_items: Optional[List[SalesOrderLineItem]] = Field(
        None, description="Line items for the sales order"
    )
    notes: Optional[str] = Field(None, description="Notes to be displayed on the sales order")
    terms: Optional[str] = Field(None, description="Terms and conditions")

    # Optional fields
    contact_persons: Optional[List[str]] = Field(None, description="IDs of contact persons")
    currency_id: Optional[str] = Field(None, description="ID of the currency")
    is_inclusive_tax: Optional[bool] = Field(None, description="Whether tax is inclusive in item rate")
    discount: Optional[str] = Field(None, description="Discount applied to the sales order")
    is_discount_before_tax: Optional[bool] = Field(None, description="Whether discount is applied before tax")
    discount_type: Optional[Literal["entity_level", "item_level"]] = Field(
        None, description="How the discount is specified"
    )
    shipping_charge: Optional[float] = Field(None, ge=0, description="Shipping charge")
    adjustment: Optional[float] = Field(None, description="Adjustment amount")
    adjustment_description: Optional[str] = Field(None, description="Description for the adjustment")

    # Address fields
    billing_address: Optional[Address] = Field(None, description="Billing address")
    shipping_address: Optional[Address] = Field(None, description="Shipping address")

    # Other fields
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom field values")
    salesperson_id: Optional[str] = Field(None, description="ID of the salesperson")
    salesperson_name: Optional[str] = Field(None, description="Name of the salesperson")
    template_id: Optional[str] = Field(None, description="ID of the PDF template")
    location_id: Optional[str] = Field(None, description="Location ID for inventory")

    @model_validator(mode='after')
    def validate_update(self) -> 'UpdateSalesOrderInput':
        """Ensure at least one field is being updated."""
        update_fields = {
            k: v for k, v in self.model_dump().items()
            if v is not None and k != 'salesorder_id'
        }
        if not update_fields:
            raise ValueError("At least one field must be provided for update")
        return self


class GetSalesOrderInput(BaseModel):
    """Model for retrieving a sales order."""
    salesorder_id: str = Field(..., description="ID of the sales order to retrieve")


class ListSalesOrdersInput(BaseModel):
    """Model for listing sales orders."""
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination")
    page_size: Optional[int] = Field(25, ge=1, le=200, description="Number of sales orders per page")
    status: Optional[Literal["draft", "open", "void", "all"]] = Field(
        None, description="Filter by sales order status"
    )
    customer_id: Optional[str] = Field(None, description="Filter by customer ID")
    date_range_start: Optional[Union[str, DateType]] = Field(
        None, description="Filter by start date (YYYY-MM-DD)"
    )
    date_range_end: Optional[Union[str, DateType]] = Field(
        None, description="Filter by end date (YYYY-MM-DD)"
    )
    search_text: Optional[str] = Field(None, description="Search text")
    sort_column: Optional[str] = Field("date", description="Column to sort by")
    sort_order: Optional[Literal["ascending", "descending"]] = Field(
        "descending", description="Sort order"
    )


class ConvertToInvoiceInput(BaseModel):
    """Model for converting a sales order to invoice."""
    salesorder_id: str = Field(..., description="ID of the sales order to convert")
    ignore_auto_number_generation: Optional[bool] = Field(
        None, description="Ignore auto invoice number generation"
    )
    invoice_number: Optional[str] = Field(
        None, description="Custom invoice number (required if ignore_auto_number_generation is True)"
    )
    date: Optional[Union[str, DateType]] = Field(
        None, description="Invoice date (YYYY-MM-DD, default: current date)"
    )
    payment_terms: Optional[int] = Field(None, description="Payment terms in days")
    payment_terms_label: Optional[str] = Field(None, description="Label for payment terms")

    @model_validator(mode='after')
    def validate_invoice_number(self) -> 'ConvertToInvoiceInput':
        """Ensure invoice_number is provided if ignore_auto_number_generation is True."""
        if self.ignore_auto_number_generation and not self.invoice_number:
            raise ValueError("invoice_number is required when ignore_auto_number_generation is True")
        return self


class SalesOrderResponse(BaseResponse):
    """Model for sales order API responses."""
    salesorder: Optional[Dict] = Field(None, description="Sales order details")


class SalesOrdersListResponse(BaseResponse):
    """Model for list sales orders API response."""
    salesorders: Optional[List[Dict]] = Field(None, description="List of sales orders")
    page_context: Optional[Dict] = Field(None, description="Pagination context")


class InvoiceResponse(BaseResponse):
    """Model for invoice API responses when converting from sales order."""
    invoice: Optional[Dict] = Field(None, description="Invoice details")
