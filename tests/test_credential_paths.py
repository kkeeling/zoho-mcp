"""
Tests for credential path changes to use ~/.zoho-mcp/
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from zoho_mcp.config.settings import Settings
from zoho_mcp.auth_flow import update_env_file


class TestCredentialPaths:
    """Test credential path handling for home directory storage."""
    
    def test_token_cache_path_uses_home_directory(self):
        """Test that TOKEN_CACHE_PATH defaults to ~/.zoho-mcp/.token_cache"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            expected_path = Path.home() / ".zoho-mcp" / ".token_cache"
            assert settings.TOKEN_CACHE_PATH == str(expected_path)
    
    
    
    def test_update_env_file_uses_home_directory(self):
        """Test that update_env_file saves to ~/.zoho-mcp/.env by default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock Path.home() to return our temp directory
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                # Create the .zoho-mcp directory
                zoho_dir = Path(tmpdir) / ".zoho-mcp"
                zoho_dir.mkdir(parents=True, exist_ok=True)
                
                # Call update_env_file
                test_token = "test_refresh_token_12345"
                update_env_file(test_token)
                
                # Verify file was created in home directory
                env_file = zoho_dir / ".env"
                assert env_file.exists()
                
                # Verify content
                content = env_file.read_text()
                assert f'ZOHO_REFRESH_TOKEN={test_token}' in content
    
    def test_update_env_file_backward_compatibility(self):
        """Test that update_env_file falls back to local config if it exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock project structure
            project_root = Path(tmpdir) / "project"
            zoho_mcp_dir = project_root / "zoho_mcp"
            zoho_mcp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create auth_flow.py in the correct location
            auth_flow_path = zoho_mcp_dir / "auth_flow.py"
            auth_flow_path.touch()
            
            # Create local config directory with existing .env
            local_config = project_root / "config"
            local_config.mkdir(parents=True, exist_ok=True)
            local_env = local_config / ".env"
            local_env.write_text('EXISTING_VAR="existing_value"\n')
            
            # Create a fake home directory that doesn't have .zoho-mcp
            fake_home = Path(tmpdir) / "fake_home"
            fake_home.mkdir(parents=True, exist_ok=True)
            
            # Mock Path.home() and __file__
            with patch('pathlib.Path.home', return_value=fake_home):
                with patch('zoho_mcp.auth_flow.__file__', str(auth_flow_path)):
                    # Call update_env_file
                    test_token = "backward_compat_token_789"
                    update_env_file(test_token)
                    
                    # Verify that the local config path was used
                    assert local_env.exists()
                    content = local_env.read_text()
                    
                    # Verify the existing variable is preserved (quotes are stripped for values without spaces)
                    assert 'EXISTING_VAR=existing_value' in content
                    
                    # Verify the new token was added
                    assert f'ZOHO_REFRESH_TOKEN={test_token}' in content
                    
                    # Verify home directory was NOT used
                    home_env = fake_home / ".zoho-mcp" / ".env"
                    assert not home_env.exists()
    
    def test_env_file_preserves_existing_variables(self):
        """Test that updating env file preserves existing variables"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock Path.home() to return our temp directory
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                # Create the .zoho-mcp directory
                zoho_dir = Path(tmpdir) / ".zoho-mcp"
                zoho_dir.mkdir(parents=True, exist_ok=True)
                
                # Create initial env file with some variables
                env_file = zoho_dir / ".env"
                env_file.write_text(
                    'ZOHO_CLIENT_ID="existing_client_id"\n'
                    'ZOHO_CLIENT_SECRET="existing_secret"\n'
                    'ZOHO_ORGANIZATION_ID="existing_org_id"\n'
                )
                
                # Update with new refresh token
                test_token = "new_refresh_token_67890"
                update_env_file(test_token)
                
                # Verify all variables are preserved
                content = env_file.read_text()
                assert 'ZOHO_CLIENT_ID=existing_client_id' in content
                assert 'ZOHO_CLIENT_SECRET=existing_secret' in content
                assert 'ZOHO_ORGANIZATION_ID=existing_org_id' in content
                assert f'ZOHO_REFRESH_TOKEN={test_token}' in content
    
    def test_env_file_handles_quoted_values(self):
        """Test that env file correctly handles quoted values with spaces"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock Path.home() to return our temp directory
            with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                # Create the .zoho-mcp directory
                zoho_dir = Path(tmpdir) / ".zoho-mcp"
                zoho_dir.mkdir(parents=True, exist_ok=True)
                
                # Create initial env file with quoted value
                env_file = zoho_dir / ".env"
                env_file.write_text(
                    'ZOHO_CLIENT_ID="client id with spaces"\n'
                )
                
                # Update with new refresh token
                test_token = "token_with_no_spaces"
                update_env_file(test_token)
                
                # Verify quoted value is preserved correctly
                content = env_file.read_text()
                assert 'ZOHO_CLIENT_ID="client id with spaces"' in content
                assert f'ZOHO_REFRESH_TOKEN={test_token}' in content