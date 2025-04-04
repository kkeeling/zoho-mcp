"""
Expense Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing expenses in Zoho Books.
"""

import logging
import datetime
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING, Literal

# Only used for type checking
if TYPE_CHECKING:
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from zoho_mcp.models.expenses import (
    ExpenseLineItem,
    ExpenseResponse,
    ExpensesListResponse,
)
from zoho_mcp.tools.api import zoho_api_request

logger = logging.getLogger(__name__)


def list_expenses(
    page: int = 1,
    page_size: int = 25,
    status: Optional[Literal["unbilled", "invoiced", "reimbursed", "all"]] = None,
    vendor_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    date_range_start: Optional[Union[str, datetime.date]] = None,
    date_range_end: Optional[Union[str, datetime.date]] = None,
    search_text: Optional[str] = None,
    sort_column: str = "created_time",
    sort_order: str = "descending",
) -> Dict[str, Any]:
    """
    List expenses in Zoho Books with pagination and filtering.
    
    Args:
        page: Page number for pagination
        page_size: Number of expenses per page
        status: Filter by expense status (unbilled, invoiced, reimbursed, all)
        vendor_id: Filter by vendor ID
        customer_id: Filter by customer ID
        date_range_start: Filter by start date (YYYY-MM-DD)
        date_range_end: Filter by end date (YYYY-MM-DD)
        search_text: Search text to filter expenses
        sort_column: Column to sort by
        sort_order: Sort order (ascending or descending)
        
    Returns:
        A paginated list of expenses matching the filters
    """
    logger.info(
        f"Listing expenses with page={page}, status={status or 'all'}, " 
        f"date_range={date_range_start or 'any'} to {date_range_end or 'any'}"
    )
    
    # Basic validation for parameters
    if page < 1:
        logger.error("Invalid page number: must be >= 1")
        raise ValueError("Invalid page number: must be >= 1")
    
    if page_size < 1:
        logger.error("Invalid page size: must be >= 1")
        raise ValueError("Invalid page size: must be >= 1")
    
    params = {
        "page": page,
        "per_page": page_size,
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
    
    # Add optional filters if provided
    if status and status != "all":
        params["status"] = status
    if vendor_id:
        params["vendor_id"] = vendor_id
    if customer_id:
        params["customer_id"] = customer_id
    if search_text:
        params["search_text"] = search_text
    
    # Add date range filters
    if date_range_start:
        if isinstance(date_range_start, datetime.date):
            params["date.from"] = date_range_start.isoformat()
        else:
            params["date.from"] = date_range_start
            
    if date_range_end:
        if isinstance(date_range_end, datetime.date):
            params["date.to"] = date_range_end.isoformat()
        else:
            params["date.to"] = date_range_end
    
    try:
        response = zoho_api_request("GET", "/expenses", params=params)
        
        # Parse the response
        expenses_response = ExpensesListResponse.model_validate(response)
        
        # Construct paginated response
        result = {
            "page": page,
            "page_size": page_size,
            "has_more_page": response.get("page_context", {}).get("has_more_page", False),
            "expenses": expenses_response.expenses or [],
            "message": expenses_response.message or "Expenses retrieved successfully",
        }
        
        # Add total count if available
        if "page_context" in response and "total" in response["page_context"]:
            result["total"] = response["page_context"]["total"]
            
        logger.info(f"Retrieved {len(result['expenses'])} expenses")
        return result
        
    except Exception as e:
        logger.error(f"Error listing expenses: {str(e)}")
        raise


def create_expense(
    account_id: str,
    date: Union[str, datetime.date],
    amount: float,
    paid_through_account_id: str,
    vendor_id: Optional[str] = None,
    is_billable: bool = False,
    customer_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    exchange_rate: Optional[float] = None,
    tax_id: Optional[str] = None,
    reference_number: Optional[str] = None,
    description: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
    **custom_fields: Any,
) -> Dict[str, Any]:
    """
    Create a new expense in Zoho Books.
    
    Args:
        account_id: ID of the expense account
        date: Date of the expense (YYYY-MM-DD)
        amount: Amount of the expense
        paid_through_account_id: ID of the account used to pay the expense
        vendor_id: ID of the vendor (optional)
        is_billable: Whether the expense is billable to a customer
        customer_id: ID of the customer if is_billable is true
        currency_id: ID of the currency
        exchange_rate: Exchange rate for the currency
        tax_id: ID of the tax to apply
        reference_number: Reference number for the expense
        description: Description of the expense
        line_items: Line items for an itemized expense
        **custom_fields: Custom field values
        
    Returns:
        The created expense details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating expense with date: {date}, amount: {amount}")
    
    # Prepare the request data
    data: Dict[str, Any] = {
        "account_id": account_id,
        "paid_through_account_id": paid_through_account_id,
        "amount": amount,
        "is_billable": is_billable,
    }
    
    # Format the date
    if isinstance(date, datetime.date):
        data["date"] = date.isoformat()
    else:
        data["date"] = date
    
    # Add optional fields if provided
    if vendor_id:
        data["vendor_id"] = vendor_id
    if customer_id and is_billable:
        data["customer_id"] = customer_id
    if currency_id:
        data["currency_id"] = currency_id
    if exchange_rate:
        data["exchange_rate"] = exchange_rate
    if tax_id:
        data["tax_id"] = tax_id
    if reference_number:
        data["reference_number"] = reference_number
    if description:
        data["description"] = description
    
    # Add line items if provided
    if line_items:
        # Validate line items
        validated_items = []
        for item in line_items:
            try:
                validated_item = ExpenseLineItem.model_validate(item)
                validated_items.append(validated_item.model_dump(exclude_none=True))
            except Exception as e:
                logger.error(f"Validation error in expense line item: {str(e)}")
                raise ValueError(f"Invalid expense line item: {str(e)}")
        
        if validated_items:
            data["line_items"] = validated_items
    
    # Add custom fields if any
    if custom_fields:
        data["custom_fields"] = [
            {"label": k, "value": v} for k, v in custom_fields.items()
        ]
    
    try:
        response = zoho_api_request("POST", "/expenses", json=data)
        
        # Parse the response
        expense_response = ExpenseResponse.model_validate(response)
        
        logger.info(f"Expense created successfully: {expense_response.expense.get('expense_id') if expense_response.expense else 'Unknown ID'}")
        
        return {
            "expense": expense_response.expense,
            "message": expense_response.message or "Expense created successfully",
        }
        
    except Exception as e:
        logger.error(f"Error creating expense: {str(e)}")
        raise


def get_expense(expense_id: str) -> Dict[str, Any]:
    """
    Get an expense by ID from Zoho Books.
    
    Args:
        expense_id: ID of the expense to retrieve
        
    Returns:
        The expense details
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Getting expense with ID: {expense_id}")
    
    # Basic validation - make sure we have a non-empty string
    if not expense_id or not isinstance(expense_id, str):
        logger.error("Invalid expense ID: ID must be a non-empty string")
        raise ValueError("Invalid expense ID: ID must be a non-empty string")
    
    try:
        response = zoho_api_request("GET", f"/expenses/{expense_id}")
        
        # Parse the response
        expense_response = ExpenseResponse.model_validate(response)
        
        if not expense_response.expense:
            logger.warning(f"Expense not found: {expense_id}")
            return {
                "message": "Expense not found",
                "expense": None,
            }
        
        logger.info(f"Expense retrieved successfully: {expense_id}")
        
        return {
            "expense": expense_response.expense,
            "message": expense_response.message or "Expense retrieved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error getting expense: {str(e)}")
        raise


def update_expense(
    expense_id: str,
    account_id: Optional[str] = None,
    date: Optional[Union[str, datetime.date]] = None,
    amount: Optional[float] = None,
    paid_through_account_id: Optional[str] = None,
    vendor_id: Optional[str] = None,
    is_billable: Optional[bool] = None,
    customer_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    exchange_rate: Optional[float] = None,
    tax_id: Optional[str] = None,
    reference_number: Optional[str] = None,
    description: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
    **custom_fields: Any,
) -> Dict[str, Any]:
    """
    Update an existing expense in Zoho Books.
    
    Args:
        expense_id: ID of the expense to update
        account_id: ID of the expense account
        date: Date of the expense (YYYY-MM-DD)
        amount: Amount of the expense
        paid_through_account_id: ID of the account used to pay the expense
        vendor_id: ID of the vendor
        is_billable: Whether the expense is billable to a customer
        customer_id: ID of the customer if is_billable is true
        currency_id: ID of the currency
        exchange_rate: Exchange rate for the currency
        tax_id: ID of the tax to apply
        reference_number: Reference number for the expense
        description: Description of the expense
        line_items: Line items for an itemized expense
        **custom_fields: Custom field values
        
    Returns:
        The updated expense details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Updating expense with ID: {expense_id}")
    
    # First, get the current expense data
    current_expense = get_expense(expense_id)
    if not current_expense.get("expense"):
        raise ValueError(f"Expense with ID {expense_id} not found")
    
    # Prepare the update data, starting with the current expense
    data: Dict[str, Any] = {}
    
    # Add required fields from the current expense or new values
    data["expense_id"] = expense_id
    data["account_id"] = account_id or current_expense["expense"]["account_id"]
    data["paid_through_account_id"] = paid_through_account_id or current_expense["expense"].get("paid_through_account_id")
    
    # Required fields with potential updates
    if amount is not None:
        data["amount"] = amount
    else:
        data["amount"] = current_expense["expense"]["amount"]
    
    # Format the date if provided
    if date:
        if isinstance(date, datetime.date):
            data["date"] = date.isoformat()
        else:
            data["date"] = date
    else:
        data["date"] = current_expense["expense"]["date"]
    
    # Add optional fields if provided or use current values
    if is_billable is not None:
        data["is_billable"] = is_billable
    elif "is_billable" in current_expense["expense"]:
        data["is_billable"] = current_expense["expense"]["is_billable"]
        
    if vendor_id:
        data["vendor_id"] = vendor_id
    elif "vendor_id" in current_expense["expense"]:
        data["vendor_id"] = current_expense["expense"]["vendor_id"]
        
    if customer_id:
        data["customer_id"] = customer_id
    elif "customer_id" in current_expense["expense"]:
        data["customer_id"] = current_expense["expense"]["customer_id"]
        
    if currency_id:
        data["currency_id"] = currency_id
    elif "currency_id" in current_expense["expense"]:
        data["currency_id"] = current_expense["expense"]["currency_id"]
        
    if exchange_rate is not None:
        data["exchange_rate"] = exchange_rate
    elif "exchange_rate" in current_expense["expense"]:
        data["exchange_rate"] = current_expense["expense"]["exchange_rate"]
        
    if tax_id:
        data["tax_id"] = tax_id
    elif "tax_id" in current_expense["expense"]:
        data["tax_id"] = current_expense["expense"]["tax_id"]
        
    if reference_number:
        data["reference_number"] = reference_number
    elif "reference_number" in current_expense["expense"]:
        data["reference_number"] = current_expense["expense"]["reference_number"]
        
    if description:
        data["description"] = description
    elif "description" in current_expense["expense"]:
        data["description"] = current_expense["expense"]["description"]
    
    # Add line items if provided
    if line_items:
        # Validate line items
        validated_items = []
        for item in line_items:
            try:
                validated_item = ExpenseLineItem.model_validate(item)
                validated_items.append(validated_item.model_dump(exclude_none=True))
            except Exception as e:
                logger.error(f"Validation error in expense line item: {str(e)}")
                raise ValueError(f"Invalid expense line item: {str(e)}")
        
        if validated_items:
            data["line_items"] = validated_items
    elif "line_items" in current_expense["expense"]:
        data["line_items"] = current_expense["expense"]["line_items"]
    
    # Add custom fields if any
    if custom_fields:
        data["custom_fields"] = [
            {"label": k, "value": v} for k, v in custom_fields.items()
        ]
    
    try:
        response = zoho_api_request("PUT", f"/expenses/{expense_id}", json=data)
        
        # Parse the response
        expense_response = ExpenseResponse.model_validate(response)
        
        logger.info(f"Expense updated successfully: {expense_id}")
        
        return {
            "expense": expense_response.expense,
            "message": expense_response.message or "Expense updated successfully",
        }
        
    except Exception as e:
        logger.error(f"Error updating expense: {str(e)}")
        raise


# Define metadata for tools that can be used by the MCP server
list_expenses.name = "list_expenses"  # type: ignore
list_expenses.description = "List expenses in Zoho Books with pagination and filtering"  # type: ignore
list_expenses.parameters = {  # type: ignore
    "page": {
        "type": "integer",
        "description": "Page number for pagination",
        "default": 1,
    },
    "page_size": {
        "type": "integer",
        "description": "Number of expenses per page",
        "default": 25,
    },
    "status": {
        "type": "string",
        "description": "Filter by expense status",
        "enum": ["unbilled", "invoiced", "reimbursed", "all"],
        "optional": True,
    },
    "vendor_id": {
        "type": "string",
        "description": "Filter by vendor ID",
        "optional": True,
    },
    "customer_id": {
        "type": "string",
        "description": "Filter by customer ID",
        "optional": True,
    },
    "date_range_start": {
        "type": "string",
        "description": "Filter by start date (YYYY-MM-DD)",
        "optional": True,
    },
    "date_range_end": {
        "type": "string",
        "description": "Filter by end date (YYYY-MM-DD)",
        "optional": True,
    },
    "search_text": {
        "type": "string",
        "description": "Search text to filter expenses",
        "optional": True,
    },
    "sort_column": {
        "type": "string",
        "description": "Column to sort by",
        "default": "created_time",
        "optional": True,
    },
    "sort_order": {
        "type": "string",
        "description": "Sort order (ascending or descending)",
        "enum": ["ascending", "descending"],
        "default": "descending",
        "optional": True,
    },
}

create_expense.name = "create_expense"  # type: ignore
create_expense.description = "Create a new expense in Zoho Books"  # type: ignore
create_expense.parameters = {  # type: ignore
    "account_id": {
        "type": "string",
        "description": "ID of the expense account (required)",
    },
    "date": {
        "type": "string",
        "description": "Date of the expense (YYYY-MM-DD) (required)",
    },
    "amount": {
        "type": "number",
        "description": "Amount of the expense (required)",
    },
    "paid_through_account_id": {
        "type": "string",
        "description": "ID of the account used to pay the expense (required)",
    },
    "vendor_id": {
        "type": "string",
        "description": "ID of the vendor",
        "optional": True,
    },
    "is_billable": {
        "type": "boolean",
        "description": "Whether the expense is billable to a customer",
        "default": False,
        "optional": True,
    },
    "customer_id": {
        "type": "string",
        "description": "ID of the customer if is_billable is true",
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency",
        "optional": True,
    },
    "exchange_rate": {
        "type": "number",
        "description": "Exchange rate for the currency",
        "optional": True,
    },
    "tax_id": {
        "type": "string",
        "description": "ID of the tax to apply",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Reference number for the expense",
        "optional": True,
    },
    "description": {
        "type": "string",
        "description": "Description of the expense",
        "optional": True,
    },
    "line_items": {
        "type": "array",
        "description": "Line items for an itemized expense",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}

get_expense.name = "get_expense"  # type: ignore
get_expense.description = "Get an expense by ID from Zoho Books"  # type: ignore
get_expense.parameters = {  # type: ignore
    "expense_id": {
        "type": "string",
        "description": "ID of the expense to retrieve",
    },
}

update_expense.name = "update_expense"  # type: ignore
update_expense.description = "Update an existing expense in Zoho Books"  # type: ignore
update_expense.parameters = {  # type: ignore
    "expense_id": {
        "type": "string",
        "description": "ID of the expense to update",
    },
    "account_id": {
        "type": "string",
        "description": "ID of the expense account",
        "optional": True,
    },
    "date": {
        "type": "string",
        "description": "Date of the expense (YYYY-MM-DD)",
        "optional": True,
    },
    "amount": {
        "type": "number",
        "description": "Amount of the expense",
        "optional": True,
    },
    "paid_through_account_id": {
        "type": "string",
        "description": "ID of the account used to pay the expense",
        "optional": True,
    },
    "vendor_id": {
        "type": "string",
        "description": "ID of the vendor",
        "optional": True,
    },
    "is_billable": {
        "type": "boolean",
        "description": "Whether the expense is billable to a customer",
        "optional": True,
    },
    "customer_id": {
        "type": "string",
        "description": "ID of the customer if is_billable is true",
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency",
        "optional": True,
    },
    "exchange_rate": {
        "type": "number",
        "description": "Exchange rate for the currency",
        "optional": True,
    },
    "tax_id": {
        "type": "string",
        "description": "ID of the tax to apply",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Reference number for the expense",
        "optional": True,
    },
    "description": {
        "type": "string",
        "description": "Description of the expense",
        "optional": True,
    },
    "line_items": {
        "type": "array",
        "description": "Line items for an itemized expense",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}