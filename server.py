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
from typing import Optional

from mcp.server.fastmcp import FastMCP

from zoho_mcp.config import settings
from zoho_mcp import tools

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("zoho_mcp")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Zoho Books MCP Integration Server")
    
    # Transport mode arguments
    transport_group = parser.add_mutually_exclusive_group(required=True)
    transport_group.add_argument("--stdio", action="store_true", help="Use STDIO transport")
    transport_group.add_argument("--port", type=int, help="HTTP/SSE port (default: 8000)")
    transport_group.add_argument("--ws", action="store_true", help="Use WebSocket transport")
    
    # Optional arguments
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket port (default: 8765)")
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the Zoho Books MCP server.
    Sets up FastMCP, registers tools, and starts the appropriate transport.
    """
    args = parse_args()
    
    # Initialize the FastMCP server
    mcp_server = FastMCP(name="zoho-books")
    
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
    
    # These tools will be registered in future tasks
    # ...
    
    # Start the appropriate transport based on command line arguments
    if args.stdio:
        logger.info("Starting MCP server in STDIO mode")
        mcp_server.run_stdio()
    elif args.port:
        logger.info(f"Starting MCP server in HTTP/SSE mode on {args.host}:{args.port}")
        mcp_server.run_http(host=args.host, port=args.port)
    elif args.ws:
        logger.info(f"Starting MCP server in WebSocket mode on {args.host}:{args.ws_port}")
        mcp_server.run_websocket(host=args.host, port=args.ws_port)


if __name__ == "__main__":
    main()