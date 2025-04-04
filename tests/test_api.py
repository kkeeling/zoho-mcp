"""
Tests for the Zoho Books API client module.
"""

import json
import time
import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

import httpx

from zoho_mcp.tools.api import (
    _load_token_from_cache,
    _save_token_to_cache,
    _get_access_token,
    _handle_api_error,
    zoho_api_request,
    zoho_api_request_async,
    validate_credentials,
    ZohoAPIError,
    ZohoAuthenticationError,
    ZohoRequestError,
    ZohoRateLimitError,
)
from zoho_mcp.config import settings


# Mock the FastMCP class
class MockFastMCP(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool = MagicMock()
        self.tool.return_value = lambda func: func


# Patch the FastMCP class
patch("mcp.server.fastmcp.FastMCP", MockFastMCP).start()


# Test loading token from cache
def test_load_token_from_cache_not_exists():
    """Test loading token when cache file doesn't exist."""
    with patch.object(Path, "exists", return_value=False):
        assert _load_token_from_cache() == {}


def test_load_token_from_cache_success():
    """Test successful token loading from cache."""
    mock_token_data = {"access_token": "test_token", "expires_at": time.time() + 3600}
    
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_token_data))):
        with patch.object(Path, "exists", return_value=True):
            loaded_token = _load_token_from_cache()
            assert loaded_token == mock_token_data


def test_load_token_from_cache_json_error():
    """Test handling of JSON decode error when loading token."""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch.object(Path, "exists", return_value=True):
            assert _load_token_from_cache() == {}


# Test saving token to cache
def test_save_token_to_cache():
    """Test saving token to cache."""
    mock_token_data = {"access_token": "test_token", "expires_at": time.time() + 3600}
    
    # Create a StringIO to capture the write
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        with patch.object(Path, "parent"):
            with patch.object(Path, "mkdir"):
                # Override json.dumps to return a simple string
                with patch("json.dumps", return_value='{"token":"data"}'):
                    _save_token_to_cache(mock_token_data)
    
    # Just verify write was called (at least once)
    assert mock_file().write.called


def test_save_token_to_cache_io_error():
    """Test handling of IO error when saving token."""
    mock_token_data = {"access_token": "test_token", "expires_at": time.time() + 3600}
    
    with patch("builtins.open", side_effect=IOError("Test IO error")):
        with patch.object(Path, "parent"):
            with patch.object(Path, "mkdir"):
                # Should not raise an exception, just log the error
                _save_token_to_cache(mock_token_data)


# Test getting access token
def test_get_access_token_from_cache():
    """Test getting access token from cache."""
    current_time = time.time()
    mock_token_data = {"access_token": "cached_token", "expires_at": current_time + 3600}
    
    with patch("zoho_mcp.tools.api._load_token_from_cache", return_value=mock_token_data):
        token = _get_access_token()
        assert token == "cached_token"


def test_get_access_token_refresh_expired():
    """Test refreshing an expired token."""
    current_time = time.time()
    # Create expired token data
    expired_token = {"access_token": "expired_token", "expires_at": current_time - 60}
    
    # Create mocks for key functions
    mock_load = MagicMock(return_value=expired_token)
    mock_save = MagicMock()
    
    # Create mock response data
    response_data = {"access_token": "new_token", "expires_in": 3600}
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()
    
    with patch("zoho_mcp.tools.api._load_token_from_cache", mock_load):
        with patch("zoho_mcp.tools.api._save_token_to_cache", mock_save):
            with patch("httpx.post", return_value=mock_response):
                # We need to patch these attributes too
                with patch("zoho_mcp.tools.api.settings.ZOHO_CLIENT_ID", "client_id"):
                    with patch("zoho_mcp.tools.api.settings.ZOHO_CLIENT_SECRET", "client_secret"):
                        with patch("zoho_mcp.tools.api.settings.ZOHO_REFRESH_TOKEN", "refresh_token"):
                            with patch("zoho_mcp.tools.api.AUTH_BASE_URL", "https://auth.url"):
                                # Call the function and verify the result
                                token = _get_access_token()
                                
                                # Only need to verify we get the new token from the response
                                assert token == "new_token"


def test_get_access_token_refresh_force():
    """Test force refreshing a token."""
    current_time = time.time()
    # Create a valid token that wouldn't normally be refreshed
    valid_token = {"access_token": "valid_token", "expires_at": current_time + 3600}
    
    # Create mocks for key functions 
    mock_load = MagicMock(return_value=valid_token)
    mock_save = MagicMock()
    
    # Create mock response data
    response_data = {"access_token": "new_token", "expires_in": 3600}
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()
    
    with patch("zoho_mcp.tools.api._load_token_from_cache", mock_load):
        with patch("zoho_mcp.tools.api._save_token_to_cache", mock_save):
            with patch("httpx.post", return_value=mock_response):
                # We need to patch these attributes too
                with patch("zoho_mcp.tools.api.settings.ZOHO_CLIENT_ID", "client_id"):
                    with patch("zoho_mcp.tools.api.settings.ZOHO_CLIENT_SECRET", "client_secret"):
                        with patch("zoho_mcp.tools.api.settings.ZOHO_REFRESH_TOKEN", "refresh_token"):
                            with patch("zoho_mcp.tools.api.AUTH_BASE_URL", "https://auth.url"):
                                # Force refresh should ignore the valid cached token
                                token = _get_access_token(force_refresh=True)
                                
                                # Only need to verify we get the new token from the response
                                assert token == "new_token"


def test_get_access_token_error():
    """Test handling of error during token refresh."""
    current_time = time.time()
    mock_expired_token = {"access_token": "expired_token", "expires_at": current_time - 60}
    
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.ZOHO_CLIENT_ID = "test_client_id"
    mock_settings.ZOHO_CLIENT_SECRET = "test_client_secret" 
    mock_settings.ZOHO_REFRESH_TOKEN = "test_refresh_token"
    mock_settings.ZOHO_AUTH_BASE_URL = "https://test-auth-url.com"
    
    # Create error response
    error_response = httpx.Response(401, json={"message": "Invalid refresh token"})
    
    with patch("zoho_mcp.tools.api.settings", mock_settings):
        with patch("zoho_mcp.tools.api._load_token_from_cache", return_value=mock_expired_token):
            with patch("httpx.post") as mock_post:
                # Set up the mock post to raise an HTTPStatusError
                error = httpx.HTTPStatusError(
                    "Test error",
                    request=httpx.Request("POST", "https://test.com"),
                    response=error_response
                )
                mock_post.side_effect = error
                
                # Test that it raises the expected exception
                with pytest.raises(ZohoAuthenticationError) as exc_info:
                    _get_access_token()
                
                # Verify error message contains response content
                assert "Invalid refresh token" in str(exc_info.value)


# Test handling API errors
def test_handle_api_error_authentication():
    """Test handling authentication error."""
    response = httpx.Response(
        401,
        json={"code": 1000, "message": "Invalid OAuth token"}
    )
    
    with pytest.raises(ZohoAuthenticationError) as exc_info:
        _handle_api_error(response)
    
    assert exc_info.value.status_code == 401
    assert "Invalid OAuth token" in exc_info.value.message


def test_handle_api_error_rate_limit():
    """Test handling rate limit error."""
    response = httpx.Response(
        429,
        json={"code": 2000, "message": "Rate limit exceeded"}
    )
    
    with pytest.raises(ZohoRateLimitError) as exc_info:
        _handle_api_error(response)
    
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in exc_info.value.message


def test_handle_api_error_generic():
    """Test handling generic error."""
    response = httpx.Response(
        400,
        json={"code": 3000, "message": "Invalid input"}
    )
    
    with pytest.raises(ZohoRequestError) as exc_info:
        _handle_api_error(response)
    
    assert exc_info.value.status_code == 400
    assert "Invalid input" in exc_info.value.message


def test_handle_api_error_no_json():
    """Test handling error with non-JSON response."""
    response = httpx.Response(400, text="Bad request")
    
    with pytest.raises(ZohoRequestError) as exc_info:
        _handle_api_error(response)
    
    assert exc_info.value.status_code == 400
    assert "Bad request" in str(exc_info.value)


# Test API requests
def test_zoho_api_request():
    """Test successful API request."""
    # Mock successful response
    mock_response = httpx.Response(200, json={"data": "test"})
    
    # Mock token retrieval
    with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
        with patch("httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.__enter__.return_value.request.return_value = mock_response
            
            response = zoho_api_request(
                method="GET",
                endpoint="/test",
            )
            
            assert response == {"data": "test"}
            assert mock_client.__enter__.return_value.request.call_count == 1


@pytest.mark.asyncio
async def test_zoho_api_request_async():
    """Test successful async API request."""
    # Mock successful response
    mock_response = httpx.Response(200, json={"data": "test"})
    
    # Mock token retrieval
    with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.__aenter__.return_value.request.return_value = mock_response
            
            response = await zoho_api_request_async(
                method="GET",
                endpoint="/test",
            )
            
            assert response == {"data": "test"}
            assert mock_client.__aenter__.return_value.request.call_count == 1


# Test credential validation
def test_validate_credentials_success():
    """Test successful credential validation."""
    # Mock settings instance since we can't patch the validate method directly
    mock_settings = MagicMock()
    mock_settings.ZOHO_ORGANIZATION_ID = "test_org_id"
    mock_settings.ORG_ID = "test_org_id"  # API module uses both
    
    # Mock API response with matching organization ID
    api_response = {
        "organizations": [
            {"organization_id": "test_org_id"}
        ]
    }
    
    with patch("zoho_mcp.tools.api.settings", mock_settings):
        with patch("zoho_mcp.tools.api.ORG_ID", "test_org_id"):
            # Mock token retrieval
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # Mock API request
                with patch("zoho_mcp.tools.api.zoho_api_request", return_value=api_response):
                    success, error = validate_credentials()
                    
                    assert success is True
                    assert error is None
                    # Verify validate was called
                    mock_settings.validate.assert_called_once()


def test_validate_credentials_missing_org():
    """Test credential validation with missing organization."""
    # Mock settings instance 
    mock_settings = MagicMock()
    mock_settings.ZOHO_ORGANIZATION_ID = "test_org_id"
    mock_settings.ORG_ID = "test_org_id"  # API module uses both
    
    with patch("zoho_mcp.tools.api.settings", mock_settings):
        with patch("zoho_mcp.tools.api.ORG_ID", "test_org_id"):
            # Mock token retrieval
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # Mock API request
                with patch("zoho_mcp.tools.api.zoho_api_request") as mock_request:
                    mock_request.return_value = {
                        "organizations": [
                            {"organization_id": "different_org_id"}
                        ]
                    }
                    
                    success, error = validate_credentials()
                    
                    assert success is False
                    assert "not found in Zoho Books account" in error
                    # Verify validate was called
                    mock_settings.validate.assert_called_once()


def test_validate_credentials_auth_error():
    """Test credential validation with authentication error."""
    # Mock settings instance
    mock_settings = MagicMock()
    
    with patch("zoho_mcp.tools.api.settings", mock_settings):
        # Mock token retrieval to raise an error
        with patch("zoho_mcp.tools.api._get_access_token", 
                  side_effect=ZohoAuthenticationError(401, "Invalid credentials")):
            success, error = validate_credentials()
            
            assert success is False
            assert "Invalid credentials" in error
            # Verify validate was called
            mock_settings.validate.assert_called_once()