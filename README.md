# Zoho Books MCP Server

Connect your Zoho Books account to AI assistants like Claude Desktop through the Model Context Protocol (MCP).

## Quick Start

### 1. Get Zoho API Credentials

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a "Server-based Application"
3. Add redirect URI: `http://localhost:8099/callback`
4. Select scope: `ZohoBooks.fullaccess.all`
5. Save your Client ID, Client Secret, and Organization ID

### 2. Install via uvx

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "uvx",
      "args": ["zoho-books-mcp"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id",
        "ZOHO_CLIENT_SECRET": "your_client_secret",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token",
        "ZOHO_ORGANIZATION_ID": "your_organization_id",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

To get a refresh token: `uvx zoho-books-mcp --setup-oauth`

### 3. Restart Claude Desktop

Look for the 🔌 icon to verify connection.

## Local Development

```bash
# Clone and setup
git clone https://github.com/kkeeling/zoho-mcp.git
cd zoho-mcp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest

# Run server
python server.py
```

For local development in Claude Desktop:
```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/zoho-mcp/server.py"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id",
        "ZOHO_CLIENT_SECRET": "your_client_secret",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token",
        "ZOHO_ORGANIZATION_ID": "your_organization_id",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

## Available Features

### Tools

**Invoices**: create_invoice, email_invoice, record_payment, send_payment_reminder, void_invoice, list_invoices, get_invoice, mark_invoice_as_sent

**Contacts**: create_customer, create_vendor, update_contact, delete_contact, email_statement, list_contacts, get_contact

**Expenses**: create_expense, update_expense, categorize_expense, upload_receipt, list_expenses, get_expense

**Items**: create_item, update_item, list_items, get_item

**Sales Orders**: create_sales_order, update_sales_order, convert_to_invoice, list_sales_orders, get_sales_order

### Resources

- **dashboard://summary** - Business metrics overview
- **invoice://overdue** - Overdue invoices list
- **invoice://unpaid** - Unpaid invoices
- **payment://recent** - Recent payments
- **contact://list** - All contacts
- **expenses://summary** - Expense overview

### Prompts

- **invoice_collection_workflow** - Complete invoice-to-payment cycle
- **monthly_invoicing** - Bulk invoice creation
- **expense_tracking_workflow** - Expense recording and categorization

## Configuration

### Regions
- US (zoho.com), EU (zoho.eu), IN (zoho.in), AU (zoho.com.au), JP (zoho.jp), UK (zoho.uk), CA (zoho.ca)

### Troubleshooting
- **Tools not showing**: Restart Claude Desktop completely
- **Auth errors**: Regenerate refresh token with `uvx zoho-books-mcp --setup-oauth`
- **Module errors**: Ensure virtual environment is activated

## Development & Releases

### Creating a Release

To publish a new version to PyPI and create a GitHub release:

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create and push a git tag**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. **Follow manual publishing steps** in `PUBLISHING.md` to build, upload to PyPI, and create GitHub release

### Prerequisites for Publishing
- PyPI account with API token
- GitHub CLI (`gh`) installed and authenticated
- Build tools: `pip install --upgrade pip build twine`

## License

MIT License - see [LICENSE](LICENSE) file for details.