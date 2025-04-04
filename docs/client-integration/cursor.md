# Integrating Zoho Books MCP Server with Cursor

This guide provides detailed instructions for integrating the Zoho Books MCP server with Cursor, allowing you to interact with your Zoho Books account through your code editor.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Setting Up the Zoho Books MCP Server](#setting-up-the-zoho-books-mcp-server)
  - [HTTP/SSE Mode Configuration](#httpsse-mode-configuration)
  - [STDIO Mode Configuration](#stdio-mode-configuration)
  - [Configuration Options](#configuration-options)
- [Testing the Integration](#testing-the-integration)
- [Using Zoho Books Tools in Cursor](#using-zoho-books-tools-in-cursor)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have:

1. **Cursor** installed on your computer ([Download Here](https://cursor.sh/))
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

### HTTP/SSE Mode Configuration

Cursor typically uses HTTP/SSE mode for connecting to MCP servers. This is the recommended approach.

1. Start the server in HTTP mode:

```bash
python server.py --port 8000
```

2. Configure Cursor to connect to the Zoho Books MCP server:
   - Open Cursor
   - Go to Settings (gear icon in the bottom left)
   - Select "AI" in the sidebar
   - Scroll down to "Model Context Protocol (MCP)" section
   - Click "Add MCP Server"
   - Fill in the following details:
     - Name: `Zoho Books`
     - URL: `http://localhost:8000`
     - Type: `HTTP`
   - Click "Add Server"

### STDIO Mode Configuration

Alternatively, you can configure Cursor to use STDIO mode, though HTTP mode is generally preferred for Cursor.

1. Create a start script (e.g., `start-zoho-mcp.sh` on macOS/Linux or `start-zoho-mcp.bat` on Windows):

For macOS/Linux:
```bash
#!/bin/bash
cd /absolute/path/to/zoho-books-mcp-server
source venv/bin/activate
python server.py --stdio
```

For Windows:
```batch
@echo off
cd C:\path\to\zoho-books-mcp-server
call venv\Scripts\activate
python server.py --stdio
```

2. Make the script executable (on macOS/Linux):
```bash
chmod +x start-zoho-mcp.sh
```

3. Configure Cursor to connect to the Zoho Books MCP server in STDIO mode:
   - Open Cursor
   - Go to Settings (gear icon)
   - Select "AI" in the sidebar
   - Scroll down to "Model Context Protocol (MCP)" section
   - Click "Add MCP Server"
   - Fill in the following details:
     - Name: `Zoho Books`
     - Command: `/absolute/path/to/start-zoho-mcp.sh` (or `C:\path\to\start-zoho-mcp.bat` on Windows)
     - Type: `STDIO`
   - Click "Add Server"

### Configuration Options

For HTTP mode, you can specify additional options:

- Set a custom host with `--host` (default is 127.0.0.1)
- Enable SSL with environment variables in your `.env` file:
  ```
  ENABLE_SECURE_TRANSPORT=True
  SSL_CERT_PATH=/path/to/cert.pem
  SSL_KEY_PATH=/path/to/key.pem
  ```
  Then access via `https://localhost:8000`

- Change logging level with `--log-level DEBUG` for more detailed logs

## Testing the Integration

1. Ensure the Zoho Books MCP server is running
2. Open Cursor
3. Check that the Zoho Books MCP server appears in the AI tools list
4. Test the integration by asking Cursor a question about your Zoho Books data, such as:
   - "Show me a list of my recent invoices"
   - "Can you get a list of my contacts from Zoho Books?"
   - "Create a new customer in Zoho Books with the name 'Acme Corp'"

## Using Zoho Books Tools in Cursor

Here are some examples of how to interact with Zoho Books through Cursor:

1. **Analyzing Financial Data**:
   - "Analyze my invoice data from the last quarter and summarize revenue trends"
   - "Compare expenses from this month to the previous month"

2. **Code Generation with Zoho Books Data**:
   - "Generate a Python script to export my Zoho Books customers to CSV"
   - "Write a JavaScript function to calculate invoice totals from this data"

3. **Data Visualization**:
   - "Create a chart showing my monthly revenue based on invoice data"
   - "Generate code for a dashboard to visualize my Zoho Books financial data"

4. **Document Generation**:
   - "Draft a financial report based on my current Zoho Books data"
   - "Generate a markdown summary of my top customers with their purchase history"

5. **Data Analysis Workflows**:
   - "Help me create a Python notebook to analyze my sales data from Zoho Books"
   - "Build a data processing pipeline to track expense categories over time"

Cursor will use natural language to communicate with you while using the appropriate Zoho Books API tools in the background.

## Troubleshooting

If you encounter issues with the integration, try these steps:

### HTTP/SSE Mode Issues

1. Verify the server is running with `python server.py --port 8000`
2. Check if the server is accessible by opening `http://localhost:8000` in a browser
3. Verify no other services are using port 8000
4. Check firewall settings to ensure the port is accessible

### STDIO Mode Issues

1. Ensure your start script has correct paths and can be executed manually
2. Check if the Python environment is correctly activated in the script
3. Verify the script has execute permissions (on macOS/Linux)

### Authorization Issues

1. Verify your Zoho API credentials in the `.env` file
2. Check that your tokens are not expired
3. Ensure your Zoho API account has the necessary permissions

### Connection Issues

If Cursor cannot connect to the server:

1. For HTTP mode, ensure the server is running and the URL is correct
2. For STDIO mode, make sure the command path is correct and the script is executable
3. Check logs for any error messages:
   - Zoho Books MCP server logs
   - Cursor logs (Help > Toggle Developer Tools > Console)

For more detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting.md).