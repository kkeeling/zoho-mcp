# Integrating Zoho Books MCP Server with Claude Desktop

This guide explains how to integrate the Zoho MCP server with Claude Desktop.

## Prerequisites

Before setting up the integration, ensure you have:
- Python 3.9 or higher installed
- A Zoho Books account with API access
- Claude Desktop installed on your system

## Configuration

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "zoho": {
      "command": "python",
      "args": ["-m", "zoho_mcp"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id",
        "ZOHO_CLIENT_SECRET": "your_client_secret",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

## Setup Steps

1. Install the Zoho MCP package:
   ```bash
   pip install zoho-mcp
   ```

2. Configure your Zoho OAuth credentials in the environment variables

3. Restart Claude Desktop to load the new server

## Usage

Once configured, you can use Zoho tools directly in Claude Desktop conversations:

- Access contact management tools
- Create and manage invoices
- Track expenses
- Manage sales orders
- Handle inventory items

The server will automatically handle OAuth authentication when needed.