"""
Transport configuration utilities for the Zoho Books MCP Integration Server.

This module provides functions to configure and initialize different transport types
(STDIO, HTTP/SSE, WebSocket) for the FastMCP server. It also includes helper functions
for command-line argument parsing and transport-specific error handling.
"""

import os
import sys
import logging
import argparse
from typing import Any, Dict, Optional, Tuple, Union, Callable

from mcp.server.fastmcp import FastMCP

from zoho_mcp.config import settings

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
        mcp_server.run_stdio()
    except Exception as e:
        logger.error(f"Failed to start STDIO transport: {str(e)}")
        raise TransportInitializationError(f"Failed to start STDIO transport: {str(e)}") from e


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
        
        http_config = {
            "host": host,
            "port": port,
            "cors_origins": cors_origins,
        }
        
        # Add any additional configs provided
        for key, value in kwargs.items():
            if key not in http_config:
                http_config[key] = value
        
        # Start the HTTP/SSE transport
        mcp_server.run_http(**http_config)
    except Exception as e:
        logger.error(f"Failed to start HTTP/SSE transport on {host}:{port}: {str(e)}")
        raise TransportInitializationError(
            f"Failed to start HTTP/SSE transport on {host}:{port}: {str(e)}"
        ) from e


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
    try:
        logger.info(f"Starting MCP server in WebSocket mode on {host}:{port}")
        
        ws_config = {
            "host": host,
            "port": port,
        }
        
        # Add any additional configs provided
        for key, value in kwargs.items():
            if key not in ws_config:
                ws_config[key] = value
        
        # Start the WebSocket transport
        mcp_server.run_websocket(**ws_config)
    except Exception as e:
        logger.error(f"Failed to start WebSocket transport on {host}:{port}: {str(e)}")
        raise TransportInitializationError(
            f"Failed to start WebSocket transport on {host}:{port}: {str(e)}"
        ) from e


def get_transport_handler(transport_type: str) -> Callable:
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
        raise TransportConfigurationError(
            f"Unsupported transport type: {transport_type}. "
            f"Supported types are: {supported}"
        )
    
    return transport_handlers[transport_type]


def configure_transport_from_args(args: argparse.Namespace) -> Tuple[str, Dict[str, Any]]:
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
        if args.stdio:
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
            raise TransportConfigurationError(
                "No transport type specified. Use --stdio, --port, or --ws."
            )
    except Exception as e:
        if not isinstance(e, TransportConfigurationError):
            raise TransportConfigurationError(f"Transport configuration error: {str(e)}") from e
        raise


def setup_argparser() -> argparse.ArgumentParser:
    """
    Create an argument parser for transport configuration.
    
    Returns:
        An ArgumentParser instance with transport-related arguments
    """
    parser = argparse.ArgumentParser(description="Zoho Books MCP Integration Server")
    
    # Transport mode arguments
    transport_group = parser.add_mutually_exclusive_group(required=True)
    transport_group.add_argument(
        "--stdio", 
        action="store_true", 
        help="Use STDIO transport"
    )
    transport_group.add_argument(
        "--port", 
        type=int, 
        help=f"HTTP/SSE port (default: {settings.DEFAULT_PORT})"
    )
    transport_group.add_argument(
        "--ws", 
        action="store_true", 
        help="Use WebSocket transport"
    )
    
    # Common options for network transports
    parser.add_argument(
        "--host", 
        default=settings.DEFAULT_HOST, 
        help=f"Server host (default: {settings.DEFAULT_HOST})"
    )
    parser.add_argument(
        "--ws-port", 
        type=int, 
        default=settings.DEFAULT_WS_PORT, 
        help=f"WebSocket port (default: {settings.DEFAULT_WS_PORT})"
    )
    
    # Security and logging options
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=settings.LOG_LEVEL,
        help=f"Set logging level (default: {settings.LOG_LEVEL})"
    )
    parser.add_argument(
        "--disable-cors", 
        action="store_true",
        help="Disable CORS for HTTP transport (not recommended for production)"
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
        handler(mcp_server, **config)
    except Exception as e:
        if not isinstance(e, TransportInitializationError):
            raise TransportInitializationError(
                f"Failed to initialize {transport_type} transport: {str(e)}"
            ) from e
        raise