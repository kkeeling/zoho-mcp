"""
Test suite for bulk operations functionality.
"""

import pytest
from unittest.mock import patch

from zoho_mcp.bulk_operations import (
    bulk_create_invoices,
    bulk_record_expenses,
    batch_process_with_progress,
)


class TestBulkInvoiceOperations:
    """Test suite for bulk invoice operations."""
    
    @pytest.mark.asyncio
    async def test_bulk_create_invoices_success(self):
        """Test successful bulk invoice creation."""
        # Mock the create_invoice function
        with patch("zoho_mcp.bulk_operations.create_invoice") as mock_create:
            mock_create.side_effect = [
                {
                    "invoice": {
                        "invoice_id": "INV-001",
                        "invoice_number": "INV-001",
                        "customer_name": "Customer 1",
                        "total": 1000.00,
                    }
                },
                {
                    "invoice": {
                        "invoice_id": "INV-002",
                        "invoice_number": "INV-002",
                        "customer_name": "Customer 2",
                        "total": 2000.00,
                    }
                },
                {
                    "invoice": {
                        "invoice_id": "INV-003",
                        "invoice_number": "INV-003",
                        "customer_name": "Customer 3",
                        "total": 1500.00,
                    }
                },
            ]
            
            # Test data
            invoices_data = [
                {
                    "customer_id": "CUST-001",
                    "line_items": [{"rate": 100, "quantity": 10}],
                },
                {
                    "customer_id": "CUST-002",
                    "line_items": [{"rate": 200, "quantity": 10}],
                },
                {
                    "customer_id": "CUST-003",
                    "line_items": [{"rate": 150, "quantity": 10}],
                    "reference_number": "CUSTOM-REF",  # Custom reference
                },
            ]
            
            # Call bulk create
            result = await bulk_create_invoices(invoices_data)
            
            # Verify summary
            assert result["summary"]["total_requested"] == 3
            assert result["summary"]["successful"] == 3
            assert result["summary"]["failed"] == 0
            assert result["summary"]["total_amount"] == 4500.00
            assert result["summary"]["average_amount"] == 1500.00
            
            # Verify successful invoices
            assert len(result["successful_invoices"]) == 3
            assert result["successful_invoices"][0]["invoice_id"] == "INV-001"
            assert result["successful_invoices"][1]["customer_name"] == "Customer 2"
            assert result["successful_invoices"][2]["total"] == 1500.00
            
            # Verify no failed invoices
            assert len(result["failed_invoices"]) == 0
            
            # Verify that create_invoice was called 3 times
            assert mock_create.call_count == 3
            
            # Check that reference numbers were added for first two invoices
            call_args = mock_create.call_args_list
            assert "reference_number" in call_args[0][1]
            assert "BULK-" in call_args[0][1]["reference_number"]
            assert call_args[2][1]["reference_number"] == "CUSTOM-REF"
    
    @pytest.mark.asyncio
    async def test_bulk_create_invoices_with_failures(self):
        """Test bulk invoice creation with some failures."""
        # Mock create_invoice to fail on second call
        with patch("zoho_mcp.bulk_operations.create_invoice") as mock_create:
            mock_create.side_effect = [
                {
                    "invoice": {
                        "invoice_id": "INV-001",
                        "invoice_number": "INV-001",
                        "customer_name": "Customer 1",
                        "total": 1000.00,
                    }
                },
                Exception("API Error: Invalid customer ID"),
                {
                    "invoice": {
                        "invoice_id": "INV-003",
                        "invoice_number": "INV-003",
                        "customer_name": "Customer 3",
                        "total": 1500.00,
                    }
                },
            ]
            
            invoices_data = [
                {"customer_id": "CUST-001", "line_items": []},
                {"customer_id": "INVALID", "line_items": []},
                {"customer_id": "CUST-003", "line_items": []},
            ]
            
            result = await bulk_create_invoices(invoices_data)
            
            # Verify summary
            assert result["summary"]["total_requested"] == 3
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 1
            assert result["summary"]["total_amount"] == 2500.00
            assert result["summary"]["average_amount"] == 1250.00
            
            # Verify failed invoices
            assert len(result["failed_invoices"]) == 1
            assert result["failed_invoices"][0]["index"] == 1
            assert result["failed_invoices"][0]["customer_id"] == "INVALID"
            assert "API Error" in result["failed_invoices"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_bulk_create_invoices_with_callback(self):
        """Test bulk invoice creation with progress callback."""
        callback_calls = []
        
        def progress_callback(current, total):
            callback_calls.append((current, total))
        
        with patch("zoho_mcp.bulk_operations.create_invoice") as mock_create:
            mock_create.return_value = {
                "invoice": {
                    "invoice_id": "INV-001",
                    "invoice_number": "INV-001",
                    "customer_name": "Customer",
                    "total": 1000.00,
                }
            }
            
            invoices_data = [
                {"customer_id": "CUST-001", "line_items": []},
                {"customer_id": "CUST-002", "line_items": []},
            ]
            
            await bulk_create_invoices(invoices_data, callback=progress_callback)
            
            # Verify callback was called for each item
            assert len(callback_calls) == 2
            assert callback_calls[0] == (1, 2)
            assert callback_calls[1] == (2, 2)


class TestBulkExpenseOperations:
    """Test suite for bulk expense operations."""
    
    @pytest.mark.asyncio
    async def test_bulk_record_expenses_success(self):
        """Test successful bulk expense recording."""
        with patch("zoho_mcp.bulk_operations.create_expense") as mock_create:
            mock_create.side_effect = [
                {
                    "expense": {
                        "expense_id": "EXP-001",
                        "date": "2023-01-01",
                        "account_name": "Office Expenses",
                        "total": 100.00,
                    }
                },
                {
                    "expense": {
                        "expense_id": "EXP-002",
                        "date": "2023-01-02",
                        "account_name": "Travel",
                        "total": 250.00,
                    }
                },
            ]
            
            expenses_data = [
                {
                    "date": "2023-01-01",
                    "account_id": "ACC-001",
                    "amount": 100.00,
                    "description": "Office supplies",
                },
                {
                    "date": "2023-01-02",
                    "account_id": "ACC-002",
                    "amount": 250.00,
                    "description": "Flight tickets",
                },
            ]
            
            result = await bulk_record_expenses(expenses_data)
            
            # Verify summary
            assert result["summary"]["total_requested"] == 2
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 0
            assert result["summary"]["total_amount"] == 350.00
            assert result["summary"]["average_amount"] == 175.00
            
            # Verify successful expenses
            assert len(result["successful_expenses"]) == 2
            assert result["successful_expenses"][0]["expense_id"] == "EXP-001"
            assert result["successful_expenses"][1]["account_name"] == "Travel"
    
    @pytest.mark.asyncio
    async def test_bulk_record_expenses_with_failures(self):
        """Test bulk expense recording with failures."""
        with patch("zoho_mcp.bulk_operations.create_expense") as mock_create:
            mock_create.side_effect = [
                {
                    "expense": {
                        "expense_id": "EXP-001",
                        "date": "2023-01-01",
                        "account_name": "Office Expenses",
                        "total": 100.00,
                    }
                },
                Exception("Invalid account ID"),
            ]
            
            expenses_data = [
                {"date": "2023-01-01", "account_id": "ACC-001", "amount": 100.00},
                {"date": "2023-01-02", "account_id": "INVALID", "amount": 250.00},
            ]
            
            result = await bulk_record_expenses(expenses_data)
            
            # Verify results
            assert result["summary"]["successful"] == 1
            assert result["summary"]["failed"] == 1
            assert len(result["failed_expenses"]) == 1
            assert result["failed_expenses"][0]["error"] == "Invalid account ID"


class TestBatchProcessing:
    """Test suite for batch processing functionality."""
    
    @pytest.mark.asyncio
    async def test_batch_process_with_progress(self):
        """Test batch processing with progress tracking."""
        # Mock processing function
        async def mock_process_batch(batch):
            return {"processed": len(batch), "batch_data": batch}
        
        items = list(range(25))  # 25 items
        batch_size = 10
        
        results = await batch_process_with_progress(
            items=items,
            process_func=mock_process_batch,
            operation_name="Test batch processing",
            batch_size=batch_size,
        )
        
        # Should have 3 batches: [0-9], [10-19], [20-24]
        assert len(results) == 3
        assert results[0]["processed"] == 10
        assert results[1]["processed"] == 10
        assert results[2]["processed"] == 5
        
        # Check batch contents
        assert results[0]["batch_data"] == list(range(10))
        assert results[1]["batch_data"] == list(range(10, 20))
        assert results[2]["batch_data"] == list(range(20, 25))
    
    @pytest.mark.asyncio
    async def test_batch_process_with_error(self):
        """Test batch processing with errors in some batches."""
        async def mock_process_batch(batch):
            if batch[0] == 10:  # Fail on second batch
                raise Exception("Batch processing error")
            return {"processed": len(batch)}
        
        items = list(range(25))
        batch_size = 10
        
        results = await batch_process_with_progress(
            items=items,
            process_func=mock_process_batch,
            operation_name="Test batch with errors",
            batch_size=batch_size,
        )
        
        # Should have 3 results
        assert len(results) == 3
        assert results[0]["processed"] == 10  # Success
        assert "error" in results[1]  # Error
        assert results[2]["processed"] == 5   # Success
        
        # Check error details
        assert results[1]["error"] == "Batch processing error"
        assert results[1]["batch_index"] == 1
    
    @pytest.mark.asyncio
    async def test_batch_process_with_callback(self):
        """Test batch processing with progress callback."""
        callback_calls = []
        
        def progress_callback(current, total):
            callback_calls.append((current, total))
        
        async def mock_process_batch(batch):
            return {"processed": len(batch)}
        
        items = list(range(15))
        batch_size = 5
        
        await batch_process_with_progress(
            items=items,
            process_func=mock_process_batch,
            operation_name="Test with callback",
            batch_size=batch_size,
            callback=progress_callback,
        )
        
        # Should have been called for each batch
        assert len(callback_calls) == 3
        assert callback_calls[0] == (1, 3)  # First batch
        assert callback_calls[1] == (2, 3)  # Second batch
        assert callback_calls[2] == (3, 3)  # Third batch