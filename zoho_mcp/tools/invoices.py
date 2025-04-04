"""
Invoice Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing invoices in Zoho Books.
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from datetime import date

# Only used for type checking
if TYPE_CHECKING:
    from typing import TypedDict
    
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from zoho_mcp.models.invoices import (
    CreateInvoiceInput,
    GetInvoiceInput,
    InvoiceResponse,
    InvoicesListResponse,
)
from zoho_mcp.tools.api import zoho_api_request

logger = logging.getLogger(__name__)


def list_invoices(
    page: int = 1,
    page_size: int = 25,
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    date_range_start: Optional[Union[str, date]] = None,
    date_range_end: Optional[Union[str, date]] = None,
    search_text: Optional[str] = None,
    sort_column: str = "created_time",
    sort_order: str = "descending",
) -> Dict[str, Any]:
    """
    List invoices in Zoho Books with pagination and filtering.
    
    Args:
        page: Page number for pagination
        page_size: Number of invoices per page
        status: Filter by invoice status (draft, sent, overdue, paid, void, all)
        customer_id: Filter by customer ID
        date_range_start: Filter by start date (YYYY-MM-DD)
        date_range_end: Filter by end date (YYYY-MM-DD)
        search_text: Search text to filter invoices
        sort_column: Column to sort by (created_time, date, invoice_number, total, balance)
        sort_order: Sort order (ascending or descending)
        
    Returns:
        A paginated list of invoices matching the filters
    """
    logger.info(
        f"Listing invoices with page={page}, status={status or 'all'}, " 
        f"date_range={date_range_start or 'any'} to {date_range_end or 'any'}"
    )
    
    params = {
        "page": page,
        "per_page": page_size,
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
    
    # Add optional filters if provided
    if status and status != "all":
        params["status"] = status
    if customer_id:
        params["customer_id"] = customer_id
    if date_range_start:
        params["date_start"] = str(date_range_start) if isinstance(date_range_start, date) else date_range_start
    if date_range_end:
        params["date_end"] = str(date_range_end) if isinstance(date_range_end, date) else date_range_end
    if search_text:
        params["search_text"] = search_text
    
    try:
        response = zoho_api_request("GET", "/invoices", params=params)
        
        # Parse the response
        invoices_response = InvoicesListResponse.model_validate(response)
        
        # Construct paginated response
        result = {
            "page": page,
            "page_size": page_size,
            "has_more_page": response.get("page_context", {}).get("has_more_page", False),
            "invoices": invoices_response.invoices or [],
            "message": invoices_response.message,
        }
        
        # Add total count if available
        if "page_context" in response and "total" in response["page_context"]:
            result["total"] = response["page_context"]["total"]
            
        logger.info(f"Retrieved {len(result['invoices'])} invoices")
        return result
        
    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        raise


def create_invoice(**kwargs) -> Dict[str, Any]:
    """
    Create a new invoice in Zoho Books.
    
    Args:
        **kwargs: Invoice details including:
          - customer_id (required): ID of the customer
          - invoice_number: Custom invoice number
          - reference_number: Reference number
          - invoice_date: Invoice date (YYYY-MM-DD, default: current date)
          - due_date: Due date (YYYY-MM-DD)
          - line_items (required): List of invoice line items
          - notes: Notes to be displayed on the invoice
          - terms: Terms and conditions
          - payment_terms: Payment terms in days
          - payment_terms_label: Label for payment terms
          - is_inclusive_tax: Whether tax is inclusive in item rate
          - salesperson_name: Name of the salesperson
          - custom_fields: Custom field values
        
    Returns:
        The created invoice details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating invoice for customer ID: {kwargs.get('customer_id')}")
    
    # Convert the kwargs to a CreateInvoiceInput model for validation
    try:
        invoice_data = CreateInvoiceInput.model_validate(kwargs)
    except Exception as e:
        logger.error(f"Validation error creating invoice: {str(e)}")
        raise ValueError(f"Invalid invoice data: {str(e)}")
    
    # Prepare data for API request
    data = invoice_data.model_dump(exclude_none=True)
    
    # Convert date objects to strings for JSON serialization
    if isinstance(data.get("invoice_date"), date):
        data["invoice_date"] = data["invoice_date"].isoformat()
    if isinstance(data.get("due_date"), date):
        data["due_date"] = data["due_date"].isoformat()
    
    try:
        response = zoho_api_request("POST", "/invoices", json=data)
        
        # Parse the response
        invoice_response = InvoiceResponse.model_validate(response)
        
        logger.info(f"Invoice created successfully: {invoice_response.invoice.get('invoice_id') if invoice_response.invoice else 'Unknown ID'}")
        
        return {
            "invoice": invoice_response.invoice,
            "message": invoice_response.message or "Invoice created successfully",
        }
        
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise


def get_invoice(invoice_id: str) -> Dict[str, Any]:
    """
    Get an invoice by ID from Zoho Books.
    
    Args:
        invoice_id: ID of the invoice to retrieve
        
    Returns:
        The invoice details
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Getting invoice with ID: {invoice_id}")
    
    try:
        response = zoho_api_request("GET", f"/invoices/{invoice_id}")
        
        # Parse the response
        invoice_response = InvoiceResponse.model_validate(response)
        
        if not invoice_response.invoice:
            logger.warning(f"Invoice not found: {invoice_id}")
            return {
                "message": "Invoice not found",
                "invoice": None,
            }
        
        logger.info(f"Invoice retrieved successfully: {invoice_id}")
        
        return {
            "invoice": invoice_response.invoice,
            "message": invoice_response.message or "Invoice retrieved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error getting invoice: {str(e)}")
        raise


def email_invoice(
    invoice_id: str,
    to_email: List[str],
    subject: Optional[str] = None,
    body: Optional[str] = None,
    cc_email: Optional[List[str]] = None,
    send_customer_statement: bool = False,
    send_attachment: bool = True,
) -> Dict[str, Any]:
    """
    Email an invoice to the customer.
    
    Args:
        invoice_id: ID of the invoice to email
        to_email: List of email addresses to send to
        subject: Email subject
        body: Email body content
        cc_email: List of email addresses to CC
        send_customer_statement: Whether to include customer statement
        send_attachment: Whether to include the invoice as an attachment
        
    Returns:
        Success message
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Emailing invoice {invoice_id} to {to_email}")
    
    # Prepare data for API request
    data = {
        "to_mail": to_email,
        "subject": subject,
        "body": body,
        "send_customer_statement": send_customer_statement,
        "send_attachment": send_attachment,
    }
    
    # Add CC email if provided
    if cc_email:
        data["cc_mail"] = cc_email
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = zoho_api_request("POST", f"/invoices/{invoice_id}/email", json=data)
        
        return {
            "success": True,
            "message": response.get("message", "Invoice emailed successfully"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error emailing invoice: {str(e)}")
        raise


def mark_invoice_as_sent(invoice_id: str) -> Dict[str, Any]:
    """
    Mark an invoice as sent in Zoho Books.
    
    Args:
        invoice_id: ID of the invoice to mark as sent
        
    Returns:
        Success message
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Marking invoice {invoice_id} as sent")
    
    try:
        response = zoho_api_request("POST", f"/invoices/{invoice_id}/status/sent")
        
        return {
            "success": True,
            "message": response.get("message", "Invoice marked as sent"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error marking invoice as sent: {str(e)}")
        raise


def void_invoice(invoice_id: str) -> Dict[str, Any]:
    """
    Void an invoice in Zoho Books.
    
    Args:
        invoice_id: ID of the invoice to void
        
    Returns:
        Success message
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Voiding invoice {invoice_id}")
    
    try:
        response = zoho_api_request("POST", f"/invoices/{invoice_id}/status/void")
        
        return {
            "success": True,
            "message": response.get("message", "Invoice voided successfully"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error voiding invoice: {str(e)}")
        raise


# Define metadata for tools that can be used by the MCP server
list_invoices.name = "list_invoices"  # type: ignore
list_invoices.description = "List invoices in Zoho Books with pagination and filtering"  # type: ignore
list_invoices.parameters = {  # type: ignore
    "page": {
        "type": "integer",
        "description": "Page number for pagination",
        "default": 1,
    },
    "page_size": {
        "type": "integer",
        "description": "Number of invoices per page",
        "default": 25,
    },
    "status": {
        "type": "string",
        "description": "Filter by invoice status",
        "enum": ["draft", "sent", "overdue", "paid", "void", "all"],
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
        "description": "Search text to filter invoices",
        "optional": True,
    },
    "sort_column": {
        "type": "string",
        "description": "Column to sort by",
        "enum": ["created_time", "date", "invoice_number", "total", "balance"],
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

create_invoice.name = "create_invoice"  # type: ignore
create_invoice.description = "Create a new invoice in Zoho Books"  # type: ignore
create_invoice.parameters = {  # type: ignore
    "customer_id": {
        "type": "string", 
        "description": "ID of the customer (required)",
    },
    "invoice_number": {
        "type": "string",
        "description": "Custom invoice number (system-generated if omitted)",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Reference number",
        "optional": True,
    },
    "invoice_date": {
        "type": "string",
        "description": "Invoice date (YYYY-MM-DD, default: current date)",
        "optional": True,
    },
    "due_date": {
        "type": "string",
        "description": "Due date (YYYY-MM-DD)",
        "optional": True,
    },
    "line_items": {
        "type": "array",
        "description": "Line items for the invoice (at least one required)",
        "items": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "ID of the existing item (from Zoho Books)",
                    "optional": True,
                },
                "name": {
                    "type": "string",
                    "description": "Name of the item (if item_id not provided)",
                    "optional": True,
                },
                "description": {
                    "type": "string",
                    "description": "Description of the line item",
                    "optional": True,
                },
                "rate": {
                    "type": "number",
                    "description": "Unit price of the item",
                },
                "quantity": {
                    "type": "number",
                    "description": "Quantity of the item",
                },
                "discount": {
                    "type": "number",
                    "description": "Discount percentage or amount",
                    "optional": True,
                },
                "discount_type": {
                    "type": "string",
                    "description": "Type of discount",
                    "enum": ["percentage", "amount"],
                    "optional": True,
                },
                "tax_id": {
                    "type": "string",
                    "description": "ID of the tax to apply",
                    "optional": True,
                },
                "tax_name": {
                    "type": "string",
                    "description": "Name of the tax (if tax_id not provided)",
                    "optional": True,
                },
                "tax_percentage": {
                    "type": "number",
                    "description": "Tax percentage",
                    "optional": True,
                },
            },
        },
    },
    "notes": {
        "type": "string",
        "description": "Notes to be displayed on the invoice",
        "optional": True,
    },
    "terms": {
        "type": "string",
        "description": "Terms and conditions",
        "optional": True,
    },
    "payment_terms": {
        "type": "integer",
        "description": "Payment terms in days",
        "optional": True,
    },
    "payment_terms_label": {
        "type": "string",
        "description": "Label for payment terms",
        "optional": True,
    },
    "is_inclusive_tax": {
        "type": "boolean",
        "description": "Whether tax is inclusive in item rate",
        "optional": True,
    },
    "salesperson_name": {
        "type": "string",
        "description": "Name of the salesperson",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}

get_invoice.name = "get_invoice"  # type: ignore
get_invoice.description = "Get an invoice by ID from Zoho Books"  # type: ignore
get_invoice.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to retrieve",
    },
}

email_invoice.name = "email_invoice"  # type: ignore
email_invoice.description = "Email an invoice to the customer"  # type: ignore
email_invoice.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to email",
    },
    "to_email": {
        "type": "array",
        "description": "List of email addresses to send to",
        "items": {
            "type": "string",
        },
    },
    "subject": {
        "type": "string",
        "description": "Email subject",
        "optional": True,
    },
    "body": {
        "type": "string",
        "description": "Email body content",
        "optional": True,
    },
    "cc_email": {
        "type": "array",
        "description": "List of email addresses to CC",
        "items": {
            "type": "string",
        },
        "optional": True,
    },
    "send_customer_statement": {
        "type": "boolean",
        "description": "Whether to include customer statement",
        "default": False,
        "optional": True,
    },
    "send_attachment": {
        "type": "boolean",
        "description": "Whether to include the invoice as an attachment",
        "default": True,
        "optional": True,
    },
}

mark_invoice_as_sent.name = "mark_invoice_as_sent"  # type: ignore
mark_invoice_as_sent.description = "Mark an invoice as sent in Zoho Books"  # type: ignore
mark_invoice_as_sent.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to mark as sent",
    },
}

void_invoice.name = "void_invoice"  # type: ignore
void_invoice.description = "Void an invoice in Zoho Books"  # type: ignore
void_invoice.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to void",
    },
}