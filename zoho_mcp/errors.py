"""
Error handling utilities for the Zoho Books MCP Integration Server.

This module provides centralized error handling for the MCP server, including:
- Custom exception classes for different error types
- Error code definitions
- Error translation utilities for MCP-compatible error responses
- Functions for handling various error scenarios
"""

import logging
import traceback
import re
from typing import Dict, Any, Optional, Union, List

from zoho_mcp.config import settings

logger = logging.getLogger("zoho_mcp.errors")


# Base Error Classes
class ZohoMCPError(Exception):
    """Base exception class for all Zoho MCP errors."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for API responses."""
        result = {
            "error": {
                "code": self.code,
                "message": self.message,
                "status": self.status_code,
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result

    def to_mcp_error(self) -> Dict[str, Any]:
        """Convert the error to an MCP-compatible error response."""
        return {
            "code": self.code,
            "message": self.message,
            "data": {
                "status": self.status_code,
                **self.details
            }
        }


# API Errors
class APIError(ZohoMCPError):
    """Error for API-related issues."""
    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status_code, details)


class RateLimitError(APIError):
    """Error for rate limit exceeded issues."""
    def __init__(
        self,
        message: str = "API rate limit exceeded. Please try again later.",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


class AuthenticationError(APIError):
    """Error for authentication issues."""
    def __init__(
        self,
        message: str = "Authentication failed. Please check your credentials.",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details
        )


class ResourceNotFoundError(APIError):
    """Error for resource not found issues."""
    def __init__(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} with ID {resource_id} not found."
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details
        )


# Validation Errors
class ValidationError(ZohoMCPError):
    """Error for validation issues."""
    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if field_errors:
            combined_details["field_errors"] = field_errors

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=combined_details
        )


# Transport Errors
class TransportError(ZohoMCPError):
    """Base error for transport-related issues."""
    def __init__(
        self,
        message: str,
        code: str = "TRANSPORT_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, status_code, details)


class TransportConfigurationError(TransportError):
    """Error for transport configuration issues."""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="TRANSPORT_CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class TransportInitializationError(TransportError):
    """Error for transport initialization issues."""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="TRANSPORT_INITIALIZATION_ERROR",
            status_code=500,
            details=details
        )


# Configuration Errors
class ConfigurationError(ZohoMCPError):
    """Error for configuration issues."""
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


# Tool Execution Errors
class ToolExecutionError(ZohoMCPError):
    """Error for tool execution issues."""
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if tool_name:
            combined_details["tool_name"] = tool_name

        super().__init__(
            message=message,
            code="TOOL_EXECUTION_ERROR",
            status_code=500,
            details=combined_details
        )


# Error Mapping Utilities
API_ERROR_MAP = {
    400: {"code": "BAD_REQUEST", "message": "Invalid request parameters"},
    401: {"code": "UNAUTHORIZED", "message": "Authentication failed"},
    403: {"code": "FORBIDDEN", "message": "Permission denied"},
    404: {"code": "NOT_FOUND", "message": "Resource not found"},
    429: {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded"},
    500: {"code": "INTERNAL_SERVER_ERROR", "message": "Internal server error"},
    502: {"code": "BAD_GATEWAY", "message": "Bad gateway"},
    503: {"code": "SERVICE_UNAVAILABLE", "message": "Service unavailable"},
    504: {"code": "GATEWAY_TIMEOUT", "message": "Gateway timeout"},
}


def map_http_status_to_error(status_code: int, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Map HTTP status code to standard error response.

    Args:
        status_code: HTTP status code
        message: Custom error message (optional)

    Returns:
        Error dict with code, message, and status
    """
    error_info = API_ERROR_MAP.get(status_code, {
        "code": "UNKNOWN_ERROR",
        "message": "An unknown error occurred"
    })

    return {
        "code": error_info["code"],
        "message": message or error_info["message"],
        "status": status_code
    }


# Pre-compiled patterns for performance
SENSITIVE_PATTERNS = [
    (re.compile(r'client_id=([^&]+)'), r'client_id=REDACTED'),
    (re.compile(r'client_secret=([^&]+)'), r'client_secret=REDACTED'),
    (re.compile(r'Bearer ([^"\' \t]+)'), r'Bearer REDACTED'),
    (re.compile(r'Zoho-oauthtoken ([^"\' \t]+)'), r'Zoho-oauthtoken REDACTED'),
    (re.compile(r'refresh_token=([^&]+)'), r'refresh_token=REDACTED'),
    (re.compile(r'access_token=([^&]+)'), r'access_token=REDACTED'),
    (re.compile(r'Authorization: ([^"\'\n]+)'), r'Authorization: REDACTED'),
    (re.compile(r'"password":\s*"([^"]+)"'), r'"password": "REDACTED"'),
    (re.compile(r'"api_key":\s*"([^"]+)"'), r'"api_key": "REDACTED"'),
    (re.compile(r'"token":\s*"([^"]+)"'), r'"token": "REDACTED"'),
    # Add more patterns as needed
]


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error message to remove sensitive information.

    Args:
        message: Raw error message

    Returns:
        Sanitized error message
    """
    sanitized = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def format_exception_for_log(exc: Exception) -> str:
    """
    Format exception for logging, with sensitive information redacted.

    Args:
        exc: Exception to forma

    Returns:
        Formatted exception string
    """
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    formatted = "".join(tb)
    return sanitize_error_message(formatted)


def handle_exception(
    exc: Exception,
    log_exception: bool = True
) -> Dict[str, Any]:
    """
    Handle an exception and convert it to an MCP-compatible error response.

    Args:
        exc: The exception to handle
        log_exception: Whether to log the exception

    Returns:
        MCP-compatible error response dictionary
    """
    # Determine the appropriate error response based on exception type
    if isinstance(exc, ZohoMCPError):
        error_response = exc.to_mcp_error()
    else:
        # For non-ZohoMCPError exceptions, create a generic error
        error_response = {
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "data": {"status": 500}
        }

        # In development mode, include more details
        if settings.LOG_LEVEL.upper() == "DEBUG":
            error_response["message"] = str(exc)

    # Log the exception if requested
    if log_exception:
        logger.error(
            f"Exception: {exc.__class__.__name__}: {sanitize_error_message(str(exc))}",
            exc_info=settings.LOG_LEVEL.upper() == "DEBUG"
        )

    return error_response


def validate_required_params(params: Dict[str, Any], required: List[str]) -> Optional[ValidationError]:
    """
    Validate that all required parameters are present.

    Args:
        params: Dictionary of parameters
        required: List of required parameter names

    Returns:
        ValidationError if any required parameters are missing, None otherwise
    """
    missing = [param for param in required if param not in params or params[param] is None]

    if missing:
        field_errors = {param: "This field is required" for param in missing}
        return ValidationError(
            message=f"Missing required parameters: {', '.join(missing)}",
            field_errors=field_errors
        )

    return None
