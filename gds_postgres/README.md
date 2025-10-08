# GDS PostgreSQL

A Python package providing PostgreSQL database connection functionality built on the `gds-database` interface. This package offers a comprehensive, production-ready PostgreSQL connection library with support for connection pooling, transaction management, and advanced PostgreSQL features.

## Features

- **Complete DatabaseConnection Implementation**: Full implementation of the `gds-database` interface
- **Connection Management**: Support for individual parameters, configuration dictionaries, and connection URLs
- **Transaction Support**: Full transaction management with commit/rollback capabilities
- **Resource Management**: Context manager support for automatic connection cleanup
- **Configuration Management**: Flexible configuration with validation
- **Metadata Access**: Built-in methods for accessing database metadata (tables, columns, etc.)
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Full type hints for better IDE support and runtime safety
- **Connection Pooling**: Support for psycopg2 connection pooling (optional)
- **Async Support**: Optional async support with asyncpg (optional)

## Installation

### Basic Installation

```bash
pip install gds-postgres
```

### With Optional Dependencies

```bash
# For connection pooling
pip install gds-postgres[pool]

# For async support
pip install gds-postgres[async]

# For development
pip install gds-postgres[dev]

# All optional dependencies
pip install gds-postgres[pool,async,dev]
```

## Requirements

- Python 3.8+
- PostgreSQL 9.6+
- `gds-database>=1.0.0`
- `psycopg2-binary>=2.8.0`

## Quick Start

### Basic Connection

```python
from gds_postgres import PostgreSQLConnection

# Connect with individual parameters
conn = PostgreSQLConnection(
    host='localhost',
    port=5432,
    database='mydb',
    user='myuser',
    password='mypassword'
)

conn.connect()
try:
    results = conn.execute_query("SELECT * FROM users")
    print(f"Found {len(results)} users")
finally:
    conn.disconnect()
```

### Using Connection URL

```python
from gds_postgres import PostgreSQLConnection

# Connect using PostgreSQL URL
conn = PostgreSQLConnection(
    connection_url='postgresql://user:password@localhost:5432/mydb'
)

with conn:  # Automatic connection management
    results = conn.execute_query_dict("SELECT id, name FROM users LIMIT 10")
    for user in results:
        print(f"User {user['id']}: {user['name']}")
```

### Configuration-Based Connection

```python
from gds_postgres import PostgreSQLConnection

config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb',
    'user': 'myuser',
    'password': 'mypassword',
    'connect_timeout': 30,
    'autocommit': False,
    'application_name': 'MyApp'
}

conn = PostgreSQLConnection(config=config)
```

## Advanced Usage

### Transaction Management

```python
with PostgreSQLConnection(
    host='localhost',
    database='mydb',
    user='myuser',
    password='mypass',
    autocommit=False  # Enable transaction mode
) as conn:
    try:
        # Begin transaction (implicit)
        conn.execute_query(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            ('John Doe', 'john@example.com')
        )
        
        conn.execute_query(
            "UPDATE user_stats SET login_count = login_count + 1 WHERE user_id = %s",
            (user_id,)
        )
        
        # Commit transaction
        conn.commit()
        print("Transaction completed successfully")
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Transaction failed: {e}")
```

### Database Metadata

```python
with PostgreSQLConnection(connection_url=db_url) as conn:
    # Get all table names
    tables = conn.get_table_names()
    print(f"Tables: {tables}")
    
    # Get column information for a table
    columns = conn.get_column_info('users')
    for col in columns:
        print(f"{col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
    
    # Get connection information
    info = conn.get_connection_info()
    print(f"Connected to PostgreSQL {info.get('server_version', 'unknown')}")
```

### Parameterized Queries

```python
with PostgreSQLConnection(config=config) as conn:
    # Safe parameterized queries
    users = conn.execute_query(
        "SELECT * FROM users WHERE age >= %s AND city = %s",
        (18, 'New York')
    )
    
    # Insert with parameters
    result = conn.execute_query(
        "INSERT INTO products (name, price, category) VALUES (%s, %s, %s)",
        ('Laptop', 999.99, 'Electronics')
    )
    print(f"Inserted {result[0]['affected_rows']} row(s)")
```

### Error Handling

```python
from gds_postgres import PostgreSQLConnection
from gds_database import ConnectionError, QueryError

try:
    conn = PostgreSQLConnection(
        host='nonexistent-host',
        database='mydb',
        user='myuser',
        password='mypass'
    )
    conn.connect()
    
except ConnectionError as e:
    print(f"Failed to connect: {e}")
    
except QueryError as e:
    print(f"Query failed: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### PostgreSQLConnection

The main connection class that implements the `DatabaseConnection` interface.

#### Constructor Parameters

- `host` (str, optional): PostgreSQL server hostname
- `port` (int, optional): PostgreSQL server port (default: 5432)
- `database` (str, optional): Database name
- `user` (str, optional): Username for authentication
- `password` (str, optional): Password for authentication
- `connection_url` (str, optional): Complete PostgreSQL connection URL
- `config` (dict, optional): Configuration dictionary
- `**kwargs`: Additional psycopg2 connection parameters

#### Core Methods

##### `connect() -> psycopg2.connection`
Establish connection to PostgreSQL database.

##### `disconnect() -> None`
Close database connection and clean up resources.

##### `execute_query(query: str, params: tuple = None, fetch_all: bool = True, return_dict: bool = False) -> List[Any]`
Execute SQL query and return results.

##### `execute_query_dict(query: str, params: tuple = None) -> List[Dict[str, Any]]`
Execute query and return results as dictionaries.

##### `is_connected() -> bool`
Check if connection is active.

##### `get_connection_info() -> Dict[str, Any]`
Get connection metadata and status.

#### Transaction Methods

##### `begin_transaction() -> None`
Begin a new transaction (for non-autocommit mode).

##### `commit() -> None`
Commit current transaction.

##### `rollback() -> None`
Rollback current transaction.

#### Metadata Methods

##### `get_table_names(schema: str = 'public') -> List[str]`
Get list of table names in specified schema.

##### `get_column_info(table_name: str, schema: str = 'public') -> List[Dict[str, Any]]`
Get column information for specified table.

## Configuration

### Configuration Parameters

The connection accepts the following configuration parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | required | PostgreSQL server hostname |
| `port` | int | 5432 | PostgreSQL server port |
| `database` | str | required | Database name |
| `user` | str | required | Username |
| `password` | str | optional | Password |
| `connect_timeout` | int | 30 | Connection timeout in seconds |
| `autocommit` | bool | False | Enable autocommit mode |
| `application_name` | str | optional | Application name for connection |

### Connection URL Format

```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

Examples:
- `postgresql://user:pass@localhost/mydb`
- `postgresql://user@localhost:5432/mydb`
- `postgresql://localhost/mydb?connect_timeout=10`

## Environment Variables

The package respects the following PostgreSQL environment variables:

- `PGHOST` - Database host
- `PGPORT` - Database port
- `PGDATABASE` - Database name
- `PGUSER` - Username
- `PGPASSWORD` - Password

## Examples

See the `examples/` directory for comprehensive usage examples:

- `connection_examples.py` - Basic connection patterns
- `transaction_examples.py` - Transaction management
- `metadata_examples.py` - Database metadata access
- `pooling_examples.py` - Connection pooling (if available)

## Testing

### Running Tests

```bash
# Install development dependencies
pip install gds-postgres[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=gds_postgres --cov-report=html

# Run specific test
pytest tests/test_connection.py::TestPostgreSQLConnection::test_connect_success
```

### Test Database Setup

To run integration tests, you'll need a PostgreSQL database:

```bash
# Using Docker
docker run --name test-postgres -e POSTGRES_PASSWORD=testpass -e POSTGRES_DB=testdb -p 5432:5432 -d postgres:13

# Or install PostgreSQL locally and create test database
createdb testdb
createuser testuser
psql -c "GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Ensure code is formatted (`black gds_postgres/`)
7. Ensure linting passes (`ruff check gds_postgres/`)
8. Commit your changes (`git commit -m 'Add some amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/davidvupham/snowflake.git
cd snowflake/gds_postgres

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black gds_postgres/

# Lint code
ruff check gds_postgres/

# Type check
mypy gds_postgres/
```

## Compatibility

### PostgreSQL Versions

- PostgreSQL 9.6+
- PostgreSQL 10+
- PostgreSQL 11+
- PostgreSQL 12+
- PostgreSQL 13+
- PostgreSQL 14+
- PostgreSQL 15+

### Python Versions

- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.12+

## Performance Considerations

- Use parameterized queries to prevent SQL injection and improve performance
- Enable connection pooling for high-traffic applications
- Use `autocommit=True` for read-only operations to avoid transaction overhead
- Consider using `execute_query_dict()` for better readability when working with result sets
- Use context managers (`with` statements) for automatic resource cleanup

## Security

- Always use parameterized queries to prevent SQL injection
- Store database credentials securely (environment variables, vault systems)
- Use SSL connections for production environments
- Limit database user permissions to minimum required
- Regularly update dependencies for security patches

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure `gds-database` is installed
2. **Connection Timeout**: Increase `connect_timeout` parameter
3. **SSL Errors**: Configure SSL parameters in connection config
4. **Permission Denied**: Check database user permissions
5. **Port Conflicts**: Ensure PostgreSQL is running on expected port

### Debugging

Enable debug logging to troubleshoot connection issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

conn = PostgreSQLConnection(...)
# Debug logs will show connection attempts and queries
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Full DatabaseConnection interface implementation
- Transaction management
- Metadata access methods
- Comprehensive test suite
- Type hints support
- Context manager support

## Related Packages

- [`gds-database`](../gds_database/) - Abstract database interface
- [`gds-snowflake`](../gds_snowflake/) - Snowflake implementation
- [`gds-vault`](../gds_vault/) - HashiCorp Vault integration

## Support

For issues and questions:

1. Check the [Issues](https://github.com/davidvupham/snowflake/issues) page
2. Review the documentation and examples
3. Create a new issue with detailed information about your problem