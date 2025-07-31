"""
Zoho Books MCP Resources

This module provides read-only resources for accessing Zoho Books data
through the MCP protocol using URI patterns.
"""

import logging
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

from zoho_mcp.tools.api import zoho_api_request_async
from zoho_mcp.tools import list_invoices

logger = logging.getLogger(__name__)


def register_resources(mcp: FastMCP) -> None:
    """
    Register all MCP resources with the server.
    
    Args:
        mcp: The FastMCP server instance
    """
    
    @mcp.resource("dashboard://summary", name="Dashboard Summary", title="Business Dashboard", description="Overview of key business metrics including revenue, expenses, and cash flow", mime_type="text/plain")
    async def get_dashboard_summary() -> str:
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
            
            # Fetch dashboard data
            dashboard_response = await zoho_api_request_async("GET", "/dashboard")
            dashboard = dashboard_response.get("dashboard", {})
            
            # Build summary content
            content = f"""# Zoho Books Dashboard Summary

**Organization**: {organization.get('name', 'N/A')}
**Currency**: {organization.get('currency_code', 'USD')}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Metrics

### Revenue (This Month)
- Total Income: {dashboard.get('total_revenue', 0):,.2f}
- Invoiced Amount: {dashboard.get('total_invoiced', 0):,.2f}
- Payments Received: {dashboard.get('total_received', 0):,.2f}

### Outstanding
- Total Receivables: {dashboard.get('total_receivables', 0):,.2f}
- Overdue Amount: {dashboard.get('total_overdue', 0):,.2f}
- Number of Overdue Invoices: {dashboard.get('overdue_invoices_count', 0)}

### Expenses (This Month)
- Total Expenses: {dashboard.get('total_expenses', 0):,.2f}
- Pending Bills: {dashboard.get('total_payables', 0):,.2f}

### Cash Flow
- Net Income: {dashboard.get('net_income', 0):,.2f}
- Cash Balance: {dashboard.get('cash_balance', 0):,.2f}

## Quick Actions
- View overdue invoices: invoice://overdue
- View unpaid invoices: invoice://unpaid
- Recent payments: payment://recent
"""
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching dashboard summary: {str(e)}")
            raise
    
    @mcp.resource("invoice://overdue", name="Overdue Invoices", title="Overdue Invoices List", description="List of all invoices that are past their due date", mime_type="text/plain")
    async def get_overdue_invoices() -> str:
        """Get list of overdue invoices."""
        logger.info("Fetching overdue invoices")
        
        try:
            # Fetch overdue invoices
            invoices_response = await list_invoices(
                status="overdue",
                sort_column="due_date",
                sort_order="ascending",
                page_size=50
            )
            
            invoices = invoices_response.get("invoices", [])
            
            # Build content
            content = f"""# Overdue Invoices

**Total Count**: {len(invoices)}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Invoice List

"""
            
            if not invoices:
                content += "No overdue invoices found. Great job! 🎉\n"
            else:
                total_overdue = sum(float(inv.get("balance", 0)) for inv in invoices)
                content += f"**Total Overdue Amount**: {total_overdue:,.2f}\n\n"
                
                for invoice in invoices:
                    days_overdue = invoice.get("overdue_days", 0)
                    content += f"""### Invoice #{invoice.get('invoice_number', 'N/A')}
- **Customer**: {invoice.get('customer_name', 'N/A')}
- **Amount Due**: {invoice.get('balance', 0):,.2f} {invoice.get('currency_code', 'USD')}
- **Due Date**: {invoice.get('due_date', 'N/A')}
- **Days Overdue**: {days_overdue}
- **Total Amount**: {invoice.get('total', 0):,.2f}
- **Status**: {invoice.get('status', 'N/A')}

"""
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching overdue invoices: {str(e)}")
            raise
    
    @mcp.resource("invoice://unpaid", name="Unpaid Invoices", title="Unpaid Invoices List", description="List of all invoices that haven't been paid yet", mime_type="text/plain")
    async def get_unpaid_invoices() -> str:
        """Get list of unpaid invoices."""
        logger.info("Fetching unpaid invoices")
        
        try:
            # Fetch unpaid invoices (includes overdue)
            invoices_response = await list_invoices(
                status="unpaid",
                sort_column="date",
                sort_order="descending",
                page_size=50
            )
            
            invoices = invoices_response.get("invoices", [])
            
            # Build content
            content = f"""# Unpaid Invoices

**Total Count**: {len(invoices)}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Invoice Summary

"""
            
            if not invoices:
                content += "No unpaid invoices found.\n"
            else:
                total_unpaid = sum(float(inv.get("balance", 0)) for inv in invoices)
                overdue_count = sum(1 for inv in invoices if inv.get("status") == "overdue")
                
                content += f"""**Total Unpaid Amount**: {total_unpaid:,.2f}
**Overdue Invoices**: {overdue_count}

## Invoice List

"""
                
                for invoice in invoices:
                    status_emoji = "🔴" if invoice.get("status") == "overdue" else "🟡"
                    content += f"""### {status_emoji} Invoice #{invoice.get('invoice_number', 'N/A')}
- **Customer**: {invoice.get('customer_name', 'N/A')}
- **Amount Due**: {invoice.get('balance', 0):,.2f} {invoice.get('currency_code', 'USD')}
- **Invoice Date**: {invoice.get('date', 'N/A')}
- **Due Date**: {invoice.get('due_date', 'N/A')}
- **Total Amount**: {invoice.get('total', 0):,.2f}
- **Status**: {invoice.get('status', 'N/A')}

"""
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching unpaid invoices: {str(e)}")
            raise
    
    @mcp.resource("payment://recent", name="Recent Payments", title="Recent Payments", description="List of payments received in the last 30 days", mime_type="text/plain")  
    async def get_recent_payments() -> str:
        """Get list of recent payments."""
        logger.info("Fetching recent payments")
        
        try:
            # Calculate date range for last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Fetch payments
            params = {
                "date_start": start_date.strftime("%Y-%m-%d"),
                "date_end": end_date.strftime("%Y-%m-%d"),
                "sort_column": "date",
                "sort_order": "descending",
            }
            
            payments_response = await zoho_api_request_async("GET", "/customerpayments", params=params)
            payments = payments_response.get("customerpayments", [])
            
            # Build content
            content = f"""# Recent Payments (Last 30 Days)

**Period**: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
**Total Payments**: {len(payments)}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Payment Summary

"""
            
            if not payments:
                content += "No payments received in the last 30 days.\n"
            else:
                total_received = sum(float(pmt.get("amount", 0)) for pmt in payments)
                content += f"**Total Received**: {total_received:,.2f}\n\n## Payment List\n\n"
                
                for payment in payments:
                    content += f"""### Payment #{payment.get('payment_number', 'N/A')}
- **Date**: {payment.get('date', 'N/A')}
- **Customer**: {payment.get('customer_name', 'N/A')}
- **Amount**: {payment.get('amount', 0):,.2f} {payment.get('currency_code', 'USD')}
- **Payment Mode**: {payment.get('payment_mode', 'N/A')}
- **Reference**: {payment.get('reference_number', 'N/A')}
- **Invoice(s)**: {', '.join([inv.get('invoice_number', '') for inv in payment.get('invoices', [])])}

"""
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching recent payments: {str(e)}")
            raise
