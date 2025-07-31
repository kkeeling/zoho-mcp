#!/usr/bin/env python3
"""
Test script to validate package installation and functionality
"""

import subprocess
import sys
import os
import zoho_mcp
import zoho_mcp.server
import zoho_mcp.tools
import zoho_mcp.config

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        # Convert string command to list format for security
        if isinstance(cmd, str):
            cmd = cmd.split()
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True,
            timeout=10
        )
        if capture_output:
            if result.stdout:
                print(f"Output: {result.stdout}")
            if result.stderr:
                print(f"Error: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def test_package_metadata():
    """Test 1: Check package metadata"""
    print("\n=== Test 1: Package Metadata ===")
    
    # Check if pyproject.toml exists
    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml not found")
        return False
    
    print("✅ pyproject.toml exists")
    
    # Check package name in pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
        if 'name = "zoho-books-mcp"' in content:
            print("✅ Package name is 'zoho-books-mcp'")
        else:
            print("❌ Package name not found or incorrect")
            return False
            
        if 'zoho-books-mcp = "zoho_mcp:main"' in content:
            print("✅ Console script entry point defined")
        else:
            print("❌ Console script entry point not found")
            return False
    
    return True

def test_import_structure():
    """Test 2: Check import structure"""
    print("\n=== Test 2: Import Structure ===")
    
    try:
        # Check if zoho_mcp package exists
        print("✅ zoho_mcp package can be imported")
        
        # Check if main function exists
        if hasattr(zoho_mcp, 'main'):
            print("✅ main function exists in zoho_mcp")
        else:
            print("❌ main function not found in zoho_mcp")
            return False
            
        # Check key submodules
        print("✅ Key submodules can be imported")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_dependency_resolution():
    """Test 3: Check if all dependencies are properly specified"""
    print("\n=== Test 3: Dependency Resolution ===")
    
    with open("pyproject.toml", "r") as f:
        content = f.read()
        
    required_deps = ["mcp", "httpx", "python-dotenv", "pydantic", "structlog", "click"]
    missing_deps = []
    
    for dep in required_deps:
        if dep in content:
            print(f"✅ {dep} dependency specified")
        else:
            print(f"❌ {dep} dependency missing")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0

def test_credential_paths():
    """Test 4: Verify credential path configuration"""
    print("\n=== Test 4: Credential Path Configuration ===")
    
    try:
        # Test that the default token cache path uses the correct directory
        from zoho_mcp.config import settings
        
        # Check if the path contains the expected directory name
        if "/.zoho-mcp/" in settings.TOKEN_CACHE_PATH:
            print(f"✅ Token cache path uses ~/.zoho-mcp/ directory")
            return True
        else:
            print(f"❌ Token cache path incorrect: {settings.TOKEN_CACHE_PATH}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing credential paths: {e}")
        return False

def test_version_management():
    """Test 5: Check version management"""
    print("\n=== Test 5: Version Management ===")
    
    with open("pyproject.toml", "r") as f:
        content = f.read()
        
    if 'version = "0.1.0"' in content:
        print("✅ Version is set to 0.1.0")
    else:
        print("❌ Version not found or incorrect")
        return False
    
    # Check if version is accessible from package
    try:
        if hasattr(zoho_mcp, '__version__'):
            print(f"✅ Package version accessible: {zoho_mcp.__version__}")
        else:
            print("⚠️  Package version not accessible via __version__ (optional)")
    except Exception as e:
        pass
    
    return True

def test_pypi_metadata():
    """Test 6: Check PyPI metadata completeness"""
    print("\n=== Test 6: PyPI Metadata ===")
    
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    required_fields = [
        ("description", "description ="),
        ("readme", "readme ="),
        ("license", "license ="),
        ("authors", "authors ="),
        ("keywords", "keywords ="),
        ("classifiers", "classifiers ="),
        ("urls", "[project.urls]")
    ]
    
    missing_fields = []
    for field_name, field_pattern in required_fields:
        if field_pattern in content:
            print(f"✅ {field_name} field present")
        else:
            print(f"❌ {field_name} field missing")
            missing_fields.append(field_name)
    
    return len(missing_fields) == 0

def test_entry_point_execution():
    """Test 7: Test if entry point can be executed"""
    print("\n=== Test 7: Entry Point Execution ===")
    
    # Test direct Python execution
    result = run_command("python -m zoho_mcp --help")
    if result and result.returncode == 0:
        print("✅ Package can be run with 'python -m zoho_mcp'")
    else:
        print("❌ Failed to run 'python -m zoho_mcp'")
        return False
    
    # Check if --stdio option exists
    if result and "--stdio" in result.stdout:
        print("✅ --stdio option is available")
    else:
        print("❌ --stdio option not found in help")
        return False
    
    return True

def main():
    """Run all validation tests"""
    print("=== Zoho MCP Package Validation Tests ===")
    print("Testing against success criteria for PyPI packaging")
    
    tests = [
        ("Package Metadata", test_package_metadata),
        ("Import Structure", test_import_structure),
        ("Dependency Resolution", test_dependency_resolution),
        ("Credential Paths", test_credential_paths),
        ("Version Management", test_version_management),
        ("PyPI Metadata", test_pypi_metadata),
        ("Entry Point Execution", test_entry_point_execution)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print(f"\n=== Summary ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All validation tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())