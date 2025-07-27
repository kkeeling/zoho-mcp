"""
Zoho Books MCP Prompt Templates

This module provides guided workflow templates for common business operations
in Zoho Books through the MCP protocol.
"""

import logging

from mcp.server.fastmcp import FastMCP
from mcp.types import Prompt, PromptArgument

logger = logging.getLogger(__name__)


def register_prompts(mcp: FastMCP) -> None:
    """
    Register all MCP prompt templates with the server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.prompt("invoice_collection_workflow")
    async def invoice_collection_workflow() -> Prompt:
        """Complete invoice-to-payment cycle workflow."""
        logger.info("Creating invoice collection workflow prompt")
        
        return Prompt(
            name="invoice_collection_workflow",
            title="Invoice Collection Workflow",
            description="Complete workflow for creating, sending, and collecting payment for an invoice",
            arguments=[
                PromptArgument(
                    name="customer_info",
                    description="Customer name, ID, or indication of new customer",
                    required=True
                ),
                PromptArgument(
                    name="items_info",
                    description="List of items/services with quantities and rates",
                    required=True
                ),
                PromptArgument(
                    name="payment_terms",
                    description="Payment terms (e.g., Net 30, Due on receipt)",
                    required=False
                ),
                PromptArgument(
                    name="send_preference",
                    description="How to handle the invoice after creation (email, draft, mark as sent)",
                    required=True
                ),
                PromptArgument(
                    name="payment_reminder",
                    description="Whether to set up automatic payment reminders",
                    required=False
                )
            ]
        )
    
    @mcp.prompt("monthly_invoicing")
    async def monthly_invoicing() -> Prompt:
        """Bulk invoice creation for recurring clients."""
        logger.info("Creating monthly invoicing workflow prompt")
        
        return Prompt(
            name="monthly_invoicing",
            title="Monthly Bulk Invoicing",
            description="Efficient workflow for creating multiple invoices for recurring clients",
            arguments=[
                PromptArgument(
                    name="client_selection",
                    description="Which clients to invoice (all, specific list, or by category)",
                    required=True
                ),
                PromptArgument(
                    name="billing_period",
                    description="Period being billed for (current month, previous month, custom)",
                    required=True
                ),
                PromptArgument(
                    name="services_items",
                    description="Services/products to bill (same for all or varies by client)",
                    required=True
                ),
                PromptArgument(
                    name="payment_terms",
                    description="Payment terms to apply to all invoices",
                    required=False
                ),
                PromptArgument(
                    name="send_action",
                    description="What to do after creation (send all, schedule, keep as drafts)",
                    required=True
                )
            ]
        )
    
    @mcp.prompt("expense_tracking_workflow")
    async def expense_tracking_workflow() -> Prompt:
        """Record and categorize business expenses."""
        logger.info("Creating expense tracking workflow prompt")
        
        return Prompt(
            name="expense_tracking_workflow",
            title="Expense Tracking Workflow",
            description="Comprehensive workflow for recording, categorizing, and managing business expenses",
            arguments=[
                PromptArgument(
                    name="expense_count",
                    description="Number of expenses to record (single, multiple, bulk)",
                    required=True
                ),
                PromptArgument(
                    name="expense_date",
                    description="Date of the expense(s)",
                    required=True
                ),
                PromptArgument(
                    name="amount",
                    description="Amount of the expense",
                    required=True
                ),
                PromptArgument(
                    name="vendor",
                    description="Vendor or payee name",
                    required=True
                ),
                PromptArgument(
                    name="category",
                    description="Expense category (travel, meals, office supplies, etc.)",
                    required=True
                ),
                PromptArgument(
                    name="description",
                    description="Description of the expense",
                    required=False
                ),
                PromptArgument(
                    name="payment_method",
                    description="How the expense was paid",
                    required=False
                ),
                PromptArgument(
                    name="receipt_available",
                    description="Whether receipts are available to attach",
                    required=False
                ),
                PromptArgument(
                    name="tax_deductible",
                    description="Whether this is a tax-deductible expense",
                    required=False
                ),
                PromptArgument(
                    name="project_customer",
                    description="Associated project or customer for reimbursable expenses",
                    required=False
                )
            ]
        )
