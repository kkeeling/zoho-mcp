"""
Unit tests for the zoho_mcp.logging module.
"""

import unittest
import logging
import json
import io
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from zoho_mcp.logging import (
    setup_logging,
    RequestContextFilter,
    SensitiveDataFilter,
    JsonFormatter,
    set_request_context,
    clear_request_context,
    request_logging_context,
    sanitize_request_data,
    log_api_call,
    log_tool_execution,
)


class TestLoggingConfiguration(unittest.TestCase):
    """Tests for logging configuration functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Save the original logger configuration
        self.original_handlers = logging.getLogger().handlers.copy()
        self.original_level = logging.getLogger().level
        self.original_filters = logging.getLogger().filters.copy()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore the original logger configuration
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        for handler in self.original_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(self.original_level)
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        setup_logging(level="INFO")
        
        # Verify the configuration
        self.assertEqual(root_logger.level, logging.INFO)
        self.assertEqual(len(root_logger.handlers), 1)  # Just stderr handler
        
        # Verify that the stderr handler has the correct formatter
        stderr_handler = root_logger.handlers[0]
        self.assertIsInstance(stderr_handler, logging.StreamHandler)
        self.assertEqual(stderr_handler.stream, sys.stderr)
        
        # Verify filters are applied
        self.assertTrue(any(isinstance(f, RequestContextFilter) for f in stderr_handler.filters))
        self.assertTrue(any(isinstance(f, SensitiveDataFilter) for f in stderr_handler.filters))
    
    def test_setup_logging_with_json(self):
        """Test logging setup with JSON formatting."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        setup_logging(level="DEBUG", use_json=True)
        
        # Verify the configuration
        self.assertEqual(root_logger.level, logging.DEBUG)
        self.assertEqual(len(root_logger.handlers), 1)  # Just stderr handler
        
        # Verify that the stderr handler has the correct formatter
        stderr_handler = root_logger.handlers[0]
        self.assertIsInstance(stderr_handler.formatter, JsonFormatter)


class TestLoggingFilters(unittest.TestCase):
    """Tests for logging filters."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Ensure request context is cleared before each test
        clear_request_context()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Ensure request context is cleared after each test
        clear_request_context()
    
    def test_request_context_filter(self):
        """Test the RequestContextFilter."""
        # Make sure context is clear
        clear_request_context()
        
        filter = RequestContextFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Test without context
        filter.filter(record)
        self.assertEqual(record.request_id, "-")
        self.assertEqual(record.client_id, "-")
        self.assertEqual(record.tool_name, "-")
        
        # Test with context
        set_request_context(request_id="req123", client_id="client456", tool_name="test_tool")
        filter.filter(record)
        self.assertEqual(record.request_id, "req123")
        self.assertEqual(record.client_id, "client456")
        self.assertEqual(record.tool_name, "test_tool")
        
        # Clean up
        clear_request_context()
    
    def test_sensitive_data_filter(self):
        """Test the SensitiveDataFilter."""
        filter = SensitiveDataFilter()
        
        # Test with sensitive data in message
        sensitive_messages = [
            'client_id=abc123&client_secret=xyz789',
            'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
            'Using Zoho-oauthtoken 1000.abcdefg.hijklmn',
            '"password": "supersecret"',
            '"api_key": "1234567890abcdef"',
        ]
        
        for message in sensitive_messages:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg=message,
                args=(),
                exc_info=None
            )
            filter.filter(record)
            
            # Check that sensitive data is redacted
            self.assertNotEqual(record.msg, message, f"Failed to redact: {message}")
            self.assertIn("REDACTED", record.msg)


class TestJsonFormatter(unittest.TestCase):
    """Tests for the JsonFormatter."""
    
    def test_json_formatter(self):
        """Test the JsonFormatter."""
        formatter = JsonFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add request context
        record.request_id = "req123"
        record.client_id = "client456"
        record.tool_name = "test_tool"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse the JSON and check fields
        data = json.loads(formatted)
        self.assertEqual(data["name"], "test")
        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["message"], "Test message")
        self.assertEqual(data["request_id"], "req123")
        self.assertEqual(data["client_id"], "client456")
        self.assertEqual(data["tool_name"], "test_tool")
        self.assertIn("timestamp", data)


class TestRequestContext(unittest.TestCase):
    """Tests for request context functions."""
    
    def tearDown(self):
        """Clear request context after each test."""
        clear_request_context()
    
    def test_set_request_context(self):
        """Test setting request context."""
        set_request_context(request_id="req123", client_id="client456", tool_name="test_tool")
        
        # Use a filter to extract the context
        filter = RequestContextFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        filter.filter(record)
        
        self.assertEqual(record.request_id, "req123")
        self.assertEqual(record.client_id, "client456")
        self.assertEqual(record.tool_name, "test_tool")
    
    def test_clear_request_context(self):
        """Test clearing request context."""
        set_request_context(request_id="req123", client_id="client456", tool_name="test_tool")
        clear_request_context()
        
        # Use a filter to extract the context
        filter = RequestContextFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        filter.filter(record)
        
        self.assertEqual(record.request_id, "-")
        self.assertEqual(record.client_id, "-")
        self.assertEqual(record.tool_name, "-")
    
    def test_request_logging_context(self):
        """Test the request_logging_context context manager."""
        with request_logging_context(
            request_id="req123",
            client_id="client456",
            tool_name="test_tool"
        ):
            # Use a filter to extract the context within the context manager
            filter = RequestContextFilter()
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None
            )
            filter.filter(record)
            
            self.assertEqual(record.request_id, "req123")
            self.assertEqual(record.client_id, "client456")
            self.assertEqual(record.tool_name, "test_tool")
        
        # Context should be cleared after exiting the context manager
        filter.filter(record)
        self.assertEqual(record.request_id, "-")
        self.assertEqual(record.client_id, "-")
        self.assertEqual(record.tool_name, "-")


class TestSanitization(unittest.TestCase):
    """Tests for data sanitization functions."""
    
    def test_sanitize_request_data(self):
        """Test sanitization of request data."""
        # Test with sensitive fields
        data = {
            "username": "testuser",
            "password": "supersecret",
            "api_key": "abcdef123456",
            "settings": {
                "token": "secret-token",
                "refresh_token": "refresh-secret",
                "preferences": {
                    "theme": "dark"
                }
            },
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2", "secret_key": "secret123"}
            ]
        }
        
        sanitized = sanitize_request_data(data)
        
        # Check that sensitive fields are redacted
        self.assertEqual(sanitized["username"], "testuser")  # Not sensitive
        self.assertEqual(sanitized["password"], "REDACTED")
        self.assertEqual(sanitized["api_key"], "REDACTED")
        self.assertEqual(sanitized["settings"]["token"], "REDACTED")
        self.assertEqual(sanitized["settings"]["refresh_token"], "REDACTED")
        self.assertEqual(sanitized["settings"]["preferences"]["theme"], "dark")  # Not sensitive
        self.assertEqual(sanitized["items"][0]["name"], "Item 1")  # Not sensitive
        self.assertEqual(sanitized["items"][1]["secret_key"], "REDACTED")


class TestContextManagers(unittest.TestCase):
    """Tests for logging context managers."""
    
    @patch('logging.Logger.info')
    @patch('logging.Logger.debug')
    @patch('logging.Logger.error')
    def test_log_api_call(self, mock_error, mock_debug, mock_info):
        """Test the log_api_call context manager."""
        logger = logging.getLogger("test")
        
        # Test successful API call
        with log_api_call("GET", "/test", logger) as context:
            context["status_code"] = 200
            context["response_body"] = {"result": "success"}
        
        # Check that appropriate logs were created
        mock_info.assert_any_call("API Request: GET /test")
        mock_info.assert_any_call(
            unittest.mock.ANY  # This will be the response log with timing
        )
        
        # Check response body log (should be at debug level)
        mock_debug.assert_called_once()
        
        # Test API call with error
        mock_info.reset_mock()
        mock_debug.reset_mock()
        mock_error.reset_mock()
        
        try:
            with log_api_call("POST", "/error", logger) as context:
                raise ValueError("API error")
        except ValueError:
            pass
        
        # Check that error was logged
        mock_info.assert_called_once_with("API Request: POST /error")
        mock_error.assert_called_once()
    
    @patch('logging.Logger.info')
    @patch('logging.Logger.debug')
    @patch('logging.Logger.error')
    def test_log_tool_execution(self, mock_error, mock_debug, mock_info):
        """Test the log_tool_execution context manager."""
        logger = logging.getLogger("test")
        
        # Test successful tool execution
        with log_tool_execution("test_tool", logger, param1="value1") as context:
            context["result"] = {"success": True, "data": "test"}
        
        # Check that appropriate logs were created
        mock_info.assert_any_call("Tool execution started: test_tool")
        mock_info.assert_any_call(
            unittest.mock.ANY  # This will be the completion log with timing
        )
        
        # Check result log (should be at debug level)
        mock_debug.assert_any_call(unittest.mock.ANY)
        
        # Test tool execution with error
        mock_info.reset_mock()
        mock_debug.reset_mock()
        mock_error.reset_mock()
        
        try:
            with log_tool_execution("error_tool", logger) as context:
                raise ValueError("Tool error")
        except ValueError:
            pass
        
        # Check that error was logged
        mock_info.assert_called_once_with("Tool execution started: error_tool")
        mock_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()