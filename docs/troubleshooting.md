# Zoho Books MCP Server Troubleshooting Guide

This guide covers common issues you might encounter when using the Zoho Books MCP server with Claude Desktop, Cursor, or other MCP clients, along with solutions and workarounds.

## Table of Contents

- [Authentication Issues](#authentication-issues)
  - [Invalid Credentials](#invalid-credentials)
  - [Token Expiration](#token-expiration)
  - [Organization Access](#organization-access)
- [Automatic OAuth Flow Setup](#automatic-oauth-flow-setup)
  - [Creating a Zoho API Application](#creating-a-zoho-api-application)
  - [Using the OAuth Setup Command](#using-the-oauth-setup-command)
  - [Custom OAuth Callback Port](#custom-oauth-callback-port)
  - [Troubleshooting OAuth Setup](#troubleshooting-oauth-setup)
- [Client Connection Problems](#client-connection-problems)
  - [Claude Desktop Connection Issues](#claude-desktop-connection-issues)
  - [Cursor Connection Issues](#cursor-connection-issues)
  - [Tool Visibility Issues](#tool-visibility-issues)
- [API Errors](#api-errors)
  - [Rate Limiting](#rate-limiting)
  - [API Permission Denied](#api-permission-denied)
  - [Resource Not Found](#resource-not-found)
- [Server Configuration Problems](#server-configuration-problems)
  - [Environment Variables](#environment-variables)
  - [Transport Configuration](#transport-configuration)
  - [SSL/TLS Issues](#ssltls-issues)
- [Tool Execution Errors](#tool-execution-errors)
  - [Input Validation Errors](#input-validation-errors)
  - [Timeout Errors](#timeout-errors)
  - [Unexpected Responses](#unexpected-responses)
- [Logging and Debugging](#logging-and-debugging)
  - [Enabling Debug Logging](#enabling-debug-logging)
  - [Checking Server Logs](#checking-server-logs)
  - [Checking Client Logs](#checking-client-logs)
- [Common Error Messages](#common-error-messages)

## Authentication Issues

### Invalid Credentials

**Symptoms:**
- "Authentication failed" errors
- "Invalid client credentials" messages
- Tools fail with authorization errors

**Possible Causes:**
- Incorrect Client ID or Client Secret
- Mistyped credentials in .env file
- Wrong region selected

**Solutions:**
1. Double-check your Zoho Books API credentials in the `.env` file
2. Verify the credentials in the Zoho API Console
3. Ensure your credentials are for the correct Zoho datacenter/region
4. Regenerate API credentials if necessary

**Example Error:**
```
ZohoAuthError: Authentication failed: invalid_client_secret - Client secret is invalid
```

### Token Expiration

**Symptoms:**
- Tools worked before but suddenly stopped working
- "Token expired" or "Invalid grant" errors

**Possible Causes:**
- Refresh token has expired
- Refresh token was revoked
- Token permissions changed

**Solutions:**
1. Use the automatic OAuth setup flow (recommended):
   ```
   python server.py --setup-oauth
   ```
   This will guide you through the authentication process and automatically save the refresh token.

2. Or manually:
   - Generate a new refresh token from the Zoho API Console
   - Update the `ZOHO_REFRESH_TOKEN` in your `.env` file
   - Restart the MCP server

**Example Error:**
```
ZohoAuthError: Authentication failed: invalid_token - expired or revoked
```

### Organization Access

**Symptoms:**
- Authentication succeeds but you get "organization not found" errors
- Cannot access organization-specific data

**Possible Causes:**
- Incorrect Organization ID
- Account doesn't have access to the specified organization
- API access not enabled for the organization

**Solutions:**
1. Verify your Organization ID in Zoho Books (Setup > Organizations)
2. Check that your user account has access to the organization
3. Enable API access for the organization in Zoho Books settings

**Example Error:**
```
ZohoAPIError: Organization not found or access denied: organization_id=123456789
```

## Automatic OAuth Flow Setup

The Zoho Books MCP server provides an automatic OAuth flow to simplify the authentication process.

### Creating a Zoho API Application

Before using the OAuth setup, you need to create a server-side application in the Zoho API Console:

1. Go to [Zoho API Console](https://api-console.zoho.com/)

2. Sign in with your Zoho account credentials.

3. Click **Add Client** to create a new application.

4. Select **Server-based Applications** as the client type.

5. Fill in the required details:
   - **Client Name**: A name for your application (e.g., "Zoho Books MCP")
   - **Homepage URL**: Your website URL or `http://localhost` for local development
   - **Authorized Redirect URIs**: Add `http://localhost:8099/callback` (or your custom port)
   - **Description**: Brief description of your application

6. Click **Create**.

7. After creation, you'll receive your **Client ID** and **Client Secret**. Save these values securely - you'll need them in the next step.

8. Under the **Scopes** tab, add the required scopes:
   - For full access to all Books features: `ZohoBooks.fullaccess.all`
   - Or select specific scopes like `ZohoBooks.contacts.READ`, `ZohoBooks.invoices.CREATE`, etc.

### Using the OAuth Setup Command

To automatically set up OAuth authentication:

1. Ensure you have the following values in your `.env` file:
   ```
   ZOHO_CLIENT_ID="your_client_id"
   ZOHO_CLIENT_SECRET="your_client_secret"
   ZOHO_ORGANIZATION_ID="your_organization_id"  
   ZOHO_REGION="US"  # Change according to your region (US, EU, IN, AU, CA, etc.)
   ```

2. Run the OAuth setup command:
   ```
   python server.py --setup-oauth
   ```

3. Your default web browser will open automatically to the Zoho authentication page.

4. Log in to your Zoho account and grant the requested permissions.

5. After successful authentication, you will be redirected to a local page confirming the successful setup.

6. The refresh token will be automatically saved to your `.env` file.

7. You can now start the server normally with your chosen transport mode.

### Custom OAuth Callback Port

By default, the OAuth callback server runs on port 8099. If this port is unavailable, you can specify a different port:

```
python server.py --setup-oauth --oauth-port 9000
```

### Troubleshooting OAuth Setup

**Browser doesn't open automatically:**
- Copy the authorization URL displayed in the terminal
- Manually paste it into your browser
- Complete the authentication process

**Port conflict errors:**
- If you see "Address already in use" errors, try a different port with `--oauth-port`
- Ensure no other services are using the specified port

**Authentication timeout:**
- The default timeout is 5 minutes
- If the process times out, run the command again and complete the steps more quickly

**Authentication errors:**
- "Invalid client" error: Verify your Client ID and Client Secret are correct
- "Access denied" error: Make sure you're granting all requested permissions
- "Redirect URI mismatch": Ensure the redirect URI in your Zoho Developer Console matches `http://localhost:PORT/callback`

**Example Successful Flow:**
```
$ python server.py --setup-oauth

=== Zoho Books OAuth Setup ===

Authorization URL: https://accounts.zoho.com/oauth/v2/auth?scope=ZohoBooks.fullaccess.all&client_id=1000.XXXXXXXXXXXX&response_type=code&access_type=offline&redirect_uri=http://localhost:8099/callback

Attempting to open your default web browser...
Your browser should open automatically.

Waiting for authentication to complete...

✅ OAuth setup completed successfully!
Refresh token has been saved to configuration.
```

## Client Connection Problems

### Claude Desktop Connection Issues

**Symptoms:**
- Claude Desktop doesn't show the tools icon
- "Could not connect to MCP server" messages
- Claude hangs when trying to use tools

**Possible Causes:**
- Incorrect configuration in claude_desktop_config.json
- MCP server not running
- Path issues in configuration

**Solutions:**
1. Verify the `claude_desktop_config.json` format:
   ```json
   {
     "mcpServers": {
       "zoho-books": {
         "command": "python",
         "args": [
           "/absolute/path/to/server.py",
           "--stdio"
         ],
         "cwd": "/absolute/path/to/zoho-books-mcp-server"
       }
     }
   }
   ```
2. Make sure all paths are absolute, not relative
3. Verify Python is in your PATH
4. Check Claude logs for connection errors
5. Restart Claude Desktop completely

**Example Error in Claude Logs:**
```
Failed to start MCP server 'zoho-books': Cannot find file at specified path
```

### Cursor Connection Issues

**Symptoms:**
- Cursor doesn't show the Zoho Books tools
- Cannot connect to the server from Cursor
- Connection timeouts

**Possible Causes:**
- Server not running on expected port
- Network/firewall blocking connection
- HTTP transport not configured correctly

**Solutions:**
1. Make sure the server is running with `python server.py --port 8000`
2. Check if the port is accessible with `curl http://localhost:8000`
3. Verify firewall settings aren't blocking the connection
4. Ensure the URL in Cursor's MCP settings is correct

**Example Error:**
```
Connection to http://localhost:8000 failed: Connection refused
```

### Tool Visibility Issues

**Symptoms:**
- Client connects but doesn't show any tools
- Tools appear but are incomplete
- "No tools available" message

**Possible Causes:**
- Server initialization failed
- Tools not properly registered
- Transport protocol mismatch

**Solutions:**
1. Check server startup logs for errors
2. Verify that the server is registering tools during startup
3. Make sure you're using the correct transport mode for your client
4. Restart both the server and client

**Example Log:**
```
Failed to register tools: Module 'zoho_mcp.tools' not found
```

## API Errors

### Rate Limiting

**Symptoms:**
- "Too many requests" errors
- Operations suddenly start failing after working
- Temporary errors that resolve after waiting

**Possible Causes:**
- Exceeded Zoho Books API rate limits
- Too many requests in a short period
- Account plan limitations

**Solutions:**
1. Add delays between operations
2. Implement retry logic for rate limit errors (already in the server)
3. Check your Zoho Books plan limits
4. Consider upgrading your Zoho Books plan for higher API limits

**Example Error:**
```
ZohoAPIError: Rate limit exceeded: too many requests. Try again after 60 seconds
```

### API Permission Denied

**Symptoms:**
- "Permission denied" errors for specific operations
- Some tools work while others fail
- Access restricted errors

**Possible Causes:**
- Refresh token doesn't have required scopes
- User doesn't have permission for the operation
- Feature not available in your Zoho Books plan

**Solutions:**
1. Generate a new refresh token with all required scopes
2. Check user permissions in Zoho Books
3. Verify your Zoho Books plan includes the features you're trying to use

**Example Error:**
```
ZohoAPIError: Permission denied: insufficient privileges for operation 'create_invoice'
```

### Resource Not Found

**Symptoms:**
- "Not found" errors when accessing specific resources
- Invalid ID errors
- Reference errors

**Possible Causes:**
- Attempting to access a resource that doesn't exist
- Using an ID from a different organization
- Resource was deleted

**Solutions:**
1. Verify resource IDs before using them
2. Use list operations to get valid IDs
3. Make sure you're working with the correct organization

**Example Error:**
```
ZohoAPIError: Resource not found: contact_id=123456789 does not exist
```

## Server Configuration Problems

### Environment Variables

**Symptoms:**
- Server fails during initialization
- "Missing required setting" errors
- Configuration-related exceptions

**Possible Causes:**
- `.env` file missing or incorrectly formatted
- Required environment variables not set
- Permissions issues with config files

**Solutions:**
1. Copy `.env.example` to `.env` if it doesn't exist
2. Ensure all required variables are set in the `.env` file:
   ```
   ZOHO_CLIENT_ID="your_client_id"
   ZOHO_CLIENT_SECRET="your_client_secret" 
   ZOHO_REFRESH_TOKEN="your_refresh_token"
   ZOHO_ORGANIZATION_ID="your_organization_id"
   ZOHO_REGION="US"  # Change according to your region
   ```
3. Check file permissions on the `.env` file

**Example Error:**
```
ValueError: Missing required settings: ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET. Please add them to your .env file or environment variables.
```

### Transport Configuration

**Symptoms:**
- "No transport type specified" errors
- Transport initialization failures
- Server crashes during startup

**Possible Causes:**
- Missing command-line arguments for transport
- Invalid transport configuration
- Transport dependencies missing

**Solutions:**
1. Specify a transport mode when starting the server:
   - STDIO: `python server.py --stdio`
   - HTTP: `python server.py --port 8000`
   - WebSocket: `python server.py --ws`
   - OAuth Setup: `python server.py --setup-oauth`
2. Check for missing dependencies with `pip install -r requirements.txt`
3. Verify the transport-specific settings in your configuration

**Example Error:**
```
TransportConfigurationError: No transport type specified. Use --stdio, --port, --ws, or --setup-oauth.
```

### SSL/TLS Issues

**Symptoms:**
- SSL handshake failures
- Certificate errors
- Connection refused with HTTPS

**Possible Causes:**
- Invalid or expired SSL certificates
- Incorrect path to certificate files
- Certificate permissions issues

**Solutions:**
1. Verify SSL certificate and key paths in `.env`:
   ```
   ENABLE_SECURE_TRANSPORT=True
   SSL_CERT_PATH=/path/to/cert.pem
   SSL_KEY_PATH=/path/to/key.pem
   ```
2. Check certificate and key file permissions
3. Generate new certificates if needed
4. For development, consider disabling SSL/TLS

**Example Error:**
```
TransportInitializationError: Failed to initialize HTTP/SSE transport: SSL_CTX_use_certificate_file error
```

## Tool Execution Errors

### Input Validation Errors

**Symptoms:**
- "Validation error" messages
- Required field errors
- Type conversion errors

**Possible Causes:**
- Missing required parameters
- Invalid data types
- Value out of acceptable range

**Solutions:**
1. Review the tool documentation for required parameters
2. Ensure input values are in the correct format
3. Be more specific in your natural language requests
4. Check the Zoho Books API documentation for field requirements

**Example Error:**
```
ValidationError: 2 validation errors:
- contact_name: field required
- email: value is not a valid email address
```

### Timeout Errors

**Symptoms:**
- Operations take too long and fail
- "Request timeout" errors
- Client disconnects during long operations

**Possible Causes:**
- Zoho Books API slow to respond
- Network latency
- Large volume of data being processed

**Solutions:**
1. Increase timeouts in the configuration:
   ```
   REQUEST_TIMEOUT=120
   ```
2. Break down large operations into smaller batches
3. Check your network connection
4. Try during off-peak hours when the API may be more responsive

**Example Error:**
```
ZohoRequestError: Request timed out after 60 seconds
```

### Unexpected Responses

**Symptoms:**
- Tool reports success but result is unexpected
- Missing or incorrect data in responses
- "Unexpected response format" errors

**Possible Causes:**
- API response format has changed
- Zoho Books updated their API
- Edge case not handled by the tool

**Solutions:**
1. Check the Zoho Books API documentation for changes
2. Enable debug logging to see the raw API responses
3. Report the issue to the server maintainers
4. Try a different approach to accomplish the same task

**Example Error:**
```
ZohoAPIError: Unexpected response format: missing expected field 'invoice'
```

## Logging and Debugging

### Enabling Debug Logging

To enable more detailed logging:

1. Add `LOG_LEVEL=DEBUG` to your `.env` file

2. Or run the server with the `--log-level DEBUG` flag:
   ```
   python server.py --stdio --log-level DEBUG
   ```

3. To save logs to a file, add to your `.env`:
   ```
   LOG_FILE_PATH=/path/to/zoho-mcp.log
   ```

### Checking Server Logs

1. Look for the log file location:
   - If `LOG_FILE_PATH` is set, check that location
   - Otherwise, logs go to standard output

2. Common log file patterns:
   - General errors: `ERROR` level messages
   - Authentication issues: Look for `ZohoAuthError` entries
   - API problems: Look for `ZohoAPIError` entries
   - Transport issues: Look for `TransportError` entries

3. In debug mode, each API request and response will be logged

### Checking Client Logs

**Claude Desktop:**
1. Open the Claude menu and select "Show Logs"
2. Look for MCP-related entries:
   - `mcp.log` contains general MCP logging
   - `mcp-server-zoho-books.log` contains Zoho Books server-specific logs

**Cursor:**
1. Open Developer Tools (usually F12 or Ctrl+Shift+I)
2. Look for MCP-related messages in the Console tab
3. Network tab may show HTTP requests to the MCP server

## Common Error Messages

Below is a reference of common error messages and their likely causes:

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `Authentication failed: invalid_client` | Incorrect Client ID | Check Client ID in `.env` or use `--setup-oauth` |
| `Authentication failed: invalid_client_secret` | Incorrect Client Secret | Check Client Secret in `.env` or use `--setup-oauth` |
| `Authentication failed: invalid_code` | Invalid or expired refresh token | Use `--setup-oauth` to generate a new token |
| `OAuth flow timed out` | Authentication not completed within timeout period | Run OAuth setup again and complete the process more quickly |
| `OAuth authorization error: access_denied` | User denied permission during OAuth flow | Re-run OAuth setup and grant all requested permissions |
| `Address already in use` during OAuth setup | Port conflict for callback server | Use `--oauth-port` to specify a different port |
| `Missing required OAuth credentials` | Client ID or Client Secret not configured | Add these to your `.env` file before running OAuth setup |
| `Organization not found or access denied` | Incorrect Organization ID | Verify Organization ID in Zoho Books |
| `Permission denied: insufficient privileges` | Missing API permissions | Check user permissions or API scopes |
| `Resource not found: contact_id=X` | Trying to access non-existent resource | Verify the resource ID exists |
| `Validation error: contact_name required` | Missing required field | Provide all required fields |
| `Rate limit exceeded` | Too many API requests | Add delays or implement backoff |

If you encounter persistent issues not covered in this guide, please:

1. Gather relevant information:
   - Error messages and logs
   - Steps to reproduce the issue
   - Server configuration
   - Client being used

2. Report the issue to the repository maintainers with the above details.