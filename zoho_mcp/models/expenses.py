"""
Expense-related models for Zoho Books MCP Integration Server.
"""

from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

from .base import BaseResponse


class ExpenseLineItem(BaseModel):
    """Model for an expense line item."""
    account_id: str = Field(..., description="ID of the expense account")
    amount: float = Field(..., gt=0, description="Amount of the expense item")
    tax_id: Optional[str] = Field(None, description="ID of the tax to apply")
    tax_name: Optional[str] = Field(None, description="Name of the tax (if tax_id not provided)")
    tax_percentage: Optional[float] = Field(None, ge=0, description="Tax percentage")
    description: Optional[str] = Field(None, description="Description of the expense item")

    @model_validator(mode='after')
    def validate_tax(self) -> 'ExpenseLineItem':
        """Ensure tax information is consistent."""
        if self.tax_id and (self.tax_name or self.tax_percentage is not None):
            raise ValueError("Cannot specify both tax_id and tax_name/tax_percentage")
        if self.tax_name and self.tax_percentage is None:
            raise ValueError("tax_percentage is required when tax_name is provided")
        return self


class GetExpenseInput(BaseModel):
    """Model for retrieving an expense."""
    expense_id: str = Field(..., description="ID of the expense to retrieve")


class ListExpensesInput(BaseModel):
    """Model for listing expenses."""
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination")
    status: Optional[Literal["unbilled", "invoiced", "reimbursed", "all"]] = Field(
        None, description="Filter by expense status"
    )
    vendor_id: Optional[str] = Field(None, description="Filter by vendor ID")
    customer_id: Optional[str] = Field(None, description="Filter by customer ID")
    date_range_start: Optional[Union[str, date]] = Field(
        None, description="Filter by start date (YYYY-MM-DD)"
    )
    date_range_end: Optional[Union[str, date]] = Field(
        None, description="Filter by end date (YYYY-MM-DD)"
    )
    search_text: Optional[str] = Field(None, description="Search text")


class ExpenseResponse(BaseResponse):
    """Model for expense API responses."""
    expense: Optional[Dict[str, Any]] = Field(None, description="Expense details")


class ExpensesListResponse(BaseResponse):
    """Model for list expenses API response."""
    expenses: Optional[List[Dict[str, Any]]] = Field(None, description="List of expenses")
