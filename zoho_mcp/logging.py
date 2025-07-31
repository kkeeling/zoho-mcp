"""
Logging utilities for the Zoho Books MCP Integration Server.

This module provides structured logging functionality, including:
- Configurable log formats and levels
- Sanitization of sensitive information in logs
- Context managers for request/response logging
- Handlers for different log destinations
"""

import sys
import os
import json
import logging
import logging.handlers
import traceback
import re
import time
import threading
import platform
from contextlib import contextmanager
from typing import Dict, Any, Optional, Union, List, Generator

from zoho_mcp.config import settings
from zoho_mcp.errors import sanitize_error_message

# ThreadLocal storage for request contex
_request_context = threading.local()


class RequestContextFilter(logging.Filter):
    """
    Filter that adds request context data to log records.
    """
    def filter(self, record):
        """Add request context to the log record if available."""
        record.request_id = getattr(_request_context, 'request_id', '-')
        record.client_id = getattr(_request_context, 'client_id', '-')
        record.tool_name = getattr(_request_context, 'tool_name', '-')
        return True


class SensitiveDataFilter(logging.Filter):
    """
    Filter that redacts sensitive information from log messages.
    """
    def __init__(self):
        super().__init__()
        # Compile regular expressions for performance
        self.patterns = [
            (re.compile(r'client_id=([^&]+)'), 'client_id=REDACTED'),
            (re.compile(r'client_secret=([^&]+)'), 'client_secret=REDACTED'),
            (re.compile(r'Bearer ([^"\'\\s]+)'), 'Bearer REDACTED'),
            (re.compile(r'Zoho-oauthtoken ([^"\'\\s]+)'), 'Zoho-oauthtoken REDACTED'),
            (re.compile(r'refresh_token=([^&]+)'), 'refresh_token=REDACTED'),
            (re.compile(r'access_token=([^&]+)'), 'access_token=REDACTED'),
            (re.compile(r'Authorization: ([^"\'\n]+)'), 'Authorization: REDACTED'),
            (re.compile(r'"password":\s*"([^"]+)"'), '"password": "REDACTED"'),
            (re.compile(r'"api_key":\s*"([^"]+)"'), '"api_key": "REDACTED"'),
            (re.compile(r'"token":\s*"([^"]+)"'), '"token": "REDACTED"'),
        ]

    def filter(self, record):
        """Redact sensitive information from log message."""
        if isinstance(record.msg, str):
            for pattern, replacement in self.patterns:
                record.msg = pattern.sub(replacement, record.msg)

        # Also check for exception info
        if record.exc_info:
            # Sanitize traceback - this is tricky to do reliably, so we use a helper
            if hasattr(record, 'exc_text') and record.exc_text:
                record.exc_text = sanitize_error_message(record.exc_text)

        return True


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs log records as JSON objects.
    """
    def __init__(self, include_time=True):
        super().__init__()
        self.include_time = include_time

    def format(self, record):
        """Format the log record as a JSON string."""
        log_data = {
            'timestamp': record.created,
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }

        # Add request context if available
        if hasattr(record, 'request_id') and record.request_id != '-':
            log_data['request_id'] = record.request_id
        if hasattr(record, 'client_id') and record.client_id != '-':
            log_data['client_id'] = record.client_id
        if hasattr(record, 'tool_name') and record.tool_name != '-':
            log_data['tool_name'] = record.tool_name

        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': sanitize_error_message(''.join(traceback.format_exception(*record.exc_info))),
            }

        return json.dumps(log_data)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    use_json: bool = False,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure the logging system for the application.

    Args:
        level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (None for stderr)
        use_json: Whether to use JSON formatting
        max_bytes: Maximum size of each log file
        backup_count: Number of backup log files to keep
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Determine log level
    log_level = level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Create formatter
    formatter: Union[JsonFormatter, logging.Formatter]
    if use_json:
        formatter = JsonFormatter()
    else:
        log_format = settings.LOG_FORMAT
        formatter = logging.Formatter(log_format)

    # Set up handlers
    handlers: List[logging.Handler] = []

    # Always add stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    handlers.append(stderr_handler)

    # Add file handler if log_file is specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Add filters
    request_filter = RequestContextFilter()
    sensitive_filter = SensitiveDataFilter()

    # Apply handlers and filters to root logger
    for handler in handlers:
        handler.addFilter(sensitive_filter)
        handler.addFilter(request_filter)
        root_logger.addHandler(handler)

    # Initialize module logger
    logger = logging.getLogger('zoho_mcp')
    logger.info(f"Logging initialized at level {log_level}")

    # Log Python version and platform info at DEBUG level
    logger.debug(f"Python {platform.python_version()} on {platform.platform()}")


def set_request_context(
    request_id: Optional[str] = None,
    client_id: Optional[str] = None,
    tool_name: Optional[str] = None,
) -> None:
    """
    Set context variables for the current request/thread.

    Args:
        request_id: Unique identifier for the reques
        client_id: Identifier for the clien
        tool_name: Name of the tool being executed
    """
    if request_id:
        _request_context.request_id = request_id
    if client_id:
        _request_context.client_id = client_id
    if tool_name:
        _request_context.tool_name = tool_name


def clear_request_context() -> None:
    """Clear request context variables for the current thread."""
    if hasattr(_request_context, 'request_id'):
        delattr(_request_context, 'request_id')
    if hasattr(_request_context, 'client_id'):
        delattr(_request_context, 'client_id')
    if hasattr(_request_context, 'tool_name'):
        delattr(_request_context, 'tool_name')


@contextmanager
def request_logging_context(
    **context_vars
) -> Generator[None, None, None]:
    """
    Context manager for handling request context in logs.

    Args:
        **context_vars: Key-value pairs to set in the request contex

    Yields:
        None
    """
    # Use a sentinel to distinguish between None and not-set
    _sentinel = object()
    
    # Save original values
    original_values = {}
    for key, value in context_vars.items():
        original_values[key] = getattr(_request_context, key, _sentinel)
        setattr(_request_context, key, value)

    try:
        yield
    finally:
        # Restore original values
        for key, original_value in original_values.items():
            if original_value is _sentinel:
                # Attribute didn't exist before, remove it
                if hasattr(_request_context, key):
                    delattr(_request_context, key)
            else:
                # Restore original value (could be None)
                setattr(_request_context, key, original_value)


def sanitize_request_data(data: Any) -> Any:
    """
    Sanitize request data to remove sensitive information.

    Args:
        data: Request data to sanitize

    Returns:
        Sanitized request data
    """
    if isinstance(data, dict):
        result = {}
        # Define sensitive fields to redac
        sensitive_fields = {
            'password', 'token', 'api_key', 'client_secret', 'refresh_token',
            'access_token', 'auth_token', 'api_secret', 'secret', 'Authorization',
            'auth', 'credentials'
        }

        for key, value in data.items():
            if key.lower() in sensitive_fields or any(s in key.lower() for s in {'password', 'token', 'secret', 'key'}):
                result[key] = 'REDACTED'
            elif isinstance(value, (dict, list)):
                result[key] = sanitize_request_data(value)
            else:
                result[key] = value
        return result
    elif isinstance(data, list):
        return [sanitize_request_data(item) for item in data]
    else:
        return data


@contextmanager
def log_api_call(
    method: str,
    endpoint: str,
    logger: logging.Logger,
    include_request_body: bool = True,
    include_response_body: bool = True
) -> Generator[Dict[str, Any], None, None]:
    """
    Context manager for logging API requests and responses.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoin
        logger: Logger instance
        include_request_body: Whether to include the request body in logs
        include_response_body: Whether to include the response body in logs

    Yields:
        Dictionary to store the response and any context
    """
    context: Dict[str, Any] = {}
    start_time = time.time()

    logger.info(f"API Request: {method} {endpoint}")

    try:
        yield context

        # Log response if available
        response_time_ms = (time.time() - start_time) * 1000
        status_code = context.get('status_code', 'unknown')

        log_msg = f"API Response: {method} {endpoint} - Status: {status_code}, Time: {response_time_ms:.2f}ms"

        # Log at appropriate level based on status code
        if isinstance(status_code, int):
            if status_code < 400:
                logger.info(log_msg)
            elif status_code < 500:
                logger.warning(log_msg)
            else:
                logger.error(log_msg)
        else:
            logger.info(log_msg)

        # Log response body if requested and available
        if include_response_body and 'response_body' in context:
            body = sanitize_request_data(context['response_body'])
            logger.debug(f"Response body: {json.dumps(body, indent=2)}")

    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        logger.error(
            f"API Error: {method} {endpoint} - Error: {e}, Time: {response_time_ms:.2f}ms",
            exc_info=True
        )
        raise


@contextmanager
def log_tool_execution(
    tool_name: str,
    logger: logging.Logger,
    **context_vars
) -> Generator[Dict[str, Any], None, None]:
    """
    Context manager for logging tool execution.

    Args:
        tool_name: Name of the tool being executed
        logger: Logger instance
        **context_vars: Additional context variables

    Yields:
        Dictionary to store execution context and results
    """
    context: Dict[str, Any] = {}
    start_time = time.time()

    # Set the tool name in request context for log filtering
    # Use a sentinel to distinguish between None and not-set
    _sentinel = object()
    original_tool_name = getattr(_request_context, 'tool_name', _sentinel)
    _request_context.tool_name = tool_name

    # Set any additional context variables
    original_context = {}
    for key, value in context_vars.items():
        original_context[key] = getattr(_request_context, key, _sentinel)
        setattr(_request_context, key, value)

    logger.info(f"Tool execution started: {tool_name}")
    logger.debug(f"Tool parameters: {sanitize_request_data(context_vars)}")

    try:
        yield context

        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Tool execution completed: {tool_name} - Time: {execution_time_ms:.2f}ms")

        # Log sanitized results if available
        if 'result' in context:
            sanitized_result = sanitize_request_data(context['result'])
            logger.debug(f"Tool result: {json.dumps(sanitized_result, indent=2)}")

    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Tool execution failed: {tool_name} - Error: {e}, Time: {execution_time_ms:.2f}ms",
            exc_info=True
        )
        raise
    finally:
        # Restore original context
        if original_tool_name is _sentinel:
            # Attribute didn't exist before, remove it
            if hasattr(_request_context, 'tool_name'):
                delattr(_request_context, 'tool_name')
        else:
            # Restore original value (could be None)
            _request_context.tool_name = original_tool_name

        for key, value in original_context.items():
            if value is _sentinel:
                # Attribute didn't exist before, remove it
                if hasattr(_request_context, key):
                    delattr(_request_context, key)
            else:
                # Restore original value (could be None)
                setattr(_request_context, key, value)
