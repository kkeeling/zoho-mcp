# Common Zoho Books Operations Examples

This guide provides examples of common operations you can perform with the Zoho Books MCP server through Claude Desktop, Cursor, or other MCP clients. Each example includes the natural language prompt you can use and the expected response.

## Table of Contents

- [Contact Management](#contact-management)
  - [Listing Contacts](#listing-contacts)
  - [Creating Customers](#creating-customers)
  - [Creating Vendors](#creating-vendors)
  - [Retrieving Contact Details](#retrieving-contact-details)
  - [Deleting Contacts](#deleting-contacts)
- [Invoice Operations](#invoice-operations)
  - [Listing Invoices](#listing-invoices)
  - [Creating Invoices](#creating-invoices)
  - [Getting Invoice Details](#getting-invoice-details)
  - [Sending Invoices](#sending-invoices)
  - [Marking Invoices as Sent](#marking-invoices-as-sent)
  - [Voiding Invoices](#voiding-invoices)
- [Expense Management](#expense-management)
  - [Listing Expenses](#listing-expenses)
  - [Creating Expenses](#creating-expenses)
  - [Retrieving Expense Details](#retrieving-expense-details)
  - [Updating Expenses](#updating-expenses)
- [Item Management](#item-management)
  - [Listing Items](#listing-items)
  - [Creating Items](#creating-items)
  - [Getting Item Details](#getting-item-details)
  - [Updating Items](#updating-items)
- [Sales Order Management](#sales-order-management)
  - [Listing Sales Orders](#listing-sales-orders)
  - [Creating Sales Orders](#creating-sales-orders)
  - [Getting Sales Order Details](#getting-sales-order-details)
  - [Updating Sales Orders](#updating-sales-orders)
  - [Converting to Invoices](#converting-to-invoices)
- [Complex Workflows](#complex-workflows)
  - [Creating a Customer and Invoice](#creating-a-customer-and-invoice)
  - [Expense Reporting](#expense-reporting)
  - [Sales Analysis](#sales-analysis)

## Contact Management

### Listing Contacts

**User Prompt:**
"Show me a list of all my contacts in Zoho Books."

**Alternative Prompts:**
- "List all customers in my Zoho Books account."
- "Get all vendors from Zoho Books."
- "Display my contacts with their email addresses."

**Expected Response:**
Claude will use the `list_contacts` tool to retrieve and display your contacts, showing information such as:
- Contact name
- Contact type (customer or vendor)
- Email address
- Phone number
- Outstanding balance

**Example:**
```
Here are your contacts from Zoho Books:

1. Acme Corporation (Customer)
   Email: contact@acmecorp.com
   Phone: (555) 123-4567
   Outstanding: $1,250.00

2. XYZ Suppliers (Vendor)
   Email: orders@xyzsuppliers.com
   Phone: (555) 987-6543
   Outstanding: $0.00

[Additional contacts...]

Showing 1-10 of 45 contacts
```

### Creating Customers

**User Prompt:**
"Create a new customer in Zoho Books named 'Globex Corporation' with email 'info@globexcorp.com' and phone number '555-789-1234'."

**Alternative Prompts:**
- "Add a new customer called 'Globex Corporation' to Zoho Books."
- "Set up a customer account for Globex Corp in Zoho Books."
- "Register Globex Corporation as a new customer with these details..."

**Expected Response:**
Claude will use the `create_customer` tool to add the new customer and confirm the creation:

```
I've created a new customer in Zoho Books:

Customer Name: Globex Corporation
Email: info@globexcorp.com
Phone: 555-789-1234
Contact ID: 460000000012345

The customer has been successfully added to your Zoho Books account.
```

### Creating Vendors

**User Prompt:**
"Add a new vendor called 'Quality Office Supplies' with email 'sales@qualityoffice.com' and phone '555-456-7890'."

**Expected Response:**
Claude will use the `create_vendor` tool to add the new vendor and confirm:

```
I've added a new vendor to your Zoho Books account:

Vendor Name: Quality Office Supplies
Email: sales@qualityoffice.com
Phone: 555-456-7890
Vendor ID: 460000000054321

The vendor has been successfully created in Zoho Books.
```

### Retrieving Contact Details

**User Prompt:**
"Get details for customer Acme Corporation."

**Alternative Prompts:**
- "Show me information about Acme Corp in Zoho Books."
- "Look up contact details for Acme Corporation."
- "What's the contact info for Acme Corporation in my Zoho Books?"

**Expected Response:**
Claude will use the `get_contact` tool to retrieve and display detailed information:

```
Here are the details for Acme Corporation:

Contact ID: 460000000012346
Contact Type: Customer
Contact Name: Acme Corporation
Company Name: Acme Corporation
First Name: John
Last Name: Smith
Email: john.smith@acmecorp.com
Phone: (555) 123-4567
Mobile: (555) 321-7654
Website: www.acmecorp.com

Billing Address:
123 Business Ave
Suite 500
New York, NY 10001
United States

Payment Terms: Net 30
Currency: USD
Outstanding Receivables: $1,250.00
Unused Credits: $0.00
```

### Deleting Contacts

**User Prompt:**
"Delete the vendor 'Old Supplier Inc' from Zoho Books."

**Alternative Prompts:**
- "Remove vendor 'Old Supplier Inc' from my contacts."
- "Delete 'Old Supplier Inc' from my Zoho Books account."

**Expected Response:**
Claude will use the `delete_contact` tool to remove the contact and confirm:

```
I've deleted the vendor 'Old Supplier Inc' from your Zoho Books account.

The contact has been successfully removed.
```

## Invoice Operations

### Listing Invoices

**User Prompt:**
"Show me my recent invoices from Zoho Books."

**Alternative Prompts:**
- "List all unpaid invoices."
- "Get invoices from the last month."
- "Show me overdue invoices from Zoho Books."

**Expected Response:**
Claude will use the `list_invoices` tool to retrieve and display your invoices:

```
Here are your recent invoices from Zoho Books:

1. INV-00001 - Acme Corporation
   Date: 2023-10-15
   Amount: $1,750.00
   Status: Sent
   Due Date: 2023-11-14

2. INV-00002 - TechStart Inc
   Date: 2023-10-18
   Amount: $2,500.00
   Status: Overdue
   Due Date: 2023-11-02

3. INV-00003 - Globex Corporation
   Date: 2023-10-25
   Amount: $950.00
   Status: Draft
   Due Date: 2023-11-24

[Additional invoices...]

Showing 1-10 of 35 invoices
```

### Creating Invoices

**User Prompt:**
"Create a new invoice for Acme Corporation for $2,000 for consulting services with a due date of November 30, 2023."

**Alternative Prompts:**
- "Generate an invoice for Acme Corp for consulting work."
- "Bill Acme Corporation $2,000 for consulting services."
- "Send a new invoice to Acme Corp with the following items..."

**Expected Response:**
Claude will use the `create_invoice` tool to create the invoice and confirm:

```
I've created a new invoice in Zoho Books:

Invoice Number: INV-00004
Customer: Acme Corporation
Date: [Today's Date]
Due Date: November 30, 2023
Status: Draft

Line Items:
- Consulting Services: $2,000.00

Total: $2,000.00

The invoice has been created as a draft in your Zoho Books account. You can review and send it directly from Zoho Books.
```

### Getting Invoice Details

**User Prompt:**
"Get the details for invoice INV-00001."

**Alternative Prompts:**
- "Show me information about invoice INV-00001."
- "What's in invoice INV-00001?"
- "Let me see the full details of INV-00001."

**Expected Response:**
Claude will use the `get_invoice` tool to retrieve and display detailed information:

```
Here are the details for invoice INV-00001:

Invoice Number: INV-00001
Customer: Acme Corporation
Status: Sent
Invoice Date: October 15, 2023
Due Date: November 14, 2023
Reference Number: PO-2023-456

Line Items:
1. Web Development Services
   Quantity: 20 hours
   Rate: $75.00/hour
   Amount: $1,500.00

2. Domain Registration
   Quantity: 1
   Rate: $250.00
   Amount: $250.00

Subtotal: $1,750.00
Tax: $0.00
Total: $1,750.00
Balance Due: $1,750.00

Notes: Payment due within 30 days. Please include invoice number with payment.
```

### Sending Invoices

**User Prompt:**
"Email invoice INV-00003 to the customer."

**Alternative Prompts:**
- "Send invoice INV-00003 to Globex Corporation."
- "Email the draft invoice INV-00003 to the client."

**Expected Response:**
Claude will use the `email_invoice` tool to send the invoice and confirm:

```
I've sent invoice INV-00003 to Globex Corporation.

Email sent to: info@globexcorp.com
Subject: Invoice INV-00003 from Your Company Name
Status: Email successfully sent

The invoice status has been updated to "Sent" in your Zoho Books account.
```

### Marking Invoices as Sent

**User Prompt:**
"Mark invoice INV-00003 as sent."

**Alternative Prompts:**
- "Update the status of invoice INV-00003 to 'sent'."
- "Change invoice INV-00003 from draft to sent."

**Expected Response:**
Claude will use the `mark_invoice_as_sent` tool to update the status and confirm:

```
I've marked invoice INV-00003 for Globex Corporation as sent.

Invoice Number: INV-00003
Previous Status: Draft
New Status: Sent
Date Marked as Sent: [Today's Date]

The invoice status has been successfully updated in your Zoho Books account.
```

### Voiding Invoices

**User Prompt:**
"Void the invoice INV-00002 for TechStart Inc."

**Alternative Prompts:**
- "Cancel invoice INV-00002."
- "Make invoice INV-00002 void."

**Expected Response:**
Claude will use the `void_invoice` tool to void the invoice and confirm:

```
I've voided invoice INV-00002 for TechStart Inc.

Invoice Number: INV-00002
Previous Status: Overdue
New Status: Void
Date Voided: [Today's Date]

The invoice has been successfully voided in your Zoho Books account.
```

## Expense Management

### Listing Expenses

**User Prompt:**
"Show me my recent expenses from Zoho Books."

**Alternative Prompts:**
- "List all expenses from last month."
- "Get expenses categorized as 'Office Supplies'."
- "Show me uncategorized expenses."

**Expected Response:**
Claude will use the `list_expenses` tool to retrieve and display your expenses:

```
Here are your recent expenses from Zoho Books:

1. EXP-00001 - Office Supplies
   Date: 2023-10-05
   Amount: $350.00
   Vendor: Quality Office Supplies
   Status: Recorded

2. EXP-00002 - Software Subscription
   Date: 2023-10-12
   Amount: $99.99
   Vendor: Tech Solutions Inc
   Status: Recorded

3. EXP-00003 - Travel Expenses
   Date: 2023-10-20
   Amount: $825.50
   Vendor: Various
   Status: Recorded

[Additional expenses...]

Showing 1-10 of 28 expenses
```

### Creating Expenses

**User Prompt:**
"Record a new expense of $175.25 for office utilities paid to City Power & Water on October 28, 2023."

**Alternative Prompts:**
- "Add a new expense for office utilities."
- "Create an expense entry for the utility bill."
- "Log $175.25 paid to City Power & Water as an expense."

**Expected Response:**
Claude will use the `create_expense` tool to record the expense and confirm:

```
I've recorded a new expense in Zoho Books:

Expense Number: EXP-00004
Date: October 28, 2023
Category: Utilities
Amount: $175.25
Vendor: City Power & Water
Status: Recorded

The expense has been successfully added to your Zoho Books account.
```

### Retrieving Expense Details

**User Prompt:**
"Get details for expense EXP-00003."

**Alternative Prompts:**
- "Show me information about expense EXP-00003."
- "What's included in expense EXP-00003?"

**Expected Response:**
Claude will use the `get_expense` tool to retrieve and display detailed information:

```
Here are the details for expense EXP-00003:

Expense Number: EXP-00003
Date: October 20, 2023
Category: Travel Expenses
Amount: $825.50
Vendor: Various
Status: Recorded
Payment Method: Corporate Credit Card

Itemized Expenses:
1. Airfare
   Amount: $450.00
   
2. Hotel Stay (2 nights)
   Amount: $275.50

3. Taxi Fares
   Amount: $100.00

Notes: Business trip to Chicago for client meeting.
```

### Updating Expenses

**User Prompt:**
"Update expense EXP-00003 to change the category to 'Business Travel' and add a note that it was for the Smith project."

**Alternative Prompts:**
- "Change the category of expense EXP-00003."
- "Edit the details of expense EXP-00003."
- "Add a note to expense EXP-00003."

**Expected Response:**
Claude will use the `update_expense` tool to modify the expense and confirm:

```
I've updated expense EXP-00003 in Zoho Books:

Expense Number: EXP-00003
Previous Category: Travel Expenses
New Category: Business Travel
Notes Added: Trip was for the Smith project.

The expense has been successfully updated in your Zoho Books account.
```

## Item Management

### Listing Items

**User Prompt:**
"Show me a list of all items in Zoho Books."

**Alternative Prompts:**
- "List all products and services from Zoho Books."
- "Show me my inventory items."
- "What items do I have in Zoho Books?"

**Expected Response:**
Claude will use the `list_items` tool to retrieve and display your items:

```
Here are the items from your Zoho Books account:

1. Web Development (Service)
   Rate: $75.00/hour
   Description: Website development services

2. SEO Consulting (Service)
   Rate: $125.00/hour
   Description: Search engine optimization consulting

3. Office Desk (Product)
   Rate: $350.00
   Description: Standard office desk
   Current Stock: 12

[Additional items...]

Showing 1-10 of 23 items
```

### Creating Items

**User Prompt:**
"Create a new service item called 'Data Analysis' with a rate of $95 per hour."

**Alternative Prompts:**
- "Add a new service to Zoho Books called 'Data Analysis'."
- "Create a service item for data analysis work."
- "Set up a 'Data Analysis' service with an hourly rate."

**Expected Response:**
Claude will use the `create_item` tool to add the new item and confirm:

```
I've created a new item in Zoho Books:

Item Name: Data Analysis
Type: Service
Rate: $95.00 per hour
Item ID: 460000000067890

The service item has been successfully added to your Zoho Books account.
```

### Getting Item Details

**User Prompt:**
"Get details for the 'Web Development' item."

**Alternative Prompts:**
- "Show me information about the Web Development service."
- "What are the details of our Web Development item?"

**Expected Response:**
Claude will use the `get_item` tool to retrieve and display detailed information:

```
Here are the details for the 'Web Development' item:

Item ID: 460000000012345
Name: Web Development
Type: Service
Status: Active
Rate: $75.00 per hour
Description: Website development services

Account: Service Revenue
Tax Preference: Taxable
Tax Percentage: 7.5%

Item has been used in 15 transactions.
```

### Updating Items

**User Prompt:**
"Update the 'Web Development' service rate to $85 per hour."

**Alternative Prompts:**
- "Change the rate for Web Development to $85/hour."
- "Update the price of our Web Development service."
- "Increase the Web Development hourly rate."

**Expected Response:**
Claude will use the `update_item` tool to modify the item and confirm:

```
I've updated the 'Web Development' item in Zoho Books:

Item ID: 460000000012345
Name: Web Development
Previous Rate: $75.00 per hour
New Rate: $85.00 per hour

The item has been successfully updated in your Zoho Books account.
```

## Sales Order Management

### Listing Sales Orders

**User Prompt:**
"Show me all open sales orders in Zoho Books."

**Alternative Prompts:**
- "List all pending sales orders."
- "Get all open sales orders from Zoho Books."
- "Show me sales orders that haven't been converted to invoices."

**Expected Response:**
Claude will use the `list_sales_orders` tool to retrieve and display your sales orders:

```
Here are your open sales orders from Zoho Books:

1. SO-00001 - Acme Corporation
   Date: 2023-10-10
   Amount: $3,500.00
   Status: Open
   Reference: PO-2023-789

2. SO-00002 - TechStart Inc
   Date: 2023-10-22
   Amount: $1,200.00
   Status: Open
   Reference: PO-TS-1234

[Additional sales orders...]

Showing 1-5 of 8 open sales orders
```

### Creating Sales Orders

**User Prompt:**
"Create a new sales order for Globex Corporation for 10 hours of Web Development at $85/hour and 5 hours of SEO Consulting at $125/hour."

**Alternative Prompts:**
- "Make a new sales order for Globex Corp."
- "Generate a sales order with these items for Globex."
- "Create an order for Globex Corporation with these services."

**Expected Response:**
Claude will use the `create_sales_order` tool to create the sales order and confirm:

```
I've created a new sales order in Zoho Books:

Sales Order Number: SO-00003
Customer: Globex Corporation
Date: [Today's Date]
Status: Open

Line Items:
1. Web Development
   Quantity: 10 hours
   Rate: $85.00/hour
   Amount: $850.00

2. SEO Consulting
   Quantity: 5 hours
   Rate: $125.00/hour
   Amount: $625.00

Subtotal: $1,475.00
Tax: $0.00
Total: $1,475.00

The sales order has been created in your Zoho Books account.
```

### Getting Sales Order Details

**User Prompt:**
"Get details for sales order SO-00001."

**Alternative Prompts:**
- "Show me information about sales order SO-00001."
- "What's included in sales order SO-00001?"

**Expected Response:**
Claude will use the `get_sales_order` tool to retrieve and display detailed information:

```
Here are the details for sales order SO-00001:

Sales Order Number: SO-00001
Customer: Acme Corporation
Status: Open
Date: October 10, 2023
Reference: PO-2023-789

Line Items:
1. Web Development
   Quantity: 30 hours
   Rate: $75.00/hour
   Amount: $2,250.00

2. SEO Consulting
   Quantity: 10 hours
   Rate: $125.00/hour
   Amount: $1,250.00

Subtotal: $3,500.00
Tax: $0.00
Total: $3,500.00

Notes: Subject to client approval of project timeline.
```

### Updating Sales Orders

**User Prompt:**
"Update sales order SO-00001 to add 5 more hours of Web Development."

**Alternative Prompts:**
- "Add more hours to sales order SO-00001."
- "Update the quantity in sales order SO-00001."
- "Change sales order SO-00001 to include more web development hours."

**Expected Response:**
Claude will use the `update_sales_order` tool to modify the sales order and confirm:

```
I've updated sales order SO-00001 in Zoho Books:

Sales Order Number: SO-00001
Customer: Acme Corporation

Changes made:
- Updated Web Development: 30 hours → 35 hours
- Updated line item amount: $2,250.00 → $2,625.00
- Updated total amount: $3,500.00 → $3,875.00

The sales order has been successfully updated in your Zoho Books account.
```

### Converting to Invoices

**User Prompt:**
"Convert sales order SO-00001 to an invoice."

**Alternative Prompts:**
- "Generate an invoice from sales order SO-00001."
- "Change sales order SO-00001 into an invoice."
- "Bill the client for sales order SO-00001."

**Expected Response:**
Claude will use the `convert_to_invoice` tool to create the invoice and confirm:

```
I've converted sales order SO-00001 to an invoice in Zoho Books:

Sales Order: SO-00001
New Invoice Number: INV-00005
Customer: Acme Corporation
Date: [Today's Date]
Amount: $3,875.00
Status: Draft

The sales order has been successfully converted to an invoice. The invoice is currently in draft status and can be reviewed before sending.
```

## Complex Workflows

### Creating a Customer and Invoice

**User Prompt:**
"Create a new customer called 'Johnson Enterprises' with email 'billing@johnsonent.com' and then create an invoice for them for $1,500 for consulting services with payment terms of Net 30."

**Expected Response:**
Claude will use multiple tools in sequence and provide a comprehensive response:

```
I've completed both tasks in Zoho Books:

1. Created a new customer:
   Name: Johnson Enterprises
   Email: billing@johnsonent.com
   Contact ID: 460000000098765

2. Created a new invoice:
   Invoice Number: INV-00006
   Customer: Johnson Enterprises
   Date: [Today's Date]
   Due Date: [Today + 30 days]
   Status: Draft
   
   Line Items:
   - Consulting Services: $1,500.00
   
   Total: $1,500.00
   Payment Terms: Net 30

Both the customer record and invoice have been created in your Zoho Books account. The invoice is in draft status and ready for review before sending.
```

### Expense Reporting

**User Prompt:**
"Generate a summary of expenses by category for the last month."

**Expected Response:**
Claude will use the `list_expenses` tool with filtering and provide analysis:

```
Here's a summary of your expenses by category for October 2023:

1. Office Supplies: $527.35 (15.2%)
   - 3 transactions

2. Software & Subscriptions: $349.99 (10.1%)
   - 5 transactions

3. Utilities: $175.25 (5.1%)
   - 1 transaction

4. Business Travel: $1,250.75 (36.1%)
   - 2 transactions

5. Marketing: $750.00 (21.6%)
   - 2 transactions

6. Other Expenses: $412.50 (11.9%)
   - 4 transactions

Total Expenses: $3,465.84
Largest Category: Business Travel ($1,250.75)
Most Frequent Category: Software & Subscriptions (5 transactions)
```

### Sales Analysis

**User Prompt:**
"Analyze my top 3 customers by invoice value in the last quarter."

**Expected Response:**
Claude will use a combination of tools to gather data and provide analysis:

```
Here's an analysis of your top 3 customers by invoice value for Q3 2023 (July-September):

1. Acme Corporation
   Total Invoiced: $15,750.00
   Number of Invoices: 5
   Average Invoice Value: $3,150.00
   Largest Invoice: INV-00001 ($3,875.00)
   Most Common Services: Web Development, SEO Consulting

2. TechStart Inc
   Total Invoiced: $8,200.00
   Number of Invoices: 3
   Average Invoice Value: $2,733.33
   Largest Invoice: INV-00002 ($4,500.00)
   Most Common Services: Web Development, Data Analysis

3. Globex Corporation
   Total Invoiced: $5,975.00
   Number of Invoices: 4
   Average Invoice Value: $1,493.75
   Largest Invoice: INV-00003 ($1,975.00)
   Most Common Services: SEO Consulting

These 3 customers represent 72% of your total invoiced amount for Q3 2023 ($41,450.00).
```

These examples demonstrate the wide range of operations possible through the Zoho Books MCP server using natural language instructions through your MCP client.