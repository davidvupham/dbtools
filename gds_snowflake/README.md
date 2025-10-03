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

## Quick Start

### Basic Connection

```python
from gds_snowflake import SnowflakeConnection

# Create connection
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    password='mypassword',
    warehouse='my_warehouse',
    role='my_role'
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

with SnowflakeConnection(account='myaccount', user='myuser', password='mypass') as conn:
    results = conn.execute_query("SELECT * FROM my_table")
    for row in results:
        print(row)
```

### Replication Monitoring

```python
from gds_snowflake import SnowflakeConnection, SnowflakeReplication

# Connect to Snowflake
conn = SnowflakeConnection(account='myaccount', user='myuser', password='mypass')
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

conn = SnowflakeConnection(account='myaccount', user='myuser', password='mypass')
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

conn = SnowflakeConnection(account='primary_account', user='myuser', password='mypass')
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
conn = SnowflakeConnection(account='myaccount', user='myuser', password='mypass')
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

with SnowflakeConnection(account='myaccount', user='myuser', password='mypass') as conn:
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

## Requirements

- Python >= 3.7
- snowflake-connector-python >= 3.0.0
- croniter >= 1.3.0

## License

MIT License

## Author

GDS Team

## Links

- [GitHub Repository](https://github.com/davidvupham/snowflake)
- [Issue Tracker](https://github.com/davidvupham/snowflake/issues)
