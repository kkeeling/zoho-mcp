"""
Tests for the server.py module.
"""

import unittest
from unittest.mock import patch, MagicMock

from zoho_mcp.server import main
from zoho_mcp.errors import AuthenticationError
from zoho_mcp.transport import TransportConfigurationError


class TestServer(unittest.TestCase):
    """Tests for server.py functionality."""
    
    @patch('zoho_mcp.server.setup_argparser')
    @patch('zoho_mcp.server.configure_server')
    @patch('zoho_mcp.server.FastMCP')
    @patch('zoho_mcp.server.register_tools')
    @patch('zoho_mcp.server.configure_transport_from_args')
    @patch('zoho_mcp.server.initialize_transport')
    @patch('sys.exit')
    def test_normal_server_startup(self, mock_exit, mock_init_transport, mock_configure_transport, 
                                   mock_register_tools, mock_fastmcp, mock_configure_server, 
                                   mock_setup_argparser):
        """Test normal server startup without OAuth setup."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.setup_oauth = False
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparser.return_value = mock_parser
        
        mock_server_config = {"name": "test-server", "version": "1.0.0"}
        mock_configure_server.return_value = mock_server_config
        
        mock_transport_type = "http"
        mock_transport_config = {"host": "localhost", "port": 8080}
        mock_configure_transport.return_value = (mock_transport_type, mock_transport_config)
        
        # Create a mock server instance
        mock_server = MagicMock()
        mock_fastmcp.return_value = mock_server
        
        # Call main function
        main()
        
        # Verify the normal server startup flow
        mock_setup_argparser.assert_called_once()
        mock_configure_server.assert_called_once_with(mock_args)
        mock_fastmcp.assert_called_once_with(**mock_server_config)
        mock_register_tools.assert_called_once_with(mock_server)
        mock_configure_transport.assert_called_once_with(mock_args)
        mock_init_transport.assert_called_once()
        mock_exit.assert_not_called()  # Server should not exit in normal startup
    
    @patch('zoho_mcp.server.setup_argparser')
    @patch('zoho_mcp.server.run_oauth_flow')
    @patch('sys.exit')
    def test_oauth_setup_flow_success(self, mock_exit, mock_run_oauth_flow, mock_setup_argparser):
        """Test OAuth setup flow when --setup-oauth flag is provided (success case)."""
        # Test the sys.exit mock to make it terminate test after first call
        mock_exit.side_effect = SystemExit
        
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.setup_oauth = True
        mock_args.oauth_port = 9999
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparser.return_value = mock_parser
        
        # Mock successful OAuth flow
        mock_refresh_token = "fake_refresh_token"
        mock_run_oauth_flow.return_value = mock_refresh_token
        
        # Call main function
        with self.assertRaises(SystemExit):
            main()
        
        # Verify the OAuth setup flow
        mock_setup_argparser.assert_called_once()
        mock_run_oauth_flow.assert_called_once_with(port=9999)
        mock_exit.assert_called_once_with(0)  # Should exit with success code
    
    @patch('zoho_mcp.server.setup_argparser')
    @patch('zoho_mcp.server.run_oauth_flow')
    @patch('sys.exit')
    def test_oauth_setup_flow_failure(self, mock_exit, mock_run_oauth_flow, mock_setup_argparser):
        """Test OAuth setup flow when --setup-oauth flag is provided (failure case)."""
        # Test the sys.exit mock to make it terminate test after first call
        mock_exit.side_effect = SystemExit
        
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.setup_oauth = True
        mock_args.oauth_port = 9999
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparser.return_value = mock_parser
        
        # Mock OAuth flow that raises an AuthenticationError
        mock_run_oauth_flow.side_effect = AuthenticationError("OAuth test error")
        
        # Call main function
        with self.assertRaises(SystemExit):
            main()
        
        # Verify the OAuth setup flow error handling
        mock_setup_argparser.assert_called_once()
        mock_run_oauth_flow.assert_called_once_with(port=9999)
        mock_exit.assert_called_once_with(1)  # Should exit with error code
    
    @patch('zoho_mcp.server.setup_argparser')
    @patch('sys.exit')
    @patch('zoho_mcp.server.configure_transport_from_args')
    def test_transport_configuration_error(self, mock_configure_transport, mock_exit, 
                                         mock_setup_argparser):
        """Test handling of TransportConfigurationError."""
        # Test the sys.exit mock to make it terminate test after first call
        mock_exit.side_effect = SystemExit
        
        # Setup mocks
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.setup_oauth = False
        mock_parser.parse_args.return_value = mock_args
        mock_setup_argparser.return_value = mock_parser
        
        # Mock configure_transport_from_args to raise TransportConfigurationError
        mock_configure_transport.side_effect = TransportConfigurationError("Test error")
        
        # Call main function
        with self.assertRaises(SystemExit):
            main()
        
        # Verify error handling
        mock_exit.assert_called_once_with(1)  # Should exit with error code


if __name__ == '__main__':
    unittest.main()