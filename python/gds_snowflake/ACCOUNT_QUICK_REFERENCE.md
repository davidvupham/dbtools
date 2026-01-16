# SnowflakeAccount Quick Reference

## Import

```python
from gds_snowflake import SnowflakeConnection, SnowflakeAccount, AccountInfo
```

## Initialization

```python
# Connect to Snowflake
conn = SnowflakeConnection(account='myaccount', user='myuser')
conn.connect()

# Create account manager
account_mgr = SnowflakeAccount(conn)

# With custom data directory
account_mgr = SnowflakeAccount(conn, data_dir='/path/to/data')
```

## Retrieve Account Information

### Get Current Account
```python
current = account_mgr.get_current_account()
print(f"Account: {current.account_name}")
print(f"Region: {current.region}")
print(f"Cloud: {current.cloud_provider}")
```

### Get All Accounts (Requires Org Admin)
```python
accounts = account_mgr.get_all_accounts()
for account in accounts:
    print(f"{account.account_name}: {account.region}/{account.cloud_provider}")
```

### Get Account Parameters
```python
params = account_mgr.get_account_parameters()
print(f"Timezone: {params['TIMEZONE']}")
print(f"Week Start: {params['WEEK_START']}")
```

## Save and Load Data

### Save to JSON
```python
# Auto-generated filename
filepath = account_mgr.save_accounts_to_json(accounts)

# Custom filename
filepath = account_mgr.save_accounts_to_json(accounts, filename='my_accounts.json')
```

### Load from JSON
```python
accounts = account_mgr.load_accounts_from_json('my_accounts.json')
```

## File Management

### List Saved Files
```python
files = account_mgr.list_saved_account_files()
for file in files:
    print(file.name)
```

### Get Latest File
```python
latest = account_mgr.get_latest_account_file()
if latest:
    accounts = account_mgr.load_accounts_from_json(latest.name)
```

## Analysis

### Generate Summary
```python
summary = account_mgr.get_account_summary(accounts)
print(f"Total: {summary['total_accounts']}")
print(f"Organizations: {summary['organizations']}")
print(f"Regions: {summary['regions']}")
print(f"Clouds: {summary['cloud_providers']}")
print(f"Editions: {summary['editions']}")
print(f"Org Admins: {summary['org_admin_accounts']}")
```

## AccountInfo Attributes

```python
account.account_name          # str
account.organization_name     # Optional[str]
account.account_locator       # Optional[str]
account.region                # Optional[str]
account.cloud_provider        # Optional[str] (AWS, Azure, GCP)
account.account_url           # Optional[str]
account.created_on            # Optional[str]
account.comment               # Optional[str]
account.is_org_admin          # bool
account.account_edition       # Optional[str]
account.is_current            # bool
account.retrieved_at          # Optional[str]
```

## Configuration

### Environment Variable
```bash
export GDS_DATA_DIR=/var/lib/snowflake_data
```

### Priority Order
1. Constructor parameter `data_dir`
2. Environment variable `GDS_DATA_DIR`
3. Default `./data`

## Complete Example

```python
from gds_snowflake import SnowflakeConnection, SnowflakeAccount
import os

# Set data directory
os.environ['GDS_DATA_DIR'] = '/var/lib/snowflake'

# Connect
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    vault_secret_path='data/snowflake'
)
conn.connect()

# Create manager
account_mgr = SnowflakeAccount(conn)

try:
    # Get accounts
    accounts = account_mgr.get_all_accounts()

    # Save to JSON
    filepath = account_mgr.save_accounts_to_json(accounts)
    print(f"Saved to: {filepath}")

    # Analyze
    summary = account_mgr.get_account_summary(accounts)
    print(f"\nSummary:")
    print(f"  Total: {summary['total_accounts']}")
    print(f"  Regions: {list(summary['regions'].keys())}")

finally:
    conn.close()
```

## Error Handling

```python
try:
    accounts = account_mgr.get_all_accounts()
except Exception as e:
    print(f"Error: {e}")
    # Fallback to current account only
    accounts = [account_mgr.get_current_account()]
```

## Context Manager Usage

```python
with SnowflakeConnection(account='myaccount', user='myuser') as conn:
    account_mgr = SnowflakeAccount(conn)
    accounts = account_mgr.get_all_accounts()
    filepath = account_mgr.save_accounts_to_json(accounts)
```

## Common Patterns

### Filter by Cloud Provider
```python
aws_accounts = [a for a in accounts if a.cloud_provider == 'AWS']
azure_accounts = [a for a in accounts if a.cloud_provider == 'Azure']
```

### Filter by Region
```python
us_accounts = [a for a in accounts if a.region and a.region.startswith('us-')]
```

### Find Current Account
```python
current = next(a for a in accounts if a.is_current)
```

### Sort by Name
```python
sorted_accounts = sorted(accounts, key=lambda a: a.account_name)
```

## JSON File Format

```json
{
  "metadata": {
    "retrieved_at": "2025-10-06T10:30:00",
    "account_count": 3,
    "data_directory": "/var/lib/snowflake"
  },
  "accounts": [
    {
      "account_name": "PROD_ACCOUNT",
      "organization_name": "MY_ORG",
      "account_locator": "ABC123",
      "region": "us-west-2",
      "cloud_provider": "AWS",
      "account_edition": "ENTERPRISE",
      "is_current": true,
      "is_org_admin": true,
      "retrieved_at": "2025-10-06T10:30:00"
    }
  ]
}
```

## Tips

1. **Permissions**: Use an account with organization admin privileges to retrieve all accounts
2. **Data Directory**: Set `GDS_DATA_DIR` environment variable for consistent file location
3. **File Naming**: Auto-generated filenames include timestamp for easy tracking
4. **Error Handling**: Always wrap calls in try/except for production code
5. **Context Managers**: Use `with` statement for automatic connection cleanup

## See Also

- [Complete Documentation](ACCOUNT_MODULE_DOCUMENTATION.md)
- [Implementation Summary](ACCOUNT_MODULE_IMPLEMENTATION_SUMMARY.md)
- [Example Usage](examples/account_example.py)
- [Main README](README.md)
