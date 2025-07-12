"""
Test suite for Zoho Books MCP resources.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent

from zoho_mcp.resources import register_resources


@pytest.fixture
def mock_mcp():
    """Create a mock FastMCP server instance."""
    mcp = MagicMock(spec=FastMCP)
    mcp.resource = MagicMock()
    return mcp


@pytest.fixture
def mock_api_request():
    """Create a mock for zoho_api_request_async."""
    with patch("zoho_mcp.resources.zoho_api_request_async") as mock:
        yield mock


@pytest.fixture
def mock_tools():
    """Create mocks for the tools used by resources."""
    with patch("zoho_mcp.resources.list_contacts") as mock_contacts, \
         patch("zoho_mcp.resources.get_contact") as mock_get_contact, \
         patch("zoho_mcp.resources.list_invoices") as mock_invoices, \
         patch("zoho_mcp.resources.list_expenses") as mock_expenses, \
         patch("zoho_mcp.resources.list_items") as mock_items:
        
        # Configure return values
        mock_contacts.return_value = {
            "contacts": [
                {"contact_name": "Test Customer", "contact_type": "customer", "email": "test@example.com"},
            ],
            "total": 1,
            "has_more_page": False,
        }
        
        mock_get_contact.return_value = {
            "contact": {
                "contact_name": "Test Customer",
                "contact_type": "customer",
                "email": "test@example.com",
                "phone": "123-456-7890",
                "status": "active",
            }
        }
        
        mock_invoices.return_value = {
            "invoices": [
                {"invoice_number": "INV-001", "customer_name": "Test Customer", "total": 1000.00},
            ],
            "total": 1,
            "has_more_page": False,
        }
        
        mock_expenses.return_value = {
            "expenses": [
                {"date": "2023-01-01", "description": "Office supplies", "total": 50.00},
            ],
            "total": 1,
            "has_more_page": False,
        }
        
        mock_items.return_value = {
            "items": [
                {"name": "Test Item", "rate": 100.00, "product_type": "service"},
            ],
            "total": 1,
            "has_more_page": False,
        }
        
        yield {
            "list_contacts": mock_contacts,
            "get_contact": mock_get_contact,
            "list_invoices": mock_invoices,
            "list_expenses": mock_expenses,
            "list_items": mock_items,
        }


class TestResources:
    """Test suite for MCP resources."""
    
    def test_register_resources(self, mock_mcp):
        """Test that all resources are registered with the MCP server."""
        # Register resources
        register_resources(mock_mcp)
        
        # Check that resource decorator was called for each resource
        assert mock_mcp.resource.call_count == 10  # We have 10 resources
        
        # Check the URIs that were registered
        registered_uris = [call[0][0] for call in mock_mcp.resource.call_args_list]
        expected_uris = [
            "dashboard://summary",
            "invoice://overdue",
            "invoice://unpaid",
            "payment://recent",
            "contact://list",
            "contact://{contact_id}",
            "invoice://list",
            "expense://list",
            "item://list",
            "report://cash_flow",
        ]
        
        for uri in expected_uris:
            assert uri in registered_uris
    
    @pytest.mark.asyncio
    async def test_dashboard_summary_resource_direct(self, mock_api_request):
        """Test the dashboard summary resource function directly."""
        # Mock API responses
        mock_api_request.side_effect = [
            # Organizations response
            {"organizations": [{"name": "Test Org", "organization_id": "123"}]},
            # Overdue invoices response
            {"page_context": {"total": 5}},
            # Unpaid invoices response
            {"page_context": {"total": 10}},
            # Revenue response
            {"invoices": [{"total": 1000}, {"total": 2000}]},
        ]
        
        # Import and call the resource function directly
        from zoho_mcp.resources import register_resources
        mcp = MagicMock()
        
        # Capture the dashboard function when it's registered
        dashboard_func = None
        def capture_dashboard(uri):
            def decorator(func):
                nonlocal dashboard_func
                if uri == "dashboard://summary":
                    dashboard_func = func
                return func
            return decorator
        
        mcp.resource = capture_dashboard
        register_resources(mcp)
        
        # Call the captured function
        result = await dashboard_func()
        
        # Verify the result
        assert isinstance(result, Resource)
        assert result.uri == "dashboard://summary"
        assert result.name == "Dashboard Summary"
        assert len(result.contents) == 1
        assert isinstance(result.contents[0], TextContent)
        
        # Check content includes key metrics
        content = result.contents[0].text
        assert "Overdue Invoices: 5" in content
        assert "Unpaid Invoices: 10" in content
        assert "Monthly Revenue: $3,000.00" in content
    
    @pytest.mark.asyncio
    async def test_overdue_invoices_resource_direct(self, mock_api_request):
        """Test the overdue invoices resource function directly."""
        # Mock API response
        mock_api_request.return_value = {
            "invoices": [
                {
                    "invoice_number": "INV-001",
                    "customer_name": "Test Customer",
                    "balance": 500.00,
                    "due_date": "2023-01-01",
                }
            ]
        }
        
        # Import and call the resource function directly
        from zoho_mcp.resources import register_resources
        mcp = MagicMock()
        
        # Capture the overdue invoices function
        overdue_func = None
        def capture_overdue(uri):
            def decorator(func):
                nonlocal overdue_func
                if uri == "invoice://overdue":
                    overdue_func = func
                return func
            return decorator
        
        mcp.resource = capture_overdue
        register_resources(mcp)
        
        # Call the captured function
        result = await overdue_func()
        
        # Verify the result
        assert isinstance(result, Resource)
        assert result.uri == "invoice://overdue"
        assert result.name == "Overdue Invoices"
        
        # Check content includes invoice details
        content = result.contents[0].text
        assert "INV-001" in content
        assert "Test Customer" in content
        assert "$500.00" in content
    
    @pytest.mark.asyncio
    async def test_contact_details_resource_direct(self, mock_tools):
        """Test the contact details resource function directly."""
        # Import and call the resource function directly
        from zoho_mcp.resources import register_resources
        mcp = MagicMock()
        
        # Capture the contact details function
        contact_func = None
        def capture_contact(uri):
            def decorator(func):
                nonlocal contact_func
                if uri == "contact://{contact_id}":
                    contact_func = func
                return func
            return decorator
        
        mcp.resource = capture_contact
        register_resources(mcp)
        
        # Call the captured function
        result = await contact_func("contact_123")
        
        # Verify the result
        assert isinstance(result, Resource)
        assert result.uri == "contact://contact_123"
        assert result.name == "Contact: Test Customer"
        
        # Check that get_contact was called with the correct ID
        mock_tools["get_contact"].assert_called_once_with("contact_123")
        
        # Check content includes contact details
        content = result.contents[0].text
        assert "Test Customer" in content
        assert "test@example.com" in content
        assert "123-456-7890" in content
    
    @pytest.mark.asyncio  
    async def test_contact_list_resource_direct(self, mock_tools):
        """Test the contact list resource function directly."""
        # Import and call the resource function directly
        from zoho_mcp.resources import register_resources
        mcp = MagicMock()
        
        # Capture the contact list function
        list_func = None
        def capture_list(uri):
            def decorator(func):
                nonlocal list_func
                if uri == "contact://list":
                    list_func = func
                return func
            return decorator
        
        mcp.resource = capture_list
        register_resources(mcp)
        
        # Call the captured function
        result = await list_func()
        
        # Verify the result
        assert isinstance(result, Resource)
        assert result.uri == "contact://list"
        assert result.name == "Contact List"
        
        # Check that list_contacts was called
        mock_tools["list_contacts"].assert_called_once_with(page_size=100)
        
        # Check content includes contact details
        content = result.contents[0].text
        assert "Test Customer" in content
        assert "customer" in content
        assert "test@example.com" in content