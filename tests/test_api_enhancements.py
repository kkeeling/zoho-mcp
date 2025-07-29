"""
Test suite for API enhancements: caching and rate limiting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import httpx

from zoho_mcp.tools.api import (
    _generate_cache_key,
    _get_cached_response,
    _set_cached_response,
    clear_cache,
    _handle_rate_limit_async,
    _check_global_rate_limit,
    zoho_api_request_async,
    _response_cache,
    MAX_RETRIES,
    INITIAL_BACKOFF,
    BACKOFF_MULTIPLIER,
)
import zoho_mcp.tools.api as api_module


class TestCaching:
    """Test suite for caching functionality."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()
    
    def test_generate_cache_key_for_get_requests(self):
        """Test cache key generation for GET requests."""
        # Test GET request
        key = _generate_cache_key("GET", "/invoices", {"page": 1}, None)
        assert key != ""
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length
        
        # Test that same parameters generate same key
        key2 = _generate_cache_key("GET", "/invoices", {"page": 1}, None)
        assert key == key2
        
        # Test that different parameters generate different keys
        key3 = _generate_cache_key("GET", "/invoices", {"page": 2}, None)
        assert key != key3
    
    def test_generate_cache_key_for_non_get_requests(self):
        """Test that non-GET requests don't generate cache keys."""
        key = _generate_cache_key("POST", "/invoices", None, {"data": "test"})
        assert key == ""
        
        key = _generate_cache_key("PUT", "/invoices/123", None, {"data": "test"})
        assert key == ""
        
        key = _generate_cache_key("DELETE", "/invoices/123", None, None)
        assert key == ""
    
    def test_cache_operations(self):
        """Test cache get and set operations."""
        cache_key = "test_key_123"
        test_response = {"invoices": [{"id": 1}], "total": 1}
        
        # Test cache miss
        assert _get_cached_response(cache_key) is None
        
        # Test cache set
        _set_cached_response(cache_key, test_response)
        
        # Test cache hit
        cached = _get_cached_response(cache_key)
        assert cached == test_response
        
        # Test clear cache
        clear_cache()
        assert _get_cached_response(cache_key) is None
    
    def test_cache_expiry(self):
        """Test that cached responses expire after TTL."""
        cache_key = "test_expiry_key"
        test_response = {"data": "test"}
        
        # Set cached response
        _set_cached_response(cache_key, test_response)
        
        # Manually modify the expiry time to be in the past
        _response_cache[cache_key] = (test_response, datetime.now() - timedelta(seconds=1))
        
        # Should return None due to expiry
        assert _get_cached_response(cache_key) is None
        
        # Cache entry should be removed
        assert cache_key not in _response_cache
    
    @pytest.mark.asyncio
    async def test_caching_in_api_request(self, monkeypatch):
        """Test that caching works in the actual API request function."""
        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invoices": [{"id": 1}]}
        
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)
        
        # Mock httpx.AsyncClient to return our mock client
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # Mock token retrieval
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # First request should hit the API
                result1 = await zoho_api_request_async("GET", "/invoices", params={"page": 1})
                assert result1 == {"invoices": [{"id": 1}]}
                assert mock_client.request.call_count == 1
                
                # Second request with same parameters should use cache
                result2 = await zoho_api_request_async("GET", "/invoices", params={"page": 1})
                assert result2 == {"invoices": [{"id": 1}]}
                assert mock_client.request.call_count == 1  # Still 1, not incremented
                
                # Request with different parameters should hit API again
                result3 = await zoho_api_request_async("GET", "/invoices", params={"page": 2})
                assert mock_client.request.call_count == 2


class TestRateLimiting:
    """Test suite for rate limiting functionality."""
    
    def setup_method(self):
        """Reset rate limit state before each test."""
        api_module._rate_limit_retry_after = None
    
    @pytest.mark.asyncio
    async def test_handle_rate_limit_with_retry_after_header(self):
        """Test rate limit handling with Retry-After header."""
        # Mock response with Retry-After header in seconds
        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "5"}
        
        wait_time = await _handle_rate_limit_async(mock_response, 0)
        
        # Should return the value from header
        assert wait_time == 5.0
        
        # Global rate limit should be set
        assert api_module._rate_limit_retry_after is not None
        assert api_module._rate_limit_retry_after > datetime.now()
    
    @pytest.mark.asyncio
    async def test_handle_rate_limit_with_exponential_backoff(self):
        """Test rate limit handling with exponential backoff."""
        # Mock response without Retry-After header
        mock_response = MagicMock()
        mock_response.headers = {}
        
        # Test exponential backoff for different attempts
        wait_time_0 = await _handle_rate_limit_async(mock_response, 0)
        assert INITIAL_BACKOFF * 0.75 <= wait_time_0 <= INITIAL_BACKOFF * 1.25
        
        wait_time_1 = await _handle_rate_limit_async(mock_response, 1)
        expected_1 = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** 1)
        assert expected_1 * 0.75 <= wait_time_1 <= expected_1 * 1.25
        
        wait_time_2 = await _handle_rate_limit_async(mock_response, 2)
        expected_2 = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** 2)
        assert expected_2 * 0.75 <= wait_time_2 <= expected_2 * 1.25
    
    def test_check_global_rate_limit(self):
        """Test global rate limit checking."""
        # No rate limit set
        assert _check_global_rate_limit() is None
        
        # Set future rate limit
        api_module._rate_limit_retry_after = datetime.now() + timedelta(seconds=5)
        wait_time = _check_global_rate_limit()
        assert wait_time is not None
        assert 4 < wait_time <= 5
        
        # Set past rate limit
        api_module._rate_limit_retry_after = datetime.now() - timedelta(seconds=1)
        assert _check_global_rate_limit() is None
        assert api_module._rate_limit_retry_after is None  # Should be cleared
    
    @pytest.mark.asyncio
    async def test_rate_limit_retry_in_api_request(self):
        """Test that rate limiting retry works in the API request function."""
        # Mock responses
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "0.1"}  # Short retry for testing
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"success": True}
        
        # Mock client that returns 429 first, then 200
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(side_effect=[rate_limit_response, success_response])
        
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # Should retry and succeed
                result = await zoho_api_request_async("POST", "/invoices", json_data={"test": "data"})
                assert result == {"success": True}
                assert mock_client.request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_rate_limit_max_retries_exceeded(self):
        """Test that rate limiting gives up after max retries."""
        # Mock response that always returns 429
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "0.01"}  # Very short for testing
        rate_limit_response.json.return_value = {"message": "Rate limit exceeded"}
        
        # Mock client that always returns 429
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=rate_limit_response)
        
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # Should raise exception after max retries
                with pytest.raises(Exception) as exc_info:
                    await zoho_api_request_async("POST", "/invoices", json_data={"test": "data"})
                
                # Should have tried MAX_RETRIES times
                assert mock_client.request.call_count == MAX_RETRIES
    
    @pytest.mark.asyncio
    async def test_network_error_retry(self):
        """Test that network errors are retried with exponential backoff."""
        # Mock successful response for final attempt
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"success": True}
        
        # Mock client that raises network error first, then succeeds
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(
            side_effect=[httpx.RequestError("Network error"), success_response]
        )
        
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with patch("zoho_mcp.tools.api._get_access_token", return_value="test_token"):
                # Should retry and succeed
                result = await zoho_api_request_async("GET", "/invoices")
                assert result == {"success": True}
                assert mock_client.request.call_count == 2