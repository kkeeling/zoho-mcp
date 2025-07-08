# Zoho Books MCP Integration Server

A Model Control Protocol (MCP) server that exposes tools for interacting with Zoho Books. This server allows AI agents like Anthropic Claude Desktop and Cursor to access Zoho Books operations through natural language commands.

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/kkeeling/zoho-mcp?utm_source=oss&utm_medium=github&utm_campaign=kkeeling%2Fzoho-mcp&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Running the Server](#running-the-server)
  - [STDIO Mode](#stdio-mode-for-claude-desktop)
  - [HTTP/SSE Mode](#httpsse-mode-for-cursor)
  - [WebSocket Mode](#websocket-mode)
- [Available Tools](#available-tools)
- [Client Integration](#client-integration)
  - [Quick Start (Claude Desktop)](#quick-start-with-claude-desktop)
- [Documentation](#documentation)
- [Development](#development)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- Provides a comprehensive API for Zoho Books operations
- Implements the MCP protocol using the Python SDK
- Supports STDIO, HTTP/SSE, and WebSocket transports
- Uses Pydantic for input/output validation
- Handles authentication with Zoho's OAuth system
- Comprehensive error handling and logging
- Secure credential management

## Getting Started

### Prerequisites

- Python 3.9+
- Zoho Books account with API access
- Zoho API credentials (Client ID, Client Secret, Refresh Token)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/zoho-books-mcp-server.git
cd zoho-books-mcp-server
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Create a configuration file by copying the example:
```bash
cp config/.env.example config/.env
```

2. Edit `config/.env` with your Zoho Books API credentials:
```
ZOHO_CLIENT_ID="your_client_id"
ZOHO_CLIENT_SECRET="your_client_secret"
ZOHO_REFRESH_TOKEN="your_refresh_token"
ZOHO_ORGANIZATION_ID="your_organization_id"
ZOHO_REGION="US"  # Change according to your region (US, EU, IN, AU, etc.)
```

## Running the Server

### STDIO Mode (for Claude Desktop)

```bash
python server.py --stdio
```

### HTTP/SSE Mode (for Cursor)

```bash
python server.py --port 8000
```

### WebSocket Mode

```bash
python server.py --ws
```

## Available Tools

The server provides the following tools for interacting with Zoho Books:

### Contacts
- `list_contacts`: Fetch all contacts with optional filters
- `create_customer`: Create a new customer
- `create_vendor`: Create a new vendor
- `get_contact`: Retrieve a specific contact
- `delete_contact`: Delete a contact

### Invoices
- `list_invoices`: List invoices with pagination and optional filters
- `create_invoice`: Create a new invoice
- `get_invoice`: Retrieve a specific invoice
- `email_invoice`: Send an invoice by email
- `mark_invoice_as_sent`: Mark an invoice as sent
- `void_invoice`: Void an existing invoice

### Expenses
- `list_expenses`: List expense transactions
- `create_expense`: Record a new expense
- `get_expense`: Retrieve a specific expense
- `update_expense`: Update an existing expense

### Items
- `list_items`: Retrieve items (products/services)
- `create_item`: Create a new item
- `get_item`: Retrieve item details
- `update_item`: Update an existing item

### Sales Orders
- `list_sales_orders`: List sales orders with pagination and filters
- `create_sales_order`: Create a new sales order
- `get_sales_order`: Retrieve a specific sales order
- `update_sales_order`: Update an existing sales order
- `convert_to_invoice`: Convert a sales order to an invoice

## Client Integration

For detailed instructions on integrating the Zoho Books MCP server with different clients, see the following documentation:

- [Claude Desktop Integration Guide](docs/client-integration/claude-desktop.md)
- [Cursor Integration Guide](docs/client-integration/cursor.md)
- [Common Operations Examples](docs/examples/common-operations.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

### Quick Start with Claude Desktop

1. Install Claude Desktop from the [official website](https://claude.ai/desktop).

2. Set up the Zoho Books MCP server by following the [Installation](#installation) and [Configuration](#configuration) steps above.

3. Add the following configuration to Claude Desktop:
   - Open Claude Desktop, click on the Claude menu and select "Settings..."
   - Click on "Developer" in the sidebar and then "Edit Config"
   - Add the following configuration (adjust paths as needed):

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "python",
      "args": [
        "/path/to/zoho-books-mcp-server/server.py",
        "--stdio"
      ],
      "cwd": "/path/to/zoho-books-mcp-server"
    }
  }
}
```

4. Restart Claude Desktop and start interacting with Zoho Books through natural language!

## Documentation

- [Claude Desktop Integration](docs/client-integration/claude-desktop.md) - Detailed guide for setting up and using with Claude Desktop
- [Cursor Integration](docs/client-integration/cursor.md) - Instructions for integrating with Cursor
- [Common Operations](docs/examples/common-operations.md) - Examples of typical Zoho Books operations
- [Troubleshooting Guide](docs/troubleshooting.md) - Solutions for common issues

## Development

### Running Tests

```bash
pytest
```

### Running with Coverage

```bash
pytest --cov=zoho_mcp
```

## License

[MIT License](LICENSE)

## Acknowledgements

- [Zoho Books API Documentation](https://www.zoho.com/books/api/v3/)
- [MCP Protocol Specification](https://github.com/mcp-sdk/mcp-python-sdk)
- [Model Context Protocol](https://modelcontextprotocol.io/)
