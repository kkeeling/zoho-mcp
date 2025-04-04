# Integrating Zoho Books MCP Server with Claude Desktop

This guide provides detailed instructions for integrating the Zoho Books MCP server with Claude Desktop, allowing you to interact with your Zoho Books account through natural language.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Setting Up the Zoho Books MCP Server](#setting-up-the-zoho-books-mcp-server)
  - [Configuring Claude Desktop](#configuring-claude-desktop)
  - [Configuration Options](#configuration-options)
- [Testing the Integration](#testing-the-integration)
- [Permissions and Security](#permissions-and-security)
- [Using Zoho Books Tools in Claude](#using-zoho-books-tools-in-claude)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have:

1. **Claude Desktop** installed on your computer ([Download Here](https://claude.ai/desktop))
2. **Python 3.9+** installed on your computer
3. **Zoho Books account** with API access enabled
4. **Zoho API credentials**:
   - Client ID
   - Client Secret
   - Refresh Token
   - Organization ID

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/zoho-books-mcp-server.git
cd zoho-books-mcp-server
```

### 2. Create a Virtual Environment

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Setting Up the Zoho Books MCP Server

1. Create a configuration file by copying the example:

```bash
cp config/.env.example config/.env
```

2. Edit the `.env` file with your Zoho Books API credentials:

```
ZOHO_CLIENT_ID="your_client_id"
ZOHO_CLIENT_SECRET="your_client_secret"
ZOHO_REFRESH_TOKEN="your_refresh_token"
ZOHO_ORGANIZATION_ID="your_organization_id"
ZOHO_REGION="US"  # Change according to your region (US, EU, IN, AU, etc.)
```

3. Test the server to make sure it starts correctly:

```bash
python server.py --stdio
```

You should see a message indicating the server is running. Press Ctrl+C to stop it for now.

### Configuring Claude Desktop

1. Open Claude Desktop on your computer

2. Access the settings by clicking on the Claude menu in the menu bar and selecting "Settings..." (not the settings inside the app window)

3. In the Settings window, click on "Developer" in the left sidebar

4. Click on "Edit Config" which will open the configuration file in your default text editor

5. Add the following configuration (adjust paths according to your setup):

```json
{
  "mcpServers": {
    "zoho-books": {
      "command": "python",
      "args": [
        "/absolute/path/to/zoho-books-mcp-server/server.py",
        "--stdio"
      ],
      "cwd": "/absolute/path/to/zoho-books-mcp-server",
      "env": {
        "PYTHONPATH": "/absolute/path/to/zoho-books-mcp-server"
      }
    }
  }
}
```

Replace `/absolute/path/to/zoho-books-mcp-server` with the actual path to your server directory.

### Configuration Options

Additional options you can add to the configuration:

- Add `"LOG_LEVEL": "DEBUG"` to the `env` object for more detailed logging
- Add `"LOG_FILE_PATH": "/path/to/logs/zoho-mcp.log"` to save logs to a file
- On Windows, use double backslashes or forward slashes for paths:
  ```
  "args": [
    "C:/path/to/zoho-books-mcp-server/server.py",
    "--stdio"
  ]
  ```

## Testing the Integration

1. After saving the configuration, restart Claude Desktop

2. You should see a "tools" (hammer) icon in the message input area at the bottom of the Claude Desktop window

3. Click on the tools icon to see available tools - you should see the Zoho Books tools listed

4. Test the integration by asking Claude a question about your Zoho Books data, such as:
   - "Show me a list of my recent invoices"
   - "Can you get a list of my contacts from Zoho Books?"
   - "Create a new customer in Zoho Books with the name 'Acme Corp'"

## Permissions and Security

When Claude attempts to use the Zoho Books tools, it will prompt you for permission. You can:

- Allow once (for that specific action)
- Always allow (for that type of action)
- Deny (prevent the action)

This ensures you maintain control over what Claude can do with your Zoho Books account.

## Using Zoho Books Tools in Claude

Here are some examples of how to interact with Zoho Books through Claude:

1. **Viewing Contacts**:
   - "Show me all my customer contacts"
   - "List vendors from Zoho Books"

2. **Managing Invoices**:
   - "Create a new invoice for customer ABC Corp"
   - "Show me unpaid invoices from last month"
   - "Get details for invoice INV-00001"

3. **Expense Management**:
   - "Record a new expense of $150 for office supplies"
   - "Show me expenses from this quarter"

4. **Item Management**:
   - "List all products in my inventory"
   - "Create a new service item called 'Consulting'"

5. **Sales Orders**:
   - "Create a sales order for customer XYZ Inc."
   - "Convert sales order SO-00001 to an invoice"

Claude will use natural language to communicate with you while using the appropriate Zoho Books API tools in the background.

## Troubleshooting

If you encounter issues with the integration, try these steps:

### Claude Desktop doesn't show the tools

1. Verify the configuration file is correctly formatted (valid JSON)
2. Make sure all paths in the configuration are absolute paths
3. Check that the `cwd` path exists and is correct
4. Restart Claude Desktop completely

### Claude shows an error when using tools

1. Check the logs by opening the Claude menu and selecting "Show Logs"
2. Verify your Zoho API credentials in the `.env` file
3. Ensure your Zoho API tokens have the necessary permissions
4. Make sure your virtual environment is activated when testing the server

### Server connection issues

If Claude cannot connect to the server:

1. Make sure the Python executable path is correct in your configuration
2. Verify that the server.py can be run manually with `python server.py --stdio`
3. Check your environment variables, especially `PYTHONPATH`

For more detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting.md).