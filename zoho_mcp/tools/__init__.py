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
from .contacts import list_contacts, create_customer, create_vendor, get_contact, delete_contact

# Import invoice management tools
from .invoices import list_invoices, create_invoice, get_invoice, email_invoice, mark_invoice_as_sent, void_invoice

# These imports will be uncommented as each tool module is implemented
# from .expenses import list_expenses, create_expense
# from .items import list_items, create_item, get_item
# from .sales import create_sales_order, update_sales_order

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
    "list_contacts", "create_customer", "create_vendor", "get_contact", "delete_contact",
    
    # Invoice management tools
    "list_invoices", "create_invoice", "get_invoice", "email_invoice", "mark_invoice_as_sent", "void_invoice",
    
    # These will be uncommented as each tool is implemented
    # "list_expenses", "create_expense",
    # "list_items", "create_item", "get_item",
    # "create_sales_order", "update_sales_order",
]
