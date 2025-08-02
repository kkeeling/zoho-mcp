# Publishing zoho-books-mcp

This document provides step-by-step instructions for manually publishing releases of zoho-books-mcp to PyPI and GitHub.

## Prerequisites

1. **PyPI Account**: Ensure you have a PyPI account with permissions to publish to `zoho-books-mcp`
2. **PyPI API Token**: Create an API token at https://pypi.org/manage/account/token/
3. **GitHub CLI**: Install `gh` CLI tool for GitHub releases
4. **Build Tools**: Install required build dependencies

```bash
pip install --upgrade pip build twine
```

## Release Process

### 1. Prepare the Release

1. **Update Version**: Update version in `pyproject.toml` if needed
2. **Update Changelog**: Add release notes to `CHANGELOG.md`
3. **Commit Changes**: Commit any final changes
4. **Create Git Tag**: 
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/

# Build source and wheel distributions
python -m build
```

This creates:
- `dist/zoho_books_mcp-0.1.0.tar.gz` (source distribution)
- `dist/zoho_books_mcp-0.1.0-py3-none-any.whl` (wheel distribution)

### 3. Upload to PyPI

```bash
# Upload to PyPI (will prompt for credentials or use API token)
twine upload dist/*
```

**Alternative using API token:**
```bash
# Set API token as environment variable
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-api-token>

# Upload
twine upload dist/*
```

### 4. Create GitHub Release

```bash
# Create GitHub release with files attached
gh release create v0.1.0 \
  --title "v0.1.0" \
  --notes-from-tag \
  dist/*
```

**Alternative manual approach:**
1. Go to https://github.com/kkeeling/zoho-mcp/releases
2. Click "Create a new release"
3. Choose tag: `v0.1.0`
4. Fill in release title: `v0.1.0`
5. Copy release notes from CHANGELOG.md
6. Attach the built files from `dist/`
7. Publish release

## Verification

After publishing:

1. **Verify PyPI**: Check https://pypi.org/project/zoho-books-mcp/
2. **Test Installation**: 
   ```bash
   pip install zoho-books-mcp==0.1.0
   ```
3. **Verify GitHub Release**: Check https://github.com/kkeeling/zoho-mcp/releases

## Troubleshooting

### Upload Errors
- **403 Forbidden**: Check PyPI credentials and package permissions
- **400 Bad Request**: Ensure version number hasn't been used before
- **File already exists**: Version already published (increment version)

### Build Errors
- Run `python -m build --help` for build options
- Check `pyproject.toml` for configuration issues
- Ensure all required files are included via `MANIFEST.in`

### GitHub Release Issues
- Ensure you're authenticated: `gh auth login`
- Check repository permissions
- Verify tag exists: `git tag -l`

## Security Notes

- Never commit API tokens to version control
- Use environment variables for sensitive credentials
- Consider using `~/.pypirc` for PyPI credentials:

```ini
[pypi]
username = __token__
password = <your-api-token>
```

## Next Steps for Automation (Optional)

If you later want to re-add automation:
1. Set up PyPI trusted publishing in PyPI project settings
2. Add repository secrets for GitHub Actions
3. Create workflow that triggers on release tags
4. Test thoroughly in a separate repository first