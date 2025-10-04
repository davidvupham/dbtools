# GDS Snowflake Package

A Python package for managing Snowflake database connections, replication monitoring, and database metadata retrieval.

## Features

- **Robust Connection Management**: Automatic reconnection, connection pooling, and account switching
- **Replication Monitoring**: Monitor failover groups for replication failures and latency
- **Failover Group Management**: Query and manage Snowflake failover groups
- **Database Metadata Retrieval**: Comprehensive metadata about Snowflake objects (databases, schemas, tables, views, functions, procedures, stages, pipes, tasks, streams, etc.)
- **Cron Schedule Parsing**: Parse replication schedules and calculate intervals

## Installation

```bash
pip install gds-snowflake
```

Or install from source:

```bash
git clone https://github.com/davidvupham/snowflake.git
cd snowflake/gds_snowflake
pip install .
```

## Configuration

### Environment Variables

The package supports the following environment variables for default configuration:

```bash
# Snowflake connection
SNOWFLAKE_USER=your_username
SNOWFLAKE_ACCOUNT=your_account

# Vault configuration (for RSA key authentication)
VAULT_ADDR=https://vault.example.com:8200
VAULT_NAMESPACE=your_namespace
VAULT_SECRET_PATH=data/snowflake
VAULT_MOUNT_POINT=secret
VAULT_ROLE_ID=your_role_id
VAULT_SECRET_ID=your_secret_id
```

When environment variables are set, you can create connections with minimal parameters.

## Quick Start

### Basic Connection

```python
from gds_snowflake import SnowflakeConnection

# Method 1: Using environment variables for Vault configuration
# Set VAULT_ADDR, VAULT_SECRET_PATH, VAULT_MOUNT_POINT, etc. in environment
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    warehouse='my_warehouse',
    role='my_role'
)

# Method 2: Explicitly specifying Vault parameters
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    warehouse='my_warehouse',
    role='my_role',
    vault_secret_path='data/snowflake',
    vault_mount_point='secret',
    vault_addr='https://vault.example.com:8200'
)

# Connect
conn.connect()

# Execute query
results = conn.execute_query("SELECT CURRENT_VERSION()")
print(results)

# Close connection
conn.close()
```

### Context Manager

```python
from gds_snowflake import SnowflakeConnection

# Using environment variables (recommended)
with SnowflakeConnection(account='myaccount', user='myuser') as conn:
    results = conn.execute_query("SELECT * FROM my_table")
    for row in results:
        print(row)

# Or with explicit Vault parameters
with SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
) as conn:
    results = conn.execute_query("SELECT * FROM my_table")
    for row in results:
        print(row)
```

### Replication Monitoring

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

# Connect to Snowflake
conn = SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
)
conn.connect()

# Create replication monitor
repl = SnowflakeReplication(conn)

# Get all failover groups
failover_groups = repl.get_failover_groups()

for group in failover_groups:
    print(f"Group: {group.name}")
    print(f"Type: {group.type}")
    print(f"Primary: {group.primary_account}")
    print(f"Secondaries: {group.get_secondary_accounts()}")
    
    # Check for replication failures
    if repl.check_replication_failure(group):
        print(f"⚠️ Replication failure detected for {group.name}")
    
    # Check for latency issues
    latency_minutes = repl.check_replication_latency(group)
    if latency_minutes and latency_minutes > 0:
        print(f"⚠️ Replication latency: {latency_minutes} minutes")

conn.close()
```

### Failover Group Details

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

conn = SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
)
conn.connect()

repl = SnowflakeReplication(conn)
groups = repl.get_failover_groups()

for group in groups:
    print(f"\nGroup: {group.name}")
    print(f"  Type: {group.type}")
    print(f"  Is Primary: {group.is_primary()}")
    print(f"  Primary Account: {group.primary_account}")
    print(f"  Replication Schedule: {group.replication_schedule}")
    
    # Parse cron schedule
    interval = repl.parse_cron_schedule(group.replication_schedule)
    if interval:
        print(f"  Replication Interval: {interval} minutes")
    
    # Get secondary accounts
    secondaries = group.get_secondary_accounts()
    print(f"  Secondary Accounts: {', '.join(secondaries)}")
    
    # Get a secondary account for querying
    secondary = group.get_secondary_account()
    if secondary:
        print(f"  Available Secondary: {secondary}")
```

### Account Switching

```python
from gds_snowflake import SnowflakeConnection

conn = SnowflakeConnection(
    account='primary_account', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
)
conn.connect()

# Do work on primary
results = conn.execute_query("SELECT * FROM primary_table")

# Switch to secondary account
conn.switch_account('secondary_account')

# Do work on secondary
results = conn.execute_query("SELECT * FROM secondary_table")

conn.close()
```

### Database Metadata Retrieval

```python
from gds_snowflake import SnowflakeConnection, SnowflakeMetadata

# Connect to Snowflake
conn = SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
)
conn.connect()

# Create metadata retriever
metadata = SnowflakeMetadata(conn)

# Get all databases
databases = metadata.get_databases()
for db in databases:
    print(f"Database: {db['DATABASE_NAME']}, Owner: {db['DATABASE_OWNER']}")

# Get schemas in a database
schemas = metadata.get_schemas(database_name='MYDB')
for schema in schemas:
    print(f"Schema: {schema['SCHEMA_NAME']}")

# Get tables in a schema
tables = metadata.get_tables(database_name='MYDB', schema_name='PUBLIC')
for table in tables:
    print(f"Table: {table['TABLE_NAME']}, Rows: {table['ROW_COUNT']}")

# Get columns for a table
columns = metadata.get_columns(
    table_name='CUSTOMERS',
    database_name='MYDB',
    schema_name='PUBLIC'
)
for col in columns:
    print(f"Column: {col['COLUMN_NAME']}, Type: {col['DATA_TYPE']}")

# Get comprehensive metadata for a database
all_metadata = metadata.get_all_metadata(database_name='MYDB')
print(f"Summary: {all_metadata['summary']}")

conn.close()
```

### Metadata for Data Pipeline Objects

```python
from gds_snowflake import SnowflakeConnection, SnowflakeMetadata

with SnowflakeConnection(
    account='myaccount', 
    user='myuser', 
    vault_secret_path='data/snowflake',
    vault_mount_point='secret'
) as conn:
    metadata = SnowflakeMetadata(conn)
    
    # Get stages
    stages = metadata.get_stages(database_name='MYDB', schema_name='PUBLIC')
    
    # Get file formats
    file_formats = metadata.get_file_formats(database_name='MYDB', schema_name='PUBLIC')
    
    # Get pipes (Snowpipe)
    pipes = metadata.get_pipes(database_name='MYDB', schema_name='PUBLIC')
    
    # Get tasks
    tasks = metadata.get_tasks(database_name='MYDB', schema_name='PUBLIC')
    
    # Get streams
    streams = metadata.get_streams(database_name='MYDB', schema_name='PUBLIC')
    
    # Get functions and procedures
    functions = metadata.get_functions(database_name='MYDB', schema_name='PUBLIC')
    procedures = metadata.get_procedures(database_name='MYDB', schema_name='PUBLIC')
```

## Monitoring with SnowflakeMonitor

The `SnowflakeMonitor` class provides comprehensive monitoring capabilities for Snowflake accounts:

```python
from gds_snowflake import SnowflakeMonitor

# Create monitor instance
monitor = SnowflakeMonitor(
    account="your-account",
    connectivity_timeout=30,
    latency_threshold_minutes=30.0,
    enable_email_alerts=True
)

# Run comprehensive monitoring
results = monitor.monitor_all()

# Check connectivity
if results['summary']['connectivity_ok']:
    print("✓ Connectivity OK")
else:
    print("✗ Connectivity Failed")

# Check for issues
failures = results['summary']['groups_with_failures']
latency_issues = results['summary']['groups_with_latency']

print(f"Replication Failures: {failures}")
print(f"Latency Issues: {latency_issues}")

# Clean up
monitor.close()
```

### Individual Monitoring Methods

```python
# Test connectivity only
connectivity = monitor.monitor_connectivity()
print(f"Connected in {connectivity.response_time_ms}ms")

# Check replication failures
failures = monitor.monitor_replication_failures()
for result in failures:
    if result.has_failure:
        print(f"✗ {result.failover_group}: {result.failure_message}")

# Check replication latency
latency_issues = monitor.monitor_replication_latency()
for result in latency_issues:
    if result.has_latency:
        print(f"⚠ {result.failover_group}: {result.latency_minutes} min")
```

### Context Manager Usage

```python
# Use with context manager for automatic cleanup
with SnowflakeMonitor(account="your-account") as monitor:
    results = monitor.monitor_all()
    # Monitor automatically closed when exiting context
```

**Key Features:**

- **Connectivity Testing**: Network and account availability monitoring
- **Replication Monitoring**: Failure detection and latency tracking
- **Email Notifications**: Automated alerts for issues
- **Configurable Thresholds**: Customizable alerting criteria
- **Production Ready**: Built-in error handling and recovery

See [SNOWFLAKE_MONITOR_GUIDE.md](SNOWFLAKE_MONITOR_GUIDE.md) for comprehensive documentation.

### Legacy Connectivity Testing

The `SnowflakeConnection` class also includes a built-in connectivity testing method:

```python
from gds_snowflake import SnowflakeConnection

# Create connection
conn = SnowflakeConnection(account="your-account")

# Test connectivity with timeout
result = conn.test_connectivity(timeout_seconds=30)

print(f"Success: {result['success']}")
print(f"Response Time: {result['response_time_ms']} ms")
print(f"Account Info: {result['account_info']}")

if not result['success']:
    print(f"Error: {result['error']}")
```

**Best Practices for Connectivity Testing:**

1. **Regular Health Checks**: Test connectivity before critical operations
2. **Timeout Configuration**: Set appropriate timeouts for your network environment
3. **Error Handling**: Always check the success flag before proceeding
4. **Monitoring Integration**: Use connectivity testing in monitoring scripts

## API Reference

### SnowflakeConnection

**Methods:**
- `connect()` - Establish connection to Snowflake
- `get_connection()` - Get current connection (auto-reconnect if needed)
- `close()` - Close the connection
- `execute_query(query, params=None)` - Execute query, return results as tuples
- `execute_query_dict(query, params=None)` - Execute query, return results as dictionaries
- `switch_account(new_account)` - Switch to different Snowflake account

**Context Manager:**
- Supports `with` statement for automatic connection management

### SnowflakeReplication

**Methods:**
- `get_failover_groups()` - Retrieve all failover groups
- `get_replication_history(group)` - Get replication history for a group
- `parse_cron_schedule(schedule)` - Parse cron schedule and return interval in minutes
- `check_replication_failure(group)` - Check if replication has failed
- `check_replication_latency(group)` - Calculate replication latency in minutes
- `switch_to_secondary_account(group)` - Switch connection to secondary account

### FailoverGroup

**Attributes:**
- `name` - Failover group name
- `type` - Type (PRIMARY or SECONDARY)
- `primary_account` - Primary account identifier
- `replication_schedule` - Replication schedule (cron format)
- `properties` - Dictionary of all properties

**Methods:**
- `is_primary()` - Check if this is a primary failover group
- `get_secondary_accounts()` - Get list of secondary account identifiers
- `get_secondary_account()` - Get a single available secondary account

### SnowflakeMetadata

**Methods:**

*Database and Schema Metadata:*
- `get_databases()` - Get metadata about all databases
- `get_database_info(database_name)` - Get detailed info about a specific database
- `get_schemas(database_name=None)` - Get metadata about schemas
- `get_all_metadata(database_name=None, schema_name=None)` - Get comprehensive metadata about all objects

*Table and View Metadata:*
- `get_tables(database_name=None, schema_name=None, include_views=False)` - Get table metadata
- `get_table_info(table_name, database_name=None, schema_name=None)` - Get info about a specific table
- `get_views(database_name=None, schema_name=None)` - Get view metadata
- `get_columns(table_name=None, database_name=None, schema_name=None)` - Get column metadata

*Function and Procedure Metadata:*
- `get_functions(database_name=None, schema_name=None)` - Get UDF metadata
- `get_procedures(database_name=None, schema_name=None)` - Get stored procedure metadata
- `get_sequences(database_name=None, schema_name=None)` - Get sequence metadata

*Data Pipeline Object Metadata:*
- `get_stages(database_name=None, schema_name=None)` - Get stage metadata
- `get_file_formats(database_name=None, schema_name=None)` - Get file format metadata
- `get_pipes(database_name=None, schema_name=None)` - Get Snowpipe metadata
- `get_tasks(database_name=None, schema_name=None)` - Get task metadata
- `get_streams(database_name=None, schema_name=None)` - Get stream metadata

### SnowflakeMonitor

**Methods:**
- `monitor_connectivity()` - Test account connectivity and return detailed results
- `monitor_replication_failures()` - Check all failover groups for replication failures
- `monitor_replication_latency()` - Check all failover groups for latency issues
- `monitor_all()` - Run comprehensive monitoring (connectivity + replication)
- `close()` - Clean up resources and connections

**Context Manager:**
- Supports `with` statement for automatic resource cleanup

**Configuration:**
- `connectivity_timeout` - Timeout for connectivity tests (seconds)
- `latency_threshold_minutes` - Threshold for latency alerts (minutes)
- `enable_email_alerts` - Enable/disable email notifications
- Email settings: `smtp_server`, `smtp_port`, `smtp_user`, `smtp_password`, `from_email`, `to_emails`

**Result Objects:**
- `ConnectivityResult` - Connectivity test results with timing and diagnostics
- `ReplicationResult` - Replication monitoring results with failure/latency details
- `MonitoringResult` - General monitoring operation results

## Requirements

- Python >= 3.7
- snowflake-connector-python >= 3.0.0
- croniter >= 1.3.0
- gds-vault (for Vault authentication)

## License

MIT License

## Author

GDS Team

## Links

- [GitHub Repository](https://github.com/davidvupham/snowflake)
- [Issue Tracker](https://github.com/davidvupham/snowflake/issues)
- [SnowflakeMonitor Guide](SNOWFLAKE_MONITOR_GUIDE.md)
