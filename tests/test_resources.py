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
    with patch("zoho_mcp.tools.list_contacts") as mock_contacts, \
         patch("zoho_mcp.tools.get_contact") as mock_get_contact, \
         patch("zoho_mcp.tools.list_invoices") as mock_invoices, \
         patch("zoho_mcp.tools.list_expenses") as mock_expenses, \
         patch("zoho_mcp.tools.list_items") as mock_items:
        
        # Configure return values with keyword arguments
        async def mock_contacts_func(**kwargs):
            return {
                "contacts": [
                    {"contact_name": "Test Customer", "contact_type": "customer", "email": "test@example.com"},
                ],
                "total": 1,
                "has_more_page": False,
            }
        mock_contacts.side_effect = mock_contacts_func
        
        async def mock_get_contact_func(**kwargs):
            return {
                "contact": {
                    "contact_name": "Test Customer",
                    "contact_type": "customer",
                    "email": "test@example.com",
                    "phone": "123-456-7890",
                    "status": "active",
                }
            }
        mock_get_contact.side_effect = mock_get_contact_func
        
        async def mock_invoices_func(**kwargs):
            return {
                "invoices": [
                    {"invoice_number": "INV-001", "customer_name": "Test Customer", "total": 1000.00},
                ],
                "total": 1,
                "has_more_page": False,
            }
        mock_invoices.side_effect = mock_invoices_func
        
        async def mock_expenses_func(**kwargs):
            return {
                "expenses": [
                    {"date": "2023-01-01", "description": "Office supplies", "total": 50.00},
                ],
                "total": 1,
                "has_more_page": False,
            }
        mock_expenses.side_effect = mock_expenses_func
        
        async def mock_items_func(**kwargs):
            return {
                "items": [
                    {"name": "Test Item", "rate": 100.00, "product_type": "service"},
                ],
                "total": 1,
                "has_more_page": False,
            }
        mock_items.side_effect = mock_items_func
        
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
        assert mock_mcp.resource.call_count == 4  # We have 4 resources
        
        # Check the URIs that were registered
        registered_uris = [call[0][0] for call in mock_mcp.resource.call_args_list]
        expected_uris = [
            "dashboard://summary",
            "invoice://overdue",
            "invoice://unpaid",
            "payment://recent",
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
        def capture_dashboard(uri, **kwargs):
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
        assert isinstance(result, str)
        
        # Check content includes key metrics  
        assert "Test Org" in result
        assert "Dashboard Summary" in result
        assert "Organization" in result
    
    @pytest.mark.asyncio
    async def test_overdue_invoices_resource_direct(self):
        """Test the overdue invoices resource function directly."""
        # Mock the list_invoices function
        with patch("zoho_mcp.resources.list_invoices") as mock_list_invoices:
            mock_list_invoices.return_value = {
                "invoices": [
                    {
                        "invoice_number": "INV-001",
                        "customer_name": "Test Customer", 
                        "balance": 500.00,
                        "due_date": "2023-01-01",
                        "total": 500.00,
                        "status": "overdue",
                        "currency_code": "USD",
                        "overdue_days": 30
                    }
                ]
            }
            
            # Import and call the resource function directly
            from zoho_mcp.resources import register_resources
            mcp = MagicMock()
            
            # Capture the overdue invoices function
            overdue_func = None
            def capture_overdue(uri, **kwargs):
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
            assert isinstance(result, str)
            
            # Check content includes invoice details
            assert "INV-001" in result
            assert "Test Customer" in result
            assert "500.00" in result
    
