"""
Tests for the documentation files.

This module checks that all required documentation files exist and contain expected content.
"""

import os
import unittest


class TestDocumentation(unittest.TestCase):
    """Test class for checking documentation files."""

    def test_readme_contains_integration_section(self):
        """Test that README.md has a client integration section with links."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        readme_path = os.path.join(base_dir, "README.md")
        
        # Check that README.md exists
        self.assertTrue(os.path.exists(readme_path), "README.md file does not exist")
        
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        # Check for client integration section
        self.assertIn("## Client Integration", readme_content, 
                     "Client Integration section missing from README.md")
        
        # Check for links to documentation files
        self.assertIn("docs/client-integration/claude-desktop.md", readme_content,
                     "Link to Claude Desktop integration guide missing from README.md")
        self.assertIn("docs/client-integration/cursor.md", readme_content,
                     "Link to Cursor integration guide missing from README.md")
        self.assertIn("docs/examples/common-operations.md", readme_content,
                     "Link to Common Operations examples missing from README.md")
        self.assertIn("docs/troubleshooting.md", readme_content,
                     "Link to Troubleshooting guide missing from README.md")
    
    def test_documentation_files_exist(self):
        """Test that all required documentation files exist."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        doc_files = [
            os.path.join(base_dir, "docs", "client-integration", "claude-desktop.md"),
            os.path.join(base_dir, "docs", "client-integration", "cursor.md"),
            os.path.join(base_dir, "docs", "examples", "common-operations.md"),
            os.path.join(base_dir, "docs", "troubleshooting.md")
        ]
        
        for file_path in doc_files:
            self.assertTrue(os.path.exists(file_path), f"Documentation file {file_path} does not exist")
    
    def test_documentation_files_content(self):
        """Test that documentation files contain expected sections."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check Claude Desktop documentation
        claude_path = os.path.join(base_dir, "docs", "client-integration", "claude-desktop.md")
        with open(claude_path, 'r') as f:
            claude_content = f.read()
        
        self.assertIn("# Integrating Zoho Books MCP Server with Claude Desktop", claude_content,
                     "Claude Desktop doc missing title")
        self.assertIn("## Prerequisites", claude_content,
                     "Claude Desktop doc missing Prerequisites section")
        self.assertIn("## Configuration", claude_content,
                     "Claude Desktop doc missing Configuration section")
        
        # Check Cursor documentation
        cursor_path = os.path.join(base_dir, "docs", "client-integration", "cursor.md")
        with open(cursor_path, 'r') as f:
            cursor_content = f.read()
        
        self.assertIn("# Integrating Zoho Books MCP Server with Cursor", cursor_content,
                     "Cursor doc missing title")
        self.assertIn("HTTP/SSE Mode", cursor_content,
                     "Cursor doc missing HTTP/SSE Mode section")
        self.assertIn("STDIO Mode", cursor_content,
                     "Cursor doc missing STDIO Mode section")
        
        # Check Common Operations documentation
        ops_path = os.path.join(base_dir, "docs", "examples", "common-operations.md")
        with open(ops_path, 'r') as f:
            ops_content = f.read()
        
        self.assertIn("# Common Zoho Books Operations Examples", ops_content,
                     "Common Operations doc missing title")
        self.assertIn("## Contact Management", ops_content,
                     "Common Operations doc missing Contact Management section")
        self.assertIn("## Invoice Operations", ops_content,
                     "Common Operations doc missing Invoice Operations section")
        
        # Check Troubleshooting documentation
        trouble_path = os.path.join(base_dir, "docs", "troubleshooting.md")
        with open(trouble_path, 'r') as f:
            trouble_content = f.read()
        
        self.assertIn("# Zoho Books MCP Server Troubleshooting Guide", trouble_content,
                     "Troubleshooting doc missing title")
        self.assertIn("## Authentication Issues", trouble_content,
                     "Troubleshooting doc missing Authentication Issues section")
        self.assertIn("## Client Connection Problems", trouble_content,
                     "Troubleshooting doc missing Client Connection Problems section")


if __name__ == "__main__":
    unittest.main()