# Release Process Documentation

This document outlines the complete process for publishing zoho-books-mcp to PyPI and creating GitHub releases.

## Prerequisites

## Release Steps

### 1. Prepare the Release

```bash
# 1. Update version in pyproject.toml
# Change version = "0.1.0" to your new version

# 2. Update CHANGELOG.md
# Add new version section with changes
# Move items from [Unreleased] to the new version section
# Update the version links at the bottom

# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v0.1.0"
git push origin main
```

### 2. Create and Push Git Tag

```bash
# Create the tag locally
git tag v0.1.0

# Push the tag to GitHub
git push origin v0.1.0
```

### 3. Create GitHub Release

1. **Go to GitHub repository** → Releases
2. **Click "Create a new release"**
3. **Choose tag**: Select `v0.1.0` from dropdown
4. **Release title**: `v0.1.0`
5. **Description**: Copy content from CHANGELOG.md for this version
6. **Click "Publish release"**

### 4. Manual Publishing

After creating the GitHub release, follow the manual publishing steps in PUBLISHING.md:

1. ✅ Build source distribution (sdist) and wheel
2. ✅ Publish to PyPI using API token
3. ✅ Verify publication on PyPI

## Verification

### Check PyPI Publication
- Visit: https://pypi.org/project/zoho-books-mcp/
- Verify new version is listed
- Test installation: `pip install zoho-books-mcp==0.1.0`

### Check GitHub Release
- Visit: https://github.com/kkeeling/zoho-mcp/releases
- Verify release has distribution files attached
- Verify release notes are complete

## Troubleshooting

### Build and Publishing Failures
- **Build failures**: Check dependencies and build configuration
- **PyPI upload errors**: Verify API token and network connectivity
- **Permission errors**: Verify PyPI account permissions for the project

### Version Conflicts
- **Version already exists**: Update version number in pyproject.toml
- **Git tag conflicts**: Delete and recreate tag if needed:
  ```bash
  git tag -d v0.1.0
  git push origin :refs/tags/v0.1.0
  git tag v0.1.0
  git push origin v0.1.0
  ```

## Manual Publishing Process

For detailed manual publishing instructions, see PUBLISHING.md:

```bash
# Build the package
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

Note: Manual publishing requires PyPI API token configured in environment or `~/.pypirc`.