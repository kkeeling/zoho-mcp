"""
Test suite for Zoho Books MCP prompt templates.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from mcp.server.fastmcp import FastMCP
from mcp.types import Prompt, PromptMessage, TextContent

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
        
        # Get the invoice collection workflow function
        workflow_func = None
        for prompt_name, func in mcp._prompts.items():
            if prompt_name == "invoice_collection_workflow":
                workflow_func = func
                break
        
        assert workflow_func is not None
        
        # Call the function
        result = await workflow_func()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "invoice_collection_workflow"
        assert result.description == "Complete workflow for creating, sending, and collecting payment for an invoice"
        
        # Check messages structure
        assert len(result.messages) == 8
        assert all(isinstance(msg, PromptMessage) for msg in result.messages)
        
        # Check that messages alternate between user and assistant
        for i, msg in enumerate(result.messages):
            expected_role = "user" if i % 2 == 0 else "assistant"
            assert msg.role == expected_role
        
        # Check arguments
        expected_args = [
            "customer_info",
            "items_info",
            "payment_terms",
            "send_preference",
            "send_action",
        ]
        assert len(result.arguments) == len(expected_args)
        for arg in result.arguments:
            assert arg["name"] in expected_args
    
    @pytest.mark.asyncio
    async def test_monthly_invoicing_prompt(self):
        """Test the monthly invoicing workflow prompt."""
        # Create and test the prompt
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Get the monthly invoicing function
        monthly_func = None
        for prompt_name, func in mcp._prompts.items():
            if prompt_name == "monthly_invoicing":
                monthly_func = func
                break
        
        assert monthly_func is not None
        
        # Call the function
        result = await monthly_func()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "monthly_invoicing"
        assert result.description == "Efficient workflow for creating multiple invoices for recurring clients"
        
        # Check messages
        assert len(result.messages) == 6
        
        # Check arguments include bulk operation parameters
        arg_names = [arg["name"] for arg in result.arguments]
        assert "current_month" in arg_names
        assert "bulk_preferences" in arg_names
        assert "client_list" in arg_names
        assert "total_count" in arg_names
        assert "total_amount" in arg_names
        assert "average_amount" in arg_names
        
        # Check content includes bulk operation guidance
        first_assistant_msg = result.messages[1]
        assert "Monthly Bulk Invoicing Workflow" in first_assistant_msg.content.text
        assert "Invoice ALL active recurring clients" in first_assistant_msg.content.text
    
    @pytest.mark.asyncio
    async def test_expense_tracking_workflow_prompt(self):
        """Test the expense tracking workflow prompt."""
        # Create and test the prompt
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Get the expense tracking function
        expense_func = None
        for prompt_name, func in mcp._prompts.items():
            if prompt_name == "expense_tracking_workflow":
                expense_func = func
                break
        
        assert expense_func is not None
        
        # Call the function
        result = await expense_func()
        
        # Verify the result
        assert isinstance(result, Prompt)
        assert result.name == "expense_tracking_workflow"
        assert result.description == "Comprehensive workflow for recording, categorizing, and managing business expenses"
        
        # Check messages
        assert len(result.messages) == 10
        
        # Check arguments include expense-specific fields
        arg_names = [arg["name"] for arg in result.arguments]
        assert "expense_details" in arg_names
        assert "amount" in arg_names
        assert "vendor" in arg_names
        assert "category" in arg_names
        assert "payment_method" in arg_names
        assert "receipt_count" in arg_names
        assert "billable_amount" in arg_names
        
        # Check content includes expense categories
        category_msg = result.messages[3]
        assert "Travel & Transportation" in category_msg.content.text
        assert "Meals & Entertainment" in category_msg.content.text
        assert "Office Supplies" in category_msg.content.text
        
        # Check final message includes expense tracking tips
        final_msg = result.messages[-1]
        assert "Expense Tracking Tips" in final_msg.content.text
        assert "Keep all receipts for tax documentation" in final_msg.content.text
    
    def test_prompt_arguments_structure(self):
        """Test that all prompt arguments have the correct structure."""
        # Create and test the prompts
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Check each prompt's arguments
        for prompt_name, func in mcp._prompts.items():
            # Call the function asynchronously
            prompt = asyncio.run(func())
            
            # Check each argument
            for arg in prompt.arguments:
                assert "name" in arg
                assert "description" in arg
                assert "required" in arg
                assert isinstance(arg["name"], str)
                assert isinstance(arg["description"], str)
                assert isinstance(arg["required"], bool)
    
    def test_prompt_messages_content(self):
        """Test that all prompt messages have valid TextContent."""
        # Create and test the prompts
        mcp = FastMCP(name="test", version="1.0.0")
        register_prompts(mcp)
        
        # Check each prompt's messages
        for prompt_name, func in mcp._prompts.items():
            # Call the function asynchronously
            prompt = asyncio.run(func())
            
            # Check each message
            for msg in prompt.messages:
                assert isinstance(msg, PromptMessage)
                assert msg.role in ["user", "assistant"]
                assert isinstance(msg.content, TextContent)
                assert isinstance(msg.content.text, str)
                assert len(msg.content.text) > 0