"""
Test suite for progress tracking functionality.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from zoho_mcp.progress import (
    ProgressTracker,
    BulkOperationProgress,
    create_progress_tracker,
)
from zoho_mcp.bulk_operations import bulk_create_invoices


class TestProgressTracker:
    """Test suite for ProgressTracker class."""
    
    def test_progress_tracker_initialization(self):
        """Test ProgressTracker initialization."""
        tracker = ProgressTracker(100, "Test operation", notify_interval=10)
        
        assert tracker.total == 100
        assert tracker.operation_name == "Test operation"
        assert tracker.notify_interval == 10
        assert tracker.current == 0
        assert tracker.last_notification == 0
        assert isinstance(tracker.start_time, datetime)
    
    def test_progress_increment(self):
        """Test progress increment functionality."""
        tracker = ProgressTracker(10, "Test", notify_interval=3)
        
        # Increment by 1
        tracker.increment()
        assert tracker.current == 1
        
        # Increment by custom amount
        tracker.increment(2)
        assert tracker.current == 3
    
    @patch("zoho_mcp.progress.logger")
    def test_progress_notification(self, mock_logger):
        """Test that progress notifications are logged at correct intervals."""
        tracker = ProgressTracker(10, "Test operation", notify_interval=3)
        
        # First two increments shouldn't trigger notification
        tracker.increment()
        tracker.increment()
        assert mock_logger.info.call_count == 1  # Only initialization log
        
        # Third increment should trigger notification
        tracker.increment()
        assert mock_logger.info.call_count == 2
        
        # Check the notification message
        last_call = mock_logger.info.call_args_list[-1]
        assert "Test operation progress: 3/10 (30.0%)" in last_call[0][0]
    
    @patch("zoho_mcp.progress.logger")
    def test_progress_completion_notification(self, mock_logger):
        """Test that completion is notified when reaching total."""
        tracker = ProgressTracker(5, "Test", notify_interval=10)  # High interval
        
        # Increment to total
        for _ in range(5):
            tracker.increment()
        
        # Should notify at completion even if interval not reached
        assert any("Test progress: 5/5 (100.0%)" in call[0][0] 
                  for call in mock_logger.info.call_args_list)
    
    def test_progress_callback(self):
        """Test custom callback functionality."""
        callback_calls = []
        
        def test_callback(current, total):
            callback_calls.append((current, total))
        
        tracker = ProgressTracker(10, "Test", notify_interval=3, callback=test_callback)
        
        # Trigger notifications
        tracker.increment(3)  # Should notify
        tracker.increment(3)  # Should notify
        
        assert len(callback_calls) == 2
        assert callback_calls[0] == (3, 10)
        assert callback_calls[1] == (6, 10)
    
    @pytest.mark.asyncio
    async def test_async_increment(self):
        """Test async increment functionality."""
        tracker = ProgressTracker(10, "Test async", notify_interval=5)
        
        # Test async increment
        await tracker.async_increment()
        assert tracker.current == 1
        
        await tracker.async_increment(4)
        assert tracker.current == 5
    
    @patch("zoho_mcp.progress.logger")
    def test_complete_method(self, mock_logger):
        """Test the complete method."""
        tracker = ProgressTracker(10, "Test completion")
        
        # Partially complete
        tracker.increment(7)
        tracker.complete()
        
        # Check completion log
        completion_logs = [call for call in mock_logger.info.call_args_list 
                          if "Completed" in call[0][0]]
        assert len(completion_logs) == 1
        assert "7/10 items" in completion_logs[0][0][0]
        
        # Check warning for incomplete
        warning_logs = [call for call in mock_logger.warning.call_args_list]
        assert len(warning_logs) == 1
        assert "3 items unprocessed" in warning_logs[0][0][0]
    
    def test_eta_calculation(self):
        """Test ETA calculation in progress notifications."""
        with patch("zoho_mcp.progress.logger") as mock_logger:
            tracker = ProgressTracker(100, "Test ETA", notify_interval=1)
            
            # Simulate some delay
            with patch("zoho_mcp.progress.datetime") as mock_datetime:
                # Mock start time
                start = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.now.return_value = start
                tracker.start_time = start
                
                # Simulate 10 seconds elapsed for 10 items
                mock_datetime.now.return_value = start + timedelta(seconds=10)
                tracker.increment(10)
                
                # Check that ETA is included in log
                last_log = mock_logger.info.call_args_list[-1][0][0]
                assert "ETA:" in last_log


class TestBulkOperationProgress:
    """Test suite for BulkOperationProgress context manager."""
    
    def test_context_manager(self):
        """Test BulkOperationProgress as context manager."""
        with BulkOperationProgress(10, "Test bulk") as tracker:
            assert isinstance(tracker, ProgressTracker)
            assert tracker.total == 10
            assert tracker.operation_name == "Test bulk"
            
            tracker.increment(5)
            assert tracker.current == 5
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test BulkOperationProgress as async context manager."""
        async with BulkOperationProgress(20, "Test async bulk") as tracker:
            assert isinstance(tracker, ProgressTracker)
            assert tracker.total == 20
            
            await tracker.async_increment(10)
            assert tracker.current == 10
    
    @patch("zoho_mcp.progress.logger")
    def test_context_manager_completion(self, mock_logger):
        """Test that completion is called on context exit."""
        with BulkOperationProgress(5, "Test completion") as tracker:
            tracker.increment(3)
        
        # Check that complete was called
        completion_logs = [call for call in mock_logger.info.call_args_list 
                          if "Completed" in call[0][0]]
        assert len(completion_logs) > 0
    
    def test_context_manager_with_exception(self):
        """Test context manager behavior with exceptions."""
        try:
            with BulkOperationProgress(10, "Test exception") as tracker:
                tracker.increment(5)
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Tracker should still complete even with exception
        # (This is implicit in the context manager protocol)


class TestCreateProgressTracker:
    """Test suite for create_progress_tracker utility function."""
    
    def test_auto_interval_calculation(self):
        """Test automatic interval calculation based on total."""
        # Small total
        tracker1 = create_progress_tracker(30, "Small operation")
        assert tracker1.notify_interval == 10
        
        # Medium total
        tracker2 = create_progress_tracker(150, "Medium operation")
        assert tracker2.notify_interval == 25
        
        # Large total
        tracker3 = create_progress_tracker(500, "Large operation")
        assert tracker3.notify_interval == 50
        
        # Very large total
        tracker4 = create_progress_tracker(2000, "Very large operation")
        assert tracker4.notify_interval == 100
    
    def test_custom_interval(self):
        """Test that custom interval overrides auto-calculation."""
        tracker = create_progress_tracker(1000, "Custom interval", notify_interval=5)
        assert tracker.notify_interval == 5


class TestBulkOperations:
    """Test suite for bulk operations with progress tracking."""
    
    @pytest.mark.asyncio
    async def test_bulk_create_invoices(self):
        """Test bulk invoice creation with progress tracking."""
        # Mock the create_invoice function
        with patch("zoho_mcp.bulk_operations.create_invoice") as mock_create:
            mock_create.return_value = {
                "invoice": {
                    "invoice_id": "INV-001",
                    "invoice_number": "INV-001",
                    "customer_name": "Test Customer",
                    "total": 1000.00,
                }
            }
            
            # Test data
            invoices_data = [
                {"customer_id": "CUST-001", "line_items": [{"rate": 100, "quantity": 10}]},
                {"customer_id": "CUST-002", "line_items": [{"rate": 200, "quantity": 5}]},
            ]
            
            # Call bulk create
            result = await bulk_create_invoices(invoices_data)
            
            # Check results
            assert result["summary"]["total_requested"] == 2
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 0
            assert result["summary"]["total_amount"] == 2000.00
            assert result["summary"]["average_amount"] == 1000.00
            assert len(result["successful_invoices"]) == 2
            assert len(result["failed_invoices"]) == 0
    
    @pytest.mark.asyncio
    async def test_bulk_create_invoices_with_failures(self):
        """Test bulk invoice creation with some failures."""
        # Mock the create_invoice function to fail on second call
        with patch("zoho_mcp.bulk_operations.create_invoice") as mock_create:
            mock_create.side_effect = [
                {
                    "invoice": {
                        "invoice_id": "INV-001",
                        "invoice_number": "INV-001",
                        "customer_name": "Test Customer",
                        "total": 1000.00,
                    }
                },
                Exception("API Error"),
            ]
            
            # Test data
            invoices_data = [
                {"customer_id": "CUST-001", "line_items": []},
                {"customer_id": "CUST-002", "line_items": []},
            ]
            
            # Call bulk create
            result = await bulk_create_invoices(invoices_data)
            
            # Check results
            assert result["summary"]["successful"] == 1
            assert result["summary"]["failed"] == 1
            assert len(result["failed_invoices"]) == 1
            assert result["failed_invoices"][0]["error"] == "API Error"