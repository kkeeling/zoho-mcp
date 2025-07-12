# Building Zoho MCP Server

This guide explains how to build standalone executables for the Zoho MCP Server.

## Prerequisites

- Python 3.9 or higher
- All project dependencies installed (`pip install -r requirements.txt`)
- PyInstaller 6.0+ (installed automatically by build script)

## Building Locally

### Quick Build

```bash
python build_executable.py
```

This will:
1. Install PyInstaller and build dependencies
2. Clean previous build artifacts
3. Build a standalone executable for your current platform
4. Test the executable
5. Output the binary to `dist/zoho-mcp-server-{platform}`

### Manual Build

If you prefer to build manually:

```bash
# Install PyInstaller
pip install pyinstaller>=6.0.0

# Build using the spec file
pyinstaller zoho-mcp-server.spec --clean --noconfirm

# The executable will be in dist/zoho-mcp-server
```

## Platform-Specific Builds

The build script automatically detects your platform and creates appropriately named binaries:

- **macOS Intel**: `zoho-mcp-server-macos-x64`
- **macOS Apple Silicon**: `zoho-mcp-server-macos-arm64`
- **Linux x64**: `zoho-mcp-server-linux-x64`
- **Windows x64**: `zoho-mcp-server-win-x64.exe`

## GitHub Actions

The project includes automated builds via GitHub Actions. When you create a new tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will:
1. Build binaries for all supported platforms
2. Create a new release
3. Upload all binaries to the release

## Testing the Binary

After building, test the executable:

```bash
# Basic test
./dist/zoho-mcp-server-{platform} --help

# Run with test credentials (set environment variables first)
export ZOHO_CLIENT_ID="test_id"
export ZOHO_CLIENT_SECRET="test_secret"
export ZOHO_REFRESH_TOKEN="test_token"
export ZOHO_ORGANIZATION_ID="test_org"
export ZOHO_REGION="US"

./dist/zoho-mcp-server-{platform} --stdio
```

## Troubleshooting

### "Module not found" errors

If the built executable fails with import errors:

1. Check that all dependencies are listed in `requirements.txt`
2. Add any missing modules to the `hiddenimports` list in `zoho-mcp-server.spec`
3. Rebuild with `python build_executable.py`

### Large executable size

PyInstaller bundles the entire Python runtime and all dependencies. To reduce size:

1. Use UPX compression (enabled by default)
2. Exclude unnecessary packages in the spec file
3. Consider using `--onedir` mode instead of `--onefile`

### Platform-specific issues

- **macOS**: You may need to sign the binary for distribution
- **Windows**: Antivirus software may flag the executable
- **Linux**: Ensure the binary has execute permissions (`chmod +x`)

## Distribution

After building, you can distribute the standalone executable without requiring users to install Python or any dependencies. Users only need to:

1. Download the appropriate binary for their platform
2. Make it executable (macOS/Linux)
3. Run it with their Zoho credentials as environment variables