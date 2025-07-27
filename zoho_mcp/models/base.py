"""
Base models for Zoho Books MCP Integration Server.

This module contains base models used across the MCP server.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

# Define a TypeVar for use in generic models
T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base model for API responses."""
    code: Optional[int] = Field(None, description="Response code from Zoho API")
    message: Optional[str] = Field(None, description="Response message from Zoho API")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic model for paginated API responses.

    Args:
        T: The type of items in the page.
    """
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_more_page: bool = Field(..., description="Whether there are more pages")
    items: List[T] = Field(..., description="List of items in the current page")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    status: str = Field("error", description="Status indicator, always 'error' for errors")
    code: int = Field(..., description="Error code from Zoho API")
    message: str = Field(..., description="Error message from Zoho API")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
