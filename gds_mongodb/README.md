# GDS MongoDB

A Python package providing MongoDB database management and usage functionality built on the `gds-database` interface. This package offers a comprehensive, production-ready MongoDB connection library with support for flexible authentication, connection strings, and all standard MongoDB operations.

## Features

- **Complete DatabaseConnection Implementation**: Full implementation of the `gds-database` interface
- **OOP Configuration Design**: Dedicated configuration classes following best practices
- **Server Configuration Management**: Built-in support for retrieving, inspecting, and modifying MongoDB server configuration settings
- **Flexible Connection Options**: Support for individual parameters, connection strings, and configuration dictionaries
- **Multiple Authentication Mechanisms**: Support for SCRAM-SHA-1, SCRAM-SHA-256, MONGODB-X509, GSSAPI (Kerberos), and PLAIN (LDAP)
- **CRUD Operations**: Complete set of create, read, update, and delete operations
- **Advanced Querying**: Support for filters, projections, sorting, limiting, and skipping
- **Resource Management**: Context manager support for automatic connection cleanup
- **Configuration Management**: Reusable, validatable configuration classes for instance management
- **Metadata Access**: Built-in methods for accessing database metadata (collections, fields, etc.)
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Full type hints for better IDE support and runtime safety

## Installation

### Basic Installation

```bash
pip install gds-mongodb
```

### With Optional Dependencies

```bash
# For development
pip install gds-mongodb[dev]
```

## Requirements

- Python 3.8+
- MongoDB 4.0+
- `gds-database>=1.0.0`
- `pymongo>=4.0.0`

## Quick Start

### Using Configuration Classes (Recommended)

```python
from gds_mongodb import MongoDBConnectionConfig, MongoDBConnection

# Create reusable configuration
config = MongoDBConnectionConfig(
    host='localhost',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword'
)

# Use config for connection
with MongoDBConnection(config=config) as conn:
    results = conn.execute_query('users', {'age': {'$gte': 18}})
```

### Basic Connection

```python
from gds_mongodb import MongoDBConnection

# Connect with individual parameters
conn = MongoDBConnection(
    host='localhost',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword'
)

# Connect and query
conn.connect()
results = conn.execute_query('users', {'age': {'$gte': 18}})
conn.disconnect()
```

### Using Connection String

```python
from gds_mongodb import MongoDBConnection

# Connect with MongoDB connection string
conn = MongoDBConnection(
    connection_string='mongodb://myuser:mypassword@localhost:27017/',
    database='mydb'
)

with conn:
    results = conn.execute_query('users', {'status': 'active'})
    for user in results:
        print(user)
```

### Using Configuration Dictionary

```python
from gds_mongodb import MongoDBConnection

config = {
    'host': 'localhost',
    'port': 27017,
    'database': 'mydb',
    'username': 'myuser',
    'password': 'mypassword',
    'auth_source': 'admin',
    'server_selection_timeout_ms': 5000
}

conn = MongoDBConnection(config=config)
```

## Usage Examples

### Context Manager (Recommended)

```python
from gds_mongodb import MongoDBConnection

# Automatic connection and cleanup
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Query documents
    users = conn.execute_query('users', {'age': {'$gte': 18}})

    # Insert document
    conn.insert_one('users', {'name': 'John Doe', 'age': 30})

    # Update documents
    conn.update_many(
        'users',
        {'age': {'$lt': 18}},
        {'$set': {'status': 'minor'}}
    )
```

### Querying with Options

```python
from gds_mongodb import MongoDBConnection
from pymongo import ASCENDING, DESCENDING

with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Query with projection, sorting, limit, and skip
    results = conn.execute_query(
        collection='users',
        filter_query={'status': 'active'},
        projection={'name': 1, 'email': 1, '_id': 0},
        sort=[('name', ASCENDING), ('age', DESCENDING)],
        limit=10,
        skip=0
    )

    for doc in results:
        print(f"Name: {doc['name']}, Email: {doc['email']}")
```

### Insert Operations

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Insert single document
    result = conn.insert_one('users', {
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'age': 28
    })
    print(f"Inserted ID: {result['inserted_id']}")

    # Insert multiple documents
    result = conn.insert_many('users', [
        {'name': 'User 1', 'age': 25},
        {'name': 'User 2', 'age': 30},
        {'name': 'User 3', 'age': 35}
    ])
    print(f"Inserted {len(result['inserted_ids'])} documents")
```

### Update Operations

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Update single document
    result = conn.update_one(
        'users',
        {'name': 'John Doe'},
        {'$set': {'age': 31, 'updated': True}}
    )
    print(f"Modified {result['modified_count']} document")

    # Update multiple documents
    result = conn.update_many(
        'users',
        {'age': {'$lt': 30}},
        {'$set': {'category': 'young'}}
    )
    print(f"Modified {result['modified_count']} documents")

    # Upsert (update or insert)
    result = conn.update_one(
        'users',
        {'email': 'new@example.com'},
        {'$set': {'name': 'New User', 'age': 25}},
        upsert=True
    )
```

### Delete Operations

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Delete single document
    result = conn.delete_one('users', {'name': 'John Doe'})
    print(f"Deleted {result['deleted_count']} document")

    # Delete multiple documents
    result = conn.delete_many('users', {'status': 'inactive'})
    print(f"Deleted {result['deleted_count']} documents")
```

### Metadata Operations

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Get all collection names
    collections = conn.get_collection_names()
    print(f"Collections: {collections}")

    # Get field information (by sampling documents)
    fields = conn.get_column_info('users', sample_size=100)
    for field in fields:
        print(f"Field: {field['field_name']}, Type: {field['data_type']}")

    # Get connection info
    info = conn.get_connection_info()
    print(f"Connected to: {info['host']}:{info['port']}")
    print(f"Database: {info['database']}")
    print(f"Server version: {info.get('server_version')}")
```

## Advanced Configuration

### Replica Sets

```python
conn = MongoDBConnection(
    host='replica1.example.com',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword',
    replica_set='myReplicaSet'
)
```

### TLS/SSL Connection

```python
conn = MongoDBConnection(
    host='secure.example.com',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword',
    tls=True
)
```

### Custom Authentication Source

```python
conn = MongoDBConnection(
    host='localhost',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword',
    auth_source='admin'  # Authenticate against admin database
)
```

### Authentication Mechanisms

#### SCRAM-SHA-256 (Default for MongoDB 4.0+)

```python
conn = MongoDBConnection(
    host='localhost',
    database='mydb',
    username='myuser',
    password='mypassword',
    auth_mechanism='SCRAM-SHA-256',
    auth_source='admin'
)
```

#### SCRAM-SHA-1

```python
conn = MongoDBConnection(
    host='localhost',
    database='mydb',
    username='myuser',
    password='mypassword',
    auth_mechanism='SCRAM-SHA-1'
)
```

#### GSSAPI (Kerberos Authentication)

```python
conn = MongoDBConnection(
    host='kerberos.example.com',
    database='mydb',
    username='user@REALM',
    auth_mechanism='GSSAPI',
    auth_source='$external'
)
```

#### PLAIN (LDAP Authentication)

```python
conn = MongoDBConnection(
    host='ldap.example.com',
    database='mydb',
    username='ldapuser',
    password='ldappass',
    auth_mechanism='PLAIN',
    auth_source='$external'
)
```

#### MONGODB-X509 (Certificate Authentication)

```python
conn = MongoDBConnection(
    host='secure.example.com',
    database='mydb',
    username='CN=myuser,OU=users,DC=example,DC=com',
    auth_mechanism='MONGODB-X509',
    auth_source='$external',
    tls=True
)
```

## Configuration Management (OOP Design)

### MongoDBConnectionConfig Class

The `MongoDBConnectionConfig` class provides a clean OOP approach to configuration management:

```python
from gds_mongodb import MongoDBConnectionConfig, MongoDBConnection

# Create reusable configuration
config = MongoDBConnectionConfig(
    host='localhost',
    port=27017,
    database='mydb',
    username='myuser',
    password='mypassword',
    auth_mechanism='SCRAM-SHA-256',
    maxPoolSize=50
)

# Reuse across multiple connections
conn1 = MongoDBConnection(config=config)
conn2 = MongoDBConnection(config=config)

# Validate configuration
config.validate_config()  # Raises ConfigurationError if invalid

# Access configuration properties
print(config.get_host())           # 'localhost'
print(config.get_database())       # 'mydb'
print(config.get_auth_mechanism()) # 'SCRAM-SHA-256'
```

### Configuration from Dictionary

```python
config_dict = {
    'host': 'mongo.example.com',
    'port': 27017,
    'database': 'production_db',
    'username': 'prod_user',
    'password': 'prod_pass',
    'replica_set': 'prod-rs',
    'tls': True
}

config = MongoDBConnectionConfig.from_dict(config_dict)
```

### Configuration Cloning

```python
# Original configuration
original = MongoDBConnectionConfig(
    host='localhost',
    database='db1',
    username='user1',
    password='pass1'
)

# Clone with overrides
clone = original.clone(
    database='db2',
    username='user2',
    password='pass2'
)
# Clone has same host but different database/credentials
```

### Configuration with Instance Metadata

For managing multiple MongoDB instances with labels and metadata:

```python
from gds_mongodb import MongoDBConnectionConfig

# Production instance with metadata
prod = MongoDBConnectionConfig(
    instance_name='production',
    environment='prod',
    description='Production MongoDB cluster',
    host='prod-mongo.example.com',
    database='prod_db',
    username='prod_user',
    password='prod_pass',
    replica_set='prod-rs',
    tls=True,
    tags=['production', 'critical'],
    metadata={
        'cluster_size': 3,
        'region': 'us-east-1',
        'backup_enabled': True
    }
)

# Development instance with metadata
dev = MongoDBConnectionConfig(
    instance_name='development',
    environment='dev',
    host='localhost',
    database='dev_db',
    tags=['development', 'local']
)

# Use configurations
with MongoDBConnection(config=prod) as conn:
    # Work with production database
    pass
```

### Configuration Serialization

```python
# Export configuration (includes sensitive data)
full_dict = config.to_dict()

# Export without sensitive data
safe_dict = config.to_safe_dict()  # Excludes password, connection_string

# Build connection string
conn_str = config.build_connection_string()

# Get connection parameters
params = config.build_connection_params()
```

### Benefits of Configuration Classes

1. **Separation of Concerns**: Configuration logic separate from connection management
2. **Reusability**: Same configuration for multiple connections
3. **Validation**: Validates before use, catching errors early
4. **Type Safety**: Strongly typed with clear interfaces
5. **Instance Management**: Easy management of multiple MongoDB environments
6. **Serialization**: Easy to save/load configurations
7. **Security**: Safe export without sensitive data

### Connection Timeouts and Pooling

```python
config = {
    'host': 'localhost',
    'port': 27017,
    'database': 'mydb',
    'username': 'myuser',
    'password': 'mypassword',
    'server_selection_timeout_ms': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 10000,
    'maxPoolSize': 50,
    'minPoolSize': 10
}

conn = MongoDBConnection(config=config)
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | 'localhost' | MongoDB server host |
| `port` | int | 27017 | MongoDB server port |
| `database` | str | Required | Database name |
| `username` | str | None | Username for authentication |
| `password` | str | None | Password for authentication |
| `connection_string` | str | None | Complete MongoDB connection string |
| `auth_source` | str | 'admin' | Authentication database |
| `auth_mechanism` | str | None | Auth mechanism (SCRAM-SHA-1, SCRAM-SHA-256, MONGODB-X509, GSSAPI, PLAIN) |
| `replica_set` | str | None | Replica set name |
| `tls` | bool | None | Enable TLS/SSL |
| `server_selection_timeout_ms` | int | 5000 | Server selection timeout |

## Error Handling

The package uses custom exceptions from `gds-database`:

```python
from gds_mongodb import MongoDBConnection
from gds_database import ConnectionError, QueryError, ConfigurationError

try:
    conn = MongoDBConnection(host='invalid-host', database='mydb')
    conn.connect()
except ConnectionError as e:
    print(f"Connection failed: {e}")

try:
    with MongoDBConnection(host='localhost', database='mydb') as conn:
        conn.execute_query('users', {'invalid_operator': {'$badop': 1}})
except QueryError as e:
    print(f"Query failed: {e}")
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install gds-mongodb[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=gds_mongodb tests/
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd gds_mongodb

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run linting
black gds_mongodb tests
ruff check gds_mongodb tests

# Run type checking
mypy gds_mongodb
```

## API Reference

### MongoDBConnection

Main class providing MongoDB database connectivity.

#### Methods

- `connect()` - Establish database connection
- `disconnect()` - Close database connection
- `is_connected()` - Check if connected
- `execute_query(collection, filter_query, projection, limit, skip, sort)` - Query documents
- `insert_one(collection, document)` - Insert single document
- `insert_many(collection, documents)` - Insert multiple documents
- `update_one(collection, filter_query, update, upsert)` - Update single document
- `update_many(collection, filter_query, update, upsert)` - Update multiple documents
- `delete_one(collection, filter_query)` - Delete single document
- `delete_many(collection, filter_query)` - Delete multiple documents
- `get_collection_names()` - Get list of collections
- `get_column_info(collection, sample_size)` - Get field information
- `get_connection_info()` - Get connection metadata

## Server Configuration Management

The `MongoDBConfiguration` class provides a unified, OOP-based interface to MongoDB server configuration settings using the `getParameter` and `setParameter` commands. This enables runtime inspection, monitoring, and modification of server settings.

Reference: https://www.mongodb.com/docs/manual/reference/command/getParameter/

### Basic Usage

```python
from gds_mongodb import MongoDBConnection, MongoDBConfiguration

# Create connection
connection = MongoDBConnection(host='localhost', database='admin')
connection.connect()

# Create configuration manager
config = MongoDBConfiguration(connection)

# Get a single configuration setting
log_level = config.get("logLevel")
print(f"Log level: {log_level}")

# Get configuration with details
details = config.get_details("maxBsonObjectSize")
print(f"Value: {details['value']}")
print(f"Runtime settable: {details.get('settable_at_runtime')}")
```

### Retrieving Multiple Configurations

```python
# Get all configurations
all_settings = config.get_all()
print(f"Total configurations: {len(all_settings)}")

# Get all configurations with details (settable at runtime/startup)
all_detailed = config.get_all(include_details=True)

# Get as list of detail dictionaries for easier filtering
setting_list = config.get_all_details()
runtime_settings = [s for s in setting_list if s.get("settable_at_runtime")]
```

### Filtering Configurations

```python
# Get runtime-settable configurations (MongoDB 8.0+, with fallback)
runtime_settings = config.get_runtime_configurable()

# Get startup-settable configurations (MongoDB 8.0+, with fallback)
startup_settings = config.get_startup_configurable()

# Search by keyword
log_settings = config.search("log")

# Get by prefix
net_settings = config.get_by_prefix("net")
```

### Modifying Runtime Configuration

```python
# Set a single configuration (must be runtime-settable)
config.set("logLevel", 2)

# Set multiple configurations at once
settings = {
    "logLevel": 2,
    "cursorTimeoutMillis": 300000
}
config.set_multiple(settings, comment="Batch update")

# Reset to default value (for known defaults)
config.reset("logLevel")
```

### Configuration Details Dictionary

Configuration details are returned as dictionaries:

```python
details = config.get_details("logLevel")

# Access properties
print(details['name'])                      # Configuration name
print(details['value'])                     # Current value
print(details.get('settable_at_runtime'))   # Can be set at runtime
print(details.get('settable_at_startup'))   # Can be set at startup

# Check capabilities
if details.get('settable_at_runtime'):
    print(f"{details['name']} can be changed without restart")
```

### Practical Use Cases

```python
# 1. Configuration backup
config_backup = config.to_dict()
# Save to file for documentation or comparison

# 2. Monitoring important settings
max_bson = config.get("maxBsonObjectSize")
if max_bson < 16777216:  # 16MB
    print("Warning: maxBsonObjectSize is below default")

# 3. Environment comparison
# Compare configurations between dev/staging/prod
dev_settings = dev_config.get_all()
prod_settings = prod_config.get_all()
differences = {k: (dev_settings[k], prod_settings[k])
               for k in dev_params if dev_params[k] != prod_params.get(k)}

# 4. Find tunable parameters
tunable = param_manager.get_runtime_parameters()
print(f"Can adjust {len(tunable)} parameters without restart")
```

### Setting Parameters at Runtime

The parameter manager supports modifying runtime-settable parameters:

```python
# Set a single parameter
result = param_manager.set_parameter("logLevel", 1)

# Set with comment for audit trail
result = param_manager.set_parameter(
    "cursorTimeoutMillis",
    300000,
    comment="Increase timeout for long-running queries"
)

# Set multiple parameters at once
params = {
    "logLevel": 2,
    "cursorTimeoutMillis": 300000,
    "notablescan": False
}
result = param_manager.set_multiple_parameters(params)
```

### Safe Parameter Modification Workflow

```python
# 1. Check if parameter can be set at runtime
param_info = param_manager.get_parameter_details("logLevel")
if not param_info.is_runtime_settable():
    print("Parameter requires server restart")
    exit()

# 2. Store original value
original = param_manager.get_parameter("logLevel")

# 3. Modify parameter
try:
    param_manager.set_parameter("logLevel", 2)

    # 4. Test your changes...

finally:
    # 5. Restore original value
    param_manager.set_parameter("logLevel", original)
```

### Parameter Manager API

**Retrieval methods:**
- `get_parameter(name)` - Get single parameter value
- `get_parameter_details(name)` - Get ParameterInfo with metadata
- `get_all_parameters(show_details)` - Get all parameters
- `get_all_parameters_info()` - Get all as ParameterInfo list
- `get_runtime_parameters()` - Get runtime-settable parameters
- `get_startup_parameters()` - Get startup-settable parameters
- `search_parameters(keyword)` - Search by keyword
- `get_parameters_by_prefix(prefix)` - Get by name prefix
- `to_dict()` - Export all parameters

**Modification methods:**
- `set_parameter(name, value, comment)` - Set single parameter
- `set_multiple_parameters(params, comment)` - Set multiple parameters
- `reset_parameter(name)` - Reset to default value (if known)

## Example Scripts

The package includes comprehensive example scripts in the `examples/` directory:

- **`basic_connection.py`** - Basic connection patterns and usage
- **`crud_operations.py`** - Create, read, update, delete operations
- **`advanced_queries.py`** - Complex queries with aggregation pipeline
- **`configuration_examples.py`** - Various connection configuration methods
- **`authentication_mechanisms.py`** - All authentication mechanism examples
- **`config_management.py`** - Configuration class usage and instance management
- **`parameter_management.py`** - Server parameter retrieval and inspection

Each example is fully documented and can be run independently:

```bash
cd examples
python parameter_management.py
```

## Comparison with Other GDS Packages

Unlike SQL-based packages (gds-mssql, gds-postgres, gds-snowflake), gds-mongodb:
- Uses collection-based data model instead of tables
- Supports document-oriented queries with MongoDB query language
- Provides BSON data types and flexible schema
- Offers different query methods optimized for document operations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the GDS Team

## Changelog

### Version 1.0.0
- Initial release
- Full DatabaseConnection interface implementation
- Support for basic CRUD operations
- Connection string and parameter-based configuration
- Context manager support
- Comprehensive error handling
