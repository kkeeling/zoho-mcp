"""
Contact Management Tools for Zoho Books MCP Integration Server.

This module provides MCP tools for managing contacts (customers and vendors) in Zoho Books.
"""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

# Only used for type checking
if TYPE_CHECKING:
    from typing import TypedDict
    
    class MCPTool:
        """Type for an MCP tool function with metadata."""
        name: str
        description: str
        parameters: Dict[str, Any]

from zoho_mcp.models.contacts import (
    ContactDeleteInput,
    CustomerInput,
    VendorInput,
    ContactResponse,
    ContactsListResponse,
)
from zoho_mcp.tools.api import zoho_api_request

logger = logging.getLogger(__name__)


def list_contacts(
    contact_type: str = "all",
    page: int = 1,
    page_size: int = 25,
    search_text: Optional[str] = None,
    filter_by: str = "active",
    sort_column: str = "contact_name",
    sort_order: str = "ascending",
) -> Dict[str, Any]:
    """
    List contacts (customers or vendors) in Zoho Books with pagination and filtering.
    
    Args:
        contact_type: Type of contacts to list (all, customer, or vendor)
        page: Page number for pagination
        page_size: Number of contacts per page
        search_text: Search text to filter contacts by name, email, etc.
        filter_by: Filter contacts by status (all, active, inactive)
        sort_column: Column to sort by (contact_name, created_time, last_modified_time)
        sort_order: Sort order (ascending or descending)
        
    Returns:
        A paginated list of contacts matching the filters
    """
    logger.info(
        f"Listing contacts with type={contact_type}, page={page}, " 
        f"filter_by={filter_by}, search_text={search_text or 'None'}"
    )
    
    params = {
        "page": page,
        "per_page": page_size,
        "filter_by": filter_by,
        "sort_column": sort_column,
        "sort_order": sort_order,
    }
    
    # Add search_text if provided
    if search_text:
        params["search_text"] = search_text
    
    # Set the endpoint based on contact_type
    if contact_type == "customer":
        endpoint = "/contacts?contact_type=customer"
    elif contact_type == "vendor":
        endpoint = "/contacts?contact_type=vendor"
    else:
        endpoint = "/contacts"
    
    try:
        response = zoho_api_request("GET", endpoint, params=params)
        
        # Parse the response
        contacts_response = ContactsListResponse.model_validate(response)
        
        # Construct paginated response
        result = {
            "page": page,
            "page_size": page_size,
            "has_more_page": response.get("page_context", {}).get("has_more_page", False),
            "contacts": contacts_response.contacts or [],
            "message": contacts_response.message,
        }
        
        # Add total count if available
        if "page_context" in response and "total" in response["page_context"]:
            result["total"] = response["page_context"]["total"]
            
        logger.info(f"Retrieved {len(result['contacts'])} contacts")
        return result
        
    except Exception as e:
        logger.error(f"Error listing contacts: {str(e)}")
        raise


def create_customer(**kwargs) -> Dict[str, Any]:
    """
    Create a new customer in Zoho Books.
    
    Args:
        **kwargs: Customer details including:
          - contact_name (required): Name of the customer
          - email: Primary email address
          - phone: Primary phone number
          - mobile: Mobile/cell phone number
          - company_name: Company name if different from contact name
          - website: Website URL
          - notes: Notes about the customer
          - currency_id: ID of the currency used by this customer
          - payment_terms: Payment terms in days
          - billing_address: Customer billing address details
          - shipping_address: Customer shipping address details
          - contact_persons: List of additional contact persons
          - custom_fields: Custom field values
        
    Returns:
        The created customer details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating customer with name: {kwargs.get('contact_name')}")
    
    # Convert the kwargs to a CustomerInput model for validation
    try:
        customer_data = CustomerInput.model_validate(kwargs)
    except Exception as e:
        logger.error(f"Validation error creating customer: {str(e)}")
        raise ValueError(f"Invalid customer data: {str(e)}")
    
    # Prepare data for API request
    data = customer_data.model_dump(exclude_none=True)
    
    try:
        response = zoho_api_request("POST", "/contacts", json=data)
        
        # Parse the response
        contact_response = ContactResponse.model_validate(response)
        
        logger.info(f"Customer created successfully: {contact_response.contact.get('contact_id') if contact_response.contact else 'Unknown ID'}")
        
        return {
            "contact": contact_response.contact,
            "message": contact_response.message or "Customer created successfully",
        }
        
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise


def create_vendor(**kwargs) -> Dict[str, Any]:
    """
    Create a new vendor in Zoho Books.
    
    Args:
        **kwargs: Vendor details including:
          - contact_name (required): Name of the vendor
          - email: Primary email address
          - phone: Primary phone number
          - mobile: Mobile/cell phone number
          - company_name: Company name if different from contact name
          - website: Website URL
          - notes: Notes about the vendor
          - currency_id: ID of the currency used by this vendor
          - payment_terms: Payment terms in days
          - billing_address: Vendor billing address details
          - shipping_address: Vendor shipping address details
          - contact_persons: List of additional contact persons
          - custom_fields: Custom field values
        
    Returns:
        The created vendor details
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Creating vendor with name: {kwargs.get('contact_name')}")
    
    # Convert the kwargs to a VendorInput model for validation
    try:
        vendor_data = VendorInput.model_validate(kwargs)
    except Exception as e:
        logger.error(f"Validation error creating vendor: {str(e)}")
        raise ValueError(f"Invalid vendor data: {str(e)}")
    
    # Prepare data for API request
    data = vendor_data.model_dump(exclude_none=True)
    
    try:
        response = zoho_api_request("POST", "/contacts", json=data)
        
        # Parse the response
        contact_response = ContactResponse.model_validate(response)
        
        logger.info(f"Vendor created successfully: {contact_response.contact.get('contact_id') if contact_response.contact else 'Unknown ID'}")
        
        return {
            "contact": contact_response.contact,
            "message": contact_response.message or "Vendor created successfully",
        }
        
    except Exception as e:
        logger.error(f"Error creating vendor: {str(e)}")
        raise


def get_contact(contact_id: str) -> Dict[str, Any]:
    """
    Get a contact by ID from Zoho Books.
    
    Args:
        contact_id: ID of the contact to retrieve
        
    Returns:
        The contact details
        
    Raises:
        Exception: If the API request fails
    """
    logger.info(f"Getting contact with ID: {contact_id}")
    
    try:
        response = zoho_api_request("GET", f"/contacts/{contact_id}")
        
        # Parse the response
        contact_response = ContactResponse.model_validate(response)
        
        if not contact_response.contact:
            logger.warning(f"Contact not found: {contact_id}")
            return {
                "message": "Contact not found",
                "contact": None,
            }
        
        logger.info(f"Contact retrieved successfully: {contact_id}")
        
        return {
            "contact": contact_response.contact,
            "message": contact_response.message or "Contact retrieved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error getting contact: {str(e)}")
        raise


def delete_contact(contact_id: str) -> Dict[str, Any]:
    """
    Delete a contact from Zoho Books.
    
    Args:
        contact_id: ID of the contact to delete
        
    Returns:
        Success message
        
    Raises:
        Exception: If validation fails or the API request fails
    """
    logger.info(f"Deleting contact with ID: {contact_id}")
    
    # Validate input
    try:
        # We validate the contact_id but don't need to use the result
        ContactDeleteInput(contact_id=contact_id)
    except Exception as e:
        logger.error(f"Validation error deleting contact: {str(e)}")
        raise ValueError(f"Invalid contact ID: {str(e)}")
    
    try:
        response = zoho_api_request("DELETE", f"/contacts/{contact_id}")
        
        # The API response for delete operations might be minimal
        # so we construct a standardized response
        return {
            "success": True,
            "message": response.get("message", "Contact deleted successfully"),
            "contact_id": contact_id,
        }
        
    except Exception as e:
        logger.error(f"Error deleting contact: {str(e)}")
        raise


# Define metadata for tools that can be used by the MCP server
list_contacts.name = "list_contacts"  # type: ignore
list_contacts.description = "List contacts (customers or vendors) in Zoho Books with pagination and filtering"  # type: ignore
list_contacts.parameters = {  # type: ignore
    "contact_type": {
        "type": "string",
        "enum": ["all", "customer", "vendor"],
        "description": "Type of contacts to list: all, customer, or vendor",
        "default": "all",
    },
    "page": {
        "type": "integer",
        "description": "Page number for pagination",
        "default": 1,
    },
    "page_size": {
        "type": "integer",
        "description": "Number of contacts per page",
        "default": 25,
    },
    "search_text": {
        "type": "string",
        "description": "Search text to filter contacts by name, email, etc.",
        "optional": True,
    },
    "filter_by": {
        "type": "string",
        "description": "Filter contacts by status",
        "enum": ["all", "active", "inactive"],
        "default": "active",
        "optional": True,
    },
    "sort_column": {
        "type": "string",
        "description": "Column to sort by",
        "enum": ["contact_name", "created_time", "last_modified_time"],
        "default": "contact_name",
        "optional": True,
    },
    "sort_order": {
        "type": "string",
        "description": "Sort order (ascending or descending)",
        "enum": ["ascending", "descending"],
        "default": "ascending",
        "optional": True,
    },
}

create_customer.name = "create_customer"  # type: ignore
create_customer.description = "Create a new customer in Zoho Books"  # type: ignore
create_customer.parameters = {  # type: ignore
    "contact_name": {
        "type": "string", 
        "description": "Name of the customer (required)",
    },
    "email": {
        "type": "string",
        "description": "Primary email address",
        "optional": True,
    },
    "phone": {
        "type": "string",
        "description": "Primary phone number",
        "optional": True,
    },
    "mobile": {
        "type": "string",
        "description": "Mobile/cell phone number",
        "optional": True,
    },
    "company_name": {
        "type": "string",
        "description": "Company name if different from contact name",
        "optional": True,
    },
    "website": {
        "type": "string",
        "description": "Website URL",
        "optional": True,
    },
    "notes": {
        "type": "string",
        "description": "Notes about the customer",
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency used by this customer",
        "optional": True,
    },
    "payment_terms": {
        "type": "integer",
        "description": "Payment terms in days",
        "optional": True,
    },
    "billing_address": {
        "type": "object",
        "description": "Customer billing address details",
        "optional": True,
    },
    "shipping_address": {
        "type": "object",
        "description": "Customer shipping address details",
        "optional": True,
    },
    "contact_persons": {
        "type": "array",
        "description": "List of additional contact persons",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}

create_vendor.name = "create_vendor"  # type: ignore
create_vendor.description = "Create a new vendor in Zoho Books"  # type: ignore
create_vendor.parameters = {  # type: ignore
    "contact_name": {
        "type": "string", 
        "description": "Name of the vendor (required)",
    },
    "email": {
        "type": "string",
        "description": "Primary email address",
        "optional": True,
    },
    "phone": {
        "type": "string",
        "description": "Primary phone number",
        "optional": True,
    },
    "mobile": {
        "type": "string",
        "description": "Mobile/cell phone number",
        "optional": True,
    },
    "company_name": {
        "type": "string",
        "description": "Company name if different from contact name",
        "optional": True,
    },
    "website": {
        "type": "string",
        "description": "Website URL",
        "optional": True,
    },
    "notes": {
        "type": "string",
        "description": "Notes about the vendor",
        "optional": True,
    },
    "currency_id": {
        "type": "string",
        "description": "ID of the currency used by this vendor",
        "optional": True,
    },
    "payment_terms": {
        "type": "integer",
        "description": "Payment terms in days",
        "optional": True,
    },
    "billing_address": {
        "type": "object",
        "description": "Vendor billing address details",
        "optional": True,
    },
    "shipping_address": {
        "type": "object",
        "description": "Vendor shipping address details",
        "optional": True,
    },
    "contact_persons": {
        "type": "array",
        "description": "List of additional contact persons",
        "optional": True,
    },
    "custom_fields": {
        "type": "object",
        "description": "Custom field values",
        "optional": True,
    },
}

get_contact.name = "get_contact"  # type: ignore
get_contact.description = "Get a contact by ID from Zoho Books"  # type: ignore
get_contact.parameters = {  # type: ignore
    "contact_id": {
        "type": "string",
        "description": "ID of the contact to retrieve",
    },
}

delete_contact.name = "delete_contact"  # type: ignore
delete_contact.description = "Delete a contact from Zoho Books"  # type: ignore
delete_contact.parameters = {  # type: ignore
    "contact_id": {
        "type": "string",
        "description": "ID of the contact to delete",
    },
}