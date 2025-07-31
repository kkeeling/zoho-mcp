"""
Invoice-related models for Zoho Books MCP Integration Server.

This module contains Pydantic models for invoice operations.
"""

from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

from .base import BaseResponse


class InvoiceLineItem(BaseModel):
    """Model for an invoice line item."""
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

    @model_validator(mode='after')
    def validate_item(self) -> 'InvoiceLineItem':
        """Ensure either item_id or name is provided."""
        if not self.item_id and not self.name:
            raise ValueError("Either item_id or name must be provided")
        return self

    @model_validator(mode='after')
    def validate_tax(self) -> 'InvoiceLineItem':
        """Ensure tax information is consistent."""
        if self.tax_id and (self.tax_name or self.tax_percentage is not None):
            raise ValueError("Cannot specify both tax_id and tax_name/tax_percentage")
        if self.tax_name and self.tax_percentage is None:
            raise ValueError("tax_percentage is required when tax_name is provided")
        return self


class CreateInvoiceInput(BaseModel):
    """Model for creating an invoice."""
    customer_id: str = Field(..., description="ID of the customer")
    invoice_number: Optional[str] = Field(None, description="Custom invoice number (system-generated if omitted)")
    reference_number: Optional[str] = Field(None, description="Reference number")
    invoice_date: Optional[Union[str, date]] = Field(
        None, description="Invoice date (YYYY-MM-DD, default: current date)"
    )
    due_date: Optional[Union[str, date]] = Field(
        None, description="Due date (YYYY-MM-DD)"
    )
    line_items: List[InvoiceLineItem] = Field(
        ..., min_length=1, description="Line items for the invoice"
    )
    notes: Optional[str] = Field(None, description="Notes to be displayed on the invoice")
    terms: Optional[str] = Field(None, description="Terms and conditions")

    # Optional flags and settings
    payment_terms: Optional[int] = Field(None, description="Payment terms in days")
    payment_terms_label: Optional[str] = Field(None, description="Label for payment terms")
    is_inclusive_tax: Optional[bool] = Field(None, description="Whether tax is inclusive in item rate")
    salesperson_name: Optional[str] = Field(None, description="Name of the salesperson")
    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom field values"
    )


class GetInvoiceInput(BaseModel):
    """Model for retrieving an invoice."""
    invoice_id: str = Field(..., description="ID of the invoice to retrieve")


class ListInvoicesInput(BaseModel):
    """Model for listing invoices."""
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination")
    status: Optional[Literal["draft", "sent", "overdue", "paid", "void", "all"]] = Field(
        None, description="Filter by invoice status"
    )
    customer_id: Optional[str] = Field(None, description="Filter by customer ID")
    date_range_start: Optional[Union[str, date]] = Field(
        None, description="Filter by start date (YYYY-MM-DD)"
    )
    date_range_end: Optional[Union[str, date]] = Field(
        None, description="Filter by end date (YYYY-MM-DD)"
    )
    search_text: Optional[str] = Field(None, description="Search text")


class InvoiceResponse(BaseResponse):
    """Model for invoice API responses."""
    invoice: Optional[Dict] = Field(None, description="Invoice details")


class InvoicesListResponse(BaseResponse):
    """Model for list invoices API response."""
    invoices: Optional[List[Dict]] = Field(None, description="List of invoices")
