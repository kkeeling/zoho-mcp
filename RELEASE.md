# Release Guide

This guide explains how to release a new version of the Zoho MCP Server.

## Prerequisites

1. **npm Account**: Create an account at https://www.npmjs.com
2. **npm Token**: Generate an access token for publishing
3. **GitHub Secrets**: Add `NPM_TOKEN` to your repository secrets

## Release Process

### 1. Update Version

Update the version in:
- `npm/package.json`
- `zoho_mcp/transport.py` (in the `--version` output)

### 2. Create and Push Tag

```bash
# Create tag
git tag v0.1.0
git push origin v0.1.0
```

### 3. Automated Release

GitHub Actions will automatically:
1. Build binaries for all platforms (Windows, macOS x64/arm64, Linux)
2. Create a GitHub release with all binaries
3. Publish the npm package

### 4. Verify Release

After about 5-10 minutes:

```bash
# Test npm package
npx zoho-mcp-server --version

# Check npm registry
npm view zoho-mcp-server
```

## Manual Steps (if needed)

### Build Binaries Locally

```bash
# Build for your platform
python build_executable.py
```

### Publish to npm Manually

```bash
cd npm
npm publish
```

## Version Numbering

Follow semantic versioning:
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

## Troubleshooting

### npm Publish Fails

1. Check your npm token is valid
2. Ensure the package name isn't taken
3. Try `npm publish --access public`

### Binary Download Fails

1. Ensure GitHub release has all platform binaries
2. Check binary names match the pattern: `zoho-mcp-server-{platform}-{arch}`
3. Verify release is not a draft

### Users Report "Binary not found"

The npm package downloads binaries during install. Common issues:
- GitHub rate limiting
- Corporate firewalls blocking GitHub
- Platform/architecture not supported

Users can manually download from GitHub releases as a workaround.