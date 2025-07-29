"""
Tests for the transport configuration module.
"""

import argparse
import unittest
from unittest.mock import patch, MagicMock

from zoho_mcp.config import settings
from zoho_mcp.transport import (
    setup_stdio_transport,
    setup_http_transport,
    setup_websocket_transport,
    get_transport_handler,
    configure_transport_from_args,
    setup_argparser,
    initialize_transport,
    TransportConfigurationError,
    TransportInitializationError
)


class TestTransportHandlers(unittest.TestCase):
    """Tests for individual transport handler functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mcp_server = MagicMock()
        self.mcp_server.run = MagicMock()
        self.mcp_server.create_initialization_options = MagicMock(return_value={})
    
    def test_stdio_transport_handler(self):
        """Test STDIO transport handler function."""
        # Test successful initialization
        setup_stdio_transport(self.mcp_server)
        
        # Check if mcp_server.run was called with the correct transport
        self.mcp_server.run.assert_called_once_with(transport="stdio")
        
        # Test initialization error
        self.mcp_server.run.side_effect = Exception("STDIO error")
        with self.assertRaises(TransportInitializationError):
            setup_stdio_transport(self.mcp_server)
    
    def test_http_transport_handler(self):
        """Test HTTP transport handler function."""
        # Test successful initialization with default parameters
        self.mcp_server.settings = MagicMock()
        
        setup_http_transport(self.mcp_server)
        
        # Verify settings were updated correctly
        self.assertEqual(self.mcp_server.settings.host, settings.DEFAULT_HOST)
        self.assertEqual(self.mcp_server.settings.port, settings.DEFAULT_PORT)
        
        # Check if run was called with the right transport
        self.mcp_server.run.assert_called_once_with(transport="sse")
        
        # Test with custom parameters
        self.mcp_server.run.reset_mock()
        self.mcp_server.settings = MagicMock()
        
        setup_http_transport(
            self.mcp_server,
            host="0.0.0.0",
            port=9000,
            cors_origins=["https://example.com"]
        )
        
        # Verify settings were updated correctly
        self.assertEqual(self.mcp_server.settings.host, "0.0.0.0")
        self.assertEqual(self.mcp_server.settings.port, 9000)
        
        # Check if run was called with the right transport
        self.mcp_server.run.assert_called_once_with(transport="sse")
        
        # Test initialization error
        self.mcp_server.run.side_effect = Exception("HTTP error")
        with self.assertRaises(TransportInitializationError):
            setup_http_transport(self.mcp_server)
    
    def test_websocket_transport_handler(self):
        """Test WebSocket transport handler function."""
        # Since we've updated the WebSocket transport to raise an error
        # directly (as it's not supported in the current MCP SDK),
        # we should test that it raises the expected error
        
        with self.assertRaises(TransportInitializationError) as context:
            setup_websocket_transport(self.mcp_server)
        
        # Check the error message
        self.assertIn("WebSocket transport is not supported", str(context.exception))


class TestTransportUtilities(unittest.TestCase):
    """Tests for transport utility functions."""
    
    def test_get_transport_handler(self):
        """Test getting transport handler functions."""
        # Test getting valid transport handlers
        self.assertEqual(get_transport_handler("stdio"), setup_stdio_transport)
        self.assertEqual(get_transport_handler("http"), setup_http_transport)
        self.assertEqual(get_transport_handler("websocket"), setup_websocket_transport)
        
        # Test invalid transport type
        with self.assertRaises(TransportConfigurationError):
            get_transport_handler("invalid_transport")
    
    def test_setup_argparser(self):
        """Test argument parser setup."""
        parser = setup_argparser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        
        # Test basic parser functionality
        args = parser.parse_args(["--stdio"])
        self.assertTrue(args.stdio)
        
        args = parser.parse_args(["--port", "8080"])
        self.assertEqual(args.port, 8080)
        
        args = parser.parse_args(["--ws", "--ws-port", "9000"])
        self.assertTrue(args.ws)
        self.assertEqual(args.ws_port, 9000)
        
        # Test OAuth setup arguments
        args = parser.parse_args(["--setup-oauth", "--oauth-port", "9001"])
        self.assertTrue(args.setup_oauth)
        self.assertEqual(args.oauth_port, 9001)
        
        # Test default OAuth port
        args = parser.parse_args(["--setup-oauth"])
        self.assertTrue(args.setup_oauth)
        self.assertEqual(args.oauth_port, 8099)
        
        # Test optional arguments
        args = parser.parse_args(["--stdio", "--log-level", "DEBUG"])
        self.assertEqual(args.log_level, "DEBUG")
        
        args = parser.parse_args(["--stdio", "--disable-cors"])
        self.assertTrue(args.disable_cors)


class TestTransportConfiguration(unittest.TestCase):
    """Tests for transport configuration functions."""
    
    def test_configure_transport_from_args(self):
        """Test configuring transport from command-line arguments."""
        # Test STDIO transport configuration
        args = argparse.Namespace(stdio=True, ws=False, port=None, setup_oauth=False)
        transport_type, config = configure_transport_from_args(args)
        self.assertEqual(transport_type, "stdio")
        self.assertEqual(config, {})
        
        # Test HTTP transport configuration
        args = argparse.Namespace(stdio=False, ws=False, port=8080, host="127.0.0.1", setup_oauth=False)
        transport_type, config = configure_transport_from_args(args)
        self.assertEqual(transport_type, "http")
        self.assertEqual(config["port"], 8080)
        self.assertEqual(config["host"], "127.0.0.1")
        
        # Test WebSocket transport configuration
        args = argparse.Namespace(stdio=False, ws=True, port=None, host="127.0.0.1", ws_port=9000, setup_oauth=False)
        transport_type, config = configure_transport_from_args(args)
        self.assertEqual(transport_type, "websocket")
        self.assertEqual(config["port"], 9000)
        self.assertEqual(config["host"], "127.0.0.1")
        
        # Test OAuth setup configuration
        args = argparse.Namespace(stdio=False, ws=False, port=None, setup_oauth=True, oauth_port=8099)
        transport_type, config = configure_transport_from_args(args)
        self.assertEqual(transport_type, "oauth")
        self.assertEqual(config["port"], 8099)
        
        # Test custom OAuth port
        args = argparse.Namespace(stdio=False, ws=False, port=None, setup_oauth=True, oauth_port=9001)
        transport_type, config = configure_transport_from_args(args)
        self.assertEqual(transport_type, "oauth")
        self.assertEqual(config["port"], 9001)
        
        # Test invalid configuration
        args = argparse.Namespace(stdio=False, ws=False, port=None, setup_oauth=False)
        with self.assertRaises(TransportConfigurationError):
            configure_transport_from_args(args)
    
    def test_initialize_transport(self):
        """Test transport initialization."""
        mcp_server = MagicMock()
        mcp_server.run = MagicMock()
        mcp_server.create_initialization_options = MagicMock(return_value={})
        
        # Test successful initialization
        with patch("zoho_mcp.transport.get_transport_handler") as mock_get_handler:
            mock_handler = MagicMock()
            mock_get_handler.return_value = mock_handler
            
            initialize_transport(mcp_server, "stdio", {})
            
            mock_get_handler.assert_called_once_with("stdio")
            mock_handler.assert_called_once_with(mcp_server)
        
        # Test initialization error
        with patch("zoho_mcp.transport.get_transport_handler") as mock_get_handler:
            mock_handler = MagicMock(side_effect=Exception("Initialization error"))
            mock_get_handler.return_value = mock_handler
            
            with self.assertRaises(TransportInitializationError):
                initialize_transport(mcp_server, "stdio", {})


if __name__ == "__main__":
    unittest.main()