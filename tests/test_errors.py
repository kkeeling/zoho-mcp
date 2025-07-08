"""
Unit tests for the zoho_mcp.errors module.
"""

import unittest
import json
from typing import Dict, Any

from zoho_mcp.config import settings

from zoho_mcp.errors import (
    ZohoMCPError,
    APIError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    TransportError,
    TransportConfigurationError,
    TransportInitializationError,
    ConfigurationError,
    ToolExecutionError,
    sanitize_error_message,
    handle_exception,
    map_http_status_to_error,
    validate_required_params,
)


class TestErrorClasses(unittest.TestCase):
    """Tests for the error classes in the errors module."""
    
    def test_base_error_class(self):
        """Test the ZohoMCPError base class."""
        error = ZohoMCPError("Test error message")
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.code, "UNKNOWN_ERROR")
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.details, {})
        
        # Test with custom parameters
        error = ZohoMCPError(
            message="Custom error",
            code="CUSTOM_ERROR",
            status_code=418,
            details={"foo": "bar"}
        )
        self.assertEqual(error.message, "Custom error")
        self.assertEqual(error.code, "CUSTOM_ERROR")
        self.assertEqual(error.status_code, 418)
        self.assertEqual(error.details, {"foo": "bar"})
        
        # Test to_dict method
        error_dict = error.to_dict()
        self.assertEqual(error_dict, {
            "error": {
                "code": "CUSTOM_ERROR",
                "message": "Custom error",
                "status": 418,
                "details": {"foo": "bar"}
            }
        })
        
        # Test to_mcp_error method
        mcp_error = error.to_mcp_error()
        self.assertEqual(mcp_error, {
            "code": "CUSTOM_ERROR",
            "message": "Custom error",
            "data": {
                "status": 418,
                "foo": "bar"
            }
        })
    
    def test_api_error(self):
        """Test the APIError class."""
        error = APIError("API error occurred")
        self.assertEqual(error.message, "API error occurred")
        self.assertEqual(error.code, "API_ERROR")
        self.assertEqual(error.status_code, 500)
        
        # Test with custom parameters
        error = APIError(
            message="Custom API error",
            code="CUSTOM_API_ERROR",
            status_code=400
        )
        self.assertEqual(error.message, "Custom API error")
        self.assertEqual(error.code, "CUSTOM_API_ERROR")
        self.assertEqual(error.status_code, 400)
    
    def test_authentication_error(self):
        """Test the AuthenticationError class."""
        error = AuthenticationError()
        self.assertEqual(error.message, "Authentication failed. Please check your credentials.")
        self.assertEqual(error.code, "AUTHENTICATION_FAILED")
        self.assertEqual(error.status_code, 401)
        
        # Test with custom message
        error = AuthenticationError("Invalid token")
        self.assertEqual(error.message, "Invalid token")
        self.assertEqual(error.code, "AUTHENTICATION_FAILED")
        self.assertEqual(error.status_code, 401)
    
    def test_rate_limit_error(self):
        """Test the RateLimitError class."""
        error = RateLimitError()
        self.assertEqual(error.message, "API rate limit exceeded. Please try again later.")
        self.assertEqual(error.code, "RATE_LIMIT_EXCEEDED")
        self.assertEqual(error.status_code, 429)
    
    def test_resource_not_found_error(self):
        """Test the ResourceNotFoundError class."""
        error = ResourceNotFoundError("Contact", "123")
        self.assertEqual(error.message, "Contact with ID 123 not found.")
        self.assertEqual(error.code, "RESOURCE_NOT_FOUND")
        self.assertEqual(error.status_code, 404)
    
    def test_validation_error(self):
        """Test the ValidationError class."""
        error = ValidationError("Validation failed")
        self.assertEqual(error.message, "Validation failed")
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertEqual(error.status_code, 400)
        
        # Test with field errors
        field_errors = {"name": "Field is required", "email": "Invalid email format"}
        error = ValidationError("Validation failed", field_errors)
        self.assertEqual(error.message, "Validation failed")
        self.assertEqual(error.code, "VALIDATION_ERROR")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.details["field_errors"], field_errors)
    
    def test_transport_error(self):
        """Test the TransportError class."""
        error = TransportError("Transport error")
        self.assertEqual(error.message, "Transport error")
        self.assertEqual(error.code, "TRANSPORT_ERROR")
        self.assertEqual(error.status_code, 500)
    
    def test_transport_configuration_error(self):
        """Test the TransportConfigurationError class."""
        error = TransportConfigurationError("Invalid transport config")
        self.assertEqual(error.message, "Invalid transport config")
        self.assertEqual(error.code, "TRANSPORT_CONFIGURATION_ERROR")
        self.assertEqual(error.status_code, 500)
    
    def test_transport_initialization_error(self):
        """Test the TransportInitializationError class."""
        error = TransportInitializationError("Failed to start transport")
        self.assertEqual(error.message, "Failed to start transport")
        self.assertEqual(error.code, "TRANSPORT_INITIALIZATION_ERROR")
        self.assertEqual(error.status_code, 500)
    
    def test_configuration_error(self):
        """Test the ConfigurationError class."""
        error = ConfigurationError("Missing required config")
        self.assertEqual(error.message, "Missing required config")
        self.assertEqual(error.code, "CONFIGURATION_ERROR")
        self.assertEqual(error.status_code, 500)
    
    def test_tool_execution_error(self):
        """Test the ToolExecutionError class."""
        error = ToolExecutionError("Tool execution failed")
        self.assertEqual(error.message, "Tool execution failed")
        self.assertEqual(error.code, "TOOL_EXECUTION_ERROR")
        self.assertEqual(error.status_code, 500)
        
        # Test with tool name
        error = ToolExecutionError("Tool execution failed", "test_tool")
        self.assertEqual(error.message, "Tool execution failed")
        self.assertEqual(error.code, "TOOL_EXECUTION_ERROR")
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.details["tool_name"], "test_tool")


class TestErrorUtilities(unittest.TestCase):
    """Tests for the error utility functions."""
    
    def test_sanitize_error_message(self):
        """Test the sanitize_error_message function."""
        # Test with client_id
        message = "Error with client_id=abc123"
        sanitized = sanitize_error_message(message)
        self.assertNotIn("abc123", sanitized)
        self.assertIn("client_id=REDACTED", sanitized)
        
        # Test with client_secret
        message = "Error with client_secret=xyz789"
        sanitized = sanitize_error_message(message)
        self.assertNotIn("xyz789", sanitized)
        self.assertIn("client_secret=REDACTED", sanitized)
        
        # Test with Bearer token
        message = 'Authorization header: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"'
        sanitized = sanitize_error_message(message)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", sanitized)
        self.assertIn("Bearer REDACTED", sanitized)
        
        # Test with Zoho auth token
        message = 'Using Zoho-oauthtoken 1000.abcdefg.hijklmn'
        sanitized = sanitize_error_message(message)
        self.assertNotIn("1000.abcdefg.hijklmn", sanitized)
        self.assertIn("Zoho-oauthtoken REDACTED", sanitized)
    
    def test_map_http_status_to_error(self):
        """Test the map_http_status_to_error function."""
        # Test known status codes
        error_400 = map_http_status_to_error(400)
        self.assertEqual(error_400["code"], "BAD_REQUEST")
        self.assertEqual(error_400["status"], 400)
        
        error_401 = map_http_status_to_error(401)
        self.assertEqual(error_401["code"], "UNAUTHORIZED")
        self.assertEqual(error_401["status"], 401)
        
        error_404 = map_http_status_to_error(404)
        self.assertEqual(error_404["code"], "NOT_FOUND")
        self.assertEqual(error_404["status"], 404)
        
        error_429 = map_http_status_to_error(429)
        self.assertEqual(error_429["code"], "RATE_LIMIT_EXCEEDED")
        self.assertEqual(error_429["status"], 429)
        
        error_500 = map_http_status_to_error(500)
        self.assertEqual(error_500["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(error_500["status"], 500)
        
        # Test unknown status code
        error_418 = map_http_status_to_error(418)  # I'm a teapot
        self.assertEqual(error_418["code"], "UNKNOWN_ERROR")
        self.assertEqual(error_418["status"], 418)
        
        # Test with custom message
        error_404_custom = map_http_status_to_error(404, "Custom not found message")
        self.assertEqual(error_404_custom["code"], "NOT_FOUND")
        self.assertEqual(error_404_custom["message"], "Custom not found message")
        self.assertEqual(error_404_custom["status"], 404)
    
    def test_handle_exception(self):
        """Test the handle_exception function."""
        # Test with ZohoMCPError
        custom_error = ZohoMCPError(
            message="Test error",
            code="TEST_ERROR",
            status_code=400,
            details={"test": "value"}
        )
        error_response = handle_exception(custom_error, log_exception=False)
        self.assertEqual(error_response["code"], "TEST_ERROR")
        self.assertEqual(error_response["message"], "Test error")
        self.assertEqual(error_response["data"]["status"], 400)
        self.assertEqual(error_response["data"]["test"], "value")
        
        # Test with standard exception
        std_error = ValueError("Invalid value")
        std_error_response = handle_exception(std_error, log_exception=False)
        self.assertEqual(std_error_response["code"], "INTERNAL_ERROR")
        
        # The message will depend on the LOG_LEVEL setting
        # - If DEBUG, it will include the actual error message
        # - Otherwise, it will be a generic message
        if settings.LOG_LEVEL.upper() == "DEBUG":
            self.assertEqual(std_error_response["message"], "Invalid value")
        else:
            self.assertEqual(std_error_response["message"], "An internal error occurred")
            
        self.assertEqual(std_error_response["data"]["status"], 500)
    
    def test_validate_required_params(self):
        """Test the validate_required_params function."""
        # Test with all required params present
        params = {"name": "Test", "email": "test@example.com", "age": 30}
        required = ["name", "email"]
        result = validate_required_params(params, required)
        self.assertIsNone(result)
        
        # Test with missing required params
        params = {"name": "Test", "age": 30}
        required = ["name", "email"]
        result = validate_required_params(params, required)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.code, "VALIDATION_ERROR")
        self.assertIn("email", result.details["field_errors"])
        
        # Test with None values
        params = {"name": "Test", "email": None}
        required = ["name", "email"]
        result = validate_required_params(params, required)
        self.assertIsInstance(result, ValidationError)
        self.assertEqual(result.code, "VALIDATION_ERROR")
        self.assertIn("email", result.details["field_errors"])


if __name__ == "__main__":
    unittest.main()