# Zoho Books MCP Server

Connect your Zoho Books account to AI assistants like Claude Desktop through the Model Context Protocol (MCP).

## Quick Start

```bash
npx zoho-mcp-server
```

## Installation

Configure your MCP client (e.g., Claude Desktop) to use this server:

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

## Documentation

Full documentation: https://github.com/kkeeling/zoho-mcp

## License

MIT