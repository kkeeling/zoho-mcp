#!/usr/bin/env python3
"""
Test script to validate all Zoho Books API endpoints used in the MCP server.
This script tests real API endpoints with actual data to ensure they work correctly.
"""

import os
import sys
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
CREDENTIALS = {
    "ZOHO_CLIENT_ID": os.getenv("ZOHO_CLIENT_ID"),
    "ZOHO_CLIENT_SECRET": os.getenv("ZOHO_CLIENT_SECRET"),
    "ZOHO_ORGANIZATION_ID": os.getenv("ZOHO_ORGANIZATION_ID"),
    "ZOHO_REGION": os.getenv("ZOHO_REGION", "US")  # Default to US if not set
}

# Validate required credentials
missing_creds = [key for key, value in CREDENTIALS.items() if not value and key != "ZOHO_REGION"]
if missing_creds:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_creds)}")
    print("\nPlease set the following environment variables:")
    print("  export ZOHO_CLIENT_ID='your_client_id'")
    print("  export ZOHO_CLIENT_SECRET='your_client_secret'")
    print("  export ZOHO_ORGANIZATION_ID='your_organization_id'")
    print("  export ZOHO_REGION='your_region' (optional, defaults to US)")
    sys.exit(1)

# Load refresh token if available
REFRESH_TOKEN_FILE = ".zoho_refresh_token"
REFRESH_TOKEN = None

if os.path.exists(REFRESH_TOKEN_FILE):
    with open(REFRESH_TOKEN_FILE, "r") as f:
        REFRESH_TOKEN = f.read().strip()

class ZohoAPITester:
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.access_token = None
        self.base_url = self._get_base_url()
        self.auth_base_url = self._get_auth_base_url()
        self.organization_id = credentials["ZOHO_ORGANIZATION_ID"]
        self.test_results = []
        self.created_resources = {
            "contacts": [],
            "invoices": [],
            "expenses": [],
            "items": [],
            "sales_orders": []
        }
        
    def _get_base_url(self) -> str:
        """Get the appropriate base URL for the region."""
        region_map = {
            "US": "com",
            "EU": "eu",
            "IN": "in",
            "AU": "com.au",
            "JP": "jp",
            "CA": "ca",
            "UK": "uk"
        }
        domain = region_map.get(self.credentials["ZOHO_REGION"], "com")
        return f"https://www.zohoapis.{domain}/books/v3"
        
    def _get_auth_base_url(self) -> str:
        """Get the appropriate auth URL for the region."""
        region_map = {
            "US": "com",
            "EU": "eu",
            "IN": "in",
            "AU": "com.au",
            "JP": "jp",
            "CA": "ca",
            "UK": "uk"
        }
        domain = region_map.get(self.credentials["ZOHO_REGION"], "com")
        return f"https://accounts.zoho.{domain}/oauth/v2"
        
    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        global REFRESH_TOKEN
        
        if not REFRESH_TOKEN:
            print("\n❌ No refresh token found!")
            print("Please run the MCP server with --setup-oauth flag first to obtain a refresh token.")
            print("Example: python server.py --setup-oauth")
            sys.exit(1)
            
        url = f"{self.auth_base_url}/token"
        data = {
            "refresh_token": REFRESH_TOKEN,
            "client_id": self.credentials["ZOHO_CLIENT_ID"],
            "client_secret": self.credentials["ZOHO_CLIENT_SECRET"],
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            print(f"✅ Successfully obtained access token")
            return self.access_token
        except Exception as e:
            print(f"❌ Failed to get access token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            sys.exit(1)
            
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None, test_name: str = "") -> Optional[Dict]:
        """Make a request to the Zoho Books API."""
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Add organization_id to params
        if params is None:
            params = {}
        params["organization_id"] = self.organization_id
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, params=params, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            result = response.json() if response.text else {}
            
            self.test_results.append({
                "test": test_name or f"{method} {endpoint}",
                "status": "✅ PASSED",
                "response_code": response.status_code
            })
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{e} - Response: {e.response.text}"
                
            self.test_results.append({
                "test": test_name or f"{method} {endpoint}",
                "status": "❌ FAILED",
                "error": error_msg
            })
            
            print(f"❌ Error in {test_name}: {error_msg}")
            return None
            
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n📋 Testing Authentication...")
        
        # Test organization validation
        result = self.make_request("GET", "/organizations", test_name="Validate Organization")
        if result and "organizations" in result:
            orgs = result["organizations"]
            print(f"  Found {len(orgs)} organization(s)")
            for org in orgs:
                if org.get("organization_id") == self.organization_id:
                    print(f"  ✅ Validated organization: {org.get('name')}")
                    
    def test_contacts(self):
        """Test contact management endpoints."""
        print("\n📋 Testing Contact Management...")
        
        # List contacts
        result = self.make_request("GET", "/contacts", params={"page": 1, "per_page": 10}, 
                                 test_name="List Contacts")
        if result and "contacts" in result:
            print(f"  Found {len(result['contacts'])} contact(s)")
            
        # Create a test customer
        customer_email = f"test{int(time.time())}@example.com"
        customer_data = {
            "contact_name": f"Test Customer {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "contact_type": "customer",
            "email": customer_email,
            "phone": "555-0123",
            "billing_address": {
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip": "12345",
                "country": "USA"
            },
            "contact_persons": [
                {
                    "first_name": "Test",
                    "last_name": "Person",
                    "email": customer_email,
                    "phone": "555-0123",
                    "is_primary_contact": True
                }
            ]
        }
        
        result = self.make_request("POST", "/contacts", data=customer_data, 
                                 test_name="Create Customer")
        if result and "contact" in result:
            contact_id = result["contact"]["contact_id"]
            self.created_resources["contacts"].append(contact_id)
            print(f"  Created customer: {result['contact']['contact_name']} (ID: {contact_id})")
            
            # Get contact details
            result = self.make_request("GET", f"/contacts/{contact_id}", 
                                     test_name="Get Contact Details")
            if result and "contact" in result:
                print(f"  Retrieved contact: {result['contact']['contact_name']}")
                
            # Update contact
            update_data = {"phone": "555-9999"}
            result = self.make_request("PUT", f"/contacts/{contact_id}", data=update_data,
                                     test_name="Update Contact")
            if result and "contact" in result:
                print(f"  Updated contact phone: {result['contact']['phone']}")
                
            # Test email statement (may fail if no transactions)
            email_data = {
                "to_mail_ids": [customer_data["email"]],
                "subject": "Test Statement",
                "body": "This is a test statement"
            }
            self.make_request("POST", f"/contacts/{contact_id}/statements/email", 
                            data=email_data, test_name="Email Statement")
                            
    def test_invoices(self):
        """Test invoice management endpoints."""
        print("\n📋 Testing Invoice Management...")
        
        # First ensure we have a customer
        if not self.created_resources["contacts"]:
            print("  Creating a customer for invoice testing...")
            customer_data = {
                "contact_name": f"Invoice Test Customer {datetime.now().strftime('%Y%m%d%H%M%S')}",
                "contact_type": "customer",
                "email": f"invoice{int(time.time())}@example.com"
            }
            result = self.make_request("POST", "/contacts", data=customer_data)
            if result and "contact" in result:
                self.created_resources["contacts"].append(result["contact"]["contact_id"])
                
        if not self.created_resources["contacts"]:
            print("  ⚠️  Skipping invoice tests - no customer available")
            return
            
        customer_id = self.created_resources["contacts"][0]
        
        # List invoices
        result = self.make_request("GET", "/invoices", params={"page": 1, "per_page": 10},
                                 test_name="List Invoices")
        if result and "invoices" in result:
            print(f"  Found {len(result['invoices'])} invoice(s)")
            
        # Get contact details to find contact persons
        contact_details = self.make_request("GET", f"/contacts/{customer_id}",
                                          test_name="Get Contact for Invoice")
        contact_person_id = None
        if contact_details and "contact" in contact_details:
            contact_persons = contact_details["contact"].get("contact_persons", [])
            if contact_persons:
                contact_person_id = contact_persons[0]["contact_person_id"]
                
        # Create invoice
        invoice_data = {
            "customer_id": customer_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "line_items": [
                {
                    "name": "Test Service",
                    "description": "Test service for API validation",
                    "rate": 100.00,
                    "quantity": 1
                }
            ]
        }
        
        # Add contact person if available
        if contact_person_id:
            invoice_data["contact_persons"] = [contact_person_id]
        
        result = self.make_request("POST", "/invoices", data=invoice_data,
                                 test_name="Create Invoice")
        if result and "invoice" in result:
            invoice_id = result["invoice"]["invoice_id"]
            self.created_resources["invoices"].append(invoice_id)
            print(f"  Created invoice: {result['invoice']['invoice_number']} (ID: {invoice_id})")
            
            # Get invoice details
            result = self.make_request("GET", f"/invoices/{invoice_id}",
                                     test_name="Get Invoice Details")
            if result and "invoice" in result:
                print(f"  Retrieved invoice: {result['invoice']['invoice_number']}")
                
            # Mark as sent
            result = self.make_request("POST", f"/invoices/{invoice_id}/status/sent",
                                     test_name="Mark Invoice as Sent")
            if result:
                print(f"  Marked invoice as sent")
                
            # Record payment - using customerpayments endpoint
            payment_data = {
                "customer_id": customer_id,
                "payment_mode": "cash",
                "amount": 50.00,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "invoices": [
                    {
                        "invoice_id": invoice_id,
                        "amount_applied": 50.00
                    }
                ]
            }
            result = self.make_request("POST", "/customerpayments",
                                     data=payment_data, test_name="Record Payment")
            if result and "payment" in result:
                print(f"  Recorded payment of ${payment_data['amount']}")
                
            # Send payment reminder
            self.make_request("POST", f"/invoices/{invoice_id}/paymentreminder",
                            test_name="Send Payment Reminder")
                            
    def test_expenses(self):
        """Test expense management endpoints."""
        print("\n📋 Testing Expense Management...")
        
        # List expenses
        result = self.make_request("GET", "/expenses", params={"page": 1, "per_page": 10},
                                 test_name="List Expenses")
        if result and "expenses" in result:
            print(f"  Found {len(result['expenses'])} expense(s)")
            
        # Get chart of accounts to find a valid expense account
        accounts_result = self.make_request("GET", "/chartofaccounts", 
                                          test_name="Get Chart of Accounts")
        expense_account_id = None
        if accounts_result and "chartofaccounts" in accounts_result:
            # Look for an expense account
            for account in accounts_result["chartofaccounts"]:
                if account.get("account_type") == "expense":
                    expense_account_id = account["account_id"]
                    print(f"  Found expense account: {account['account_name']} (ID: {expense_account_id})")
                    break
                    
        if not expense_account_id:
            print("  ⚠️  No expense account found, skipping expense creation")
            return
            
        # Get a bank/cash account for paid_through_account_id
        paid_through_account_id = None
        if accounts_result and "chartofaccounts" in accounts_result:
            for account in accounts_result["chartofaccounts"]:
                if account.get("account_type") in ["bank", "cash", "other_current_asset"]:
                    paid_through_account_id = account["account_id"]
                    print(f"  Found payment account: {account['account_name']} (ID: {paid_through_account_id})")
                    break
                    
        if not paid_through_account_id:
            print("  ⚠️  No payment account found, skipping expense creation")
            return
            
        expense_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": 250.00,
            "description": "Test expense for API validation",
            "account_id": expense_account_id,  # Use the expense account
            "paid_through_account_id": paid_through_account_id  # Use different account
        }
        
        result = self.make_request("POST", "/expenses", data=expense_data,
                                 test_name="Create Expense")
        if result and "expense" in result:
            expense_id = result["expense"]["expense_id"]
            self.created_resources["expenses"].append(expense_id)
            print(f"  Created expense: ${result['expense']['total']} (ID: {expense_id})")
            
            # Get expense details
            result = self.make_request("GET", f"/expenses/{expense_id}",
                                     test_name="Get Expense Details")
            if result and "expense" in result:
                print(f"  Retrieved expense: ${result['expense']['total']}")
                
            # Update expense
            update_data = {"description": "Updated test expense"}
            result = self.make_request("PUT", f"/expenses/{expense_id}",
                                     data=update_data, test_name="Update Expense")
            if result and "expense" in result:
                print(f"  Updated expense description")
                
            # Simulate receipt upload (MVP doesn't actually upload)
            self.make_request("POST", f"/expenses/{expense_id}/receipt",
                            test_name="Upload Receipt (Simulated)")
                            
    def test_items(self):
        """Test item management endpoints."""
        print("\n📋 Testing Item Management...")
        
        # List items
        result = self.make_request("GET", "/items", params={"page": 1, "per_page": 10},
                                 test_name="List Items")
        if result and "items" in result:
            print(f"  Found {len(result['items'])} item(s)")
            
        # Create item
        item_data = {
            "name": f"Test Item {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "rate": 50.00,
            "description": "Test item for API validation",
            "type": "service"  # Changed from item_type to type
        }
        
        result = self.make_request("POST", "/items", data=item_data,
                                 test_name="Create Item")
        if result and "item" in result:
            item_id = result["item"]["item_id"]
            self.created_resources["items"].append(item_id)
            print(f"  Created item: {result['item']['name']} (ID: {item_id})")
            
            # Get item details
            result = self.make_request("GET", f"/items/{item_id}",
                                     test_name="Get Item Details")
            if result and "item" in result:
                print(f"  Retrieved item: {result['item']['name']}")
                
            # Update item
            update_data = {"rate": 75.00}
            result = self.make_request("PUT", f"/items/{item_id}",
                                     data=update_data, test_name="Update Item")
            if result and "item" in result:
                print(f"  Updated item rate to ${result['item']['rate']}")
                
    def test_sales_orders(self):
        """Test sales order management endpoints."""
        print("\n📋 Testing Sales Order Management...")
        
        # Note: Sales Orders might be disabled on free/basic plans
        print("  Note: Sales Orders require upgraded Zoho Books plan")
        
        # Ensure we have a customer
        if not self.created_resources["contacts"]:
            print("  ⚠️  Skipping sales order tests - no customer available")
            return
            
        customer_id = self.created_resources["contacts"][0]
        
        # List sales orders
        result = self.make_request("GET", "/salesorders", params={"page": 1, "per_page": 10},
                                 test_name="List Sales Orders")
        if result and "salesorders" in result:
            print(f"  Found {len(result['salesorders'])} sales order(s)")
            
        # Create sales order
        so_data = {
            "customer_id": customer_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "line_items": [
                {
                    "name": "Test Product",
                    "description": "Test product for sales order",
                    "rate": 200.00,
                    "quantity": 2
                }
            ]
        }
        
        result = self.make_request("POST", "/salesorders", data=so_data,
                                 test_name="Create Sales Order")
        if result and "salesorder" in result:
            so_id = result["salesorder"]["salesorder_id"]
            self.created_resources["sales_orders"].append(so_id)
            print(f"  Created sales order: {result['salesorder']['salesorder_number']} (ID: {so_id})")
            
            # Get sales order details
            result = self.make_request("GET", f"/salesorders/{so_id}",
                                     test_name="Get Sales Order Details")
            if result and "salesorder" in result:
                print(f"  Retrieved sales order: {result['salesorder']['salesorder_number']}")
                
            # Update sales order
            update_data = {"reference_number": "TEST-REF-001"}
            result = self.make_request("PUT", f"/salesorders/{so_id}",
                                     data=update_data, test_name="Update Sales Order")
            if result and "salesorder" in result:
                print(f"  Updated sales order reference")
                
            # Convert to invoice
            convert_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            }
            result = self.make_request("POST", f"/salesorders/{so_id}/convert",
                                     data=convert_data, test_name="Convert SO to Invoice")
            if result and "invoice" in result:
                self.created_resources["invoices"].append(result["invoice"]["invoice_id"])
                print(f"  Converted to invoice: {result['invoice']['invoice_number']}")
                
    def cleanup(self):
        """Clean up test resources created during testing."""
        print("\n🧹 Cleaning up test resources...")
        
        # Clean up in reverse order of dependencies
        # Delete invoices first (before contacts)
        for invoice_id in self.created_resources["invoices"]:
            # First void the invoice if possible
            self.make_request("POST", f"/invoices/{invoice_id}/status/void",
                            test_name=f"Void Invoice {invoice_id}")
            self.make_request("DELETE", f"/invoices/{invoice_id}",
                            test_name=f"Delete Invoice {invoice_id}")
                            
        # Delete sales orders
        for so_id in self.created_resources["sales_orders"]:
            self.make_request("DELETE", f"/salesorders/{so_id}",
                            test_name=f"Delete Sales Order {so_id}")
                            
        # Delete expenses
        for expense_id in self.created_resources["expenses"]:
            self.make_request("DELETE", f"/expenses/{expense_id}",
                            test_name=f"Delete Expense {expense_id}")
                            
        # Delete items
        for item_id in self.created_resources["items"]:
            self.make_request("DELETE", f"/items/{item_id}",
                            test_name=f"Delete Item {item_id}")
                            
        # Delete contacts last
        for contact_id in self.created_resources["contacts"]:
            self.make_request("DELETE", f"/contacts/{contact_id}",
                            test_name=f"Delete Contact {contact_id}")
                            
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if "PASSED" in r["status"])
        failed = sum(1 for r in self.test_results if "FAILED" in r["status"])
        
        print(f"\nTotal Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if "FAILED" in result["status"]:
                    print(f"  - {result['test']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
                        
        print("\n" + "="*60)
        
    def run_all_tests(self):
        """Run all API endpoint tests."""
        print("🚀 Starting Zoho Books API Endpoint Tests")
        print(f"Organization ID: {self.organization_id}")
        print(f"Region: {self.credentials['ZOHO_REGION']}")
        print(f"API Base URL: {self.base_url}")
        
        try:
            # Run tests in order
            self.test_authentication()
            self.test_contacts()
            self.test_items()  # Create items before invoices/orders
            self.test_invoices()
            self.test_expenses()
            self.test_sales_orders()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            
        finally:
            # Always try to clean up
            self.cleanup()
            self.print_results()


def main():
    """Main entry point."""
    print("="*60)
    print("Zoho Books MCP API Endpoint Tester")
    print("="*60)
    
    # Check for refresh token
    if not REFRESH_TOKEN and not os.path.exists(REFRESH_TOKEN_FILE):
        print("\n❌ No refresh token found!")
        print("\nTo obtain a refresh token:")
        print("1. Run: python server.py --setup-oauth")
        print("2. Follow the browser prompts to authorize")
        print("3. The token will be saved automatically")
        print("\nAlternatively, if you have a refresh token, create a file named")
        print(f"'{REFRESH_TOKEN_FILE}' in the project root and paste the token there.")
        sys.exit(1)
        
    tester = ZohoAPITester(CREDENTIALS)
    tester.run_all_tests()


if __name__ == "__main__":
    main()