#!/usr/bin/env python3
"""
Build script for creating standalone executables of Zoho MCP Server.

This script uses PyInstaller to create platform-specific binaries.
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

def get_platform_name() -> str:
    """Get a standardized platform name for the binary."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize machine architecture names
    if machine in ['x86_64', 'amd64']:
        machine = 'x64'
    elif machine in ['arm64', 'aarch64']:
        machine = 'arm64'
    elif machine in ['i386', 'i686']:
        machine = 'x86'
    
    # Map system names
    if system == 'darwin':
        system = 'macos'
    elif system == 'windows':
        system = 'win'
    
    return f"{system}-{machine}"

def clean_build_artifacts():
    """Remove previous build artifacts."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove pyc files
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))

def install_dependencies():
    """Ensure PyInstaller and other build dependencies are installed."""
    print("Installing build dependencies...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', '--upgrade',
        'pyinstaller>=6.0.0',
        'setuptools',
        'wheel'
    ])

def build_executable():
    """Build the executable using PyInstaller."""
    platform_name = get_platform_name()
    print(f"\nBuilding for platform: {platform_name}")
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        'zoho-mcp-server.spec',
        '--clean',
        '--noconfirm'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Build failed:\n{result.stderr}")
        sys.exit(1)
    
    print("Build successful!")
    
    # Rename the output file with platform information
    source_exe = Path('dist') / 'zoho-mcp-server'
    if platform.system() == 'Windows':
        source_exe = source_exe.with_suffix('.exe')
    
    if source_exe.exists():
        target_name = f"zoho-mcp-server-{platform_name}"
        if platform.system() == 'Windows':
            target_name += '.exe'
        
        target_exe = Path('dist') / target_name
        shutil.move(str(source_exe), str(target_exe))
        print(f"\nExecutable created: {target_exe}")
        
        # Create a simple version info file
        version_file = Path('dist') / f"version-{platform_name}.txt"
        with open(version_file, 'w') as f:
            f.write(f"Zoho MCP Server\n")
            f.write(f"Version: 0.1.0\n")
            f.write(f"Platform: {platform_name}\n")
            f.write(f"Built with Python {sys.version.split()[0]}\n")
        
        return target_exe
    else:
        print(f"Error: Expected output file not found: {source_exe}")
        sys.exit(1)

def test_executable(exe_path):
    """Test the built executable."""
    print(f"\nTesting executable: {exe_path}")
    
    # Test --help
    result = subprocess.run([str(exe_path), '--help'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Help command works")
    else:
        print(f"✗ Help command failed: {result.stderr}")
        return False
    
    # Test --version (if implemented)
    result = subprocess.run([str(exe_path), '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Version command works")
    else:
        print("  Version command not implemented (optional)")
    
    return True

def main():
    """Main build process."""
    print("Zoho MCP Server - Build Script")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Install dependencies
    install_dependencies()
    
    # Build the executable
    exe_path = build_executable()
    
    # Test the executable
    if test_executable(exe_path):
        print(f"\n✅ Build completed successfully!")
        print(f"📦 Executable: {exe_path}")
        print(f"📏 Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print("\n❌ Build completed but tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()