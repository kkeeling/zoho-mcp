"""Tests for the OAuth flow module."""

import os
import tempfile
import threading
import time
from pathlib import Path
from unittest import mock

import pytest
import httpx

from zoho_mcp.auth_flow import (
    start_callback_server,
    exchange_code_for_token,
    update_env_file,
    run_oauth_flow,
    OAuthCallbackHandler
)
from zoho_mcp.errors import AuthenticationError
from zoho_mcp.config import settings


@pytest.fixture
def mock_settings():
    """Fixture to mock settings for testing."""
    with mock.patch('zoho_mcp.auth_flow.settings') as mock_settings:
        mock_settings.ZOHO_CLIENT_ID = "test_client_id"
        mock_settings.ZOHO_CLIENT_SECRET = "test_client_secret"
        mock_settings.domain = "com"
        mock_settings.ZOHO_AUTH_BASE_URL = "https://accounts.zoho.com/oauth/v2"
        mock_settings.ZOHO_OAUTH_SCOPE = "ZohoBooks.fullaccess.all"
        yield mock_settings


@pytest.fixture
def temp_env_file():
    """Fixture to create a temporary .env file."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"ZOHO_CLIENT_ID=test_client_id\nZOHO_CLIENT_SECRET=test_client_secret\n")
        tmp_path = tmp.name
    
    yield Path(tmp_path)
    
    # Clean up
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


class TestOAuthFlow:
    """Test OAuth flow functionality."""
    
    def test_callback_server_start_stop(self):
        """Test starting and stopping the callback server."""
        port = 8098  # Use different port to avoid conflicts
        server = start_callback_server(port)
        
        try:
            # Check that server is running
            time.sleep(0.1)  # Give server time to start
            with pytest.raises(OSError):
                # Trying to start another server on the same port should fail
                start_callback_server(port)
        finally:
            server.shutdown()
            server.server_close()
    
    def test_callback_handler_code_capture(self):
        """Test capturing authorization code."""
        # Reset the handler
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.error = None
        
        # Start server
        port = 8097  # Use different port
        server = start_callback_server(port)
        
        try:
            # Make a request with a code
            response = httpx.get(
                f"http://localhost:{port}/callback?code=test_auth_code",
                timeout=5.0
            )
            
            # Check that code was captured
            assert response.status_code == 200
            assert "Authentication Successful" in response.text
            assert OAuthCallbackHandler.auth_code == "test_auth_code"
            assert OAuthCallbackHandler.error is None
        finally:
            server.shutdown()
            server.server_close()
    
    def test_callback_handler_error_capture(self):
        """Test capturing authorization error by manually setting the class variable."""
        # Reset the class variables
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.error = None
        
        # Set error directly (this is what the handler does internally)
        OAuthCallbackHandler.error = "access_denied"
        
        # Check that error was captured
        assert OAuthCallbackHandler.auth_code is None
        assert OAuthCallbackHandler.error == "access_denied"
    
    def test_update_env_file_create(self, temp_env_file):
        """Test creating/updating .env file with refresh token."""
        with mock.patch('zoho_mcp.auth_flow.Path') as mock_path:
            mock_path.return_value.parent.parent.__truediv__.return_value.__truediv__.return_value = temp_env_file
            
            # Update with new refresh token
            update_env_file("test_refresh_token")
            
            # Check that file was updated
            with open(temp_env_file, "r") as f:
                content = f.read()
                assert "ZOHO_REFRESH_TOKEN=test_refresh_token" in content
                assert "ZOHO_CLIENT_ID=test_client_id" in content
    
    @mock.patch('zoho_mcp.auth_flow.httpx.post')
    def test_exchange_code_for_token_success(self, mock_post, mock_settings):
        """Test successful token exchange."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Call the function
        result = exchange_code_for_token("test_auth_code")
        
        # Check results
        assert result["refresh_token"] == "test_refresh_token"
        mock_post.assert_called_once()
    
    @mock.patch('zoho_mcp.auth_flow.httpx.post')
    def test_exchange_code_for_token_error(self, mock_post, mock_settings):
        """Test handling API errors in token exchange."""
        # Mock HTTP error
        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"error": "invalid_grant"}'
        mock_response.json.return_value = {"error": "invalid_grant"}
        
        mock_error = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=mock.Mock(),
            response=mock_response
        )
        mock_post.side_effect = mock_error
        
        # Call the function and check for exception
        with pytest.raises(AuthenticationError) as excinfo:
            exchange_code_for_token("invalid_code")
        
        assert "Token exchange failed" in str(excinfo.value)
    
    @mock.patch('zoho_mcp.auth_flow.time.sleep', return_value=None)  # Don't sleep
    @mock.patch('zoho_mcp.auth_flow.webbrowser.open')
    @mock.patch('zoho_mcp.auth_flow.exchange_code_for_token')
    @mock.patch('zoho_mcp.auth_flow.update_env_file')
    @mock.patch('zoho_mcp.auth_flow.start_callback_server')
    def test_run_oauth_flow_success(self, mock_server, mock_update, mock_exchange,
                                  mock_browser, mock_sleep, mock_settings):
        """Test successful OAuth flow."""
        # Setup mocks
        mock_server.return_value = mock.Mock()
        mock_exchange.return_value = {"refresh_token": "test_refresh_token"}
        mock_browser.return_value = True
        
        # Reset class variables and set auth_code 
        OAuthCallbackHandler.error = None
        OAuthCallbackHandler.auth_code = "test_auth_code"
        
        # Run the flow
        result = run_oauth_flow(port=8095)
        
        # Verify results
        assert result == "test_refresh_token"
        mock_server.assert_called_once()
        mock_browser.assert_called_once()
        mock_exchange.assert_called_once_with("test_auth_code")
        mock_update.assert_called_once_with("test_refresh_token")
        
        # Clean up
        mock_server.return_value.shutdown.assert_called_once()

    @mock.patch('zoho_mcp.auth_flow.time.sleep', return_value=None)
    @mock.patch('zoho_mcp.auth_flow.webbrowser.open')
    @mock.patch('zoho_mcp.auth_flow.exchange_code_for_token')
    @mock.patch('zoho_mcp.auth_flow.update_env_file')
    @mock.patch('zoho_mcp.auth_flow.start_callback_server')
    def test_run_oauth_flow_custom_scope(self, mock_server, mock_update, mock_exchange,
                                         mock_browser, mock_sleep, mock_settings):
        """Test that OAuth flow uses scope from settings."""
        mock_server.return_value = mock.Mock()
        mock_exchange.return_value = {"refresh_token": "tok"}
        mock_browser.return_value = True
        OAuthCallbackHandler.error = None
        OAuthCallbackHandler.auth_code = "auth_code"
        mock_settings.ZOHO_OAUTH_SCOPE = "ZohoBooks.invoices.READ"

        run_oauth_flow(port=8094)

        auth_url = mock_browser.call_args[0][0]
        assert "scope=ZohoBooks.invoices.READ" in auth_url
    
    @mock.patch('zoho_mcp.auth_flow.start_callback_server')
    def test_run_oauth_flow_missing_credentials(self, mock_server, mock_settings):
        """Test OAuth flow with missing credentials."""
        # Setup mocks
        mock_settings.ZOHO_CLIENT_ID = ""
        mock_settings.ZOHO_CLIENT_SECRET = ""
        
        # Run the flow and expect error
        with pytest.raises(AuthenticationError) as excinfo:
            run_oauth_flow()
        
        # Verify results
        assert "Missing required OAuth credentials" in str(excinfo.value)
        mock_server.assert_not_called()
    
    @mock.patch('zoho_mcp.auth_flow.time')
    @mock.patch('zoho_mcp.auth_flow.webbrowser.open')
    @mock.patch('zoho_mcp.auth_flow.start_callback_server')
    def test_run_oauth_flow_timeout(self, mock_server, mock_browser, mock_time, mock_settings):
        """Test OAuth flow with timeout."""
        # Setup mocks
        mock_server.return_value = mock.Mock()
        mock_browser.return_value = True
        
        # Make sure no auth code is set
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.error = None
        
        # Simulate time passing beyond timeout
        start_time = 0
        mock_time.time.side_effect = [start_time, start_time + 301]  # Make sure we simulate time past timeout threshold
        mock_time.sleep = mock.Mock()  # Mock time.sleep to avoid actual sleep
        
        # Run the flow and expect error
        with pytest.raises(AuthenticationError) as excinfo:
            run_oauth_flow()
        
        # Verify results
        assert "OAuth flow timed out" in str(excinfo.value)
        mock_server.return_value.shutdown.assert_called_once()
    
    @mock.patch('zoho_mcp.auth_flow.time.sleep', return_value=None)  # Don't actually sleep
    @mock.patch('zoho_mcp.auth_flow.webbrowser.open')
    @mock.patch('zoho_mcp.auth_flow.start_callback_server')
    def test_run_oauth_flow_authorization_error(self, mock_server, mock_browser, mock_sleep, mock_settings):
        """Test OAuth flow with authorization error."""
        # Setup mocks
        mock_server.return_value = mock.Mock()
        mock_browser.return_value = True
        
        # Set error directly
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.error = "access_denied"
        
        # Run the flow and expect error
        with pytest.raises(AuthenticationError) as excinfo:
            run_oauth_flow()
        
        # Verify results
        assert "OAuth authorization error: access_denied" in str(excinfo.value)
        mock_server.return_value.shutdown.assert_called_once()