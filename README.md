# Zoho Books MCP Server

Connect your Zoho Books account to AI assistants like Claude Desktop through the Model Context Protocol (MCP).

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/kkeeling/zoho-mcp?utm_source=oss&utm_medium=github&utm_campaign=kkeeling%2Fzoho-mcp&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

## Table of Contents

- [What is this?](#what-is-this)
- [Quick Start](#quick-start)
- [Installation Options](#installation-options)
- [Available Features](#available-features)
- [Configuration Guide](#configuration-guide)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## What is this?

This MCP server enables AI assistants to interact with your Zoho Books data through natural language. You can ask Claude to create invoices, track expenses, manage contacts, and more - all through simple conversation.

### Example Interactions

- "Create an invoice for Acme Corp for $5,000 for consulting services"
- "Show me all overdue invoices"
- "Record an expense of $150 for office supplies"
- "Email last month's statement to all customers with outstanding balances"

## Quick Start

### Prerequisites

- **Zoho Books account** with API access
- **Claude Desktop** (latest version)
- **Python 3.9+** or **Docker** (depending on installation method)

### Get Your Zoho API Credentials

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new client:
   - **IMPORTANT**: Choose "Server-based Applications" (required for OAuth refresh tokens)
   - Add redirect URI: `http://localhost:8099/callback`
   - Select required scopes: `ZohoBooks.fullaccess.all` (or specific scopes you need)
3. Note your **Client ID** and **Client Secret**
4. Get your **Organization ID** from Zoho Books settings

**Note**: The MCP server handles OAuth token generation automatically - you don't need to manually generate refresh tokens.

## Installation Options

### Option 1: Using npx (Simplest - No Installation Required)

Configure Claude Desktop to use the server directly with npx:

**macOS/Linux:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "npx",
      "args": ["zoho-mcp-server"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id_here",
        "ZOHO_CLIENT_SECRET": "your_client_secret_here",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token_here",
        "ZOHO_ORGANIZATION_ID": "your_organization_id_here",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

That's it! No need to install Python or download anything manually.

### Option 2: Using Docker (No Python Required)

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "ZOHO_CLIENT_ID",
        "-e", "ZOHO_CLIENT_SECRET",
        "-e", "ZOHO_REFRESH_TOKEN",
        "-e", "ZOHO_ORGANIZATION_ID",
        "-e", "ZOHO_REGION",
        "ghcr.io/kkeeling/zoho-mcp-server:latest"
      ],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id_here",
        "ZOHO_CLIENT_SECRET": "your_client_secret_here",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token_here",
        "ZOHO_ORGANIZATION_ID": "your_organization_id_here",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

### Option 3: Local Development Setup

If you want to modify the server or run it locally:

1. Clone the repository:
```bash
git clone https://github.com/kkeeling/zoho-mcp.git
cd zoho-mcp
```

2. Create a virtual environment and install:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure Claude Desktop:
```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/path/to/zoho-mcp/server.py",
        "--stdio"
      ],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id_here",
        "ZOHO_CLIENT_SECRET": "your_client_secret_here",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token_here",
        "ZOHO_ORGANIZATION_ID": "your_organization_id_here",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

### After Configuration

After saving any configuration:
1. **Restart Claude Desktop** completely (not just reload)
2. Look for the 🔌 icon in the bottom-right of the Claude interface
3. Click it to see available Zoho Books tools

## Available Features

### 🛠️ Tools (15 Essential Operations)

#### Invoice Management
- **Create & Send Invoices** - Generate professional invoices and email them to customers
- **Record Payments** - Track customer payments and update invoice status
- **Send Reminders** - Automated payment reminders for overdue invoices
- **Void Invoices** - Cancel incorrect invoices with proper documentation

#### Contact Management  
- **Create Customers & Vendors** - Add new business contacts with complete details
- **Update Contact Info** - Modify contact information as needed
- **Email Statements** - Send account statements to customers
- **Delete Contacts** - Remove outdated contact records

#### Expense Tracking
- **Record Expenses** - Log business expenses with categories
- **Categorize Transactions** - Organize expenses for better reporting
- **Upload Receipts** - Attach digital receipts to expense records
- **Update Expense Details** - Modify expense information after creation

### 📊 Resources (Real-time Data Access)

- **Dashboard Overview** - Business metrics and KPIs at a glance
- **Invoice Status** - View overdue, unpaid, and recent invoices
- **Payment Tracking** - Monitor recent payments received
- **Cash Flow Reports** - Basic financial health indicators
- **Contact Lists** - Search and filter your business contacts
- **Expense Reports** - Track spending by category and date

### 🔄 Automated Workflows

- **Invoice Collection Workflow** - Complete cycle from invoice creation to payment
- **Monthly Invoicing** - Bulk invoice generation for recurring clients
- **Expense Tracking** - Streamlined expense recording and categorization

## Configuration Guide

### Region Settings

Set `ZOHO_REGION` based on your Zoho Books data center:

- `US` - United States (zoho.com)
- `EU` - Europe (zoho.eu)
- `IN` - India (zoho.in)
- `AU` - Australia (zoho.com.au)
- `JP` - Japan (zoho.jp)
- `UK` - United Kingdom (zoho.uk)
- `CA` - Canada (zoho.ca)

### Scopes and Permissions

The server requires the following Zoho Books API scopes:
- `ZohoBooks.contacts.ALL`
- `ZohoBooks.invoices.ALL`
- `ZohoBooks.expenses.ALL`
- `ZohoBooks.items.ALL`
- `ZohoBooks.salesorders.ALL`

### Other MCP Clients

#### VS Code / Cursor
For HTTP transport support:
```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "python3",
      "args": [
        "-m",
        "zoho_mcp",
        "--port",
        "8000"
      ],
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

## Troubleshooting

### Common Issues

**"Tools not showing in Claude Desktop"**
- Ensure the configuration file path is correct
- Check that Python path in config matches your installation
- Restart Claude Desktop after configuration changes

**"Authentication failed"**
- Verify your Zoho API credentials are correct
- Check that your refresh token hasn't expired
- Ensure you're using the correct region setting

**"Module not found errors"**
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again
- Check that the `cwd` in config points to the project root

For more detailed troubleshooting, see our [Troubleshooting Guide](docs/troubleshooting.md).

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zoho_mcp

# Run specific test file
pytest tests/test_invoice_tools.py
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [API Documentation](docs/api.md) - Detailed API reference
- [Common Operations](docs/examples/common-operations.md) - Example use cases
- [Architecture Overview](docs/architecture.md) - Technical design details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## How It Works

When you use `npx zoho-mcp-server`, it:
1. Downloads the appropriate pre-built binary for your platform
2. Runs it with your provided credentials
3. No Python, no dependencies, no installation needed!

## Future Improvements

We're working on making this server even easier to use:

- **Dynamic Credentials**: Input credentials through Claude Desktop UI (no environment variables needed)
- **One-Click Install**: Desktop extension (.dxt) for automatic setup
- **Auto-updates**: Built-in update notifications and seamless upgrades

Want to help? Check our [Contributing Guide](#contributing) or open an issue!

## Acknowledgements

- [Zoho Books API](https://www.zoho.com/books/api/v3/) - Official API documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Anthropic](https://www.anthropic.com/) - Creator of Claude and MCP
