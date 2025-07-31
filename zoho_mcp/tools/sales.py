"""
Sales Order Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing sales orders in Zoho Books.
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, Union

# Only used for type checking
if TYPE_CHECKING:
    from typing import TypedDict
    
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from pydantic import BaseModel, ValidationError
from zoho_mcp.models.base import BaseResponse
from zoho_mcp.tools.api import zoho_api_request_async

logger = logging.getLogger(__name__)


async def list_sales_orders(
    page: int = 1,
    page_size: int = 25,
    status: Optional[Literal["draft", "open", "void", "all"]] = None,
    customer_id: Optional[str] = None,
    date_range_start: Optional[Union[str, date]] = None,
    date_range_end: Optional[Union[str, date]] = None,
    search_text: Optional[str] = None,
    sort_column: str = "date",
    sort_order: Literal["ascending", "descending"] = "descending",
) -> Dict[str, Any]:
    """
    List sales orders in Zoho Books with pagination and filtering.
    
    Args:
        page: Page number for pagination
        page_size: Number of sales orders per page
        status: Filter by sales order status
        customer_id: Filter by customer ID
        date_range_start: Filter by start date (YYYY-MM-DD)
        date_range_end: Filter by end date (YYYY-MM-DD)
        search_text: Search text to filter sales orders
        sort_column: Column to sort by
        sort_order: Sort order (ascending or descending)
        
    Returns:
        A paginated list of sales orders matching the filters
    """
    logger.info(
        f"Listing sales orders with page={page}, " 
        f"status={status or 'all'}, customer_id={customer_id or 'None'}"
    )
    
    # Basic validation for inputs
    if page < 1:
        raise ValueError("Page number must be at least 1")
    if page_size < 1 or page_size > 200:
        raise ValueError("Page size must be between 1 and 200")
    if status and status not in ["draft", "open", "void", "all"]:
        raise ValueError("Status must be one of 'draft', 'open', 'void', 'all'")
    if sort_order and sort_order not in ["ascending", "descending"]:
        raise ValueError("Sort order must be 'ascending' or 'descending'")
    
    # Prepare API request parameters
    params = {
        "page": page,
        "per_page": page_size,
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
    
    # Add optional filters if provided
    if status:
        params["filter_by"] = status
    
    if customer_id:
        params["customer_id"] = customer_id
    
    if search_text:
        params["search_text"] = search_text
    
    # Date range filtering
    if date_range_start:
        # Convert to string if it's a date object
        if isinstance(date_range_start, date):
            date_range_start = date_range_start.isoformat()
        params["date_start"] = date_range_start
    
    if date_range_end:
        # Convert to string if it's a date object
        if isinstance(date_range_end, date):
            date_range_end = date_range_end.isoformat()
        params["date_end"] = date_range_end
    
    try:
        response = await zoho_api_request_async("GET", "/salesorders", params=params)
        
        # Basic response handling
        sales_orders = response.get("salesorders", [])
        message = response.get("message", "")
        page_context = response.get("page_context", {})
        
        # Construct paginated response
        result = {
            "page": page,
            "page_size": page_size,
            "sales_orders": sales_orders,
            "message": message,
        }
        
        # Add pagination context if available
        if page_context:
            result["has_more_page"] = page_context.get("has_more_page", False)
            if "total" in page_context:
                result["total"] = page_context["total"]
        
        logger.info(f"Retrieved {len(result['sales_orders'])} sales orders")
        return result
        
    except Exception as e:
        logger.error(f"Error listing sales orders: {str(e)}")
        raise


async def create_sales_order(
    customer_id: str,
    line_items: List[Dict[str, Any]],
    date: Optional[Union[str, date]] = None,
    salesorder_number: Optional[str] = None,
    reference_number: Optional[str] = None,
    shipment_date: Optional[Union[str, date]] = None,
    notes: Optional[str] = None,
    terms: Optional[str] = None,
    contact_persons: Optional[List[str]] = None,
    currency_id: Optional[str] = None,
    is_inclusive_tax: Optional[bool] = None,
    discount: Optional[str] = None,
    is_discount_before_tax: Optional[bool] = None,
    discount_type: Optional[Literal["entity_level", "item_level"]] = None,
    shipping_charge: Optional[float] = None,
    adjustment: Optional[float] = None,
    adjustment_description: Optional[str] = None,
    billing_address: Optional[Dict[str, Any]] = None,
    shipping_address: Optional[Dict[str, Any]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    salesperson_id: Optional[str] = None,
    salesperson_name: Optional[str] = None,
    template_id: Optional[str] = None,
    location_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new sales order in Zoho Books.
    
    Args:
        customer_id: ID of the customer (required)
        line_items: List of line items for the sales order (required)
        date: Sales order date (YYYY-MM-DD)
        salesorder_number: Custom sales order number
        reference_number: Reference number
        shipment_date: Expected shipment date (YYYY-MM-DD)
        notes: Notes to be displayed on the sales order
        terms: Terms and conditions
        contact_persons: IDs of contact persons
        currency_id: ID of the currency
        is_inclusive_tax: Whether tax is inclusive in item rate
        discount: Discount applied to the sales order
        is_discount_before_tax: Whether discount is applied before tax
        discount_type: How the discount is specified
        shipping_charge: Shipping charge
        adjustment: Adjustment amount
        adjustment_description: Description for the adjustment
        billing_address: Billing address details
        shipping_address: Shipping address details
        custom_fields: Custom field values
        salesperson_id: ID of the salesperson
        salesperson_name: Name of the salesperson
        template_id: ID of the PDF template
        location_id: Location ID for inventory
        
    Returns:
        The created sales order details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating sales order for customer: {customer_id}")
    
    # Prepare input data
    input_data: Dict[str, Any] = {
        "customer_id": customer_id,
        "line_items": line_items,
    }
    
    # Add optional fields if provided
    if date is not None:
        input_data["date"] = date
    if salesorder_number is not None:
        input_data["salesorder_number"] = salesorder_number
    if reference_number is not None:
        input_data["reference_number"] = reference_number
    if shipment_date is not None:
        input_data["shipment_date"] = shipment_date
    if notes is not None:
        input_data["notes"] = notes
    if terms is not None:
        input_data["terms"] = terms
    if contact_persons is not None:
        input_data["contact_persons"] = contact_persons
    if currency_id is not None:
        input_data["currency_id"] = currency_id
    if is_inclusive_tax is not None:
        input_data["is_inclusive_tax"] = is_inclusive_tax
    if discount is not None:
        input_data["discount"] = discount
    if is_discount_before_tax is not None:
        input_data["is_discount_before_tax"] = is_discount_before_tax
    if discount_type is not None:
        input_data["discount_type"] = discount_type
    if shipping_charge is not None:
        input_data["shipping_charge"] = shipping_charge
    if adjustment is not None:
        input_data["adjustment"] = adjustment
    if adjustment_description is not None:
        input_data["adjustment_description"] = adjustment_description
    if billing_address is not None:
        input_data["billing_address"] = billing_address
    if shipping_address is not None:
        input_data["shipping_address"] = shipping_address
    if custom_fields is not None:
        input_data["custom_fields"] = custom_fields
    if salesperson_id is not None:
        input_data["salesperson_id"] = salesperson_id
    if salesperson_name is not None:
        input_data["salesperson_name"] = salesperson_name
    if template_id is not None:
        input_data["template_id"] = template_id
    if location_id is not None:
        input_data["location_id"] = location_id
    
    # Basic validation
    if not customer_id:
        raise ValueError("customer_id is required")
    
    if not line_items or not isinstance(line_items, list) or len(line_items) == 0:
        raise ValueError("At least one line item is required")
    
    for item in line_items:
        if not isinstance(item, dict):
            raise ValueError("Line items must be dictionaries")
        
        # Validate each line item
        if not (item.get('item_id') or item.get('name')):
            raise ValueError("Each line item must have either item_id or name")
        
        rate = item.get('rate')
        if not rate or not isinstance(rate, (int, float)) or rate <= 0:
            raise ValueError("Each line item must have a positive rate")
        
        quantity = item.get('quantity')
        if not quantity or not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("Each line item must have a positive quantity")
    
    # Prepare data for API request - filter out None values
    data = {k: v for k, v in input_data.items() if v is not None}
    
    try:
        response = await zoho_api_request_async("POST", "/salesorders", json_data=data)
        
        # Parse the response
        salesorder = response.get("salesorder", {})
        message = response.get("message", "Sales order created successfully")
        
        logger.info(f"Sales order created successfully: {salesorder.get('salesorder_id', 'Unknown ID')}")
        
        return {
            "salesorder": salesorder,
            "message": message,
        }
        
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}")
        raise


async def get_sales_order(salesorder_id: str) -> Dict[str, Any]:
    """
    Get a sales order by ID from Zoho Books.
    
    Args:
        salesorder_id: ID of the sales order to retrieve
        
    Returns:
        The sales order details
        
    Raises:
        Exception: If the API request fails or the sales order ID is invalid
    """
    logger.info(f"Getting sales order with ID: {salesorder_id}")
    
    # Validate input
    if not salesorder_id or not isinstance(salesorder_id, str):
        logger.error("Invalid sales order ID")
        raise ValueError("Invalid sales order ID")
    
    try:
        response = await zoho_api_request_async("GET", f"/salesorders/{salesorder_id}")
        
        # Parse the response
        salesorder = response.get("salesorder")
        message = response.get("message", "Sales order retrieved successfully")
        
        if not salesorder:
            logger.warning(f"Sales order not found: {salesorder_id}")
            return {
                "message": "Sales order not found",
                "salesorder": None,
            }
        
        logger.info(f"Sales order retrieved successfully: {salesorder_id}")
        
        return {
            "salesorder": salesorder,
            "message": message,
        }
        
    except Exception as e:
        logger.error(f"Error getting sales order: {str(e)}")
        raise


async def update_sales_order(
    salesorder_id: str,
    customer_id: Optional[str] = None,
    line_items: Optional[List[Dict[str, Any]]] = None,
    date: Optional[Union[str, date]] = None,
    salesorder_number: Optional[str] = None,
    reference_number: Optional[str] = None,
    shipment_date: Optional[Union[str, date]] = None,
    notes: Optional[str] = None,
    terms: Optional[str] = None,
    contact_persons: Optional[List[str]] = None,
    currency_id: Optional[str] = None,
    is_inclusive_tax: Optional[bool] = None,
    discount: Optional[str] = None,
    is_discount_before_tax: Optional[bool] = None,
    discount_type: Optional[Literal["entity_level", "item_level"]] = None,
    shipping_charge: Optional[float] = None,
    adjustment: Optional[float] = None,
    adjustment_description: Optional[str] = None,
    billing_address: Optional[Dict[str, Any]] = None,
    shipping_address: Optional[Dict[str, Any]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    salesperson_id: Optional[str] = None,
    salesperson_name: Optional[str] = None,
    template_id: Optional[str] = None,
    location_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing sales order in Zoho Books.
    
    Args:
        salesorder_id: ID of the sales order to update (required)
        customer_id: ID of the customer
        line_items: List of line items for the sales order
        date: Sales order date (YYYY-MM-DD)
        salesorder_number: Custom sales order number
        reference_number: Reference number
        shipment_date: Expected shipment date (YYYY-MM-DD)
        notes: Notes to be displayed on the sales order
        terms: Terms and conditions
        contact_persons: IDs of contact persons
        currency_id: ID of the currency
        is_inclusive_tax: Whether tax is inclusive in item rate
        discount: Discount applied to the sales order
        is_discount_before_tax: Whether discount is applied before tax
        discount_type: How the discount is specified
        shipping_charge: Shipping charge
        adjustment: Adjustment amount
        adjustment_description: Description for the adjustment
        billing_address: Billing address details
        shipping_address: Shipping address details
        custom_fields: Custom field values
        salesperson_id: ID of the salesperson
        salesperson_name: Name of the salesperson
        template_id: ID of the PDF template
        location_id: Location ID for inventory
        
    Returns:
        The updated sales order details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Updating sales order with ID: {salesorder_id}")
    
    # Validate sales order ID
    if not salesorder_id or not isinstance(salesorder_id, str):
        logger.error("Invalid sales order ID")
        raise ValueError("Invalid sales order ID")
    
    # Prepare input data with provided fields
    input_data: Dict[str, Any] = {}
    
    # Add fields only if they are provided (not None)
    if customer_id is not None:
        input_data["customer_id"] = customer_id
    if line_items is not None:
        input_data["line_items"] = line_items
    if date is not None:
        input_data["date"] = date
    if salesorder_number is not None:
        input_data["salesorder_number"] = salesorder_number
    if reference_number is not None:
        input_data["reference_number"] = reference_number
    if shipment_date is not None:
        input_data["shipment_date"] = shipment_date
    if notes is not None:
        input_data["notes"] = notes
    if terms is not None:
        input_data["terms"] = terms
    if contact_persons is not None:
        input_data["contact_persons"] = contact_persons
    if currency_id is not None:
        input_data["currency_id"] = currency_id
    if is_inclusive_tax is not None:
        input_data["is_inclusive_tax"] = is_inclusive_tax
    if discount is not None:
        input_data["discount"] = discount
    if is_discount_before_tax is not None:
        input_data["is_discount_before_tax"] = is_discount_before_tax
    if discount_type is not None:
        input_data["discount_type"] = discount_type
    if shipping_charge is not None:
        input_data["shipping_charge"] = shipping_charge
    if adjustment is not None:
        input_data["adjustment"] = adjustment
    if adjustment_description is not None:
        input_data["adjustment_description"] = adjustment_description
    if billing_address is not None:
        input_data["billing_address"] = billing_address
    if shipping_address is not None:
        input_data["shipping_address"] = shipping_address
    if custom_fields is not None:
        input_data["custom_fields"] = custom_fields
    if salesperson_id is not None:
        input_data["salesperson_id"] = salesperson_id
    if salesperson_name is not None:
        input_data["salesperson_name"] = salesperson_name
    if template_id is not None:
        input_data["template_id"] = template_id
    if location_id is not None:
        input_data["location_id"] = location_id
    
    # Ensure at least one field is being updated
    if not input_data:
        logger.error("No fields provided for update")
        raise ValueError("At least one field must be provided for update")
    
    # Prepare data for API request - filter out None values
    data = {k: v for k, v in input_data.items() if v is not None}
    
    try:
        response = await zoho_api_request_async("PUT", f"/salesorders/{salesorder_id}", json_data=data)
        
        # Parse the response
        salesorder = response.get("salesorder", {})
        message = response.get("message", "Sales order updated successfully")
        
        logger.info(f"Sales order updated successfully: {salesorder_id}")
        
        return {
            "salesorder": salesorder,
            "message": message,
        }
        
    except Exception as e:
        logger.error(f"Error updating sales order: {str(e)}")
        raise


async def convert_to_invoice(
    salesorder_id: str,
    ignore_auto_number_generation: Optional[bool] = None,
    invoice_number: Optional[str] = None,
    date: Optional[Union[str, date]] = None,
    payment_terms: Optional[int] = None,
    payment_terms_label: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a sales order to an invoice in Zoho Books.
    
    Args:
        salesorder_id: ID of the sales order to convert (required)
        ignore_auto_number_generation: Whether to ignore auto invoice number generation
        invoice_number: Custom invoice number (required if ignore_auto_number_generation is True)
        date: Invoice date (YYYY-MM-DD)
        payment_terms: Payment terms in days
        payment_terms_label: Label for payment terms
        
    Returns:
        The created invoice details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Converting sales order to invoice: {salesorder_id}")
    
    # Prepare input data
    input_data: Dict[str, Any] = {
        "salesorder_id": salesorder_id,
    }
    
    # Add optional fields if provided
    if ignore_auto_number_generation is not None:
        input_data["ignore_auto_number_generation"] = ignore_auto_number_generation
    if invoice_number is not None:
        input_data["invoice_number"] = invoice_number
    if date is not None:
        input_data["date"] = date
    if payment_terms is not None:
        input_data["payment_terms"] = payment_terms
    if payment_terms_label is not None:
        input_data["payment_terms_label"] = payment_terms_label
    
    # Basic validation
    if not salesorder_id:
        raise ValueError("salesorder_id is required")
    
    # If ignore_auto_number_generation is True, invoice_number is required
    if ignore_auto_number_generation and not invoice_number:
        raise ValueError("invoice_number is required when ignore_auto_number_generation is True")
    
    # Prepare data for API request - filter out None values
    data = {k: v for k, v in input_data.items() if v is not None}
    
    # The conversion endpoint is not documented in the API docs but typically follows this pattern
    endpoint = f"/salesorders/{salesorder_id}/convert"
    
    try:
        # Query parameters for optional settings
        params = {}
        if ignore_auto_number_generation is not None:
            params["ignore_auto_number_generation"] = str(ignore_auto_number_generation).lower()
        
        response = await zoho_api_request_async("POST", endpoint, params=params, json_data=data)
        
        # Parse the response
        invoice = response.get("invoice", {})
        message = response.get("message", "Sales order converted to invoice successfully")
        
        logger.info(f"Sales order {salesorder_id} converted to invoice successfully")
        
        return {
            "invoice": invoice,
            "message": message,
        }
        
    except Exception as e:
        logger.error(f"Error converting sales order to invoice: {str(e)}")
        raise


# Define metadata for tools that can be used by the MCP server
list_sales_orders.name = "list_sales_orders"  # type: ignore
list_sales_orders.description = "List sales orders in Zoho Books with pagination and filtering"  # type: ignore
list_sales_orders.parameters = {  # type: ignore
    "page": {
        "type": "integer",
        "description": "Page number for pagination",
        "default": 1,
    },
    "page_size": {
        "type": "integer",
        "description": "Number of sales orders per page",
        "default": 25,
    },
    "status": {
        "type": "string",
        "description": "Filter by sales order status",
        "enum": ["draft", "open", "void", "all"],
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
        "description": "Search text to filter sales orders",
        "optional": True,
    },
    "sort_column": {
        "type": "string",
        "description": "Column to sort by",
        "default": "date",
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

create_sales_order.name = "create_sales_order"  # type: ignore
create_sales_order.description = "Create a new sales order in Zoho Books"  # type: ignore
create_sales_order.parameters = {  # type: ignore
    "customer_id": {
        "type": "string",
        "description": "ID of the customer (required)",
    },
    "line_items": {
        "type": "array",
        "description": "List of line items for the sales order (required)",
        "items": {
            "type": "object",
            "properties": {
                "item_id": {"type": "string", "description": "ID of the item"},
                "name": {"type": "string", "description": "Name of the item"},
                "description": {"type": "string", "description": "Description of the item"},
                "rate": {"type": "number", "description": "Rate/price of the item"},
                "quantity": {"type": "number", "description": "Quantity of the item"},
                "unit": {"type": "string", "description": "Unit (e.g., pcs, hr)"},
                "discount": {"type": "string", "description": "Discount (e.g., 10%, 50)"},
                "tax_id": {"type": "string", "description": "ID of the tax to apply"},
            },
        },
    },
    "date": {
        "type": "string",
        "description": "Sales order date (YYYY-MM-DD)",
        "optional": True,
    },
    "salesorder_number": {
        "type": "string",
        "description": "Custom sales order number",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Reference number",
        "optional": True,
    },
    "shipment_date": {
        "type": "string",
        "description": "Expected shipment date (YYYY-MM-DD)",
        "optional": True,
    },
    "notes": {
        "type": "string",
        "description": "Notes to be displayed on the sales order",
        "optional": True,
    },
    "terms": {
        "type": "string",
        "description": "Terms and conditions",
        "optional": True,
    },
    "contact_persons": {
        "type": "array",
        "description": "IDs of contact persons",
        "items": {"type": "string"},
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency",
        "optional": True,
    },
    "is_inclusive_tax": {
        "type": "boolean",
        "description": "Whether tax is inclusive in item rate",
        "optional": True,
    },
    "discount": {
        "type": "string",
        "description": "Discount applied to the sales order",
        "optional": True,
    },
    "is_discount_before_tax": {
        "type": "boolean",
        "description": "Whether discount is applied before tax",
        "optional": True,
    },
    "discount_type": {
        "type": "string",
        "description": "How the discount is specified",
        "enum": ["entity_level", "item_level"],
        "optional": True,
    },
    "shipping_charge": {
        "type": "number",
        "description": "Shipping charge",
        "optional": True,
    },
    "adjustment": {
        "type": "number",
        "description": "Adjustment amount",
        "optional": True,
    },
    "adjustment_description": {
        "type": "string",
        "description": "Description for the adjustment",
        "optional": True,
    },
    "billing_address": {
        "type": "object",
        "description": "Billing address details",
        "optional": True,
    },
    "shipping_address": {
        "type": "object",
        "description": "Shipping address details",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
    "salesperson_id": {
        "type": "string",
        "description": "ID of the salesperson",
        "optional": True,
    },
    "salesperson_name": {
        "type": "string",
        "description": "Name of the salesperson",
        "optional": True,
    },
    "template_id": {
        "type": "string",
        "description": "ID of the PDF template",
        "optional": True,
    },
    "location_id": {
        "type": "string",
        "description": "Location ID for inventory",
        "optional": True,
    },
}

get_sales_order.name = "get_sales_order"  # type: ignore
get_sales_order.description = "Get a sales order by ID from Zoho Books"  # type: ignore
get_sales_order.parameters = {  # type: ignore
    "salesorder_id": {
        "type": "string",
        "description": "ID of the sales order to retrieve",
    },
}

update_sales_order.name = "update_sales_order"  # type: ignore
update_sales_order.description = "Update an existing sales order in Zoho Books"  # type: ignore
update_sales_order.parameters = {  # type: ignore
    "salesorder_id": {
        "type": "string",
        "description": "ID of the sales order to update (required)",
    },
    "customer_id": {
        "type": "string",
        "description": "ID of the customer",
        "optional": True,
    },
    "line_items": {
        "type": "array",
        "description": "List of line items for the sales order",
        "items": {
            "type": "object",
            "properties": {
                "line_item_id": {"type": "string", "description": "ID of the line item (for updates)"},
                "item_id": {"type": "string", "description": "ID of the item"},
                "name": {"type": "string", "description": "Name of the item"},
                "description": {"type": "string", "description": "Description of the item"},
                "rate": {"type": "number", "description": "Rate/price of the item"},
                "quantity": {"type": "number", "description": "Quantity of the item"},
                "unit": {"type": "string", "description": "Unit (e.g., pcs, hr)"},
                "discount": {"type": "string", "description": "Discount (e.g., 10%, 50)"},
                "tax_id": {"type": "string", "description": "ID of the tax to apply"},
            },
        },
        "optional": True,
    },
    "date": {
        "type": "string",
        "description": "Sales order date (YYYY-MM-DD)",
        "optional": True,
    },
    "salesorder_number": {
        "type": "string",
        "description": "Custom sales order number",
        "optional": True,
    },
    "reference_number": {
        "type": "string",
        "description": "Reference number",
        "optional": True,
    },
    "shipment_date": {
        "type": "string",
        "description": "Expected shipment date (YYYY-MM-DD)",
        "optional": True,
    },
    "notes": {
        "type": "string",
        "description": "Notes to be displayed on the sales order",
        "optional": True,
    },
    "terms": {
        "type": "string",
        "description": "Terms and conditions",
        "optional": True,
    },
    "contact_persons": {
        "type": "array",
        "description": "IDs of contact persons",
        "items": {"type": "string"},
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency",
        "optional": True,
    },
    "is_inclusive_tax": {
        "type": "boolean",
        "description": "Whether tax is inclusive in item rate",
        "optional": True,
    },
    "discount": {
        "type": "string",
        "description": "Discount applied to the sales order",
        "optional": True,
    },
    "is_discount_before_tax": {
        "type": "boolean",
        "description": "Whether discount is applied before tax",
        "optional": True,
    },
    "discount_type": {
        "type": "string",
        "description": "How the discount is specified",
        "enum": ["entity_level", "item_level"],
        "optional": True,
    },
    "shipping_charge": {
        "type": "number",
        "description": "Shipping charge",
        "optional": True,
    },
    "adjustment": {
        "type": "number",
        "description": "Adjustment amount",
        "optional": True,
    },
    "adjustment_description": {
        "type": "string",
        "description": "Description for the adjustment",
        "optional": True,
    },
    "billing_address": {
        "type": "object",
        "description": "Billing address details",
        "optional": True,
    },
    "shipping_address": {
        "type": "object",
        "description": "Shipping address details",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
    "salesperson_id": {
        "type": "string",
        "description": "ID of the salesperson",
        "optional": True,
    },
    "salesperson_name": {
        "type": "string",
        "description": "Name of the salesperson",
        "optional": True,
    },
    "template_id": {
        "type": "string",
        "description": "ID of the PDF template",
        "optional": True,
    },
    "location_id": {
        "type": "string",
        "description": "Location ID for inventory",
        "optional": True,
    },
}

convert_to_invoice.name = "convert_to_invoice"  # type: ignore
convert_to_invoice.description = "Convert a sales order to an invoice in Zoho Books"  # type: ignore
convert_to_invoice.parameters = {  # type: ignore
    "salesorder_id": {
        "type": "string",
        "description": "ID of the sales order to convert (required)",
    },
    "ignore_auto_number_generation": {
        "type": "boolean",
        "description": "Whether to ignore auto invoice number generation",
        "optional": True,
    },
    "invoice_number": {
        "type": "string",
        "description": "Custom invoice number (required if ignore_auto_number_generation is True)",
        "optional": True,
    },
    "date": {
        "type": "string",
        "description": "Invoice date (YYYY-MM-DD)",
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
}
