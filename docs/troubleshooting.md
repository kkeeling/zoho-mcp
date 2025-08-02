# Zoho Books MCP Server Troubleshooting Guide

This document provides solutions to common issues when using the Zoho MCP server.

## Table of Contents

- [Automatic OAuth Flow Setup](#automatic-oauth-flow-setup)
  - [Using the OAuth Setup Command](#using-the-oauth-setup-command)
  - [Custom OAuth Callback Port](#custom-oauth-callback-port)
  - [Troubleshooting OAuth Setup](#troubleshooting-oauth-setup)
- [Authentication Issues](#authentication-issues)
- [Client Connection Problems](#client-connection-problems)
- [Configuration Issues](#configuration-issues)

## Automatic OAuth Flow Setup

The Zoho MCP server provides an automatic OAuth flow to simplify authentication setup.

### Using the OAuth Setup Command

To initiate the OAuth flow, run the following command:

```bash
python server.py --setup-oauth
```

This will:
1. Start a local web server for OAuth callback
2. Open your browser to Zoho's authorization page
3. Handle the OAuth callback automatically
4. Save your tokens securely

Use the automatic OAuth setup flow (recommended) for easier configuration and token management.

### Custom OAuth Callback Port

You can customize the OAuth callback port using the --oauth-port flag:

```bash
python server.py --setup-oauth --oauth-port 8080
```

### Troubleshooting OAuth Setup

If you encounter issues during OAuth setup:

1. Ensure your Zoho app redirect URI matches the callback URL
2. Check that the specified port is available
3. Verify your client credentials are correct
4. Make sure your browser can access the callback URL

OAuth Setup: `python server.py --setup-oauth`

### OAuth Flow Examples

#### Basic OAuth setup:
```bash
# Start OAuth flow for US region
python -m zoho_mcp --auth-flow --region US

# Start OAuth flow for EU region
python -m zoho_mcp --auth-flow --region EU

# Start OAuth flow for IN region
python -m zoho_mcp --auth-flow --region IN
```

#### OAuth with custom callback port:
```bash
python -m zoho_mcp --auth-flow --callback-port 8080
```

## Common OAuth Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `invalid_client` | Client ID or secret is incorrect | Verify your ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET environment variables |
| `redirect_uri_mismatch` | Callback URL doesn't match registered URI | Ensure your Zoho app is configured with the correct redirect URI |
| `access_denied` | User denied authorization | Re-run the OAuth flow and grant the required permissions |
| `token_expired` | Access token has expired | The server will automatically refresh tokens, or re-run OAuth flow |
| `insufficient_scope` | Missing required permissions | Check that your Zoho app has the necessary scopes configured |
| `invalid_region` | Incorrect region specified | Use the correct region (US, EU, IN, etc.) for your Zoho account |
| `OAuth flow timed out` | OAuth authorization process timed out | Restart the OAuth setup process and complete authorization within the time limit |
| `OAuth authorization error` | General OAuth authorization error | Check client credentials and app configuration, then retry |
| `Missing required OAuth credentials` | OAuth credentials not configured | Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET environment variables |

## Authentication Issues

### Token Expiration
When your access tokens expire, the server will automatically attempt to refresh them. If refresh fails:

1. Use the automatic OAuth setup flow (recommended): `python server.py --setup-oauth`
2. Manually clear stored tokens and re-authenticate
3. Verify your refresh token hasn't been revoked

### Invalid Credentials
If you receive authentication errors:

1. Double-check your ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET
2. Ensure your Zoho app is approved and active
3. Verify the correct region is configured

## Client Connection Problems

### MCP Client Cannot Connect
If your MCP client (Claude Desktop, Cursor) cannot connect to the server:

1. Check that the server command and arguments are correct
2. Verify environment variables are properly set
3. Ensure the Python environment has all required dependencies
4. Check server logs for detailed error information

### Server Startup Failures
If the server fails to start:

1. Verify Python version compatibility (3.9+)
2. Check that all dependencies are installed
3. Ensure no other process is using the same port
4. Review environment variable configuration

## Connection Issues

### Server won't start
- Check that all required dependencies are installed
- Verify Python version is 3.9 or higher
- Ensure environment variables are properly set

### Authentication failures
- Verify your OAuth credentials are correct
- Check that tokens haven't expired
- Ensure proper region configuration

### API rate limiting
- The server automatically handles rate limits
- If you encounter persistent rate limiting, reduce request frequency

## Configuration Issues

### Environment Variables
Ensure these environment variables are set:
- `ZOHO_CLIENT_ID`: Your Zoho app's client ID
- `ZOHO_CLIENT_SECRET`: Your Zoho app's client secret
- `ZOHO_REGION`: Your Zoho account region (US, EU, IN, etc.)

### Token Storage
- Tokens are stored securely in your system's credential store
- If authentication fails, try clearing stored tokens and re-running OAuth flow

## Getting Help

If you continue to experience issues:
1. Check the server logs for detailed error messages
2. Verify your Zoho app configuration
3. Ensure your Zoho account has the necessary permissions
4. Review the examples in the documentation