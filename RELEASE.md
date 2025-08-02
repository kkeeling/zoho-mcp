# Release Process Documentation

This document outlines the complete process for publishing zoho-books-mcp to PyPI and creating GitHub releases.

## Prerequisites

### 1. PyPI Trusted Publishing Setup

Before releases can be automated, you must configure PyPI Trusted Publishing:

1. **Create PyPI account** if you don't have one: https://pypi.org/account/register/
2. **Navigate to Publishing** section in your PyPI account settings
3. **Add a new trusted publisher** with these details:
   - PyPI project name: `zoho-books-mcp`
   - Owner: `kkeeling`
   - Repository name: `zoho-mcp`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`

### 2. GitHub Environment Protection

1. **Go to repository Settings** → Environments
2. **Create new environment** named `pypi`
3. **Add protection rules**:
   - ✅ Required reviewers (recommended: repository maintainers)
   - ✅ Wait timer: 0 minutes
   - ✅ Deployment branches: Selected branches → Only default branch

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

### 4. Automated Publishing

Once the GitHub release is published, the workflow will automatically:

1. ✅ Build source distribution (sdist) and wheel
2. ✅ Publish to PyPI using trusted publishing
3. ✅ Attach distribution files to GitHub release

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

### PyPI Trusted Publishing Issues
- **Error: "Trusted publishing exchange failure"**
  - Verify PyPI project name matches exactly: `zoho-books-mcp`
  - Check environment name is exactly: `pypi`
  - Ensure workflow filename is: `publish.yml`

### GitHub Actions Failures
- **Environment protection**: Approve the deployment in GitHub Actions
- **Build failures**: Check dependencies and build configuration
- **Permission errors**: Verify repository secrets and permissions

### Version Conflicts
- **Version already exists**: Update version number in pyproject.toml
- **Git tag conflicts**: Delete and recreate tag if needed:
  ```bash
  git tag -d v0.1.0
  git push origin :refs/tags/v0.1.0
  git tag v0.1.0
  git push origin v0.1.0
  ```

## Manual Override (Emergency)

If automated publishing fails, you can publish manually:

```bash
# Build the package
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

Note: Manual publishing requires PyPI API token configured in environment or `~/.pypirc`.