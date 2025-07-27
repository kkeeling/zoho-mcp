"""
Progress tracking and notification system for long-running operations.

This module provides utilities for tracking progress of bulk operations
and notifying users about the progress through logging.
"""

import logging
import asyncio
from typing import Optional, Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Track progress of long-running operations and provide notifications.
    
    This class helps track the progress of bulk operations and provides
    periodic updates through logging. It's designed to work with async
    operations.
    """
    
    def __init__(
        self,
        total: int,
        operation_name: str,
        notify_interval: int = 10,
        callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Initialize a progress tracker.
        
        Args:
            total: Total number of items to process
            operation_name: Name of the operation being tracked
            notify_interval: Notify progress every N items (default: 10)
            callback: Optional callback function(current, total) for custom notifications
        """
        self.total = total
        self.operation_name = operation_name
        self.notify_interval = notify_interval
        self.callback = callback
        self.current = 0
        self.start_time = datetime.now()
        self.last_notification = 0
        
        # Log the start of the operation
        logger.info(f"Starting {operation_name}: {total} items to process")
    
    def increment(self, count: int = 1) -> None:
        """
        Increment the progress counter and notify if needed.
        
        Args:
            count: Number of items processed (default: 1)
        """
        self.current += count
        
        # Check if we should notify
        if (self.current - self.last_notification >= self.notify_interval or 
            self.current == self.total):
            self._notify_progress()
            self.last_notification = self.current
    
    async def async_increment(self, count: int = 1) -> None:
        """
        Async version of increment for use in async contexts.
        
        Args:
            count: Number of items processed (default: 1)
        """
        self.increment(count)
        # Yield control to allow other async operations
        await asyncio.sleep(0)
    
    def _notify_progress(self) -> None:
        """Send progress notification through logging and optional callback."""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate estimated time remaining
        if self.current > 0:
            avg_time_per_item = elapsed / self.current
            remaining_items = self.total - self.current
            eta_seconds = avg_time_per_item * remaining_items
            eta_minutes = eta_seconds / 60
            eta_str = f", ETA: {eta_minutes:.1f} minutes" if eta_minutes > 0 else ""
        else:
            eta_str = ""
        
        # Log progress
        logger.info(
            f"{self.operation_name} progress: {self.current}/{self.total} "
            f"({percentage:.1f}%){eta_str}"
        )
        
        # Call custom callback if provided
        if self.callback:
            try:
                self.callback(self.current, self.total)
            except Exception as e:
                logger.warning(f"Progress callback error: {str(e)}")
    
    def complete(self) -> None:
        """Mark the operation as complete and log final statistics."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info(
            f"Completed {self.operation_name}: {self.current}/{self.total} items "
            f"in {elapsed:.1f} seconds"
        )
        
        if self.current < self.total:
            logger.warning(
                f"{self.operation_name} completed with {self.total - self.current} "
                f"items unprocessed"
            )


class BulkOperationProgress:
    """
    Context manager for tracking bulk operation progress.
    
    This provides a convenient way to track progress using a with statement.
    """
    
    def __init__(
        self,
        total: int,
        operation_name: str,
        notify_interval: int = 10,
        callback: Optional[Callable[[int, int], None]] = None
    ):
        """Initialize the bulk operation progress tracker."""
        self.tracker = ProgressTracker(total, operation_name, notify_interval, callback)
    
    def __enter__(self) -> ProgressTracker:
        """Enter the context and return the tracker."""
        return self.tracker
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context and complete the tracking."""
        self.tracker.complete()
    
    async def __aenter__(self) -> ProgressTracker:
        """Async enter the context and return the tracker."""
        return self.tracker
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async exit the context and complete the tracking."""
        self.tracker.complete()


def create_progress_tracker(
    total: int,
    operation_name: str,
    notify_interval: Optional[int] = None
) -> ProgressTracker:
    """
    Create a progress tracker with sensible defaults.
    
    Args:
        total: Total number of items to process
        operation_name: Name of the operation
        notify_interval: Custom notification interval (auto-calculated if None)
        
    Returns:
        Configured ProgressTracker instance
    """
    if notify_interval is None:
        # Auto-calculate interval based on total
        if total <= 50:
            notify_interval = 10
        elif total <= 200:
            notify_interval = 25
        elif total <= 1000:
            notify_interval = 50
        else:
            notify_interval = 100
    
    return ProgressTracker(total, operation_name, notify_interval)


# Example usage for bulk operations
async def example_bulk_invoice_creation(invoices_to_create: list) -> None:
    """Example of using progress tracking in a bulk operation."""
    async with BulkOperationProgress(
        len(invoices_to_create),
        "Bulk invoice creation"
    ) as progress:
        for invoice_data in invoices_to_create:
            # Process invoice...
            await asyncio.sleep(0.1)  # Simulate work
            await progress.async_increment()
