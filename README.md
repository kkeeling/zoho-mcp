# Zoho Books MCP Integration Server

A Model Control Protocol (MCP) server that exposes tools for interacting with Zoho Books. This server allows AI agents like Anthropic Claude Desktop and Cursor to access Zoho Books operations through natural language commands.

## Features

- Provides a comprehensive API for Zoho Books operations
- Implements the MCP protocol using the Python SDK
- Supports STDIO, HTTP/SSE, and WebSocket transports
- Uses Pydantic for input/output validation
- Handles authentication with Zoho's OAuth system

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

3. Configure your Zoho API credentials:
```bash
cp config/.env.example config/.env
```
Edit `config/.env` with your Zoho Books API credentials.

### Running the Server

#### STDIO Mode (for Claude Desktop)

```bash
python server.py --stdio
```

#### HTTP/SSE Mode (for Cursor)

```bash
python server.py --port 8000
```

#### WebSocket Mode

```bash
python server.py --ws
```

## Available Tools

The server provides the following tools for interacting with Zoho Books:

### Contacts
- `list_contacts`: Fetch all contacts with optional filters
- `create_customer`: Create a new customer
- `create_vendor`: Create a new vendor
- `delete_contact`: Delete a contact

### Invoices
- `list_invoices`: List invoices with pagination and optional filters
- `create_invoice`: Create a new invoice
- `get_invoice`: Retrieve a specific invoice

### Expenses
- `list_expenses`: List expense transactions
- `create_expense`: Record a new expense

### Items
- `list_items`: Retrieve items (products/services)
- `create_item`: Create a new item
- `get_item`: Retrieve item details

### Sales Orders
- `create_sales_order`: Create a new sales order
- `update_sales_order`: Update an existing sales order

## Client Integration

See the documentation in `docs/client-integration/` for detailed instructions on integrating with:
- Claude Desktop
- Cursor

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