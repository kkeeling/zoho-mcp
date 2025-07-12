"""
Transport configuration utilities for the Zoho Books MCP Integration Server.

This module provides functions to configure and initialize different
transport types (STDIO, HTTP/SSE, WebSocket) for the FastMCP server.
It also includes helper functions for command-line argument parsing
and transport-specific error handling.
"""

import logging
import argparse
from typing import Any, Dict, Optional, Tuple, Callable, TypeVar, cast

from mcp.server.fastmcp import FastMCP

from zoho_mcp.config import settings

T = TypeVar('T')

logger = logging.getLogger("zoho_mcp.transport")


class TransportError(Exception):
    """Base exception for transport-related errors."""
    pass


class TransportConfigurationError(TransportError):
    """Exception raised for errors in transport configuration."""
    pass


class TransportInitializationError(TransportError):
    """Exception raised for errors during transport initialization."""
    pass


def setup_stdio_transport(
    mcp_server: FastMCP, **kwargs: Any
) -> None:
    """
    Configure and start the STDIO transport for the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        **kwargs: Additional arguments (unused for STDIO)

    Raises:
        TransportInitializationError: If the transport fails to start
    """
    try:
        logger.info("Starting MCP server in STDIO mode")
        
        # In our version of FastMCP, we can directly call run with "stdio" transport
        mcp_server.run(transport="stdio")
        
    except Exception as e:
        logger.error(f"Failed to start STDIO transport: {str(e)}")
        msg = f"Failed to start STDIO transport: {str(e)}"
        raise TransportInitializationError(msg) from e


def setup_http_transport(
    mcp_server: FastMCP,
    host: str = settings.DEFAULT_HOST,
    port: int = settings.DEFAULT_PORT,
    cors_origins: Optional[list] = None,
    **kwargs: Any
) -> None:
    """
    Configure and start the HTTP/SSE transport for the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        host: The host address to bind to
        port: The port to listen on
        cors_origins: List of allowed CORS origins
        **kwargs: Additional arguments for HTTP configuration

    Raises:
        TransportInitializationError: If the transport fails to start
    """
    try:
        # Default CORS configuration if not provided
        if cors_origins is None:
            cors_origins = settings.CORS_ORIGINS

        logger.info(f"Starting MCP server in HTTP/SSE mode on {host}:{port}")
        logger.debug(f"CORS configuration: {cors_origins}")

        # Configure settings for the SSE transport
        # These settings will be used by the FastMCP internally
        mcp_server.settings.host = host
        mcp_server.settings.port = port
        
        # Process any other keyword arguments
        for key, value in kwargs.items():
            if hasattr(mcp_server.settings, key):
                setattr(mcp_server.settings, key, value)
        
        # Run the server with SSE transport
        mcp_server.run(transport="sse")
        
    except Exception as e:
        error_msg = f"HTTP/SSE transport error on {host}:{port}: {str(e)}"
        logger.error(error_msg)
        msg = f"Failed to start HTTP/SSE transport on {host}:{port}:"
        msg += f" {str(e)}"
        raise TransportInitializationError(msg) from e


def setup_websocket_transport(
    mcp_server: FastMCP,
    host: str = settings.DEFAULT_HOST,
    port: int = settings.DEFAULT_WS_PORT,
    **kwargs: Any
) -> None:
    """
    Configure and start the WebSocket transport for the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        host: The host address to bind to
        port: The port to listen on
        **kwargs: Additional arguments for WebSocket configuration

    Raises:
        TransportInitializationError: If the transport fails to start
    """
    # Note: The current version of the MCP SDK does not support WebSocket transport
    # through the FastMCP.run() method. It only supports 'stdio' and 'sse' transports.
    # This function is maintained for backward compatibility but will raise an error.
    
    error_msg = (
        "WebSocket transport is not supported in the current version of the MCP SDK. "
        "Please use STDIO or HTTP/SSE transport instead."
    )
    logger.error(error_msg)
    raise TransportInitializationError(error_msg)


def get_transport_handler(transport_type: str) -> Callable[[FastMCP], None]:
    """
    Get the appropriate transport handler function based on the transport type.

    Args:
        transport_type: Type of transport (stdio, http, websocket)

    Returns:
        The transport handler function

    Raises:
        TransportConfigurationError: If the transport type is not supported
    """
    transport_handlers = {
        "stdio": setup_stdio_transport,
        "http": setup_http_transport,
        "websocket": setup_websocket_transport,
    }

    if transport_type not in transport_handlers:
        supported = ", ".join(transport_handlers.keys())
        msg = f"Unsupported transport type: {transport_type}. "
        msg += f"Supported types are: {supported}"
        raise TransportConfigurationError(msg)

    # Cast the function to the expected callable type
    handler = cast(Callable[[FastMCP], None],
                   transport_handlers[transport_type])
    return handler


def configure_transport_from_args(
    args: argparse.Namespace
) -> Tuple[str, Dict[str, Any]]:
    """
    Configure transport settings from command-line arguments.

    Args:
        args: Command-line arguments namespace

    Returns:
        A tuple containing the transport type and configuration parameters

    Raises:
        TransportConfigurationError: If transport configuration is invalid
    """
    try:
        if args.setup_oauth:
            return "oauth", {
                "port": args.oauth_port
            }
        elif args.stdio:
            return "stdio", {}
        elif args.port is not None:
            return "http", {
                "host": args.host,
                "port": args.port,
                "cors_origins": settings.CORS_ORIGINS,
            }
        elif args.ws:
            return "websocket", {
                "host": args.host,
                "port": args.ws_port,
            }
        else:
            msg = "No transport type specified. "
            msg += "Use --stdio, --port, --ws, or --setup-oauth."
            raise TransportConfigurationError(msg)
    except Exception as e:
        if not isinstance(e, TransportConfigurationError):
            msg = f"Transport configuration error: {str(e)}"
            raise TransportConfigurationError(msg) from e
        raise


def setup_argparser() -> argparse.ArgumentParser:
    """
    Create an argument parser for transport configuration.

    Returns:
        An ArgumentParser instance with transport-related arguments
    """
    description = "Zoho Books MCP Integration Server"
    parser = argparse.ArgumentParser(description=description)
    
    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version="Zoho MCP Server v0.1.0"
    )

    # Transport mode arguments
    transport_group = parser.add_mutually_exclusive_group(required=False)
    transport_group.add_argument(
        "--stdio",
        action="store_true",
        help="Use STDIO transport"
    )
    transport_group.add_argument(
        "--port",
        type=int,
        help="HTTP/SSE port (default: {})".format(settings.DEFAULT_PORT)
    )
    transport_group.add_argument(
        "--ws",
        action="store_true",
        help="Use WebSocket transport"
    )
    transport_group.add_argument(
        "--setup-oauth",
        action="store_true",
        help="Run OAuth setup flow to obtain a refresh token"
    )

    # Common options for network transports
    parser.add_argument(
        "--host",
        default=settings.DEFAULT_HOST,
        help="Server host (default: {})".format(settings.DEFAULT_HOST)
    )
    parser.add_argument(
        "--ws-port",
        type=int,
        default=settings.DEFAULT_WS_PORT,
        help="WebSocket port (default: {})".format(settings.DEFAULT_WS_PORT)
    )

    # OAuth setup options
    parser.add_argument(
        "--oauth-port",
        type=int,
        default=8099,
        help="Port to use for OAuth callback server (default: 8099)"
    )

    # Security and logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=settings.LOG_LEVEL,
        help="Set logging level (default: {})".format(settings.LOG_LEVEL)
    )
    parser.add_argument(
        "--disable-cors",
        action="store_true",
        help="Disable CORS for HTTP transport (not recommended)"
    )

    return parser


def initialize_transport(
    mcp_server: FastMCP, transport_type: str, config: Dict[str, Any]
) -> None:
    """
    Initialize the specified transport for the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        transport_type: The type of transport to initialize
        config: Configuration parameters for the transport

    Raises:
        TransportInitializationError: If the transport fails to initialize
    """
    handler = get_transport_handler(transport_type)

    try:
        # We need to pass the config as kwargs, not as a second positional arg
        handler(mcp_server, **config)
    except Exception as e:
        if not isinstance(e, TransportInitializationError):
            msg = f"Failed to initialize {transport_type} transport: {str(e)}"
            raise TransportInitializationError(msg) from e
        raise
