"""
Unit tests for the contact management tools.

These tests validate the functionality of the contact management tools
using mocked API responses.
"""

import json
import pytest
from unittest.mock import patch

import zoho_mcp.tools.contacts as contact_tools
from zoho_mcp.tools.contacts import (
    list_contacts,
    create_customer,
    create_vendor,
    get_contact,
    delete_contact,
)
from zoho_mcp.tools.api import ZohoRequestError


# Mock API responses
MOCK_CONTACTS_LIST = {
    "contacts": [
        {
            "contact_id": "123456789",
            "contact_name": "Test Customer",
            "company_name": "Test Company",
            "contact_type": "customer",
            "status": "active",
            "email": "test@example.com",
        },
        {
            "contact_id": "987654321",
            "contact_name": "Test Vendor",
            "company_name": "Vendor Company",
            "contact_type": "vendor",
            "status": "active",
            "email": "vendor@example.com",
        },
    ],
    "page_context": {
        "page": 1,
        "per_page": 25,
        "has_more_page": False,
        "total": 2,
    },
}

MOCK_CONTACT_RESPONSE = {
    "contact": {
        "contact_id": "123456789",
        "contact_name": "Test Customer",
        "company_name": "Test Company",
        "contact_type": "customer",
        "status": "active",
        "email": "test@example.com",
    },
    "message": "Contact created successfully",
}

MOCK_DELETE_RESPONSE = {
    "message": "Contact deleted successfully",
}


@pytest.fixture
def mock_zoho_api():
    """Create a mock for the zoho_api_request function."""
    with patch("zoho_mcp.tools.contacts.zoho_api_request") as mock:
        yield mock


class TestContactTools:
    """Test suite for contact management tools."""
    
    def test_list_contacts_all(self, mock_zoho_api):
        """Test listing all contacts."""
        mock_zoho_api.return_value = MOCK_CONTACTS_LIST
        
        result = list_contacts()
        
        mock_zoho_api.assert_called_once()
        assert "contacts" in result
        assert len(result["contacts"]) == 2
        assert result["page"] == 1
        assert result["has_more_page"] is False
        assert result["total"] == 2
    
    def test_list_contacts_customers(self, mock_zoho_api):
        """Test listing only customer contacts."""
        # Mock response with only customers
        customer_response = {
            "contacts": [MOCK_CONTACTS_LIST["contacts"][0]],
            "page_context": {
                "page": 1,
                "per_page": 25,
                "has_more_page": False,
                "total": 1,
            },
        }
        mock_zoho_api.return_value = customer_response
        
        result = list_contacts(contact_type="customer")
        
        # Verify correct endpoint was called
        mock_zoho_api.assert_called_once()
        call_args = mock_zoho_api.call_args[0]
        assert "GET" in call_args
        assert "?contact_type=customer" in call_args[1]
        
        assert len(result["contacts"]) == 1
        assert result["contacts"][0]["contact_type"] == "customer"
    
    def test_list_contacts_with_pagination(self, mock_zoho_api):
        """Test listing contacts with pagination parameters."""
        mock_zoho_api.return_value = MOCK_CONTACTS_LIST
        
        result = list_contacts(page=2, page_size=10)
        
        mock_zoho_api.assert_called_once()
        call_kwargs = mock_zoho_api.call_args[1]
        assert call_kwargs["params"]["page"] == 2
        assert call_kwargs["params"]["per_page"] == 10
    
    def test_list_contacts_with_search(self, mock_zoho_api):
        """Test listing contacts with search text."""
        mock_zoho_api.return_value = {
            "contacts": [MOCK_CONTACTS_LIST["contacts"][0]],
            "page_context": {
                "page": 1,
                "per_page": 25,
                "has_more_page": False,
                "total": 1,
            },
        }
        
        result = list_contacts(search_text="Test Customer")
        
        mock_zoho_api.assert_called_once()
        call_kwargs = mock_zoho_api.call_args[1]
        assert call_kwargs["params"]["search_text"] == "Test Customer"
        assert len(result["contacts"]) == 1
    
    def test_list_contacts_error(self, mock_zoho_api):
        """Test error handling when listing contacts."""
        mock_zoho_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        with pytest.raises(ZohoRequestError):
            list_contacts()
    
    def test_create_customer_success(self, mock_zoho_api):
        """Test creating a customer successfully."""
        mock_zoho_api.return_value = MOCK_CONTACT_RESPONSE
        
        result = create_customer(
            contact_name="Test Customer",
            email="test@example.com",
            phone="1234567890",
            company_name="Test Company",
        )
        
        mock_zoho_api.assert_called_once()
        call_args = mock_zoho_api.call_args
        
        # Check that the right endpoint was called
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/contacts"
        
        # Check that the request body contains expected data
        request_data = call_args[1]["json"]
        assert request_data["contact_name"] == "Test Customer"
        assert request_data["email"] == "test@example.com"
        assert request_data["contact_type"] == "customer"
        
        # Check the response
        assert "contact" in result
        assert result["contact"]["contact_id"] == "123456789"
        assert "message" in result
    
    def test_create_customer_validation_error(self, mock_zoho_api):
        """Test validation error when creating a customer."""
        # Try to create a customer without required fields
        with pytest.raises(ValueError) as exc_info:
            create_customer()
        
        assert "Invalid customer data" in str(exc_info.value)
        mock_zoho_api.assert_not_called()
    
    def test_create_customer_api_error(self, mock_zoho_api):
        """Test API error when creating a customer."""
        mock_zoho_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        with pytest.raises(ZohoRequestError):
            create_customer(
                contact_name="Test Customer",
                email="test@example.com",
            )
    
    def test_create_vendor_success(self, mock_zoho_api):
        """Test creating a vendor successfully."""
        vendor_response = {
            "contact": {
                "contact_id": "987654321",
                "contact_name": "Test Vendor",
                "company_name": "Vendor Company",
                "contact_type": "vendor",
                "status": "active",
                "email": "vendor@example.com",
            },
            "message": "Vendor created successfully",
        }
        mock_zoho_api.return_value = vendor_response
        
        result = create_vendor(
            contact_name="Test Vendor",
            email="vendor@example.com",
            phone="9876543210",
            company_name="Vendor Company",
        )
        
        mock_zoho_api.assert_called_once()
        call_args = mock_zoho_api.call_args
        
        # Check that the right endpoint was called
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/contacts"
        
        # Check that the request body contains expected data
        request_data = call_args[1]["json"]
        assert request_data["contact_name"] == "Test Vendor"
        assert request_data["email"] == "vendor@example.com"
        assert request_data["contact_type"] == "vendor"
        
        # Check the response
        assert "contact" in result
        assert result["contact"]["contact_id"] == "987654321"
        assert "message" in result
    
    def test_get_contact_success(self, mock_zoho_api):
        """Test getting a contact successfully."""
        mock_zoho_api.return_value = MOCK_CONTACT_RESPONSE
        
        result = get_contact(contact_id="123456789")
        
        mock_zoho_api.assert_called_once()
        call_args = mock_zoho_api.call_args
        
        # Check that the right endpoint was called
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "/contacts/123456789"
        
        # Check the response
        assert "contact" in result
        assert result["contact"]["contact_id"] == "123456789"
        assert "message" in result
    
    def test_get_contact_not_found(self, mock_zoho_api):
        """Test getting a contact that doesn't exist."""
        mock_zoho_api.return_value = {"message": "Contact not found"}
        
        result = get_contact(contact_id="nonexistent")
        
        mock_zoho_api.assert_called_once()
        assert result["contact"] is None
        assert "Contact not found" in result["message"]
    
    def test_get_contact_error(self, mock_zoho_api):
        """Test error handling when getting a contact."""
        mock_zoho_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        with pytest.raises(ZohoRequestError):
            get_contact(contact_id="123456789")
    
    def test_delete_contact_success(self, mock_zoho_api):
        """Test deleting a contact successfully."""
        mock_zoho_api.return_value = MOCK_DELETE_RESPONSE
        
        result = delete_contact(contact_id="123456789")
        
        mock_zoho_api.assert_called_once()
        call_args = mock_zoho_api.call_args
        
        # Check that the right endpoint was called
        assert call_args[0][0] == "DELETE"
        assert call_args[0][1] == "/contacts/123456789"
        
        # Check the response
        assert result["success"] is True
        assert "Contact deleted successfully" in result["message"]
        assert result["contact_id"] == "123456789"
    
    def test_delete_contact_error(self, mock_zoho_api):
        """Test error handling when deleting a contact."""
        mock_zoho_api.side_effect = ZohoRequestError(400, "Bad Request")
        
        with pytest.raises(ZohoRequestError):
            delete_contact(contact_id="123456789")