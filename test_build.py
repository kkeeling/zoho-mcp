#!/usr/bin/env python3
"""
Quick test to verify the server can be imported and basic functionality works.
Run this before building to catch any import issues.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test basic imports
    print("Testing imports...")
    from server import main
    from zoho_mcp import tools
    from zoho_mcp.config import settings
    from zoho_mcp.resources import register_resources
    from zoho_mcp.prompts import register_prompts
    print("✓ All imports successful")
    
    # Test creating the FastMCP instance
    print("\nTesting FastMCP creation...")
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("Zoho Books")
    print("✓ FastMCP instance created")
    
    # Test argument parsing
    print("\nTesting argument parser...")
    from zoho_mcp.transport import setup_argparser
    parser = setup_argparser()
    
    # Test version flag
    try:
        parser.parse_args(['--version'])
    except SystemExit as e:
        if e.code == 0:
            print("✓ Version flag works correctly")
        else:
            print("✗ Version flag failed")
    
    # Test help flag
    try:
        parser.parse_args(['--help'])
    except SystemExit as e:
        if e.code == 0:
            print("✓ Help flag works correctly")
        else:
            print("✗ Help flag failed")
    
    print("\n✅ All tests passed! Ready to build.")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)