"""Tests for OAuth documentation."""

import re
from pathlib import Path


def test_oauth_setup_documentation():
    """Test that troubleshooting docs contain OAuth setup information."""
    docs_dir = Path(__file__).parent.parent / "docs"
    troubleshooting_path = docs_dir / "troubleshooting.md"

    # Verify the troubleshooting.md file exists
    assert troubleshooting_path.exists(), "Troubleshooting doc file not found"

    # Read the troubleshooting documentation
    with open(troubleshooting_path, "r") as f:
        content = f.read()

    # Check for presence of OAuth setup section
    assert "## Automatic OAuth Flow Setup" in content, (
        "OAuth setup section not found in documentation"
    )

    # Check for presence of required sections
    section_headers = [
        "### Using the OAuth Setup Command",
        "### Custom OAuth Callback Port",
        "### Troubleshooting OAuth Setup"
    ]

    for header in section_headers:
        assert header in content, f"Section {header} not found in OAuth docs"

    # Check for setup command examples
    assert "python server.py --setup-oauth" in content, (
        "OAuth setup command example not found"
    )
    assert "--oauth-port" in content, "OAuth port customization not documented"

    # Check for instructions on manual vs automatic flow
    assert "Use the automatic OAuth setup flow (recommended)" in content, (
        "Automatic flow recommendation not found in Token Expiration section"
    )

    # Check for OAuth-related error messages in the common errors table
    oauth_errors = [
        "OAuth flow timed out",
        "OAuth authorization error",
        "Missing required OAuth credentials"
    ]

    for error in oauth_errors:
        assert error in content, f"Common OAuth error '{error}' not documented"

    # Check for reference to OAuth setup flag in transport configuration
    assert "OAuth Setup: `python server.py --setup-oauth`" in content, (
        "OAuth Setup not listed as a transport option in config section"
    )


def test_oauth_setup_in_table_of_contents():
    """Test that the OAuth setup is included in the table of contents."""
    docs_dir = Path(__file__).parent.parent / "docs"
    troubleshooting_path = docs_dir / "troubleshooting.md"

    # Read the troubleshooting documentation
    with open(troubleshooting_path, "r") as f:
        content = f.read()

    # Extract the table of contents
    toc_pattern = r"## Table of Contents\n(.*?)\n##"
    toc_match = re.search(toc_pattern, content, re.DOTALL)
    assert toc_match, "Table of Contents not found in documentation"

    toc_content = toc_match.group(1)

    # Check for OAuth setup entries in the TOC
    toc_entries = [
        "Automatic OAuth Flow Setup",
        "Using the OAuth Setup Command",
        "Custom OAuth Callback Port",
        "Troubleshooting OAuth Setup"
    ]

    for entry in toc_entries:
        assert entry in toc_content, f"'{entry}' not in Table of Contents"
