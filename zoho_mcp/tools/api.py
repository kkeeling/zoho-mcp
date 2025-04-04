"""
Zoho Books API client module.

This module handles API requests to the Zoho Books API,
including authentication, token refresh, and error handling.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import httpx

from zoho_mcp.config import settings

logger = logging.getLogger(__name__)

# Constants
TOKEN_CACHE_FILE = Path(settings.TOKEN_CACHE_PATH)
API_BASE_URL = settings.ZOHO_API_BASE_URL
AUTH_BASE_URL = settings.ZOHO_AUTH_BASE_URL
ORG_ID = settings.ZOHO_ORGANIZATION_ID


class ZohoAPIError(Exception):
    """Exception raised for errors in the Zoho API responses."""
    def __init__(self, status_code: int, message: str, code: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.code = code
        super().__init__(f"Zoho API error {code or status_code}: {message}")


class ZohoAuthenticationError(ZohoAPIError):
    """Exception raised for authentication errors."""
    pass


class ZohoRequestError(ZohoAPIError):
    """Exception raised for request errors."""
    pass


class ZohoRateLimitError(ZohoAPIError):
    """Exception raised when rate limits are exceeded."""
    pass


def _load_token_from_cache() -> Dict[str, Any]:
    """
    Load the OAuth token from the cache file.
    
    Returns:
        A dictionary with the token details including:
        - access_token: The OAuth access token
        - expires_at: The token expiry timestamp
    """
    if not TOKEN_CACHE_FILE.exists():
        return {}
    
    try:
        with open(TOKEN_CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load token from cache: {str(e)}")
        return {}


def _save_token_to_cache(token_data: Dict[str, Any]) -> None:
    """
    Save the OAuth token to the cache file.
    
    Args:
        token_data: Dictionary with token details including:
        - access_token: The OAuth access token
        - expires_at: The token expiry timestamp
    """
    # Create directory if it doesn't exist
    TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(TOKEN_CACHE_FILE, "w") as f:
            json.dump(token_data, f)
    except IOError as e:
        logger.warning(f"Failed to save token to cache: {str(e)}")


def _get_access_token(force_refresh: bool = False) -> str:
    """
    Get a valid OAuth access token, refreshing if necessary.
    
    Args:
        force_refresh: If True, force a token refresh regardless of expiry.
        
    Returns:
        A valid OAuth access token.
        
    Raises:
        ZohoAuthenticationError: If unable to obtain a token.
    """
    # Check if we have a cached and valid token
    token_data = _load_token_from_cache()
    current_time = time.time()
    
    # If we have a token and it's not expired and we're not forcing a refresh, use it
    if (
        not force_refresh
        and token_data
        and "access_token" in token_data
        and "expires_at" in token_data
        and token_data["expires_at"] > current_time + 60  # Add buffer
    ):
        logger.debug("Using cached access token")
        return token_data["access_token"]
    
    logger.info("Refreshing Zoho OAuth token")
    
    # Prepare the refresh token request
    refresh_token = settings.ZOHO_REFRESH_TOKEN
    client_id = settings.ZOHO_CLIENT_ID
    client_secret = settings.ZOHO_CLIENT_SECRET
    
    if not all([refresh_token, client_id, client_secret]):
        raise ZohoAuthenticationError(
            401, "Missing OAuth credentials", "MISSING_CREDENTIALS"
        )
    
    url = f"{AUTH_BASE_URL}/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }
    
    try:
        response = httpx.post(url, params=params, timeout=30.0)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        if "access_token" not in data:
            logger.error(f"Unexpected token response: {data}")
            raise ZohoAuthenticationError(
                401, "Invalid token response", "INVALID_TOKEN_RESPONSE"
            )
        
        # Cache the token with its expiry time
        # Zoho tokens are valid for 1 hour (3600 seconds)
        token_data = {
            "access_token": data["access_token"],
            "expires_at": current_time + int(data.get("expires_in", 3600)),
        }
        
        _save_token_to_cache(token_data)
        logger.info("Successfully refreshed OAuth token")
        
        return token_data["access_token"]
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during token refresh: {e.response.status_code}")
        response_data = {}
        if e.response.content:
            try:
                response_data = e.response.json()
            except json.JSONDecodeError:
                response_data = {}
        message = response_data.get("message", str(e))
        raise ZohoAuthenticationError(e.response.status_code, message)
        
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.error(f"Request error during token refresh: {str(e)}")
        raise ZohoAuthenticationError(500, f"Request failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise ZohoAuthenticationError(500, f"Unexpected error: {str(e)}")


def _handle_api_error(response: httpx.Response) -> None:
    """
    Handle error responses from the Zoho API.
    
    Args:
        response: The HTTP response from Zoho.
        
    Raises:
        ZohoAPIError: With the appropriate error details.
    """
    status_code = response.status_code
    
    try:
        data = response.json()
        # Zoho API errors are typically in the format:
        # {"code": 1000, "message": "Error message"}
        message = data.get("message", "Unknown error")
        code = data.get("code", None)
    except (json.JSONDecodeError, ValueError):
        message = response.text or f"HTTP error {status_code}"
        code = None
    
    if status_code == 401:
        raise ZohoAuthenticationError(status_code, message, code)
    elif status_code == 429:
        raise ZohoRateLimitError(status_code, message, code)
    else:
        raise ZohoRequestError(status_code, message, code)


async def zoho_api_request_async(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    retry_auth: bool = True,
) -> Dict[str, Any]:
    """
    Make an async request to the Zoho Books API.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint, starting with /
        params: Query parameters
        json_data: JSON data for POST/PUT requests
        headers: Additional HTTP headers
        retry_auth: Whether to retry once after authentication failures
        
    Returns:
        The JSON response from the API
        
    Raises:
        ZohoAPIError: If the API returns an error
    """
    if params is None:
        params = {}
    
    # Add organization_id to every request
    if "organization_id" not in params and ORG_ID:
        params["organization_id"] = ORG_ID
    
    # Get access token for authentication
    try:
        access_token = _get_access_token()
    except ZohoAuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise
    
    # Prepare headers
    request_headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json",
    }
    
    if headers:
        request_headers.update(headers)
    
    # Prepare URL (ensure endpoint starts with /)
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    # Make the request
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=request_headers,
            )
            
            # Check if the request was successful
            if response.status_code >= 400:
                # If we get a 401 Unauthorized and retry_auth is True,
                # refresh the token and try again
                if response.status_code == 401 and retry_auth:
                    logger.info("Received 401, refreshing token and retrying")
                    _get_access_token(force_refresh=True)
                    return await zoho_api_request_async(
                        method, endpoint, params, json_data, headers,
                        retry_auth=False
                    )
                else:
                    _handle_api_error(response)
            
            # Parse JSON response
            try:
                return response.json()
            except Exception:  # Handle any JSON parsing errors
                # If the response is not JSON, return a dict with the text
                if response.status_code == 204:  # No Content
                    return {
                        "status": "success",
                        "message": "Operation completed successfully"
                    }
                return {"text": response.text}
                
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.error(f"Request error: {str(e)}")
        raise ZohoRequestError(500, f"Request failed: {str(e)}")


def zoho_api_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    retry_auth: bool = True,
) -> Dict[str, Any]:
    """
    Make a synchronous request to the Zoho Books API.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint, starting with /
        params: Query parameters
        json: JSON data for POST/PUT requests
        headers: Additional HTTP headers
        retry_auth: Whether to retry once after authentication failures
        
    Returns:
        The JSON response from the API
        
    Raises:
        ZohoAPIError: If the API returns an error
    """
    if params is None:
        params = {}
    
    # Add organization_id to every request
    if "organization_id" not in params and ORG_ID:
        params["organization_id"] = ORG_ID
    
    # Get access token for authentication
    try:
        access_token = _get_access_token()
    except ZohoAuthenticationError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise
    
    # Prepare headers
    request_headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json",
    }
    
    if headers:
        request_headers.update(headers)
    
    # Prepare URL (ensure endpoint starts with /)
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    # Make the request
    try:
        with httpx.Client(timeout=settings.REQUEST_TIMEOUT) as client:
            response = client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=request_headers,
            )
            
            # Check if the request was successful
            if response.status_code >= 400:
                # If we get a 401 Unauthorized and retry_auth is True,
                # refresh the token and try again
                if response.status_code == 401 and retry_auth:
                    logger.info("Received 401, refreshing token and retrying")
                    _get_access_token(force_refresh=True)
                    return zoho_api_request(
                        method, endpoint, params, json, headers,
                        retry_auth=False
                    )
                else:
                    _handle_api_error(response)
            
            # Parse JSON response
            try:
                return response.json()
            except Exception:  # Handle any JSON parsing errors
                # If the response is not JSON, return a dict with the text
                if response.status_code == 204:  # No Content
                    return {
                        "status": "success",
                        "message": "Operation completed successfully"
                    }
                return {"text": response.text}
                
    except (httpx.RequestError, httpx.TimeoutException) as e:
        logger.error(f"Request error: {str(e)}")
        raise ZohoRequestError(500, f"Request failed: {str(e)}")


# Utility function to validate Zoho credentials
def validate_credentials() -> Tuple[bool, Optional[str]]:
    """
    Validate the Zoho API credentials.
    
    Returns:
        A tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # Check if required settings are present
        settings.validate()
        
        # Try to get an access token
        _get_access_token(force_refresh=True)
        
        # Make a simple request to test the token
        response = zoho_api_request(
            method="GET",
            endpoint="/organizations",
        )
        
        # Check if our organization ID exists in the response
        orgs = response.get("organizations", [])
        org_ids = [org.get("organization_id") for org in orgs]
        
        if ORG_ID not in org_ids:
            return False, f"Organization ID {ORG_ID} not found in Zoho Books account."
        
        return True, None
        
    except (ZohoAuthenticationError, ZohoRequestError, ValueError) as e:
        return False, str(e)


# Expose main functions
__all__ = [
    "zoho_api_request",
    "zoho_api_request_async",
    "validate_credentials",
    "ZohoAPIError",
    "ZohoAuthenticationError",
    "ZohoRequestError",
    "ZohoRateLimitError",
]