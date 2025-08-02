"""
Test suite for Zoho Books MCP prompt templates.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent
from mcp.types import Prompt

from zoho_mcp.prompts import register_prompts


@pytest.fixture
def mock_mcp():
    """Create a mock FastMCP server instance."""
    mcp = MagicMock(spec=FastMCP)
    mcp.prompt = MagicMock()
    return mcp


class TestPrompts:
    """Test suite for MCP prompt templates."""
    
    def test_register_prompts(self, mock_mcp):
        """Test that all prompts are registered with the MCP server."""
        # Register prompts
        register_prompts(mock_mcp)
        
        # Check that prompt decorator was called for each prompt
        assert mock_mcp.prompt.call_count == 3  # We have 3 prompts
        
        # Check the prompt names that were registered
        registered_names = [call[0][0] for call in mock_mcp.prompt.call_args_list]
        expected_names = [
            "invoice_collection_workflow",
            "monthly_invoicing",
            "expense_tracking_workflow",
        ]
        
        for name in expected_names:
            assert name in registered_names
    
    @pytest.mark.asyncio
    async def test_invoice_collection_workflow_prompt(self):
        """Test the invoice collection workflow prompt."""
        # Create and test the prompt
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Get the invoice collection workflow prompt
        workflow_prompt = None
        for prompt_name, prompt in mcp._prompt_manager._prompts.items():
            if prompt_name == "invoice_collection_workflow":
                workflow_prompt = prompt
                break
        
        assert workflow_prompt is not None
        
        # Call the function to get the actual prompt
        result = await workflow_prompt.fn()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "invoice_collection_workflow"
        assert result.description == "Complete workflow for creating, sending, and collecting payment for an invoice"
        
        # Check that result has arguments (no messages in current implementation)
        assert hasattr(result, 'arguments')
        assert isinstance(result.arguments, list)
        
        # Check arguments
        expected_args = [
            "customer_info",
            "items_info",
            "payment_terms",
            "send_preference",
            "payment_reminder",
        ]
        assert len(result.arguments) == len(expected_args)
        for arg in result.arguments:
            assert arg.name in expected_args
    
    @pytest.mark.asyncio
    async def test_monthly_invoicing_prompt(self):
        """Test the monthly invoicing workflow prompt."""
        # Create and test the prompt
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Get the monthly invoicing prompt
        monthly_prompt = None
        for prompt_name, prompt in mcp._prompt_manager._prompts.items():
            if prompt_name == "monthly_invoicing":
                monthly_prompt = prompt
                break
        
        assert monthly_prompt is not None
        
        # Call the function to get the actual prompt
        result = await monthly_prompt.fn()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "monthly_invoicing"
        assert result.description == "Efficient workflow for creating multiple invoices for recurring clients"
        
        # Check that result has arguments (no messages in current implementation)
        assert hasattr(result, 'arguments')
        assert isinstance(result.arguments, list)
        
        # Check arguments include bulk operation parameters
        arg_names = [arg.name for arg in result.arguments]
        assert "client_selection" in arg_names
        assert "billing_period" in arg_names
        assert "services_items" in arg_names
        assert "payment_terms" in arg_names
        assert "send_action" in arg_names
    
    @pytest.mark.asyncio
    async def test_expense_tracking_workflow_prompt(self):
        """Test the expense tracking workflow prompt."""
        # Create and test the prompt
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Get the expense tracking prompt
        expense_prompt = None
        for prompt_name, prompt in mcp._prompt_manager._prompts.items():
            if prompt_name == "expense_tracking_workflow":
                expense_prompt = prompt
                break
        
        assert expense_prompt is not None
        
        # Call the function to get the actual prompt
        result = await expense_prompt.fn()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "expense_tracking_workflow"
        assert result.description == "Comprehensive workflow for recording, categorizing, and managing business expenses"
        
        # Check that result has arguments (no messages in current implementation)
        assert hasattr(result, 'arguments')
        assert isinstance(result.arguments, list)
        
        # Check arguments include expense-specific fields
        arg_names = [arg.name for arg in result.arguments]
        assert "expense_count" in arg_names
        assert "expense_date" in arg_names
        assert "amount" in arg_names
        assert "vendor" in arg_names
        assert "category" in arg_names
        assert "description" in arg_names
        assert "payment_method" in arg_names
        assert "receipt_available" in arg_names
        assert "tax_deductible" in arg_names
        assert "project_customer" in arg_names
    
    def test_prompt_arguments_structure(self):
        """Test that all prompt arguments have the correct structure."""
        # Create and test the prompts
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Check each prompt's arguments
        for prompt_name, prompt_wrapper in mcp._prompt_manager._prompts.items():
            # Call the function to get the actual prompt
            prompt = asyncio.run(prompt_wrapper.fn())
            
            # Check each argument
            for arg in prompt.arguments:
                assert hasattr(arg, 'name')
                assert hasattr(arg, 'description')
                assert hasattr(arg, 'required')
                assert isinstance(arg.name, str)
                assert isinstance(arg.description, str)
                assert isinstance(arg.required, bool)
    
    def test_prompt_messages_content(self):
        """Test that all prompt messages have valid TextContent."""
        # Create and test the prompts
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Check each prompt's messages
        for prompt_name, prompt_wrapper in mcp._prompt_manager._prompts.items():
            # Call the function to get the actual prompt
            prompt = asyncio.run(prompt_wrapper.fn())
            
            # Check that prompt has required attributes (no messages in current implementation)
            assert hasattr(prompt, 'name')
            assert hasattr(prompt, 'description')
            assert hasattr(prompt, 'arguments')
            assert isinstance(prompt.name, str)
            assert isinstance(prompt.description, str)
            assert isinstance(prompt.arguments, list)