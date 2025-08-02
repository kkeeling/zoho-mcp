# Integrating Zoho Books MCP Server with Cursor

This guide explains how to integrate the Zoho MCP server with Cursor IDE.

## HTTP/SSE Mode

For HTTP/SSE mode configuration, add the following to your Cursor settings:

```json
{
  "mcpServers": {
    "zoho": {
      "command": "python",
      "args": ["-m", "zoho_mcp", "--transport", "sse"],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id",
        "ZOHO_CLIENT_SECRET": "your_client_secret",
        "ZOHO_REGION": "US"
      }
    }
  }
}
```

## STDIO Mode

For STDIO mode configuration, use:

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

## Configuration

Add the following to your Cursor MCP configuration:

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

1. Install the Zoho MCP package in your project environment:
   ```bash
   pip install zoho-mcp
   ```

2. Configure your Zoho OAuth credentials

3. Restart Cursor to load the MCP server

## Development Workflow

With the Zoho MCP server integrated in Cursor, you can:

- Query Zoho data directly from the IDE
- Generate code that interacts with Zoho APIs
- Test Zoho integrations within your development environment
- Access real-time Zoho data for development and testing

The server provides seamless access to Zoho's business management tools through the MCP protocol.