"""
Contact-related models for Zoho Books MCP Integration Server.

This module contains Pydantic models for contact operations (customers, vendors).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator

from .base import BaseResponse


class AddressInput(BaseModel):
    """Model for a contact address."""
    attention: Optional[str] = Field(None, description="Attention line for the address")
    address: Optional[str] = Field(None, description="Street address")
    street2: Optional[str] = Field(None, description="Second line of street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province name")
    zip: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Country name")
    phone: Optional[str] = Field(None, description="Phone number for this address")
    fax: Optional[str] = Field(None, description="Fax number for this address")


class ContactPersonInput(BaseModel):
    """Model for a contact person."""
    salutation: Optional[str] = Field(None, description="Salutation (e.g., Mr., Mrs., etc.)")
    first_name: str = Field(..., description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile: Optional[str] = Field(None, description="Mobile/cell number")
    is_primary_contact: Optional[bool] = Field(None, description="Whether this is the primary contact")


class BaseContactInput(BaseModel):
    """Base model for contact inputs (shared between customers and vendors)."""
    contact_name: str = Field(..., description="Name of the contact")
    company_name: Optional[str] = Field(None, description="Company name if different from contact name")
    website: Optional[str] = Field(None, description="Website URL")
    notes: Optional[str] = Field(None, description="Notes about the contact")

    # Contact details
    email: Optional[EmailStr] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Primary phone number")
    mobile: Optional[str] = Field(None, description="Mobile/cell phone number")

    # Addresses
    billing_address: Optional[AddressInput] = Field(None, description="Billing address")
    shipping_address: Optional[AddressInput] = Field(None, description="Shipping address")

    # Additional contacts
    contact_persons: Optional[List["ContactPersonInput"]] = Field(None, description="Additional contact persons")

    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom field values"
    )


class CustomerInput(BaseContactInput):
    """Model for creating or updating a customer."""
    contact_type: Literal["customer"] = Field("customer", description="Contact type, must be 'customer'")
    currency_id: Optional[str] = Field(None, description="ID of the currency used by this customer")
    payment_terms: Optional[int] = Field(None, description="Payment terms in days")
    payment_terms_label: Optional[str] = Field(None, description="Label for payment terms")
    credit_limit: Optional[float] = Field(None, description="Credit limit amount")
    tax_id: Optional[str] = Field(None, description="Tax ID or VAT number")

    @model_validator(mode='after')
    def check_required_fields(self) -> 'CustomerInput':
        """Ensure at least one of email or phone is provided."""
        if not self.email and not self.phone and not self.mobile:
            raise ValueError("At least one of email, phone, or mobile must be provided")
        return self


class VendorInput(BaseContactInput):
    """Model for creating or updating a vendor."""
    contact_type: Literal["vendor"] = Field("vendor", description="Contact type, must be 'vendor'")
    currency_id: Optional[str] = Field(None, description="ID of the currency used by this vendor")
    payment_terms: Optional[int] = Field(None, description="Payment terms in days")
    payment_terms_label: Optional[str] = Field(None, description="Label for payment terms")
    tax_id: Optional[str] = Field(None, description="Tax ID or VAT number")


class ContactDeleteInput(BaseModel):
    """Model for deleting a contact."""
    contact_id: str = Field(..., description="ID of the contact to delete")


class ContactResponse(BaseResponse):
    """Model for contact API responses."""
    contact: Optional[Dict] = Field(None, description="Contact details")


class ContactsListResponse(BaseResponse):
    """Model for list contacts API response."""
    contacts: Optional[List[Dict]] = Field(None, description="List of contacts")
