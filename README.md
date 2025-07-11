# Zoho Books MCP Server

Connect your Zoho Books account to AI assistants like Claude Desktop and Claude Code through the Model Context Protocol (MCP).

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/kkeeling/zoho-mcp?utm_source=oss&utm_medium=github&utm_campaign=kkeeling%2Fzoho-mcp&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

## Table of Contents

- [What is this?](#what-is-this)
- [Quick Start](#quick-start)
- [Available Features](#available-features)
- [Other MCP Clients](#other-mcp-clients)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Documentation](#documentation)
- [License](#license)

## What is this?

This MCP server enables AI assistants to interact with your Zoho Books data through natural language. You can ask Claude to create invoices, track expenses, manage contacts, and more - all through simple conversation.

### Example Interactions

- "Create an invoice for Acme Corp for $5,000 for consulting services"
- "Show me all overdue invoices"
- "Record an expense of $150 for office supplies"
- "Email last month's statement to all customers with outstanding balances"

## Quick Start

### 1. Prerequisites

- **Python 3.9+**
- **Zoho Books account** with API access
- **Claude Desktop** or another MCP-compatible client

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/kkeeling/zoho-mcp.git
cd zoho-mcp

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get Zoho API Credentials

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new client (choose "Server-based Applications")
3. Note your **Client ID** and **Client Secret**
4. Generate a **Refresh Token** (see [Zoho OAuth Guide](https://www.zoho.com/books/api/v3/oauth/#generate-refresh-token))
5. Get your **Organization ID** from Zoho Books settings

### 4. Configure the Server

Create your configuration file:

```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your credentials:

```env
ZOHO_CLIENT_ID="your_client_id_here"
ZOHO_CLIENT_SECRET="your_client_secret_here"
ZOHO_REFRESH_TOKEN="your_refresh_token_here"
ZOHO_ORGANIZATION_ID="your_organization_id_here"
ZOHO_REGION="US"  # Options: US, EU, IN, AU, UK, CA
```

### 5. Configure Claude Desktop

Add this server to your Claude Desktop configuration:

#### macOS
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "python",
      "args": [
        "/absolute/path/to/zoho-mcp/server.py",
        "--stdio"
      ],
      "cwd": "/absolute/path/to/zoho-mcp"
    }
  }
}
```

**Note:** Replace `/absolute/path/to/zoho-mcp` with the actual path where you cloned the repository.

#### Alternative: Using conda/venv

If using a virtual environment:

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/absolute/path/to/zoho-mcp/server.py",
        "--stdio"
      ],
      "cwd": "/absolute/path/to/zoho-mcp"
    }
  }
}
```

### 6. Restart Claude Desktop

After saving the configuration, restart Claude Desktop. You should see the Zoho Books tools available in the MCP tools menu.

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

## Other MCP Clients

While this guide focuses on Claude Desktop, the server also works with:

### Claude Code
Use the same configuration as Claude Desktop in your Claude Code settings.

### Cursor
```bash
# Start the server in HTTP mode
python server.py --port 8000

# Configure Cursor to connect to http://localhost:8000
```

### Custom Integrations
The server supports STDIO, HTTP/SSE, and WebSocket transports for custom MCP client implementations.

## Advanced Configuration

### Environment Variables

You can also set credentials via environment variables instead of the `.env` file:

```bash
export ZOHO_CLIENT_ID="your_client_id"
export ZOHO_CLIENT_SECRET="your_client_secret"
export ZOHO_REFRESH_TOKEN="your_refresh_token"
export ZOHO_ORGANIZATION_ID="your_organization_id"
export ZOHO_REGION="US"
```

### Transport Options

```bash
# STDIO (default, for Claude Desktop)
python server.py --stdio

# HTTP with SSE (for web clients)
python server.py --port 8000

# WebSocket
python server.py --ws --port 8001
```

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

## Acknowledgements

- [Zoho Books API](https://www.zoho.com/books/api/v3/) - Official API documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Anthropic](https://www.anthropic.com/) - Creator of Claude and MCP
