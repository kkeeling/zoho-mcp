"""
Invoice Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing invoices in Zoho Books.
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from datetime import date

# Only used for type checking
if TYPE_CHECKING:
    
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from zoho_mcp.models.invoices import (
    CreateInvoiceInput,
    InvoiceResponse,
    InvoicesListResponse,
)
from zoho_mcp.tools.api import zoho_api_request_async

logger = logging.getLogger(__name__)


async def list_invoices(
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
        response = await zoho_api_request_async("GET", "/invoices", params=params)
        
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


async def create_invoice(**kwargs) -> Dict[str, Any]:
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
        response = await zoho_api_request_async("POST", "/invoices", json_data=data)
        
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


async def get_invoice(invoice_id: str) -> Dict[str, Any]:
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
        response = await zoho_api_request_async("GET", f"/invoices/{invoice_id}")
        
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


async def email_invoice(
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
        response = await zoho_api_request_async("POST", f"/invoices/{invoice_id}/email", json_data=data)
        
        return {
            "success": True,
            "message": response.get("message", "Invoice emailed successfully"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error emailing invoice: {str(e)}")
        raise


async def mark_invoice_as_sent(invoice_id: str) -> Dict[str, Any]:
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
        response = await zoho_api_request_async("POST", f"/invoices/{invoice_id}/status/sent")
        
        return {
            "success": True,
            "message": response.get("message", "Invoice marked as sent"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error marking invoice as sent: {str(e)}")
        raise


async def void_invoice(invoice_id: str) -> Dict[str, Any]:
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
        response = await zoho_api_request_async("POST", f"/invoices/{invoice_id}/status/void")
        
        return {
            "success": True,
            "message": response.get("message", "Invoice voided successfully"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error voiding invoice: {str(e)}")
        raise


async def record_payment(
    invoice_id: str,
    amount: float,
    payment_date: Optional[Union[str, date]] = None,
    payment_mode: str = "cash",
    reference_number: Optional[str] = None,
    description: Optional[str] = None,
    bank_charges: Optional[float] = None,
    tax_amount_withheld: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Record a payment for an invoice in Zoho Books.
    
    Args:
        invoice_id: ID of the invoice to record payment for
        amount: Payment amount
        payment_date: Date of payment (YYYY-MM-DD, default: current date)
        payment_mode: Mode of payment (cash, check, bank_transfer, credit_card, etc.)
        reference_number: Payment reference number
        description: Payment description
        bank_charges: Bank charges if any
        tax_amount_withheld: Tax amount withheld if any
        
    Returns:
        Payment details and updated invoice information
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Recording payment of {amount} for invoice {invoice_id}")
    
    # Prepare payment data
    data = {
        "amount": amount,
        "payment_mode": payment_mode,
    }
    
    # Add optional fields if provided
    if payment_date:
        data["date"] = str(payment_date) if isinstance(payment_date, date) else payment_date
    if reference_number:
        data["reference_number"] = reference_number
    if description:
        data["description"] = description
    if bank_charges is not None:
        data["bank_charges"] = bank_charges
    if tax_amount_withheld is not None:
        data["tax_amount_withheld"] = tax_amount_withheld
    
    try:
        response = await zoho_api_request_async("POST", f"/invoices/{invoice_id}/payments", json_data=data)
        
        return {
            "success": True,
            "message": response.get("message", "Payment recorded successfully"),
            "payment": response.get("payment", {}),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error recording payment: {str(e)}")
        raise


async def send_payment_reminder(
    invoice_id: str,
    to_email: Optional[List[str]] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    cc_email: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Send a payment reminder for an overdue invoice.
    
    Args:
        invoice_id: ID of the invoice to send reminder for
        to_email: List of email addresses to send to (uses customer email if not provided)
        subject: Email subject (uses default reminder subject if not provided)
        body: Email body content (uses default reminder template if not provided)
        cc_email: List of email addresses to CC
        
    Returns:
        Success message
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Sending payment reminder for invoice {invoice_id}")
    
    # Prepare data for API request
    data: Dict[str, Any] = {}
    
    if to_email:
        data["to_mail"] = to_email
    if subject:
        data["subject"] = subject
    if body:
        data["body"] = body
    if cc_email:
        data["cc_mail"] = cc_email
    
    try:
        response = await zoho_api_request_async("POST", f"/invoices/{invoice_id}/paymentreminder", json_data=data if data else None)
        
        return {
            "success": True,
            "message": response.get("message", "Payment reminder sent successfully"),
            "invoice_id": invoice_id,
        }
        
    except Exception as e:
        logger.error(f"Error sending payment reminder: {str(e)}")
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

record_payment.name = "record_payment"  # type: ignore
record_payment.description = "Record a payment for an invoice in Zoho Books"  # type: ignore
record_payment.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to record payment for",
    },
    "amount": {
        "type": "number",
        "description": "Payment amount",
    },
    "payment_date": {
        "type": "string",
        "description": "Date of payment (YYYY-MM-DD, default: current date)",
        "optional": True,
    },
    "payment_mode": {
        "type": "string",
        "description": "Mode of payment (cash, check, bank_transfer, credit_card, etc.)",
        "default": "cash",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Payment reference number",
        "optional": True,
    },
    "description": {
        "type": "string",
        "description": "Payment description",
        "optional": True,
    },
    "bank_charges": {
        "type": "number",
        "description": "Bank charges if any",
        "optional": True,
    },
    "tax_amount_withheld": {
        "type": "number",
        "description": "Tax amount withheld if any",
        "optional": True,
    },
}

send_payment_reminder.name = "send_payment_reminder"  # type: ignore
send_payment_reminder.description = "Send a payment reminder for an overdue invoice"  # type: ignore
send_payment_reminder.parameters = {  # type: ignore
    "invoice_id": {
        "type": "string",
        "description": "ID of the invoice to send reminder for",
    },
    "to_email": {
        "type": "array",
        "description": "List of email addresses to send to (uses customer email if not provided)",
        "optional": True,
    },
    "subject": {
        "type": "string",
        "description": "Email subject (uses default reminder subject if not provided)",
        "optional": True,
    },
    "body": {
        "type": "string",
        "description": "Email body content (uses default reminder template if not provided)",
        "optional": True,
    },
    "cc_email": {
        "type": "array",
        "description": "List of email addresses to CC",
        "optional": True,
    },
}
