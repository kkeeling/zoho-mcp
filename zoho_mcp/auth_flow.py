"""
OAuth flow handler for Zoho Books API authentication.

Implements a local OAuth flow with browser-based authentication 
and a temporary HTTP server to capture the authorization code.
"""

import logging
import time
import webbrowser
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import httpx

from zoho_mcp.config import settings
from zoho_mcp.errors import AuthenticationError
from zoho_mcp.logging import set_request_context

logger = logging.getLogger(__name__)

# HTML response templates
SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head><title>Zoho Books OAuth - Success</title></head>
<body>
    <h1>Authentication Successful!</h1>
    <p>You have successfully authenticated with Zoho Books.</p>
    <p>You can now close this window and return to the terminal.</p>
</body>
</html>"""

ERROR_HTML = """<!DOCTYPE html>
<html>
<head><title>Zoho Books OAuth - Error</title></head>
<body>
    <h1>Authentication Error</h1>
    <p>{error_message}</p>
    <p>Please close this window and try again.</p>
</body>
</html>"""


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""
    
    # Class variable to store the auth code
    auth_code: Optional[str] = None
    error: Optional[str] = None
    
    def do_GET(self):
        """Handle GET request with OAuth callback."""
        try:
            # Parse the URL and extract query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Check if we received an error
            if 'error' in query_params:
                self.error = query_params['error'][0]
                error_desc = query_params.get('error_description', ['Unknown error'])[0]
                logger.error(f"OAuth error: {self.error} - {error_desc}")
                
                # Send error response to browser
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = ERROR_HTML.format(error_message=f"Error: {error_desc}")
                self.wfile.write(error_html.encode())
                return
            
            # Check if we received the authorization code
            if 'code' in query_params:
                # Store the authorization code in the class variable
                OAuthCallbackHandler.auth_code = query_params['code'][0]
                logger.info("Successfully received authorization code")
                
                # Send success response to browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(SUCCESS_HTML.encode())
            else:
                # No code or error was received
                logger.error(f"No authorization code in callback. Path: {self.path}")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = ERROR_HTML.format(error_message="No authorization code received.")
                self.wfile.write(error_html.encode())
        
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = ERROR_HTML.format(error_message=f"Server error: {str(e)}")
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr."""
        logger.debug(f"OAuth callback server: {format % args}")


def start_callback_server(port: int = 8099) -> HTTPServer:
    """
    Start a temporary HTTP server to receive the OAuth callback.
    
    Args:
        port: Port to run the server on
    
    Returns:
        The HTTPServer instance
    """
    server = HTTPServer(('localhost', port), OAuthCallbackHandler)
    # Reset the class variables
    OAuthCallbackHandler.auth_code = None
    OAuthCallbackHandler.error = None
    
    # Start the server in a separate thread
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    logger.info(f"Started OAuth callback server on http://localhost:{port}")
    return server


def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        code: The authorization code from the OAuth callback
    
    Returns:
        Dictionary with token data including refresh_token
    
    Raises:
        AuthenticationError: If token exchange fails
    """
    try:
        # Prepare the token request
        client_id = settings.ZOHO_CLIENT_ID
        client_secret = settings.ZOHO_CLIENT_SECRET
        domain = settings.domain
        
        url = f"{settings.ZOHO_AUTH_BASE_URL}/token"
        params = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": f"http://localhost:8099/callback",
            "grant_type": "authorization_code",
        }
        
        # Make the request
        response = httpx.post(url, params=params, timeout=30.0)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        if "refresh_token" not in data:
            logger.error(f"Unexpected token response: {data}")
            raise AuthenticationError(
                message="Invalid token response: missing refresh_token", 
                details={"response": data}
            )
        
        return data
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token exchange: {e.response.status_code}")
        response_data = {}
        if e.response.content:
            try:
                response_data = e.response.json()
            except json.JSONDecodeError:
                response_data = {"raw": e.response.text}
        
        message = response_data.get("message", str(e))
        raise AuthenticationError(
            message=f"Token exchange failed: {message}",
            details={"status_code": e.response.status_code, "response": response_data}
        )
    
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.error(f"Request error during token exchange: {str(e)}")
        raise AuthenticationError(
            message=f"Request failed during token exchange: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {str(e)}", exc_info=True)
        raise AuthenticationError(
            message=f"Unexpected error during token exchange: {str(e)}"
        )


def update_env_file(refresh_token: str) -> None:
    """
    Update the .env file with the new refresh token.
    
    Args:
        refresh_token: The refresh token to save
    
    Raises:
        IOError: If unable to write to the .env file
    """
    # Determine the path to the .env file
    env_path = Path(__file__).parent.parent / "config" / ".env"
    
    # Create config directory if it doesn't exist
    env_path.parent.mkdir(parents=True, exist_ok=True)
    
    env_content = ""
    env_dict = {}
    
    # Read existing .env file if it exists
    if env_path.exists():
        with open(env_path, "r") as f:
            env_content = f.read()
        
        # Parse existing variables
        for line in env_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_dict[key.strip()] = value.strip().strip('"\'')
    
    # Update or add the refresh token
    env_dict["ZOHO_REFRESH_TOKEN"] = refresh_token
    
    # Reconstruct the .env file
    env_lines = []
    for key, value in env_dict.items():
        # Quote the value if it contains spaces
        if ' ' in value:
            env_lines.append(f'{key}="{value}"')
        else:
            env_lines.append(f'{key}={value}')
    
    # Write back to the .env file
    with open(env_path, "w") as f:
        f.write('\n'.join(env_lines) + '\n')
    
    logger.info(f"Updated refresh token in {env_path}")


def run_oauth_flow(port: int = 8099) -> str:
    """
    Run the complete OAuth flow to obtain a refresh token.
    
    Args:
        port: Port to use for the callback server
    
    Returns:
        The obtained refresh token
    
    Raises:
        AuthenticationError: If the OAuth flow fails
    """
    # Set up request context for logging
    set_request_context(request_id="oauth-setup")
    
    # Validate required settings
    client_id = settings.ZOHO_CLIENT_ID
    client_secret = settings.ZOHO_CLIENT_SECRET
    
    if not client_id or not client_secret:
        raise AuthenticationError(
            message="Missing required OAuth credentials (ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET)"
        )
    
    # Start the callback server
    server = start_callback_server(port)
    
    try:
        # Build the authorization URL
        domain = settings.domain
        redirect_uri = f"http://localhost:{port}/callback"
        
        scope = settings.ZOHO_OAUTH_SCOPE
        auth_url = (
            f"https://accounts.zoho.{domain}/oauth/v2/auth?"
            f"scope={scope}&"
            f"client_id={client_id}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"redirect_uri={redirect_uri}"
        )
        
        # Display the authorization URL to the user
        logger.info(f"Opening browser for Zoho OAuth authorization")
        print("\n" + "=" * 80)
        print(f"Zoho Books OAuth Setup")
        print("=" * 80)
        print(f"\nAuthorization URL: {auth_url}")
        print("\nAttempting to open your default web browser...")
        
        # Try to open the browser automatically
        if webbrowser.open(auth_url):
            print("\nYour browser should open automatically.")
        else:
            print("\nUnable to open browser automatically.")
            print("Please copy and paste the above URL into your browser to continue.")
        
        print("\nWaiting for authentication to complete...")
        
        # Wait for the authorization code
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while (
            OAuthCallbackHandler.auth_code is None and 
            OAuthCallbackHandler.error is None and
            time.time() - start_time < max_wait_time
        ):
            time.sleep(1)
        
        # Check if we got an error
        if OAuthCallbackHandler.error:
            raise AuthenticationError(
                message=f"OAuth authorization error: {OAuthCallbackHandler.error}"
            )
        
        # Check if we timed out
        if OAuthCallbackHandler.auth_code is None:
            raise AuthenticationError(
                message="OAuth flow timed out. No authorization code received."
            )
        
        # Exchange the authorization code for tokens
        logger.info("Exchanging authorization code for tokens")
        token_data = exchange_code_for_token(OAuthCallbackHandler.auth_code)
        
        # Save the refresh token to the .env file
        logger.info("Saving refresh token to environment")
        update_env_file(token_data["refresh_token"])
        
        print("\n✅ OAuth setup complete!")
        print(f"Refresh token has been saved to your configuration.")
        
        return token_data["refresh_token"]
        
    finally:
        # Shutdown the server
        logger.info("Shutting down OAuth callback server")
        server.shutdown()
        server.server_close()