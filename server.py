#!/usr/bin/env python3
"""
Zoho Books MCP Integration Server

A server that exposes tools for interacting with Zoho Books via the MCP protocol.
Supports STDIO, HTTP/SSE, and WebSocket transports.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from zoho_mcp.config import settings
from zoho_mcp import tools
from zoho_mcp.transport import (
    setup_argparser, 
    configure_transport_from_args, 
    initialize_transport,
    TransportConfigurationError,
    TransportInitializationError
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger("zoho_mcp")


def register_tools(mcp_server: FastMCP) -> None:
    """
    Register all available tools with the MCP server.
    
    Args:
        mcp_server: The FastMCP server instance
    """
    # Register contact management tools
    mcp_server.add_tool(tools.list_contacts)
    mcp_server.add_tool(tools.create_customer)
    mcp_server.add_tool(tools.create_vendor)
    mcp_server.add_tool(tools.get_contact)
    mcp_server.add_tool(tools.delete_contact)
    
    # Register invoice management tools
    mcp_server.add_tool(tools.list_invoices)
    mcp_server.add_tool(tools.create_invoice)
    mcp_server.add_tool(tools.get_invoice)
    mcp_server.add_tool(tools.email_invoice)
    mcp_server.add_tool(tools.mark_invoice_as_sent)
    mcp_server.add_tool(tools.void_invoice)
    
    # Register expense management tools
    mcp_server.add_tool(tools.list_expenses)
    mcp_server.add_tool(tools.create_expense)
    mcp_server.add_tool(tools.get_expense)
    mcp_server.add_tool(tools.update_expense)
    
    # Register item management tools
    mcp_server.add_tool(tools.list_items)
    mcp_server.add_tool(tools.create_item)
    mcp_server.add_tool(tools.get_item)
    mcp_server.add_tool(tools.update_item)
    
    # Register sales order management tools
    mcp_server.add_tool(tools.list_sales_orders)
    mcp_server.add_tool(tools.create_sales_order)
    mcp_server.add_tool(tools.get_sales_order)
    mcp_server.add_tool(tools.update_sales_order)
    mcp_server.add_tool(tools.convert_to_invoice)
    
    # These tools will be registered in future tasks
    # ...


def configure_server(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Configure server settings based on command line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary of server configuration settings
    """
    # Override logging level if specified in command line
    if hasattr(args, 'log_level') and args.log_level:
        log_level = args.log_level
        logging.getLogger().setLevel(getattr(logging, log_level))
        logger.info(f"Log level set to {log_level}")
    
    # Configure CORS for HTTP transport
    cors_origins = settings.CORS_ORIGINS
    if hasattr(args, 'disable_cors') and args.disable_cors:
        logger.warning("CORS is disabled. This is not recommended for production.")
        cors_origins = ["*"]
    
    # Prepare server configuration
    server_config = {
        "name": "zoho-books",
        "version": "1.0.0",
    }
    
    return server_config


def main() -> None:
    """
    Main entry point for the Zoho Books MCP server.
    Sets up FastMCP, registers tools, and starts the appropriate transport.
    """
    try:
        # Parse command-line arguments
        parser = setup_argparser()
        args = parser.parse_args()
        
        # Configure server settings
        server_config = configure_server(args)
        
        # Initialize the FastMCP server
        mcp_server = FastMCP(**server_config)
        
        # Register all tools
        register_tools(mcp_server)
        
        # Configure and initialize the appropriate transport
        transport_type, transport_config = configure_transport_from_args(args)
        
        # Enable SSL if configured and not using STDIO
        if (
            transport_type != "stdio" and 
            settings.ENABLE_SECURE_TRANSPORT and 
            settings.SSL_CERT_PATH and 
            settings.SSL_KEY_PATH
        ):
            logger.info("Enabling secure transport (SSL)")
            transport_config["ssl_certfile"] = settings.SSL_CERT_PATH
            transport_config["ssl_keyfile"] = settings.SSL_KEY_PATH
        
        # Start the transport
        initialize_transport(mcp_server, transport_type, transport_config)
    
    except TransportConfigurationError as e:
        logger.error(f"Transport configuration error: {str(e)}")
        sys.exit(1)
    except TransportInitializationError as e:
        logger.error(f"Transport initialization error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()