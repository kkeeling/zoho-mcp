"""
Zoho Books MCP Resources

This module provides read-only resources for accessing Zoho Books data
through the MCP protocol using URI patterns.
"""

import logging
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent

from zoho_mcp.tools.api import zoho_api_request_async
from zoho_mcp.tools import (
    list_contacts,
    get_contact,
    list_invoices,
    list_expenses,
    list_items,
)

logger = logging.getLogger(__name__)


def register_resources(mcp: FastMCP) -> None:
    """
    Register all MCP resources with the server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.resource("dashboard://summary")
    async def get_dashboard_summary() -> Resource:
        """Get business overview with key metrics."""
        logger.info("Fetching dashboard summary")
        
        try:
            # Fetch organization info
            org_response = await zoho_api_request_async("GET", "/organizations")
            organization = org_response.get("organizations", [{}])[0]
            
            # Get current date for filtering
            today = datetime.now()
            start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
            end_of_month = today.strftime("%Y-%m-%d")
            
            # Fetch key metrics in parallel
            # Get overdue invoices count
            overdue_params = {
                "filter_by": "overdue",
                "per_page": 1,
            }
            overdue_response = await zoho_api_request_async("GET", "/invoices", params=overdue_params)
            overdue_count = overdue_response.get("page_context", {}).get("total", 0)
            
            # Get unpaid invoices total
            unpaid_params = {
                "filter_by": "unpaid",
                "per_page": 1,
            }
            unpaid_response = await zoho_api_request_async("GET", "/invoices", params=unpaid_params)
            unpaid_count = unpaid_response.get("page_context", {}).get("total", 0)
            
            # Get this month's revenue
            revenue_params = {
                "filter_by": "paid",
                "date_start": start_of_month,
                "date_end": end_of_month,
                "per_page": 200,
            }
            revenue_response = await zoho_api_request_async("GET", "/invoices", params=revenue_params)
            invoices = revenue_response.get("invoices", [])
            monthly_revenue = sum(float(inv.get("total", 0)) for inv in invoices)
            
            # Build dashboard content
            content = f"""# Zoho Books Dashboard Summary

**Organization**: {organization.get('name', 'Unknown')}
**Date**: {today.strftime('%Y-%m-%d %H:%M')}

## Key Metrics

- **Overdue Invoices**: {overdue_count}
- **Unpaid Invoices**: {unpaid_count}
- **Monthly Revenue**: ${monthly_revenue:,.2f} ({today.strftime('%B %Y')})

## Quick Links
- View overdue invoices: invoice://overdue
- View unpaid invoices: invoice://unpaid
- Recent payments: payment://recent
"""
            
            return Resource(
                uri="dashboard://summary",
                name="Dashboard Summary",
                contents=[TextContent(text=content)],
                metadata={
                    "organization_id": organization.get("organization_id"),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching dashboard summary: {str(e)}")
            raise
    
    @mcp.resource("invoice://overdue")
    async def get_overdue_invoices() -> Resource:
        """Get list of overdue invoices."""
        logger.info("Fetching overdue invoices")
        
        try:
            # Fetch overdue invoices
            params = {
                "filter_by": "overdue",
                "sort_column": "due_date",
                "sort_order": "ascending",  # Will be converted to "A" by API layer
                "per_page": 100,
            }
            response = await zoho_api_request_async("GET", "/invoices", params=params)
            invoices = response.get("invoices", [])
            
            # Build content
            content = f"# Overdue Invoices\n\nTotal: {len(invoices)}\n\n"
            
            if invoices:
                content += "| Invoice # | Customer | Amount | Due Date | Days Overdue |\n"
                content += "|-----------|----------|--------|----------|-------------|\n"
                
                today = datetime.now().date()
                for inv in invoices:
                    due_date = datetime.strptime(inv["due_date"], "%Y-%m-%d").date()
                    days_overdue = (today - due_date).days
                    content += f"| {inv['invoice_number']} | {inv['customer_name']} | ${inv['balance']:,.2f} | {inv['due_date']} | {days_overdue} |\n"
            else:
                content += "*No overdue invoices found.*"
            
            return Resource(
                uri="invoice://overdue",
                name="Overdue Invoices",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(invoices),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching overdue invoices: {str(e)}")
            raise
    
    @mcp.resource("invoice://unpaid")
    async def get_unpaid_invoices() -> Resource:
        """Get list of unpaid invoices."""
        logger.info("Fetching unpaid invoices")
        
        try:
            # Fetch unpaid invoices
            params = {
                "filter_by": "unpaid",
                "sort_column": "date",
                "sort_order": "descending",  # Will be converted to "D" by API layer
                "per_page": 100,
            }
            response = await zoho_api_request_async("GET", "/invoices", params=params)
            invoices = response.get("invoices", [])
            
            # Build content
            content = f"# Unpaid Invoices\n\nTotal: {len(invoices)}\n\n"
            
            if invoices:
                content += "| Invoice # | Customer | Amount | Date | Due Date | Status |\n"
                content += "|-----------|----------|--------|------|----------|--------|\n"
                
                for inv in invoices:
                    status = inv.get("status", "unpaid")
                    if status == "overdue":
                        status = "**Overdue**"
                    content += f"| {inv['invoice_number']} | {inv['customer_name']} | ${inv['balance']:,.2f} | {inv['date']} | {inv['due_date']} | {status} |\n"
            else:
                content += "*No unpaid invoices found.*"
            
            return Resource(
                uri="invoice://unpaid",
                name="Unpaid Invoices",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(invoices),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching unpaid invoices: {str(e)}")
            raise
    
    @mcp.resource("payment://recent")
    async def get_recent_payments() -> Resource:
        """Get recent payments received."""
        logger.info("Fetching recent payments")
        
        try:
            # Get payments from the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "date_start": start_date.strftime("%Y-%m-%d"),
                "date_end": end_date.strftime("%Y-%m-%d"),
                "sort_column": "date",
                "sort_order": "descending",  # Will be converted to "D" by API layer
                "per_page": 50,
            }
            
            response = await zoho_api_request_async("GET", "/customerpayments", params=params)
            payments = response.get("customerpayments", [])
            
            # Build content
            content = f"# Recent Payments (Last 30 Days)\n\nTotal: {len(payments)}\n\n"
            
            if payments:
                content += "| Date | Customer | Amount | Reference # | Invoice # |\n"
                content += "|------|----------|--------|-------------|----------|\n"
                
                for payment in payments:
                    invoice_numbers = ", ".join([inv.get("invoice_number", "") for inv in payment.get("invoices", [])])
                    content += f"| {payment['date']} | {payment['customer_name']} | ${payment['amount']:,.2f} | {payment.get('reference_number', '-')} | {invoice_numbers} |\n"
                
                # Calculate total
                total_amount = sum(float(p.get("amount", 0)) for p in payments)
                content += f"\n**Total Received**: ${total_amount:,.2f}"
            else:
                content += "*No recent payments found.*"
            
            return Resource(
                uri="payment://recent",
                name="Recent Payments",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(payments),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching recent payments: {str(e)}")
            raise
    
    @mcp.resource("contact://list")
    async def get_contact_list() -> Resource:
        """Get list of contacts with basic information."""
        logger.info("Fetching contact list")
        
        try:
            # Use the existing list_contacts tool
            result = await list_contacts(page_size=100)
            contacts = result.get("contacts", [])
            
            # Build content
            content = f"# Contact List\n\nTotal: {result.get('total', len(contacts))}\n\n"
            
            if contacts:
                content += "| Name | Type | Email | Phone | Balance |\n"
                content += "|------|------|-------|-------|--------|\n"
                
                for contact in contacts:
                    contact_type = contact.get("contact_type", "unknown")
                    email = contact.get("email", "-")
                    phone = contact.get("phone", "-")
                    balance = contact.get("outstanding_receivable_amount", 0)
                    content += f"| {contact['contact_name']} | {contact_type} | {email} | {phone} | ${balance:,.2f} |\n"
            else:
                content += "*No contacts found.*"
            
            return Resource(
                uri="contact://list",
                name="Contact List",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(contacts),
                    "has_more": result.get("has_more_page", False),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching contact list: {str(e)}")
            raise
    
    @mcp.resource("contact://{contact_id}")
    async def get_contact_details(contact_id: str) -> Resource:
        """Get specific contact details."""
        logger.info(f"Fetching contact details for: {contact_id}")
        
        try:
            # Use the existing get_contact tool
            result = await get_contact(contact_id)
            contact = result.get("contact")
            
            if not contact:
                content = f"# Contact Not Found\n\nContact ID: {contact_id}"
            else:
                # Build detailed content
                content = f"""# Contact Details

**Name**: {contact.get('contact_name', 'Unknown')}
**Type**: {contact.get('contact_type', 'Unknown')}
**Status**: {contact.get('status', 'Unknown')}

## Contact Information
- **Email**: {contact.get('email', '-')}
- **Phone**: {contact.get('phone', '-')}
- **Mobile**: {contact.get('mobile', '-')}

## Financial Summary
- **Outstanding Receivable**: ${contact.get('outstanding_receivable_amount', 0):,.2f}
- **Outstanding Payable**: ${contact.get('outstanding_payable_amount', 0):,.2f}
- **Currency**: {contact.get('currency_code', 'USD')}

## Addresses"""
                
                # Add billing address
                billing = contact.get('billing_address', {})
                if billing:
                    content += f"""
### Billing Address
{billing.get('address', '')}
{billing.get('city', '')}, {billing.get('state', '')} {billing.get('zip', '')}
{billing.get('country', '')}"""
                
                # Add shipping address if different
                shipping = contact.get('shipping_address', {})
                if shipping and shipping != billing:
                    content += f"""

### Shipping Address
{shipping.get('address', '')}
{shipping.get('city', '')}, {shipping.get('state', '')} {shipping.get('zip', '')}
{shipping.get('country', '')}"""
            
            return Resource(
                uri=f"contact://{contact_id}",
                name=f"Contact: {contact.get('contact_name', contact_id) if contact else contact_id}",
                contents=[TextContent(text=content)],
                metadata={
                    "contact_id": contact_id,
                    "exists": contact is not None,
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching contact details: {str(e)}")
            raise
    
    @mcp.resource("invoice://list")
    async def get_invoice_list() -> Resource:
        """Get list of invoices with filters."""
        logger.info("Fetching invoice list")
        
        try:
            # Use the existing list_invoices tool
            result = await list_invoices(page_size=50)
            invoices = result.get("invoices", [])
            
            # Build content
            content = f"# Invoice List\n\nTotal: {result.get('total', len(invoices))}\n\n"
            
            if invoices:
                content += "| Invoice # | Customer | Date | Amount | Balance | Status |\n"
                content += "|-----------|----------|------|--------|---------|--------|\n"
                
                for inv in invoices:
                    status = inv.get("status", "unknown")
                    if status == "overdue":
                        status = "**Overdue**"
                    content += f"| {inv['invoice_number']} | {inv['customer_name']} | {inv['date']} | ${inv['total']:,.2f} | ${inv['balance']:,.2f} | {status} |\n"
            else:
                content += "*No invoices found.*"
            
            return Resource(
                uri="invoice://list",
                name="Invoice List",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(invoices),
                    "has_more": result.get("has_more_page", False),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching invoice list: {str(e)}")
            raise
    
    @mcp.resource("expense://list")
    async def get_expense_list() -> Resource:
        """Get list of expenses with filters."""
        logger.info("Fetching expense list")
        
        try:
            # Use the existing list_expenses tool
            result = await list_expenses(page_size=50)
            expenses = result.get("expenses", [])
            
            # Build content
            content = f"# Expense List\n\nTotal: {result.get('total', len(expenses))}\n\n"
            
            if expenses:
                content += "| Date | Description | Account | Amount | Status |\n"
                content += "|------|-------------|---------|--------|--------|\n"
                
                for expense in expenses:
                    description = expense.get("description", "-")[:50]  # Truncate long descriptions
                    content += f"| {expense['date']} | {description} | {expense.get('account_name', '-')} | ${expense['total']:,.2f} | {expense.get('status', '-')} |\n"
            else:
                content += "*No expenses found.*"
            
            return Resource(
                uri="expense://list",
                name="Expense List",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(expenses),
                    "has_more": result.get("has_more_page", False),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching expense list: {str(e)}")
            raise
    
    @mcp.resource("item://list")
    async def get_item_list() -> Resource:
        """Get list of products/services."""
        logger.info("Fetching item list")
        
        try:
            # Use the existing list_items tool
            result = await list_items(page_size=100)
            items = result.get("items", [])
            
            # Build content
            content = f"# Item List (Products & Services)\n\nTotal: {result.get('total', len(items))}\n\n"
            
            if items:
                content += "| Name | Type | SKU | Rate | Stock | Status |\n"
                content += "|------|------|-----|------|-------|--------|\n"
                
                for item in items:
                    item_type = item.get("product_type", "service")
                    sku = item.get("sku", "-")
                    stock = item.get("stock_on_hand", "-")
                    status = "Active" if item.get("status") == "active" else "Inactive"
                    content += f"| {item['name']} | {item_type} | {sku} | ${item['rate']:,.2f} | {stock} | {status} |\n"
            else:
                content += "*No items found.*"
            
            return Resource(
                uri="item://list",
                name="Item List",
                contents=[TextContent(text=content)],
                metadata={
                    "count": len(items),
                    "has_more": result.get("has_more_page", False),
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching item list: {str(e)}")
            raise
    
    @mcp.resource("report://cash_flow")
    async def get_cash_flow_report() -> Resource:
        """Get basic cash flow summary."""
        logger.info("Fetching cash flow report")
        
        try:
            # Get current month dates
            today = datetime.now()
            start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
            end_of_month = today.strftime("%Y-%m-%d")
            
            # Fetch income (paid invoices)
            income_params = {
                "filter_by": "paid",
                "date_start": start_of_month,
                "date_end": end_of_month,
                "per_page": 200,
            }
            income_response = await zoho_api_request_async("GET", "/invoices", params=income_params)
            paid_invoices = income_response.get("invoices", [])
            total_income = sum(float(inv.get("total", 0)) for inv in paid_invoices)
            
            # Fetch expenses
            expense_params = {
                "date.from": start_of_month,
                "date.to": end_of_month,
                "per_page": 200,
            }
            expense_response = await zoho_api_request_async("GET", "/expenses", params=expense_params)
            expenses = expense_response.get("expenses", [])
            total_expenses = sum(float(exp.get("total", 0)) for exp in expenses)
            
            # Calculate net cash flow
            net_cash_flow = total_income - total_expenses
            
            # Build content
            content = f"""# Cash Flow Summary - {today.strftime('%B %Y')}

## Summary
- **Total Income**: ${total_income:,.2f}
- **Total Expenses**: ${total_expenses:,.2f}
- **Net Cash Flow**: ${net_cash_flow:,.2f}

## Income Details
- **Paid Invoices**: {len(paid_invoices)}
- **Average Invoice**: ${total_income / len(paid_invoices):,.2f} (if any)

## Expense Details
- **Total Transactions**: {len(expenses)}
- **Average Expense**: ${total_expenses / len(expenses):,.2f} (if any)

## Cash Position
"""
            
            if net_cash_flow > 0:
                content += f"✅ **Positive cash flow** of ${net_cash_flow:,.2f}"
            elif net_cash_flow < 0:
                content += f"⚠️ **Negative cash flow** of ${abs(net_cash_flow):,.2f}"
            else:
                content += "➖ **Break-even** - Income equals expenses"
            
            return Resource(
                uri="report://cash_flow",
                name="Cash Flow Report",
                contents=[TextContent(text=content)],
                metadata={
                    "period": today.strftime('%B %Y'),
                    "start_date": start_of_month,
                    "end_date": end_of_month,
                    "last_updated": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            logger.error(f"Error fetching cash flow report: {str(e)}")
            raise