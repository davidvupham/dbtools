# GDS MongoDB Developer's Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Connection Management](#connection-management)
6. [Authentication](#authentication)
7. [CRUD Operations](#crud-operations)
8. [Advanced Querying](#advanced-querying)
9. [Configuration Management](#configuration-management)
10. [Replica Sets](#replica-sets)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)
13. [Testing](#testing)
14. [Examples](#examples)

---

## Introduction

`gds_mongodb` is a comprehensive Python package for MongoDB database management and monitoring, built on the `gds-database` interface. It provides a production-ready, object-oriented solution for MongoDB database operations with extensive support for:

- **Connection Management**: Flexible connection configuration with multiple authentication mechanisms
- **Database Operations**: Complete CRUD operations with advanced query capabilities
- **Server Configuration**: Runtime and startup configuration parameters retrieval, modification, and inspection
- **Database Administration**: Collection management, indexing, and metadata access
- **Monitoring & Operations**: MongoDB operational monitoring and database administration
- **Resource Management**: Context manager support for automatic connection cleanup
- **Type Safety**: Full type hints for better IDE support and runtime safety

### Architecture

The package follows a clean separation of concerns:

- **MongoDBConnection**: Main connection class implementing `DatabaseConnection` interface
- **MongoDBConnectionConfig**: Configuration management for reusable connection settings
- **MongoDBConfiguration**: Server configuration parameters management
- **Resource Management**: Automatic connection cleanup via context managers

---

## Installation

### Basic Installation

```bash
pip install gds-mongodb
```

### Development Installation

```bash
pip install gds-mongodb[dev]
```

### Requirements

- Python 3.8+
- MongoDB 4.0+
- `gds-database>=1.0.0`
- `pymongo>=4.0.0`

---

## Quick Start

### Simple Connection

```python
from gds_mongodb import MongoDBConnection

# Connect using individual parameters
with MongoDBConnection(
    host='localhost',
    port=27017,
    database='mydb',
    username='admin',
    password='secret'
) as conn:
    # Query documents
    users = conn.execute_query('users', {'age': {'$gte': 18}})
    print(f"Found {len(users)} adult users")
```

### Using Configuration Objects

```python
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig

# Create reusable configuration
config = MongoDBConnectionConfig(
    host='localhost',
    port=27017,
    database='mydb',
    username='admin',
    password='secret',
    auth_mechanism='SCRAM-SHA-256'
)

# Use configuration for connection
with MongoDBConnection(config=config) as conn:
    collections = conn.get_collection_names()
    print(f"Collections: {collections}")
```

---

## Core Concepts

### DatabaseConnection Interface

`MongoDBConnection` implements the `gds-database` interface, providing a consistent API across different database types. This ensures:

- **Portability**: Easy switching between database backends
- **Consistency**: Standard methods across all database implementations
- **Best Practices**: Built-in patterns for connection management

### Configuration Classes

The package uses configuration classes to separate configuration from connection logic:

```python
from gds_mongodb import MongoDBConnectionConfig

# Create configuration with metadata
config = MongoDBConnectionConfig(
    host='prod-mongo-01',
    database='analytics',
    username='analyst',
    password='secret',
    instance_name='production-analytics',
    environment='production',
    description='Production analytics database',
    tags=['analytics', 'production', 'reporting']
)

# Configuration can be reused
conn1 = MongoDBConnection(config=config)
conn2 = MongoDBConnection(config=config)

# Configuration can be serialized
config_dict = config.to_dict()
saved_config = MongoDBConnectionConfig.from_dict(config_dict)
```

### Resource Management

All connection objects support Python's context manager protocol:

```python
# Automatic connection and cleanup
with MongoDBConnection(host='localhost', database='mydb') as conn:
    results = conn.execute_query('users', {})
    # Connection automatically closed on exit
```

---

## Connection Management

### Connection Methods

There are three ways to create connections:

#### 1. Individual Parameters

```python
conn = MongoDBConnection(
    host='localhost',
    port=27017,
    database='mydb',
    username='admin',
    password='secret',
    auth_source='admin',
    auth_mechanism='SCRAM-SHA-256'
)
```

#### 2. Connection String

```python
conn = MongoDBConnection(
    connection_string='mongodb://admin:secret@localhost:27017/',
    database='mydb'
)
```

#### 3. Configuration Object or Dictionary

```python
# Using MongoDBConnectionConfig
config = MongoDBConnectionConfig(
    host='localhost',
    database='mydb',
    username='admin',
    password='secret'
)
conn = MongoDBConnection(config=config)

# Using dictionary
config_dict = {
    'host': 'localhost',
    'port': 27017,
    'database': 'mydb',
    'username': 'admin',
    'password': 'secret'
}
conn = MongoDBConnection(config=config_dict)
```

### Connection Lifecycle

```python
# Manual connection management
conn = MongoDBConnection(host='localhost', database='mydb')

# Connect
conn.connect()
print(f"Connected: {conn.is_connected()}")

# Use connection
results = conn.execute_query('users', {})

# Disconnect
conn.disconnect()
print(f"Connected: {conn.is_connected()}")

# Context manager (recommended)
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Connection automatically established
    results = conn.execute_query('users', {})
    # Connection automatically closed
```

### Connection Information

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    info = conn.get_connection_info()
    print(f"Host: {info['host']}")
    print(f"Port: {info['port']}")
    print(f"Database: {info['database']}")
    print(f"Connected: {info['connected']}")
    print(f"Auth Mechanism: {info['auth_mechanism']}")
```

---

## Authentication

### SCRAM-SHA-256 (Recommended)

Default authentication mechanism for MongoDB 4.0+:

```python
conn = MongoDBConnection(
    host='localhost',
    database='mydb',
    username='admin',
    password='secret',
    auth_mechanism='SCRAM-SHA-256',
    auth_source='admin'
)
```

### SCRAM-SHA-1

For older MongoDB versions:

```python
conn = MongoDBConnection(
    host='localhost',
    database='mydb',
    username='admin',
    password='secret',
    auth_mechanism='SCRAM-SHA-1',
    auth_source='admin'
)
```

### X.509 Certificate Authentication

For certificate-based authentication:

```python
conn = MongoDBConnection(
    host='secure.example.com',
    database='mydb',
    username='CN=client,OU=MyUnit,O=MyOrg',
    auth_mechanism='MONGODB-X509',
    auth_source='$external',
    tls=True,
    tlsCertificateKeyFile='/path/to/client.pem',
    tlsCAFile='/path/to/ca.pem'
)
```

### Kerberos (GSSAPI)

For enterprise Kerberos authentication:

```python
# Requires: pip install pymongo[gssapi]
conn = MongoDBConnection(
    host='kerberos.example.com',
    database='mydb',
    username='user@EXAMPLE.COM',
    auth_mechanism='GSSAPI',
    auth_source='$external'
)
```

### LDAP (PLAIN)

For LDAP/Active Directory authentication:

```python
conn = MongoDBConnection(
    host='ldap.example.com',
    database='mydb',
    username='ldapuser',
    password='ldappass',
    auth_mechanism='PLAIN',
    auth_source='$external',
    tls=True  # Recommended for PLAIN
)
```

---

## CRUD Operations

### Create (Insert)

#### Insert Single Document

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Insert one document
    user = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'city': 'New York'
    }

    result = conn.insert_one('users', user)
    print(f"Inserted ID: {result['inserted_id']}")
```

#### Insert Multiple Documents

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    users = [
        {'name': 'Jane Smith', 'age': 25},
        {'name': 'Bob Johnson', 'age': 35},
        {'name': 'Alice Williams', 'age': 28}
    ]

    result = conn.insert_many('users', users)
    print(f"Inserted {len(result['inserted_ids'])} documents")
    print(f"IDs: {result['inserted_ids']}")
```

### Read (Query)

#### Find All Documents

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Get all documents
    all_users = conn.execute_query('users', {})
    print(f"Total users: {len(all_users)}")
```

#### Find with Filter

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Find users over 25
    adults = conn.execute_query('users', {'age': {'$gt': 25}})

    for user in adults:
        print(f"{user['name']}: {user['age']}")
```

#### Find with Projection

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Get only name and email fields
    users = conn.execute_query(
        'users',
        {},
        projection={'name': 1, 'email': 1, '_id': 0}
    )

    for user in users:
        print(f"{user['name']}: {user['email']}")
```

### Update

#### Update Single Document

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Update one user
    result = conn.update_one(
        'users',
        {'name': 'John Doe'},
        {'$set': {'age': 31, 'status': 'updated'}}
    )

    print(f"Matched: {result['matched_count']}")
    print(f"Modified: {result['modified_count']}")
```

#### Update Multiple Documents

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Update all young users
    result = conn.update_many(
        'users',
        {'age': {'$lt': 30}},
        {'$set': {'category': 'young'}}
    )

    print(f"Updated {result['modified_count']} documents")
```

#### Upsert (Update or Insert)

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Update if exists, insert if not
    result = conn.update_one(
        'users',
        {'email': 'new@example.com'},
        {'$set': {'name': 'New User', 'age': 22}},
        upsert=True
    )

    if result['upserted_id']:
        print(f"Inserted new document: {result['upserted_id']}")
    else:
        print(f"Updated existing document")
```

### Delete

#### Delete Single Document

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    result = conn.delete_one('users', {'name': 'John Doe'})
    print(f"Deleted {result['deleted_count']} document")
```

#### Delete Multiple Documents

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Delete all inactive users
    result = conn.delete_many('users', {'status': 'inactive'})
    print(f"Deleted {result['deleted_count']} documents")
```

---

## Advanced Querying

### Sorting

```python
from pymongo import ASCENDING, DESCENDING

with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Sort by age descending
    users = conn.execute_query(
        'users',
        {},
        sort=[('age', DESCENDING)]
    )

    # Sort by multiple fields
    users = conn.execute_query(
        'users',
        {},
        sort=[('city', ASCENDING), ('age', DESCENDING)]
    )
```

### Limiting and Skipping

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Get top 10 users
    users = conn.execute_query('users', {}, limit=10)

    # Skip first 10, get next 10 (pagination)
    users = conn.execute_query('users', {}, skip=10, limit=10)
```

### Complex Filters

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # AND condition (implicit)
    users = conn.execute_query(
        'users',
        {'age': {'$gte': 25}, 'city': 'New York'}
    )

    # OR condition
    users = conn.execute_query(
        'users',
        {'$or': [
            {'age': {'$lt': 20}},
            {'age': {'$gt': 60}}
        ]}
    )

    # IN operator
    users = conn.execute_query(
        'users',
        {'city': {'$in': ['New York', 'Los Angeles', 'Chicago']}}
    )

    # NOT operator
    users = conn.execute_query(
        'users',
        {'age': {'$not': {'$lt': 18}}}
    )

    # EXISTS operator
    users = conn.execute_query(
        'users',
        {'phone': {'$exists': True}}
    )
```

### Aggregation Pipeline

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    # Get collection directly for aggregation
    collection = conn._db['users']

    pipeline = [
        {'$match': {'age': {'$gte': 18}}},
        {'$group': {
            '_id': '$city',
            'count': {'$sum': 1},
            'avg_age': {'$avg': '$age'}
        }},
        {'$sort': {'count': -1}}
    ]

    results = list(collection.aggregate(pipeline))
    for result in results:
        print(f"{result['_id']}: {result['count']} users, avg age {result['avg_age']:.1f}")
```

---

## Configuration Management

The `MongoDBConfiguration` class provides access to MongoDB server configuration settings.

### Getting Configuration Values

```python
from gds_mongodb import MongoDBConnection, MongoDBConfiguration

with MongoDBConnection(host='localhost', database='admin') as conn:
    config = MongoDBConfiguration(conn)

    # Get single configuration value
    log_level = config.get('logLevel')
    print(f"Log Level: {log_level}")

    # Get configuration with details
    details = config.get_details('maxBsonObjectSize')
    print(f"Value: {details['value']}")
    print(f"Runtime settable: {details.get('settable_at_runtime')}")
    print(f"Startup settable: {details.get('settable_at_startup')}")
```

### Getting All Configurations

```python
with MongoDBConnection(host='localhost', database='admin') as conn:
    config = MongoDBConfiguration(conn)

    # Get all configuration values
    all_settings = config.get_all()
    print(f"Total settings: {len(all_settings)}")

    for name, value in list(all_settings.items())[:10]:
        print(f"{name}: {value}")

    # Get all with details
    all_detailed = config.get_all(include_details=True)
    for name, details in list(all_detailed.items())[:5]:
        print(f"\n{name}:")
        print(f"  Value: {details['value']}")
        print(f"  Runtime: {details.get('settable_at_runtime')}")
```

### Filtering Configurations

```python
with MongoDBConnection(host='localhost', database='admin') as conn:
    config = MongoDBConfiguration(conn)

    # Get only runtime-settable configurations
    runtime_settings = config.get_runtime_settable()
    print(f"Runtime settable: {len(runtime_settings)}")

    # Get only startup-settable configurations
    startup_settings = config.get_startup_settable()
    print(f"Startup settable: {len(startup_settings)}")
```

### Setting Configuration Values

```python
with MongoDBConnection(host='localhost', database='admin') as conn:
    config = MongoDBConfiguration(conn)

    # Set a runtime configuration
    config.set('logLevel', 2)
    print("Log level changed to 2")

    # Verify the change
    new_level = config.get('logLevel')
    print(f"New log level: {new_level}")
```

---

## Replica Sets

### Connecting to Replica Sets

```python
from gds_mongodb import MongoDBConnection

# Connect to replica set
conn = MongoDBConnection(
    host='mongo1.example.com,mongo2.example.com,mongo3.example.com',
    port=27017,
    database='mydb',
    username='admin',
    password='secret',
    replica_set='myReplicaSet'
)

# Or use connection string
conn = MongoDBConnection(
    connection_string='mongodb://admin:secret@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=myReplicaSet',
    database='mydb'
)
```

### Read Preferences

```python
from pymongo import ReadPreference

conn = MongoDBConnection(
    host='mongo1,mongo2,mongo3',
    database='mydb',
    replica_set='myReplicaSet',
    read_preference=ReadPreference.SECONDARY_PREFERRED
)
```

---

## Error Handling

### Exception Hierarchy

The package uses exceptions from both `gds-database` and `pymongo`:

```python
from gds_database import (
    DatabaseConnectionError,
    QueryError,
    ConfigurationError
)
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    ServerSelectionTimeoutError
)

# Handle connection errors
try:
    conn = MongoDBConnection(host='invalid-host', database='mydb')
    conn.connect()
except DatabaseConnectionError as e:
    print(f"Connection failed: {e}")
except ServerSelectionTimeoutError as e:
    print(f"Could not reach server: {e}")

# Handle query errors
try:
    with MongoDBConnection(host='localhost', database='mydb') as conn:
        results = conn.execute_query('users', {'$invalid': 'operator'})
except QueryError as e:
    print(f"Query failed: {e}")
except OperationFailure as e:
    print(f"Operation error: {e}")

# Handle configuration errors
try:
    config = MongoDBConnectionConfig(
        host='localhost',
        # Missing required database field
    )
    conn = MongoDBConnection(config=config)
    conn.connect()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Proper Error Handling Pattern

```python
from gds_mongodb import MongoDBConnection
from gds_database import DatabaseConnectionError, QueryError
import logging

logger = logging.getLogger(__name__)

def safe_query_users(min_age: int):
    """Query users with proper error handling."""
    conn = None
    try:
        conn = MongoDBConnection(
            host='localhost',
            database='mydb',
            username='admin',
            password='secret'
        )
        conn.connect()

        users = conn.execute_query('users', {'age': {'$gte': min_age}})
        return users

    except DatabaseConnectionError as e:
        logger.error(f"Failed to connect: {e}")
        return []
    except QueryError as e:
        logger.error(f"Query failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []
    finally:
        if conn:
            conn.disconnect()

# Better: Use context manager
def safe_query_users_context(min_age: int):
    """Query users with context manager."""
    try:
        with MongoDBConnection(
            host='localhost',
            database='mydb',
            username='admin',
            password='secret'
        ) as conn:
            return conn.execute_query('users', {'age': {'$gte': min_age}})
    except (DatabaseConnectionError, QueryError) as e:
        logger.error(f"Database error: {e}")
        return []
```

---

## Best Practices

### 1. Always Use Context Managers

```python
# Good: Automatic cleanup
with MongoDBConnection(host='localhost', database='mydb') as conn:
    results = conn.execute_query('users', {})

# Avoid: Manual cleanup required
conn = MongoDBConnection(host='localhost', database='mydb')
conn.connect()
results = conn.execute_query('users', {})
conn.disconnect()
```

### 2. Use Configuration Objects for Reusability

```python
# Good: Reusable configuration
config = MongoDBConnectionConfig(
    host='localhost',
    database='mydb',
    username='admin',
    password='secret'
)

conn1 = MongoDBConnection(config=config)
conn2 = MongoDBConnection(config=config)

# Avoid: Repeating parameters
conn1 = MongoDBConnection(host='localhost', database='mydb', username='admin', password='secret')
conn2 = MongoDBConnection(host='localhost', database='mydb', username='admin', password='secret')
```

### 3. Use Projections to Reduce Network Traffic

```python
# Good: Only retrieve needed fields
users = conn.execute_query(
    'users',
    {},
    projection={'name': 1, 'email': 1}
)

# Avoid: Retrieving all fields when not needed
users = conn.execute_query('users', {})
```

### 4. Use Indexes for Better Performance

```python
with MongoDBConnection(host='localhost', database='mydb') as conn:
    collection = conn._db['users']

    # Create index for frequently queried fields
    collection.create_index('email', unique=True)
    collection.create_index([('city', 1), ('age', -1)])
```

### 5. Batch Operations When Possible

```python
# Good: Batch insert
users = [{'name': f'User{i}'} for i in range(1000)]
conn.insert_many('users', users)

# Avoid: Individual inserts
for i in range(1000):
    conn.insert_one('users', {'name': f'User{i}'})
```

### 6. Handle Errors Appropriately

```python
# Good: Specific error handling
try:
    with MongoDBConnection(host='localhost', database='mydb') as conn:
        results = conn.execute_query('users', filter_dict)
except QueryError as e:
    logger.error(f"Query failed: {e}")
    # Handle query error
except DatabaseConnectionError as e:
    logger.error(f"Connection failed: {e}")
    # Handle connection error

# Avoid: Generic error handling
try:
    with MongoDBConnection(host='localhost', database='mydb') as conn:
        results = conn.execute_query('users', filter_dict)
except Exception as e:
    pass  # Swallowing all errors
```

### 7. Use Environment Variables for Credentials

```python
import os

config = MongoDBConnectionConfig(
    host=os.getenv('MONGO_HOST', 'localhost'),
    port=int(os.getenv('MONGO_PORT', '27017')),
    database=os.getenv('MONGO_DB'),
    username=os.getenv('MONGO_USER'),
    password=os.getenv('MONGO_PASSWORD')
)

conn = MongoDBConnection(config=config)
```

### 8. Add Metadata to Configurations

```python
# Good: Document your configurations
config = MongoDBConnectionConfig(
    host='prod-mongo-01',
    database='analytics',
    instance_name='production-analytics',
    environment='production',
    description='Primary analytics database for production reporting',
    tags=['analytics', 'production', 'critical'],
    metadata={
        'owner': 'data-team@example.com',
        'backup_schedule': 'hourly',
        'retention_days': 90
    }
)
```

### 9. Validate Configuration Before Use

```python
config = MongoDBConnectionConfig(
    host='localhost',
    database='mydb',
    username='admin',
    password='secret'
)

# Validate before using
try:
    conn = MongoDBConnection(config=config)
    is_valid = conn.validate_config()
    if is_valid:
        conn.connect()
except ConfigurationError as e:
    print(f"Invalid configuration: {e}")
```

### 10. Use Type Hints

```python
from typing import List, Dict, Any
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig

def get_users_by_city(config: MongoDBConnectionConfig, city: str) -> List[Dict[str, Any]]:
    """
    Get all users from a specific city.

    Args:
        config: MongoDB connection configuration
        city: City name to filter by

    Returns:
        List of user documents
    """
    with MongoDBConnection(config=config) as conn:
        return conn.execute_query('users', {'city': city})
```

---

## Testing

### Unit Testing with Mock

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig

def test_connection_config():
    """Test configuration creation."""
    config = MongoDBConnectionConfig(
        host='localhost',
        port=27017,
        database='testdb',
        username='testuser',
        password='testpass'
    )

    assert config.config['host'] == 'localhost'
    assert config.config['port'] == 27017
    assert config.config['database'] == 'testdb'

@patch('gds_mongodb.connection.MongoClient')
def test_connection_connect(mock_client):
    """Test connection establishment."""
    mock_client.return_value = MagicMock()

    conn = MongoDBConnection(
        host='localhost',
        database='testdb'
    )
    conn.connect()

    assert conn.is_connected()
    mock_client.assert_called_once()

@patch('gds_mongodb.connection.MongoClient')
def test_execute_query(mock_client):
    """Test query execution."""
    # Setup mock
    mock_collection = MagicMock()
    mock_collection.find.return_value = [
        {'name': 'User1', 'age': 25},
        {'name': 'User2', 'age': 30}
    ]

    mock_db = MagicMock()
    mock_db.__getitem__.return_value = mock_collection

    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = mock_db
    mock_client.return_value = mock_client_instance

    # Test
    with MongoDBConnection(host='localhost', database='testdb') as conn:
        results = conn.execute_query('users', {'age': {'$gte': 25}})

        assert len(results) == 2
        assert results[0]['name'] == 'User1'
```

### Integration Testing

```python
import pytest
from gds_mongodb import MongoDBConnection

@pytest.fixture
def mongo_connection():
    """Fixture for MongoDB connection."""
    conn = MongoDBConnection(
        host='localhost',
        port=27017,
        database='test_db'
    )
    conn.connect()

    # Cleanup before test
    conn.delete_many('test_users', {})

    yield conn

    # Cleanup after test
    conn.delete_many('test_users', {})
    conn.disconnect()

def test_insert_and_query(mongo_connection):
    """Test insert and query operations."""
    # Insert test data
    test_user = {'name': 'Test User', 'email': 'test@example.com', 'age': 25}
    result = mongo_connection.insert_one('test_users', test_user)

    assert result['inserted_id'] is not None

    # Query inserted data
    users = mongo_connection.execute_query('test_users', {'name': 'Test User'})

    assert len(users) == 1
    assert users[0]['email'] == 'test@example.com'
    assert users[0]['age'] == 25

def test_update_operations(mongo_connection):
    """Test update operations."""
    # Insert test data
    mongo_connection.insert_one('test_users', {'name': 'Test', 'age': 25})

    # Update
    result = mongo_connection.update_one(
        'test_users',
        {'name': 'Test'},
        {'$set': {'age': 26}}
    )

    assert result['modified_count'] == 1

    # Verify update
    users = mongo_connection.execute_query('test_users', {'name': 'Test'})
    assert users[0]['age'] == 26
```

---

## Examples

### Example 1: User Management System

```python
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig
from typing import List, Dict, Any, Optional

class UserManager:
    """User management system using MongoDB."""

    def __init__(self, config: MongoDBConnectionConfig):
        self.config = config
        self.collection = 'users'

    def create_user(self, name: str, email: str, age: int) -> str:
        """Create a new user."""
        with MongoDBConnection(config=self.config) as conn:
            user = {
                'name': name,
                'email': email,
                'age': age,
                'status': 'active'
            }
            result = conn.insert_one(self.collection, user)
            return str(result['inserted_id'])

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        with MongoDBConnection(config=self.config) as conn:
            users = conn.execute_query(self.collection, {'email': email})
            return users[0] if users else None

    def get_users_by_age_range(self, min_age: int, max_age: int) -> List[Dict[str, Any]]:
        """Get users within age range."""
        with MongoDBConnection(config=self.config) as conn:
            return conn.execute_query(
                self.collection,
                {'age': {'$gte': min_age, '$lte': max_age}}
            )

    def update_user_status(self, email: str, status: str) -> bool:
        """Update user status."""
        with MongoDBConnection(config=self.config) as conn:
            result = conn.update_one(
                self.collection,
                {'email': email},
                {'$set': {'status': status}}
            )
            return result['modified_count'] > 0

    def delete_user(self, email: str) -> bool:
        """Delete user by email."""
        with MongoDBConnection(config=self.config) as conn:
            result = conn.delete_one(self.collection, {'email': email})
            return result['deleted_count'] > 0

# Usage
config = MongoDBConnectionConfig(
    host='localhost',
    database='user_db',
    username='admin',
    password='secret'
)

manager = UserManager(config)

# Create users
user_id = manager.create_user('John Doe', 'john@example.com', 30)
print(f"Created user: {user_id}")

# Query users
young_users = manager.get_users_by_age_range(20, 30)
print(f"Found {len(young_users)} young users")

# Update user
manager.update_user_status('john@example.com', 'inactive')
```

### Example 2: Product Inventory System

```python
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig
from typing import List, Dict, Any
from pymongo import DESCENDING

class InventoryManager:
    """Product inventory management system."""

    def __init__(self, config: MongoDBConnectionConfig):
        self.config = config
        self.collection = 'products'

    def add_product(self, name: str, price: float, stock: int, category: str) -> str:
        """Add a new product."""
        with MongoDBConnection(config=self.config) as conn:
            product = {
                'name': name,
                'price': price,
                'stock': stock,
                'category': category
            }
            result = conn.insert_one(self.collection, product)
            return str(result['inserted_id'])

    def update_stock(self, product_name: str, quantity: int) -> bool:
        """Update product stock."""
        with MongoDBConnection(config=self.config) as conn:
            result = conn.update_one(
                self.collection,
                {'name': product_name},
                {'$inc': {'stock': quantity}}
            )
            return result['modified_count'] > 0

    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with low stock."""
        with MongoDBConnection(config=self.config) as conn:
            return conn.execute_query(
                self.collection,
                {'stock': {'$lt': threshold}},
                sort=[('stock', 1)]
            )

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all products in a category."""
        with MongoDBConnection(config=self.config) as conn:
            return conn.execute_query(
                self.collection,
                {'category': category},
                sort=[('name', 1)]
            )

    def get_expensive_products(self, min_price: float) -> List[Dict[str, Any]]:
        """Get products above a price threshold."""
        with MongoDBConnection(config=self.config) as conn:
            return conn.execute_query(
                self.collection,
                {'price': {'$gte': min_price}},
                sort=[('price', DESCENDING)]
            )

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get inventory summary statistics."""
        with MongoDBConnection(config=self.config) as conn:
            collection = conn._db[self.collection]

            pipeline = [
                {'$group': {
                    '_id': '$category',
                    'total_products': {'$sum': 1},
                    'total_stock': {'$sum': '$stock'},
                    'avg_price': {'$avg': '$price'}
                }},
                {'$sort': {'total_stock': -1}}
            ]

            return list(collection.aggregate(pipeline))

# Usage
config = MongoDBConnectionConfig(
    host='localhost',
    database='inventory_db',
    username='admin',
    password='secret'
)

inventory = InventoryManager(config)

# Add products
inventory.add_product('Laptop', 1200, 15, 'Electronics')
inventory.add_product('Mouse', 25, 100, 'Electronics')
inventory.add_product('Desk', 250, 5, 'Furniture')

# Check low stock
low_stock = inventory.get_low_stock_products(threshold=10)
for product in low_stock:
    print(f"Low stock alert: {product['name']} - {product['stock']} remaining")

# Get summary
summary = inventory.get_inventory_summary()
for cat in summary:
    print(f"{cat['_id']}: {cat['total_products']} products, {cat['total_stock']} total stock")
```

### Example 3: Configuration Management Application

```python
from gds_mongodb import MongoDBConnection, MongoDBConnectionConfig, MongoDBConfiguration
from typing import Dict, Any
import json

class MongoConfigManager:
    """MongoDB configuration management and monitoring."""

    def __init__(self, config: MongoDBConnectionConfig):
        self.config = config

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all MongoDB configuration settings."""
        with MongoDBConnection(config=self.config) as conn:
            mongo_config = MongoDBConfiguration(conn)
            return mongo_config.get_all()

    def get_runtime_settings(self) -> Dict[str, Any]:
        """Get runtime-modifiable settings."""
        with MongoDBConnection(config=self.config) as conn:
            mongo_config = MongoDBConfiguration(conn)
            return mongo_config.get_runtime_settable()

    def update_log_level(self, level: int) -> None:
        """Update MongoDB log level."""
        with MongoDBConnection(config=self.config) as conn:
            mongo_config = MongoDBConfiguration(conn)
            mongo_config.set('logLevel', level)
            print(f"Log level updated to {level}")

    def export_configuration(self, filepath: str) -> None:
        """Export configuration to JSON file."""
        settings = self.get_all_settings()
        with open(filepath, 'w') as f:
            json.dump(settings, f, indent=2, default=str)
        print(f"Configuration exported to {filepath}")

    def compare_configurations(self, other_config: MongoDBConnectionConfig) -> Dict[str, Any]:
        """Compare configurations between two MongoDB instances."""
        settings1 = self.get_all_settings()

        other_manager = MongoConfigManager(other_config)
        settings2 = other_manager.get_all_settings()

        differences = {}
        for key in settings1:
            if key in settings2 and settings1[key] != settings2[key]:
                differences[key] = {
                    'instance1': settings1[key],
                    'instance2': settings2[key]
                }

        return differences

# Usage
admin_config = MongoDBConnectionConfig(
    host='localhost',
    port=27017,
    database='admin',
    username='admin',
    password='secret'
)

manager = MongoConfigManager(admin_config)

# Get all settings
all_settings = manager.get_all_settings()
print(f"Total settings: {len(all_settings)}")

# Get runtime settings
runtime_settings = manager.get_runtime_settings()
print(f"Runtime modifiable settings: {len(runtime_settings)}")

# Update log level
manager.update_log_level(2)

# Export configuration
manager.export_configuration('mongo_config.json')
```

---

## Additional Resources

### Package Structure

```
gds_mongodb/
├── __init__.py              # Package initialization
├── connection.py            # MongoDBConnection class
├── connection_config.py     # MongoDBConnectionConfig class
├── configuration.py         # MongoDBConfiguration class
└── replica_set.py          # Replica set utilities
```

### Related Packages

- **gds-database**: Base interface package
- **pymongo**: MongoDB Python driver
- **gds-mssql**: SQL Server implementation
- **gds-postgres**: PostgreSQL implementation

### MongoDB Documentation

- [MongoDB Official Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Query Operators](https://docs.mongodb.com/manual/reference/operator/query/)
- [MongoDB Aggregation](https://docs.mongodb.com/manual/aggregation/)

### Support

For issues, questions, or contributions, please refer to the package repository or contact the GDS team.

---

## Conclusion

The `gds_mongodb` package provides a robust, production-ready solution for MongoDB database management in Python. By following the patterns and best practices outlined in this guide, you can build reliable, maintainable database applications.

Key takeaways:

1. Use configuration objects for reusability
2. Leverage context managers for automatic resource management
3. Implement proper error handling
4. Use projections and indexes for performance
5. Follow MongoDB best practices for queries and operations
6. Test your database code thoroughly

Happy coding!
