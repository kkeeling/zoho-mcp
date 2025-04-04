"""
Tests for Pydantic models used for input and output validation.
"""

import pytest
from datetime import date
from pydantic import ValidationError

from zoho_mcp.models.base import BaseResponse, PaginatedResponse, ErrorResponse
from zoho_mcp.models.contacts import (
    AddressInput, ContactPersonInput, CustomerInput, VendorInput, ContactDeleteInput
)
from zoho_mcp.models.invoices import (
    InvoiceLineItem, CreateInvoiceInput, GetInvoiceInput, ListInvoicesInput
)
from zoho_mcp.models.items import (
    ItemInput, GetItemInput, ListItemsInput
)
from zoho_mcp.models.expenses import (
    ExpenseLineItem, GetExpenseInput, ListExpensesInput
)


# Test base models
def test_base_response():
    """Test the BaseResponse model."""
    response = BaseResponse(code=200, message="Success")
    assert response.code == 200
    assert response.message == "Success"
    
    # Test without optional fields
    response = BaseResponse()
    assert response.code is None
    assert response.message is None


def test_paginated_response():
    """Test the PaginatedResponse model."""
    # Test with string items
    response = PaginatedResponse[str](
        page=1,
        page_size=10,
        has_more_page=True,
        items=["item1", "item2"]
    )
    assert response.page == 1
    assert response.page_size == 10
    assert response.has_more_page is True
    assert response.items == ["item1", "item2"]
    
    # Test with dictionary items
    response = PaginatedResponse[dict](
        page=2,
        page_size=20,
        has_more_page=False,
        items=[{"id": "1"}, {"id": "2"}]
    )
    assert response.page == 2
    assert response.page_size == 20
    assert response.has_more_page is False
    assert response.items == [{"id": "1"}, {"id": "2"}]


def test_error_response():
    """Test the ErrorResponse model."""
    error = ErrorResponse(
        code=400,
        message="Bad Request",
        details={"field": "name", "error": "Required"}
    )
    assert error.status == "error"
    assert error.code == 400
    assert error.message == "Bad Request"
    assert error.details == {"field": "name", "error": "Required"}


# Test contact models
def test_address_input():
    """Test the AddressInput model."""
    address = AddressInput(
        attention="Attn: John",
        address="123 Main St",
        city="San Francisco",
        state="CA",
        zip="94105",
        country="USA"
    )
    assert address.attention == "Attn: John"
    assert address.address == "123 Main St"
    assert address.city == "San Francisco"
    assert address.state == "CA"
    assert address.zip == "94105"
    assert address.country == "USA"
    
    # Test with empty data (all fields optional)
    address = AddressInput()
    assert address.address is None
    assert address.city is None


def test_contact_person_input():
    """Test the ContactPersonInput model."""
    contact = ContactPersonInput(
        salutation="Mr.",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-1234"
    )
    assert contact.salutation == "Mr."
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.phone == "555-1234"
    
    # Test with only required fields
    contact = ContactPersonInput(first_name="Jane")
    assert contact.first_name == "Jane"
    assert contact.last_name is None


def test_customer_input():
    """Test the CustomerInput model."""
    customer = CustomerInput(
        contact_name="Acme Inc.",
        company_name="Acme Corporation",
        email="contact@acme.com",
        phone="555-5555",
        billing_address=AddressInput(
            address="123 Main St",
            city="San Francisco"
        )
    )
    assert customer.contact_type == "customer"
    assert customer.contact_name == "Acme Inc."
    assert customer.company_name == "Acme Corporation"
    assert customer.email == "contact@acme.com"
    assert customer.phone == "555-5555"
    assert customer.billing_address.address == "123 Main St"
    
    # Test minimum required fields
    customer = CustomerInput(
        contact_name="Acme Inc.",
        email="contact@acme.com"
    )
    assert customer.contact_name == "Acme Inc."
    assert customer.email == "contact@acme.com"
    
    # Test validation error when no contact method is provided
    with pytest.raises(ValidationError):
        CustomerInput(contact_name="Acme Inc.")


def test_vendor_input():
    """Test the VendorInput model."""
    vendor = VendorInput(
        contact_name="Supplier Co.",
        company_name="Supplier Company",
        email="contact@supplier.com",
        phone="555-7777",
        billing_address=AddressInput(
            address="456 Vendor St",
            city="Chicago"
        )
    )
    assert vendor.contact_type == "vendor"
    assert vendor.contact_name == "Supplier Co."
    assert vendor.company_name == "Supplier Company"
    assert vendor.email == "contact@supplier.com"
    assert vendor.phone == "555-7777"
    assert vendor.billing_address.address == "456 Vendor St"
    
    # Unlike customers, vendors don't require email or phone
    vendor = VendorInput(contact_name="Supplier Co.")
    assert vendor.contact_name == "Supplier Co."


def test_contact_delete_input():
    """Test the ContactDeleteInput model."""
    delete_input = ContactDeleteInput(contact_id="123456")
    assert delete_input.contact_id == "123456"
    
    # Test validation error for missing contact_id
    with pytest.raises(ValidationError):
        ContactDeleteInput()


# Test invoice models
def test_invoice_line_item():
    """Test the InvoiceLineItem model."""
    # Test with item_id
    line_item = InvoiceLineItem(
        item_id="item123",
        description="Professional services",
        rate=100.0,
        quantity=2.0
    )
    assert line_item.item_id == "item123"
    assert line_item.description == "Professional services"
    assert line_item.rate == 100.0
    assert line_item.quantity == 2.0
    
    # Test with name instead of item_id
    line_item = InvoiceLineItem(
        name="Consulting",
        rate=150.0,
        quantity=1.5
    )
    assert line_item.name == "Consulting"
    assert line_item.rate == 150.0
    assert line_item.quantity == 1.5
    
    # Test validation error when neither item_id nor name is provided
    with pytest.raises(ValidationError):
        InvoiceLineItem(rate=100.0, quantity=2.0)
    
    # Test validation error for negative rate
    with pytest.raises(ValidationError):
        InvoiceLineItem(item_id="item123", rate=-100.0, quantity=2.0)
    
    # Test validation error for zero quantity
    with pytest.raises(ValidationError):
        InvoiceLineItem(item_id="item123", rate=100.0, quantity=0)


def test_create_invoice_input():
    """Test the CreateInvoiceInput model."""
    # Test with minimal required fields
    invoice = CreateInvoiceInput(
        customer_id="cust123",
        line_items=[
            InvoiceLineItem(item_id="item1", rate=100.0, quantity=2.0)
        ]
    )
    assert invoice.customer_id == "cust123"
    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].item_id == "item1"
    
    # Test with all fields
    invoice = CreateInvoiceInput(
        customer_id="cust123",
        invoice_number="INV-001",
        reference_number="REF-001",
        invoice_date="2023-01-15",
        due_date=date(2023, 2, 15),
        line_items=[
            InvoiceLineItem(item_id="item1", rate=100.0, quantity=2.0),
            InvoiceLineItem(name="Custom Item", rate=50.0, quantity=1.0)
        ],
        notes="Thank you for your business",
        terms="Net 30",
        payment_terms=30,
        salesperson_name="John Salesman"
    )
    assert invoice.customer_id == "cust123"
    assert invoice.invoice_number == "INV-001"
    assert invoice.invoice_date == "2023-01-15"
    assert invoice.due_date == date(2023, 2, 15)
    assert len(invoice.line_items) == 2
    assert invoice.notes == "Thank you for your business"
    assert invoice.payment_terms == 30
    
    # Test validation error for empty line_items
    with pytest.raises(ValidationError):
        CreateInvoiceInput(
            customer_id="cust123",
            line_items=[]  # should have at least 1 item
        )


def test_get_invoice_input():
    """Test the GetInvoiceInput model."""
    get_invoice = GetInvoiceInput(invoice_id="inv123")
    assert get_invoice.invoice_id == "inv123"
    
    # Test validation error for missing invoice_id
    with pytest.raises(ValidationError):
        GetInvoiceInput()


def test_list_invoices_input():
    """Test the ListInvoicesInput model."""
    # Test defaults
    list_invoices = ListInvoicesInput()
    assert list_invoices.page == 1
    assert list_invoices.status is None
    
    # Test with filters
    list_invoices = ListInvoicesInput(
        page=2,
        status="sent",
        customer_id="cust123",
        date_range_start="2023-01-01",
        date_range_end=date(2023, 12, 31)
    )
    assert list_invoices.page == 2
    assert list_invoices.status == "sent"
    assert list_invoices.customer_id == "cust123"
    assert list_invoices.date_range_start == "2023-01-01"
    assert list_invoices.date_range_end == date(2023, 12, 31)
    
    # Test validation error for invalid page
    with pytest.raises(ValidationError):
        ListInvoicesInput(page=0)
    
    # Test validation error for invalid status
    with pytest.raises(ValidationError):
        ListInvoicesInput(status="invalid")
        
        
# Test item models
def test_item_input():
    """Test the ItemInput model."""
    # Test service item
    item = ItemInput(
        name="Consulting Services",
        rate=150.0,
        description="Professional consulting services"
    )
    assert item.name == "Consulting Services"
    assert item.rate == 150.0
    assert item.item_type == "service"
    assert item.description == "Professional consulting services"
    
    # Test inventory item
    item = ItemInput(
        name="Widget",
        rate=25.0,
        item_type="inventory",
        initial_stock=100,
        initial_stock_rate=15.0,
        inventory_account_id="inv123",
        sku="WDG-001"
    )
    assert item.name == "Widget"
    assert item.rate == 25.0
    assert item.item_type == "inventory"
    assert item.initial_stock == 100
    assert item.initial_stock_rate == 15.0
    assert item.inventory_account_id == "inv123"
    assert item.sku == "WDG-001"
    
    # Test with tax information
    item = ItemInput(
        name="Taxable Item",
        rate=100.0,
        tax_id="tax123"
    )
    assert item.name == "Taxable Item"
    assert item.tax_id == "tax123"
    
    # Test validation error for inventory item without required fields
    with pytest.raises(ValidationError):
        ItemInput(
            name="Widget",
            rate=25.0,
            item_type="inventory"
        )
    
    # Test validation error when both tax_id and tax_name are provided
    with pytest.raises(ValidationError):
        ItemInput(
            name="Taxable Item",
            rate=100.0,
            tax_id="tax123",
            tax_name="VAT",
            tax_percentage=20.0
        )
    
    # Test validation error when tax_name is provided without tax_percentage
    with pytest.raises(ValidationError):
        ItemInput(
            name="Taxable Item",
            rate=100.0,
            tax_name="VAT"
        )


def test_get_item_input():
    """Test the GetItemInput model."""
    get_item = GetItemInput(item_id="item123")
    assert get_item.item_id == "item123"
    
    # Test validation error for missing item_id
    with pytest.raises(ValidationError):
        GetItemInput()


def test_list_items_input():
    """Test the ListItemsInput model."""
    # Test defaults
    list_items = ListItemsInput()
    assert list_items.page == 1
    assert list_items.item_type is None
    assert list_items.status is None
    
    # Test with filters
    list_items = ListItemsInput(
        page=2,
        item_type="inventory",
        status="active",
        search_text="widget"
    )
    assert list_items.page == 2
    assert list_items.item_type == "inventory"
    assert list_items.status == "active"
    assert list_items.search_text == "widget"
    
    # Test validation error for invalid page
    with pytest.raises(ValidationError):
        ListItemsInput(page=0)
    
    # Test validation error for invalid item_type
    with pytest.raises(ValidationError):
        ListItemsInput(item_type="invalid")
    
    # Test validation error for invalid status
    with pytest.raises(ValidationError):
        ListItemsInput(status="invalid")


# Test expense models
def test_expense_line_item():
    """Test the ExpenseLineItem model."""
    line_item = ExpenseLineItem(
        account_id="acc123",
        amount=500.0,
        description="Office supplies"
    )
    assert line_item.account_id == "acc123"
    assert line_item.amount == 500.0
    assert line_item.description == "Office supplies"
    
    # Test with tax information
    line_item = ExpenseLineItem(
        account_id="acc123",
        amount=500.0,
        tax_id="tax123"
    )
    assert line_item.account_id == "acc123"
    assert line_item.amount == 500.0
    assert line_item.tax_id == "tax123"
    
    # Test validation error when both tax_id and tax_name are provided
    with pytest.raises(ValidationError):
        ExpenseLineItem(
            account_id="acc123",
            amount=500.0,
            tax_id="tax123",
            tax_name="VAT",
            tax_percentage=20.0
        )
    
    # Test validation error when tax_name is provided without tax_percentage
    with pytest.raises(ValidationError):
        ExpenseLineItem(
            account_id="acc123",
            amount=500.0,
            tax_name="VAT"
        )


def test_get_expense_input():
    """Test the GetExpenseInput model."""
    get_expense = GetExpenseInput(expense_id="exp123")
    assert get_expense.expense_id == "exp123"
    
    # Test validation error for missing expense_id
    with pytest.raises(ValidationError):
        GetExpenseInput()


def test_list_expenses_input():
    """Test the ListExpensesInput model."""
    # Test defaults
    list_expenses = ListExpensesInput()
    assert list_expenses.page == 1
    assert list_expenses.status is None
    
    # Test with filters
    list_expenses = ListExpensesInput(
        page=2,
        status="unbilled",
        vendor_id="vendor123",
        customer_id="cust123",
        date_range_start="2023-01-01",
        date_range_end=date(2023, 12, 31)
    )
    assert list_expenses.page == 2
    assert list_expenses.status == "unbilled"
    assert list_expenses.vendor_id == "vendor123"
    assert list_expenses.customer_id == "cust123"
    assert list_expenses.date_range_start == "2023-01-01"
    assert list_expenses.date_range_end == date(2023, 12, 31)
    
    # Test validation error for invalid page
    with pytest.raises(ValidationError):
        ListExpensesInput(page=0)
    
    # Test validation error for invalid status
    with pytest.raises(ValidationError):
        ListExpensesInput(status="invalid")