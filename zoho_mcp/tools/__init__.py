"""
Zoho Books MCP Integration Server Tools

This module contains all the MCP tools for interacting with Zoho Books.
"""

from .api import (
    zoho_api_request,
    zoho_api_request_async,
    validate_credentials,
    ZohoAPIError,
    ZohoAuthenticationError,
    ZohoRequestError,
    ZohoRateLimitError,
)

# Import contact management tools
from .contacts import list_contacts, create_customer, create_vendor, get_contact, delete_contact, update_contact, email_statement

# Import invoice management tools
from .invoices import list_invoices, create_invoice, get_invoice, email_invoice, mark_invoice_as_sent, void_invoice, record_payment, send_payment_reminder

# Import expense management tools
from .expenses import list_expenses, create_expense, get_expense, update_expense, categorize_expense, upload_receipt

# Import item management tools
from .items import list_items, create_item, get_item, update_item

# Import sales order management tools
from .sales import list_sales_orders, create_sales_order, get_sales_order, update_sales_order, convert_to_invoice

__all__ = [
    # API utilities
    "zoho_api_request",
    "zoho_api_request_async",
    "validate_credentials",
    "ZohoAPIError",
    "ZohoAuthenticationError",
    "ZohoRequestError",
    "ZohoRateLimitError",
    
    # Contact management tools
    "list_contacts", "create_customer", "create_vendor", "get_contact", "delete_contact", "update_contact", "email_statement",
    
    # Invoice management tools
    "list_invoices", "create_invoice", "get_invoice", "email_invoice", "mark_invoice_as_sent", "void_invoice", "record_payment", "send_payment_reminder",
    
    # Expense management tools
    "list_expenses", "create_expense", "get_expense", "update_expense", "categorize_expense", "upload_receipt",
    
    # Item management tools
    "list_items", "create_item", "get_item", "update_item",
    
    # Sales order management tools
    "list_sales_orders", "create_sales_order", "get_sales_order", "update_sales_order", "convert_to_invoice",
]
