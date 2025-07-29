"""
Zoho Books MCP Integration Server Package

This package provides tools for interacting with Zoho Books via the MCP protocol.
"""

from .progress import (
    ProgressTracker,
    BulkOperationProgress,
    create_progress_tracker
)
from .server import main as server_main

__version__ = "0.1.0"

__all__ = [
    "ProgressTracker",
    "BulkOperationProgress",
    "create_progress_tracker"
]

def main():
    """Console script entry point for uvx compatibility."""
    server_main()
