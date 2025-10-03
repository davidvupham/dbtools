# SnowflakeMetadata Quick Reference

## Import

```python
from gds_snowflake import SnowflakeConnection, SnowflakeMetadata
```

## Initialization

```python
# Create connection
conn = SnowflakeConnection(
    account='myaccount',
    user='myuser',
    vault_secret_path='secret/data/snowflake'
)
conn.connect()

# Create metadata retriever
metadata = SnowflakeMetadata(conn)
```

## Quick Reference Table

| Method | Description | Example |
|--------|-------------|---------|
| `get_databases()` | Get all databases | `dbs = metadata.get_databases()` |
| `get_database_info(db)` | Get specific database | `db = metadata.get_database_info('MYDB')` |
| `get_schemas(db)` | Get schemas | `schemas = metadata.get_schemas('MYDB')` |
| `get_tables(db, schema)` | Get tables | `tables = metadata.get_tables('MYDB', 'PUBLIC')` |
| `get_table_info(tbl, db, schema)` | Get specific table | `tbl = metadata.get_table_info('CUSTOMERS')` |
| `get_views(db, schema)` | Get views | `views = metadata.get_views('MYDB', 'PUBLIC')` |
| `get_columns(tbl, db, schema)` | Get columns | `cols = metadata.get_columns('CUSTOMERS')` |
| `get_functions(db, schema)` | Get functions | `funcs = metadata.get_functions('MYDB')` |
| `get_procedures(db, schema)` | Get procedures | `procs = metadata.get_procedures('MYDB')` |
| `get_sequences(db, schema)` | Get sequences | `seqs = metadata.get_sequences('MYDB')` |
| `get_stages(db, schema)` | Get stages | `stages = metadata.get_stages('MYDB')` |
| `get_file_formats(db, schema)` | Get file formats | `fmts = metadata.get_file_formats('MYDB')` |
| `get_pipes(db, schema)` | Get pipes | `pipes = metadata.get_pipes('MYDB')` |
| `get_tasks(db, schema)` | Get tasks | `tasks = metadata.get_tasks('MYDB')` |
| `get_streams(db, schema)` | Get streams | `streams = metadata.get_streams('MYDB')` |
| `get_all_metadata(db, schema)` | Get everything | `all_meta = metadata.get_all_metadata('MYDB')` |

## Common Patterns

### Get all objects in a database

```python
all_metadata = metadata.get_all_metadata(database_name='MYDB')
print(all_metadata['summary'])  # Object counts
```

### List all databases

```python
databases = metadata.get_databases()
for db in databases:
    print(f"{db['DATABASE_NAME']} - Owner: {db['DATABASE_OWNER']}")
```

### Get table details

```python
# Get all tables in a schema
tables = metadata.get_tables(
    database_name='MYDB',
    schema_name='PUBLIC'
)

# Get specific table info
table = metadata.get_table_info(
    table_name='CUSTOMERS',
    database_name='MYDB',
    schema_name='PUBLIC'
)

# Get columns for a table
columns = metadata.get_columns(
    table_name='CUSTOMERS',
    database_name='MYDB',
    schema_name='PUBLIC'
)

for col in columns:
    print(f"{col['COLUMN_NAME']}: {col['DATA_TYPE']}")
```

### Include views with tables

```python
tables_and_views = metadata.get_tables(
    database_name='MYDB',
    schema_name='PUBLIC',
    include_views=True
)
```

### Get data pipeline objects

```python
# Stages
stages = metadata.get_stages(database_name='MYDB', schema_name='PUBLIC')

# Pipes (Snowpipe)
pipes = metadata.get_pipes(database_name='MYDB', schema_name='PUBLIC')

# Tasks
tasks = metadata.get_tasks(database_name='MYDB', schema_name='PUBLIC')

# Streams
streams = metadata.get_streams(database_name='MYDB', schema_name='PUBLIC')
```

### Error handling

```python
try:
    db_info = metadata.get_database_info('MYDB')
    if db_info is None:
        print("Database not found")
except Exception as e:
    print(f"Error: {e}")
```

### Using context manager

```python
with SnowflakeConnection(
    account='myaccount',
    user='myuser',
    vault_secret_path='secret/data/snowflake'
) as conn:
    metadata = SnowflakeMetadata(conn)
    databases = metadata.get_databases()
    print(f"Found {len(databases)} databases")
```

## Return Value Structure

All methods return `List[Dict[str, Any]]` with keys in UPPERCASE matching Snowflake's information schema column names.

### Example: Database

```python
{
    'DATABASE_NAME': 'MYDB',
    'DATABASE_OWNER': 'SYSADMIN',
    'IS_TRANSIENT': 'NO',
    'COMMENT': 'My database',
    'CREATED': datetime(...),
    'LAST_ALTERED': datetime(...),
    'RETENTION_TIME': 7
}
```

### Example: Table

```python
{
    'DATABASE_NAME': 'MYDB',
    'SCHEMA_NAME': 'PUBLIC',
    'TABLE_NAME': 'CUSTOMERS',
    'TABLE_TYPE': 'BASE TABLE',
    'IS_TRANSIENT': 'NO',
    'CLUSTERING_KEY': None,
    'ROW_COUNT': 1000000,
    'BYTES': 50000000,
    'RETENTION_TIME': 1,
    'CREATED': datetime(...),
    'LAST_ALTERED': datetime(...),
    'AUTO_CLUSTERING_ON': 'NO',
    'COMMENT': ''
}
```

### Example: Column

```python
{
    'DATABASE_NAME': 'MYDB',
    'SCHEMA_NAME': 'PUBLIC',
    'TABLE_NAME': 'CUSTOMERS',
    'COLUMN_NAME': 'ID',
    'ORDINAL_POSITION': 1,
    'COLUMN_DEFAULT': None,
    'IS_NULLABLE': 'NO',
    'DATA_TYPE': 'NUMBER',
    'CHARACTER_MAXIMUM_LENGTH': None,
    'NUMERIC_PRECISION': 38,
    'NUMERIC_SCALE': 0,
    'IS_IDENTITY': 'YES',
    'IDENTITY_START': 1,
    'IDENTITY_INCREMENT': 1,
    'COMMENT': 'Customer ID'
}
```

## Filtering Options

All parameters are optional:

```python
# No filter - get all
objects = metadata.get_tables()

# Filter by database
objects = metadata.get_tables(database_name='MYDB')

# Filter by database and schema
objects = metadata.get_tables(
    database_name='MYDB',
    schema_name='PUBLIC'
)
```

## Summary from get_all_metadata()

```python
all_metadata = metadata.get_all_metadata(database_name='MYDB')

summary = all_metadata['summary']
# {
#     'database_count': 1,
#     'schema_count': 3,
#     'table_count': 25,
#     'view_count': 10,
#     'function_count': 5,
#     'procedure_count': 3,
#     'sequence_count': 2,
#     'stage_count': 4,
#     'file_format_count': 3,
#     'pipe_count': 2,
#     'task_count': 1,
#     'stream_count': 1
# }
```

## Tips

1. **Use filtering** - Specify database/schema to reduce query time
2. **Check for None** - Methods return None if object not found
3. **Use context managers** - Ensures connection cleanup
4. **Cache results** - Metadata doesn't change frequently
5. **Handle errors** - Wrap calls in try/except blocks
6. **Check permissions** - Ensure user has access to INFORMATION_SCHEMA

## See Also

- Full examples: `examples/metadata_example.py`
- Complete documentation: `README.md`
- API tests: `tests/test_database.py`
