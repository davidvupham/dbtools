# Robocorp Tutorial

Python-based Robotic Process Automation (RPA).

## Overview

**Robocorp** provides an open-source Python framework for building software robots that automate repetitive tasks. It includes libraries for browser automation, document processing, and integration with the Robocorp Control Room for orchestration.

| | |
|---|---|
| **Package** | `robocorp` |
| **Install** | `pip install robocorp` |
| **Documentation** | [robocorp.com/docs](https://robocorp.com/docs/) |
| **GitHub** | [robocorp/robocorp](https://github.com/robocorp/robocorp) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Task Definition](#task-definition)
4. [Browser Automation](#browser-automation)
5. [Excel Processing](#excel-processing)
6. [PDF Processing](#pdf-processing)
7. [Email Automation](#email-automation)
8. [Error Handling](#error-handling)
9. [Control Room Integration](#control-room-integration)
10. [Best Practices](#best-practices)

---

## Installation

```bash
# Core package
pip install robocorp

# Browser automation
pip install robocorp-browser

# Excel processing
pip install robocorp-excel

# Additional libraries
pip install rpaframework  # Full RPA framework
```

### VS Code Extension

Install the **Robocorp Code** extension for:

- Task discovery and running
- Debugging support
- Control Room integration

---

## Quick Start

Create a simple automation:

```python
# tasks.py
from robocorp.tasks import task

@task
def hello_robot():
    """A simple hello world robot."""
    print("Hello from Robocorp!")
    return "Robot completed successfully"
```

Run the task:

```bash
python -m robocorp.tasks run tasks.py
```

---

## Task Definition

### Basic Task

```python
from robocorp.tasks import task

@task
def process_invoices():
    """Process all pending invoices."""
    invoices = fetch_pending_invoices()
    for invoice in invoices:
        process_invoice(invoice)
    return f"Processed {len(invoices)} invoices"
```

### Multiple Tasks

```python
from robocorp.tasks import task

@task
def task_one():
    """First task."""
    print("Running task one")

@task
def task_two():
    """Second task."""
    print("Running task two")

@task
def main_task():
    """Main orchestration task."""
    task_one()
    task_two()
```

### Task with Work Items

```python
from robocorp.tasks import task
from robocorp import workitems

@task
def process_orders():
    """Process orders from work items."""
    for item in workitems.inputs:
        try:
            order = item.payload
            process_order(order)
            item.done()
        except Exception as e:
            item.fail(exception_type="ORDER_ERROR", message=str(e))
```

---

## Browser Automation

### Basic Browser Usage

```python
from robocorp.tasks import task
from robocorp import browser

@task
def web_automation():
    """Automate web interactions."""
    # Open browser and navigate
    browser.goto("https://example.com")

    # Wait for page load
    page = browser.page()

    # Click elements
    page.click("text=Login")

    # Fill forms
    page.fill("#username", "myuser")
    page.fill("#password", "mypassword")
    page.click("button[type=submit]")

    # Wait for navigation
    page.wait_for_url("**/dashboard")

    # Take screenshot
    page.screenshot(path="screenshot.png")
```

### Advanced Browser Operations

```python
from robocorp.tasks import task
from robocorp import browser

@task
def advanced_browser():
    """Advanced browser automation."""
    page = browser.page()

    # Wait for elements
    page.wait_for_selector("#data-table", timeout=10000)

    # Get element text
    title = page.text_content("h1")
    print(f"Page title: {title}")

    # Get all links
    links = page.query_selector_all("a")
    for link in links:
        href = link.get_attribute("href")
        print(f"Link: {href}")

    # Handle dropdowns
    page.select_option("#country", "US")

    # Handle checkboxes
    page.check("#agree-terms")

    # Execute JavaScript
    result = page.evaluate("document.title")
    print(f"Document title: {result}")
```

### Form Automation

```python
from robocorp.tasks import task
from robocorp import browser

@task
def fill_form():
    """Fill and submit a web form."""
    browser.goto("https://forms.example.com/application")
    page = browser.page()

    # Personal information
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#email", "john.doe@example.com")
    page.fill("#phone", "+1-555-123-4567")

    # Date picker
    page.fill("#birth-date", "1990-01-15")

    # Radio buttons
    page.click("input[name='gender'][value='male']")

    # Multi-select
    page.select_option("#interests", ["technology", "finance"])

    # Rich text editor
    page.fill(".rich-editor", "This is my application message.")

    # Submit
    page.click("button[type='submit']")

    # Verify success
    page.wait_for_selector(".success-message")
    print("Form submitted successfully!")
```

---

## Excel Processing

### Read Excel Files

```python
from robocorp.tasks import task
from robocorp import excel

@task
def read_excel():
    """Read data from Excel file."""
    workbook = excel.open_workbook("data/input.xlsx")
    worksheet = workbook.worksheet("Sheet1")

    # Get all rows
    rows = worksheet.as_list(header=True)
    for row in rows:
        print(f"Name: {row['Name']}, Email: {row['Email']}")

    # Get specific range
    data = worksheet.get_cell_value("A1")
    print(f"Cell A1: {data}")
```

### Write Excel Files

```python
from robocorp.tasks import task
from robocorp import excel

@task
def write_excel():
    """Write data to Excel file."""
    # Create new workbook
    workbook = excel.create_workbook()
    worksheet = workbook.create_worksheet("Results")

    # Write headers
    headers = ["Name", "Status", "Date"]
    worksheet.append_rows_to_worksheet([headers])

    # Write data
    data = [
        ["Order 001", "Completed", "2024-01-15"],
        ["Order 002", "Pending", "2024-01-16"],
        ["Order 003", "Completed", "2024-01-17"],
    ]
    worksheet.append_rows_to_worksheet(data)

    # Save
    workbook.save("output/results.xlsx")
```

### Process Large Excel Files

```python
from robocorp.tasks import task
from robocorp import excel

@task
def process_large_excel():
    """Process large Excel file efficiently."""
    workbook = excel.open_workbook("data/large_file.xlsx")
    worksheet = workbook.worksheet("Data")

    # Process in chunks
    rows = worksheet.as_list(header=True)

    results = []
    for i, row in enumerate(rows):
        # Process each row
        result = process_row(row)
        results.append(result)

        # Log progress every 100 rows
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} rows")

    return results
```

---

## PDF Processing

### Read PDF Content

```python
from robocorp.tasks import task
from RPA.PDF import PDF

@task
def read_pdf():
    """Extract text from PDF."""
    pdf = PDF()

    # Get all text
    text = pdf.get_text_from_pdf("documents/invoice.pdf")
    print(text)

    # Get text from specific pages
    page_text = pdf.get_text_from_pdf(
        "documents/report.pdf",
        pages=[1, 2, 3]
    )
```

### Extract PDF Tables

```python
from robocorp.tasks import task
from RPA.PDF import PDF

@task
def extract_tables():
    """Extract tables from PDF."""
    pdf = PDF()

    # Extract tables
    tables = pdf.extract_tables_from_pdf("documents/report.pdf")

    for i, table in enumerate(tables):
        print(f"Table {i + 1}:")
        for row in table:
            print(row)
```

### Fill PDF Forms

```python
from robocorp.tasks import task
from RPA.PDF import PDF

@task
def fill_pdf_form():
    """Fill out a PDF form."""
    pdf = PDF()

    # Get form fields
    fields = pdf.get_pdf_info("forms/application.pdf")
    print(f"Form fields: {fields}")

    # Fill fields
    pdf.update_field_values(
        "forms/application.pdf",
        "forms/completed_application.pdf",
        {
            "name": "John Doe",
            "email": "john@example.com",
            "date": "2024-01-15",
        }
    )
```

---

## Email Automation

### Send Emails

```python
from robocorp.tasks import task
from RPA.Email.ImapSmtp import ImapSmtp

@task
def send_email():
    """Send an email with attachment."""
    mail = ImapSmtp(
        smtp_server="smtp.gmail.com",
        smtp_port=587
    )

    mail.authorize(
        account="your-email@gmail.com",
        password="your-app-password"
    )

    mail.send_message(
        sender="your-email@gmail.com",
        recipients="recipient@example.com",
        subject="Automation Report",
        body="Please find the attached report.",
        attachments=["output/report.xlsx"]
    )
```

### Read Emails

```python
from robocorp.tasks import task
from RPA.Email.ImapSmtp import ImapSmtp

@task
def process_emails():
    """Read and process emails."""
    mail = ImapSmtp(
        imap_server="imap.gmail.com",
        imap_port=993
    )

    mail.authorize(
        account="your-email@gmail.com",
        password="your-app-password"
    )

    # Get unread emails
    mail.select_folder("INBOX")
    messages = mail.list_messages(criterion="UNSEEN")

    for msg in messages:
        print(f"From: {msg['From']}")
        print(f"Subject: {msg['Subject']}")

        # Download attachments
        if msg.get_payload():
            mail.save_attachments(msg, "downloads/")
```

---

## Error Handling

### Try-Catch Pattern

```python
from robocorp.tasks import task
from robocorp import browser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def robust_automation():
    """Automation with error handling."""
    try:
        browser.goto("https://example.com")
        page = browser.page()

        # Attempt action with retry
        for attempt in range(3):
            try:
                page.click("#submit-button", timeout=5000)
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise

        logger.info("Automation completed successfully")

    except Exception as e:
        logger.error(f"Automation failed: {e}")
        # Take screenshot for debugging
        browser.page().screenshot(path="error_screenshot.png")
        raise
```

### Work Item Error Handling

```python
from robocorp.tasks import task
from robocorp import workitems

@task
def process_with_retry():
    """Process work items with error handling."""
    for item in workitems.inputs:
        try:
            result = process_item(item.payload)

            # Create output work item
            workitems.outputs.create(payload=result)
            item.done()

        except ValueError as e:
            # Business logic error - don't retry
            item.fail(
                exception_type="BUSINESS_ERROR",
                message=str(e)
            )

        except ConnectionError as e:
            # Technical error - retry later
            item.fail(
                exception_type="APPLICATION_ERROR",
                message=str(e)
            )
```

---

## Control Room Integration

### Configure robot.yaml

```yaml
# robot.yaml
tasks:
  Process Orders:
    shell: python -m robocorp.tasks run tasks.py -t process_orders

  Generate Reports:
    shell: python -m robocorp.tasks run tasks.py -t generate_reports

condaConfigFile: conda.yaml

environmentConfigs:
  - environment_windows_amd64_freeze.yaml
  - environment_linux_amd64_freeze.yaml
  - environment_darwin_amd64_freeze.yaml
  - conda.yaml
```

### Vault Secrets

```python
from robocorp.tasks import task
from robocorp import vault

@task
def use_secrets():
    """Access secrets from Control Room vault."""
    # Get secret
    credentials = vault.get_secret("database_credentials")

    username = credentials["username"]
    password = credentials["password"]

    # Use credentials
    connect_to_database(username, password)
```

### Asset Storage

```python
from robocorp.tasks import task
from robocorp import storage

@task
def use_assets():
    """Work with Control Room assets."""
    # Download asset
    storage.get_file("config/settings.json", "local_settings.json")

    # Upload result
    storage.set_file("results/output.xlsx", "output/report.xlsx")
```

---

## Best Practices

### 1. Use Logging

```python
import logging
from robocorp.tasks import task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@task
def logged_task():
    logger.info("Starting task")
    # ... work ...
    logger.info("Task completed")
```

### 2. Modular Code Structure

```
my_robot/
├── tasks.py           # Task definitions
├── pages/             # Page objects for web automation
│   ├── login_page.py
│   └── dashboard_page.py
├── processors/        # Business logic
│   └── invoice_processor.py
├── utils/             # Utilities
│   └── helpers.py
├── robot.yaml
└── conda.yaml
```

### 3. Page Object Pattern

```python
# pages/login_page.py
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#login-btn"

    def login(self, username: str, password: str):
        self.page.fill(self.username_input, username)
        self.page.fill(self.password_input, password)
        self.page.click(self.login_button)
        self.page.wait_for_url("**/dashboard")
```

### 4. Configuration Management

```python
# config.py
from dataclasses import dataclass
import os

@dataclass
class Config:
    base_url: str = os.getenv("BASE_URL", "https://example.com")
    timeout: int = int(os.getenv("TIMEOUT", "30000"))
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"

config = Config()
```

---

## Quick Reference

### CLI Commands

```bash
# Run specific task
python -m robocorp.tasks run tasks.py -t task_name

# List available tasks
python -m robocorp.tasks list tasks.py

# Run with work items (local)
python -m robocorp.tasks run tasks.py --input work-items.json
```

### Common Browser Actions

```python
page.goto(url)                    # Navigate
page.click(selector)              # Click
page.fill(selector, value)        # Type text
page.select_option(selector, val) # Select dropdown
page.check(selector)              # Check checkbox
page.screenshot(path=path)        # Screenshot
page.wait_for_selector(selector)  # Wait for element
```

---

## See Also

- [Robocorp Documentation](https://robocorp.com/docs/)
- [RPA Framework](https://rpaframework.org/)
- [Faker Tutorial](../faker/README.md) - Generate test data for RPA

---

[← Back to Modules Index](../README.md)
