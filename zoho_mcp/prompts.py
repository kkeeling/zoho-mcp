"""
Zoho Books MCP Prompt Templates

This module provides guided workflow templates for common business operations
in Zoho Books through the MCP protocol.
"""

import logging
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from mcp.types import Prompt, PromptMessage, TextContent

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
            description="Complete workflow for creating, sending, and collecting payment for an invoice",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="""I need help with the complete invoice collection process. Let's work through these steps:

1. First, let's identify the customer. Who is this invoice for?
2. What items or services are we invoicing?
3. Are there any special terms or discounts?
4. Should we send the invoice immediately?
5. How should we track payment?

Please guide me through each step of creating and managing this invoice until payment is received."""
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""I'll help you through the complete invoice collection workflow. Let me gather the necessary information step by step.

**Step 1: Customer Selection**
First, I need to identify the customer. You can either:
- Provide a customer name (I'll search for existing customers)
- Provide a customer ID if you know it
- Tell me if this is a new customer (I'll help create their profile)

Who would you like to invoice?"""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${customer_info}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Great! Now let's move to the invoice details.

**Step 2: Invoice Items**
What products or services are you invoicing for? Please provide:
- Item names or descriptions
- Quantities
- Rates (if custom pricing applies)
- Any applicable taxes

You can list multiple items, and I'll help format them properly."""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${items_info}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Perfect! Let me summarize what we have so far and check on additional details.

**Step 3: Invoice Terms & Conditions**
- Payment terms (e.g., Net 30, Due on receipt): ${payment_terms}
- Any special notes or terms?
- Discount if applicable?

**Step 4: Review and Send**
Once I create the invoice, would you like me to:
1. Email it immediately to the customer
2. Save as draft for your review
3. Mark as sent (if sending outside the system)

What's your preference?"""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${send_preference}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Excellent! I'll now:

1. ✅ Create the invoice with all the details provided
2. ✅ ${send_action}
3. 📅 Set up payment tracking

**Step 5: Payment Collection**
For payment follow-up, I can:
- Check payment status regularly
- Send payment reminders for overdue invoices
- Record payments when received
- Update the invoice status

Would you like me to set up automatic payment reminders? If yes, when should the first reminder be sent?"""
                    )
                )
            ],
            arguments=[
                {
                    "name": "customer_info",
                    "description": "Customer name, ID, or indication of new customer",
                    "required": True
                },
                {
                    "name": "items_info",
                    "description": "List of items/services with quantities and rates",
                    "required": True
                },
                {
                    "name": "payment_terms",
                    "description": "Payment terms (e.g., Net 30, Due on receipt)",
                    "required": False
                },
                {
                    "name": "send_preference",
                    "description": "How to handle the invoice after creation",
                    "required": True
                },
                {
                    "name": "send_action",
                    "description": "Action taken with the invoice (for the summary)",
                    "required": True
                }
            ]
        )
    
    @mcp.prompt("monthly_invoicing")
    async def monthly_invoicing() -> Prompt:
        """Bulk invoice creation for recurring clients."""
        logger.info("Creating monthly invoicing workflow prompt")
        
        return Prompt(
            name="monthly_invoicing",
            description="Efficient workflow for creating multiple invoices for recurring clients",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="""I need to create invoices for my recurring monthly clients. Please help me process these efficiently."""
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""I'll help you efficiently create invoices for all your recurring monthly clients. Let's set this up systematically.

**Monthly Bulk Invoicing Workflow**

First, let me understand your recurring billing:

1. **Client List**: Do you want to:
   - Invoice ALL active recurring clients
   - Invoice a specific list of clients
   - Invoice clients with a certain tag/category

2. **Billing Period**: 
   - Current month (${current_month})
   - Previous month
   - Custom period

3. **Standard Items**: Are the services/products the same for all clients or do they vary?

Please let me know your preferences, and I'll help process these invoices in bulk."""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${bulk_preferences}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Perfect! Based on your preferences, I'll prepare the bulk invoicing.

**Clients to Invoice:**
${client_list}

**Common Invoice Details:**
- Billing Period: ${billing_period}
- Due Date: ${due_date}
- Payment Terms: ${payment_terms}

**Services/Items to Include:**
${services_list}

Before I proceed, would you like to:
1. Review and modify any client-specific details
2. Apply a bulk discount
3. Add a common note/message to all invoices
4. Proceed with creating all invoices as configured

What would you prefer?"""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${final_preferences}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Excellent! I'm now creating the monthly invoices.

**Bulk Invoice Creation Progress:**
${progress_summary}

**Summary:**
- Total Invoices Created: ${total_count}
- Total Amount: ${total_amount}
- Average Invoice: ${average_amount}

**Next Steps:**
1. All invoices have been created in draft status
2. Would you like me to:
   - [ ] Send all invoices via email now
   - [ ] Schedule emails for a specific date/time
   - [ ] Keep as drafts for individual review
   - [ ] Generate a summary report

What would you like to do with these invoices?"""
                    )
                )
            ],
            arguments=[
                {
                    "name": "current_month",
                    "description": "Current month and year",
                    "required": True
                },
                {
                    "name": "bulk_preferences",
                    "description": "User's preferences for bulk invoicing",
                    "required": True
                },
                {
                    "name": "client_list",
                    "description": "List of clients to be invoiced",
                    "required": True
                },
                {
                    "name": "billing_period",
                    "description": "Period being billed for",
                    "required": True
                },
                {
                    "name": "due_date",
                    "description": "Due date for the invoices",
                    "required": True
                },
                {
                    "name": "payment_terms",
                    "description": "Payment terms applied",
                    "required": True
                },
                {
                    "name": "services_list",
                    "description": "List of services/items being billed",
                    "required": True
                },
                {
                    "name": "final_preferences",
                    "description": "User's final preferences before creation",
                    "required": True
                },
                {
                    "name": "progress_summary",
                    "description": "Progress of invoice creation",
                    "required": True
                },
                {
                    "name": "total_count",
                    "description": "Total number of invoices created",
                    "required": True
                },
                {
                    "name": "total_amount",
                    "description": "Total amount of all invoices",
                    "required": True
                },
                {
                    "name": "average_amount",
                    "description": "Average invoice amount",
                    "required": True
                }
            ]
        )
    
    @mcp.prompt("expense_tracking_workflow")
    async def expense_tracking_workflow() -> Prompt:
        """Record and categorize business expenses."""
        logger.info("Creating expense tracking workflow prompt")
        
        return Prompt(
            name="expense_tracking_workflow",
            description="Comprehensive workflow for recording, categorizing, and managing business expenses",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="""I need to track some business expenses. Can you help me record and categorize them properly?"""
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""I'll help you properly track and categorize your business expenses. This ensures accurate financial records and makes tax preparation easier.

**Expense Tracking Workflow**

Let's start with the basic information:

1. **Number of Expenses**: Are you recording:
   - A single expense
   - Multiple related expenses (e.g., from a business trip)
   - Bulk upload of various expenses

2. **Documentation**: Do you have:
   - Receipts to attach (digital/photos)
   - Credit card statements
   - Manual entry only

3. **Time Period**: Are these expenses from:
   - Today
   - This week
   - Specific dates

Please let me know what you'd like to record."""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${expense_details}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Great! Let me help you record these expenses properly. For each expense, I'll need:

**Expense #${expense_number}:**
- Date: ${expense_date}
- Amount: ${amount}
- Vendor/Payee: ${vendor}
- Description: ${description}
- Category: ${category}
- Payment Method: ${payment_method}

**Categories Available:**
- 🚗 Travel & Transportation
- 🍽️ Meals & Entertainment
- 💼 Office Supplies
- 💻 Software & Subscriptions
- 📞 Communications
- 🏢 Rent & Utilities
- 📚 Professional Development
- 🔧 Equipment & Tools
- 📄 Professional Services
- 🏥 Insurance
- 📢 Marketing & Advertising
- 💳 Bank Charges
- 📦 Other (specify)

Please provide the details for your expense(s)."""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${expense_info}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Perfect! I've recorded your expense(s). Here's a summary:

**Expenses Recorded:**
${expense_summary}

**Total Amount:** ${total_amount}

**Additional Options:**
1. **Billable**: Should any of these be marked as billable to a client?
2. **Receipt Upload**: Would you like to attach receipts to any expense?
3. **Recurring**: Are any of these recurring monthly expenses?
4. **Notes**: Any additional notes for tax purposes?

Would you like to:
- [ ] Add more expenses
- [ ] Upload receipts
- [ ] Mark specific expenses as billable
- [ ] View expense report for this period
- [ ] Complete and save all expenses

What would you like to do next?"""
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        text="${next_action}"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        text="""Excellent! ${action_response}

**Final Summary:**
- Expenses Recorded: ${final_count}
- Total Amount: ${final_total}
- Categories Used: ${categories_list}
- Receipts Attached: ${receipt_count}
- Billable Amount: ${billable_amount}

**Expense Tracking Tips:**
✅ Keep all receipts for tax documentation
✅ Categorize expenses immediately for accurate reporting
✅ Mark client-billable expenses promptly
✅ Review expenses monthly for budgeting
✅ Use consistent descriptions for similar expenses

Your expenses have been successfully recorded in Zoho Books. You can view detailed reports anytime through the expense reports section."""
                    )
                )
            ],
            arguments=[
                {
                    "name": "expense_details",
                    "description": "Initial expense recording preferences",
                    "required": True
                },
                {
                    "name": "expense_number",
                    "description": "Current expense number being recorded",
                    "required": True
                },
                {
                    "name": "expense_date",
                    "description": "Date of the expense",
                    "required": True
                },
                {
                    "name": "amount",
                    "description": "Expense amount",
                    "required": True
                },
                {
                    "name": "vendor",
                    "description": "Vendor or payee name",
                    "required": True
                },
                {
                    "name": "description",
                    "description": "Expense description",
                    "required": True
                },
                {
                    "name": "category",
                    "description": "Expense category",
                    "required": True
                },
                {
                    "name": "payment_method",
                    "description": "Payment method used",
                    "required": True
                },
                {
                    "name": "expense_info",
                    "description": "Detailed expense information provided",
                    "required": True
                },
                {
                    "name": "expense_summary",
                    "description": "Summary of recorded expenses",
                    "required": True
                },
                {
                    "name": "total_amount",
                    "description": "Total amount of expenses",
                    "required": True
                },
                {
                    "name": "next_action",
                    "description": "User's chosen next action",
                    "required": True
                },
                {
                    "name": "action_response",
                    "description": "Response to user's action",
                    "required": True
                },
                {
                    "name": "final_count",
                    "description": "Final count of expenses",
                    "required": True
                },
                {
                    "name": "final_total",
                    "description": "Final total amount",
                    "required": True
                },
                {
                    "name": "categories_list",
                    "description": "List of categories used",
                    "required": True
                },
                {
                    "name": "receipt_count",
                    "description": "Number of receipts attached",
                    "required": True
                },
                {
                    "name": "billable_amount",
                    "description": "Total billable amount",
                    "required": True
                }
            ]
        )
    
    logger.info("All prompt templates registered successfully")