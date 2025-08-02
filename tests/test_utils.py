"""Common test utilities for async testing patterns."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict


@pytest.fixture
def async_api_mock():
    """Common async mock for API requests."""
    mock = AsyncMock()
    return mock


def create_mock_response(data: Dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock response object for API calls."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data
    return mock_response


def create_async_mock_response(data: Dict[str, Any], status_code: int = 200) -> AsyncMock:
    """Create an async mock response object for API calls."""
    mock_response = AsyncMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = data
    return mock_response