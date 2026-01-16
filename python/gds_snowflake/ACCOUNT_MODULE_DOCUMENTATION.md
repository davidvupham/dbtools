# Snowflake Account Management - OOP Design Documentation

## Overview

The Snowflake Account Management module provides a comprehensive, object-oriented solution for retrieving, managing, and storing Snowflake account information. This document describes the OOP class design, architecture, and usage patterns.

## Architecture

### Class Hierarchy

```
SnowflakeAccount
    ├── Depends on: SnowflakeConnection
    └── Uses: AccountInfo (dataclass)
```

### Design Principles

The module follows these OOP principles:

1. **Single Responsibility Principle (SRP)**: 
   - `SnowflakeAccount` handles account information retrieval and storage
   - `AccountInfo` represents account data
   - `SnowflakeConnection` manages database connections

2. **Dependency Injection**: 
   - `SnowflakeAccount` receives a `SnowflakeConnection` instance, allowing for loose coupling and easier testing

3. **Encapsulation**: 
   - Data directory management is encapsulated within the class
   - Private methods (prefixed with `_`) handle internal operations

4. **Composition over Inheritance**: 
   - Uses composition by accepting a connection object rather than inheriting from connection classes

## Classes

### 1. AccountInfo (Dataclass)

A dataclass representing a Snowflake account and its attributes.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `account_name` | `str` | The name of the Snowflake account (required) |
| `organization_name` | `Optional[str]` | The organization the account belongs to |
| `account_locator` | `Optional[str]` | The unique locator for the account |
| `region` | `Optional[str]` | The cloud region where the account is hosted |
| `cloud_provider` | `Optional[str]` | The cloud provider (AWS, Azure, GCP) |
| `account_url` | `Optional[str]` | The URL for accessing the account |
| `created_on` | `Optional[str]` | When the account was created |
| `comment` | `Optional[str]` | Optional description or comment |
| `is_org_admin` | `bool` | Whether the account has org admin privileges |
| `account_edition` | `Optional[str]` | The Snowflake edition (Standard, Enterprise, etc.) |
| `is_current` | `bool` | Whether this is the currently connected account |
| `retrieved_at` | `Optional[str]` | Timestamp when information was retrieved |

#### Methods

- **`to_dict() -> dict[str, Any]`**: Convert AccountInfo to dictionary format

#### Design Rationale

- Uses Python's `@dataclass` decorator for automatic generation of `__init__`, `__repr__`, and `__eq__` methods
- Immutable by default to ensure data integrity
- Provides type hints for all attributes for better IDE support and type checking

### 2. SnowflakeAccount (Primary Class)

Manages Snowflake account information retrieval and storage.

#### Constructor

```python
def __init__(
    self,
    connection: SnowflakeConnection,
    data_dir: Optional[str] = None
):
```

**Parameters:**
- `connection`: Active `SnowflakeConnection` instance (dependency injection)
- `data_dir`: Optional data directory path (defaults to `GDS_DATA_DIR` env var or `./data`)

**Design Decision:** Constructor uses dependency injection for the connection, making the class testable and following the Dependency Inversion Principle.

#### Public Methods

##### Data Retrieval Methods

1. **`get_current_account() -> AccountInfo`**
   - Retrieves information about the currently connected account
   - Returns: `AccountInfo` object with current account details
   - Raises: `Exception` if query execution fails
   - SQL Query: Uses Snowflake system functions like `CURRENT_ACCOUNT()`

2. **`get_all_accounts() -> list[AccountInfo]`**
   - Retrieves all Snowflake accounts in the organization
   - Returns: List of `AccountInfo` objects
   - Requires: Organization-level privileges
   - Raises: `Exception` if user lacks privileges or query fails
   - SQL Query: Queries `SNOWFLAKE.ORGANIZATION_USAGE.ACCOUNTS` view

3. **`get_account_parameters(account_name: Optional[str] = None) -> dict[str, Any]`**
   - Retrieves account-level parameters and settings
   - Parameters: Optional account name (defaults to current account)
   - Returns: Dictionary of parameter names and values
   - SQL Query: `SHOW PARAMETERS IN ACCOUNT`

##### Data Persistence Methods

4. **`save_accounts_to_json(accounts: list[AccountInfo], filename: Optional[str] = None) -> Path`**
   - Saves account information to JSON file
   - Parameters:
     - `accounts`: List of `AccountInfo` objects to save
     - `filename`: Optional filename (auto-generated if not provided)
   - Returns: `Path` object pointing to saved file
   - Format: Pretty-printed JSON with metadata wrapper
   - File naming: `snowflake_accounts_YYYYMMDD_HHMMSS.json`

5. **`load_accounts_from_json(filename: str) -> list[AccountInfo]`**
   - Loads account information from JSON file
   - Parameters: `filename` - Name of JSON file in data directory
   - Returns: List of `AccountInfo` objects
   - Raises: `FileNotFoundError` if file doesn't exist

##### Analysis Methods

6. **`get_account_summary(accounts: list[AccountInfo]) -> dict[str, Any]`**
   - Generates summary statistics for accounts
   - Parameters: List of `AccountInfo` objects
   - Returns: Dictionary with aggregated statistics:
     - `total_accounts`: Total number of accounts
     - `organizations`: Count of unique organizations
     - `regions`: Dictionary of region counts
     - `cloud_providers`: Dictionary of provider counts
     - `editions`: Dictionary of edition counts
     - `org_admin_accounts`: Count of accounts with org admin privileges

##### File Management Methods

7. **`list_saved_account_files() -> list[Path]`**
   - Lists all saved account JSON files in data directory
   - Returns: List of `Path` objects sorted by date (newest first)

8. **`get_latest_account_file() -> Optional[Path]`**
   - Gets the most recently saved account JSON file
   - Returns: `Path` to latest file or `None` if no files exist

#### Private Methods

1. **`_get_data_directory(data_dir: Optional[str] = None) -> Path`**
   - Determines data directory path with priority order:
     1. Explicitly provided `data_dir` parameter
     2. `GDS_DATA_DIR` environment variable
     3. Default to `./data` in current working directory
   - Returns: `Path` object for data directory

2. **`_ensure_data_directory() -> None`**
   - Ensures data directory exists, creates if necessary
   - Uses `Path.mkdir(parents=True, exist_ok=True)`
   - Raises: `OSError` if directory cannot be created

#### Design Patterns Used

##### 1. Dependency Injection Pattern
```python
account_mgr = SnowflakeAccount(connection)  # Connection injected
```

##### 2. Factory Pattern (for AccountInfo creation)
```python
account = AccountInfo(
    account_name=row.get('ACCOUNT_NAME', ''),
    organization_name=row.get('ORGANIZATION_NAME'),
    # ... other fields
)
```

##### 3. Template Method Pattern (for data directory management)
- Public interface: `__init__` calls private methods
- Private methods: `_get_data_directory()`, `_ensure_data_directory()`

##### 4. Strategy Pattern (for file naming)
- Auto-generated names: `snowflake_accounts_{timestamp}.json`
- Custom names: User-provided filename

## Data Storage Format

### JSON File Structure

```json
{
  "metadata": {
    "retrieved_at": "2025-10-06T10:30:00",
    "account_count": 3,
    "data_directory": "/path/to/data"
  },
  "accounts": [
    {
      "account_name": "PROD_ACCOUNT",
      "organization_name": "MY_ORG",
      "account_locator": "ABC123",
      "region": "us-west-2",
      "cloud_provider": "AWS",
      "account_url": "https://abc123.snowflakecomputing.com",
      "created_on": "2023-01-01T00:00:00",
      "comment": "Production account",
      "is_org_admin": true,
      "account_edition": "ENTERPRISE",
      "is_current": true,
      "retrieved_at": "2025-10-06T10:30:00"
    }
  ]
}
```

### Design Decisions

1. **Metadata Wrapper**: Includes metadata for version tracking and auditing
2. **ISO 8601 Timestamps**: All timestamps use ISO 8601 format for portability
3. **Pretty Printing**: JSON is indented for human readability
4. **Null Handling**: Optional fields use `null` rather than empty strings

## Configuration

### Environment Variables

The module supports the following environment variable:

| Variable | Description | Default |
|----------|-------------|---------|
| `GDS_DATA_DIR` | Base directory for storing account data | `./data` |

### Priority Order

1. Constructor parameter `data_dir`
2. Environment variable `GDS_DATA_DIR`
3. Default value `./data`

## Usage Examples

### Basic Usage

```python
from gds_snowflake import SnowflakeConnection, SnowflakeAccount

# Connect to Snowflake
conn = SnowflakeConnection(account='myaccount', user='myuser')
conn.connect()

# Create account manager
account_mgr = SnowflakeAccount(conn)

# Get all accounts
accounts = account_mgr.get_all_accounts()

# Save to JSON
filepath = account_mgr.save_accounts_to_json(accounts)
print(f"Saved to {filepath}")
```

### Advanced Usage with Custom Data Directory

```python
import os
from gds_snowflake import SnowflakeConnection, SnowflakeAccount

# Set custom data directory
os.environ['GDS_DATA_DIR'] = '/var/lib/snowflake_data'

conn = SnowflakeConnection(account='myaccount', user='myuser')
conn.connect()

# Create account manager with custom directory
account_mgr = SnowflakeAccount(conn, data_dir='/custom/path')

# Get accounts and generate summary
accounts = account_mgr.get_all_accounts()
summary = account_mgr.get_account_summary(accounts)

print(f"Total accounts: {summary['total_accounts']}")
print(f"Regions: {summary['regions']}")
```

### Loading and Analyzing Historical Data

```python
from gds_snowflake import SnowflakeConnection, SnowflakeAccount

conn = SnowflakeConnection(account='myaccount', user='myuser')
conn.connect()

account_mgr = SnowflakeAccount(conn)

# Get latest saved file
latest_file = account_mgr.get_latest_account_file()

if latest_file:
    # Load historical data
    accounts = account_mgr.load_accounts_from_json(latest_file.name)
    
    # Analyze
    summary = account_mgr.get_account_summary(accounts)
    print(f"Historical snapshot from {latest_file.name}")
    print(f"Accounts by cloud provider: {summary['cloud_providers']}")
```

## Error Handling

The module implements comprehensive error handling:

### Exception Types

1. **ValueError**: Invalid data or missing required information
2. **FileNotFoundError**: Requested JSON file doesn't exist
3. **OSError**: File system operations fail
4. **Exception**: Database query failures or permission issues

### Logging

All operations are logged using Python's `logging` module:

```python
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
```

Log levels:
- **INFO**: Successful operations, counts, file paths
- **WARNING**: Permission issues, fallback behaviors
- **ERROR**: Query failures, file I/O errors

## Testing

The module includes comprehensive unit tests in `tests/test_account.py`:

### Test Coverage

- ✅ AccountInfo dataclass creation and serialization
- ✅ Data directory initialization and creation
- ✅ Current account retrieval
- ✅ All accounts retrieval
- ✅ Account parameters retrieval
- ✅ JSON saving and loading
- ✅ Account summary generation
- ✅ File listing and latest file retrieval
- ✅ Error handling for various failure scenarios

### Running Tests

```bash
cd gds_snowflake
python -m pytest tests/test_account.py -v
```

## Performance Considerations

1. **Database Queries**: 
   - Queries use indexed system views for optimal performance
   - Connection pooling handled by `SnowflakeConnection`

2. **File I/O**: 
   - JSON files are written atomically
   - Large account lists are handled efficiently with streaming

3. **Memory Usage**: 
   - Account data is loaded into memory as needed
   - No unnecessary data duplication

## Security Considerations

1. **Authentication**: 
   - Uses existing `SnowflakeConnection` authentication
   - No credential storage in this module

2. **File Permissions**: 
   - JSON files inherit system umask
   - Data directory permissions should be set appropriately

3. **Data Privacy**: 
   - Account metadata may contain sensitive information
   - Ensure proper access controls on data directory

## Future Enhancements

Potential improvements:

1. **Compression**: Add support for compressed JSON files
2. **Encryption**: Encrypt sensitive account data at rest
3. **Caching**: Cache account information with TTL
4. **Async Operations**: Support for async/await patterns
5. **Export Formats**: Support CSV, Excel, or Parquet formats
6. **Change Detection**: Track changes between snapshots
7. **Notifications**: Alert on account changes or anomalies

## Version History

- **v1.0.0** (2025-10-06): Initial release
  - Account information retrieval
  - JSON storage and loading
  - Summary generation
  - File management utilities

## License

MIT License - See LICENSE file for details.
