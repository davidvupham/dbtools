# GDS Database

A Python package providing abstract database interfaces and common patterns for database connections.

## Overview

The `gds_database` package provides abstract base classes and interfaces that can be used to build database connection libraries with consistent APIs. It serves as the foundation for database-specific packages like `gds_snowflake`, `gds_postgres`, etc.

## Features

- **Abstract Database Connection Interface**: `DatabaseConnection` ABC defining standard database operations
- **Configurable Components**: Base classes for configuration management
- **Resource Management**: Context manager support for proper resource cleanup
- **Retry Logic**: Built-in retry mechanisms for database operations
- **Type Safety**: Full type hints for better IDE support and runtime safety

## Installation

```bash
pip install gds-database
```

For development:
```bash
pip install gds-database[dev]
```

## Quick Start

### Basic Usage

```python
from gds_database import DatabaseConnection
from abc import ABC

class MyDatabaseConnection(DatabaseConnection):
    """Custom database connection implementation."""
    
    def connect(self):
        # Implement connection logic
        pass
    
    def disconnect(self):
        # Implement disconnection logic
        pass
    
    def execute_query(self, query, params=None):
        # Implement query execution
        pass
    
    def is_connected(self):
        # Check connection status
        pass
    
    def get_connection_info(self):
        # Return connection information
        pass
```

### Using Configuration Management

```python
from gds_database import ConfigurableComponent

class MyComponent(ConfigurableComponent):
    def validate_config(self):
        required_keys = ['host', 'port', 'database']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")
        return True

# Usage
component = MyComponent({
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb'
})
```

### Resource Management

```python
from gds_database import ResourceManager

class DatabaseManager(ResourceManager):
    def initialize(self):
        self.connection = create_connection()
    
    def cleanup(self):
        if hasattr(self, 'connection'):
            self.connection.close()
    
    def is_initialized(self):
        return hasattr(self, 'connection') and self.connection.is_open()

# Usage with context manager
with DatabaseManager() as db:
    # Connection is automatically managed
    pass
```

## Architecture

The package is built around several core abstract base classes:

### DatabaseConnection
The main interface that all database connections should implement:
- `connect()` - Establish database connection
- `disconnect()` - Close database connection  
- `execute_query()` - Execute queries
- `is_connected()` - Check connection status
- `get_connection_info()` - Get connection metadata

### ConfigurableComponent
Provides configuration management capabilities:
- `validate_config()` - Validate configuration
- `get_config()` / `set_config()` - Access configuration values
- `update_config()` - Bulk configuration updates

### ResourceManager
Enables proper resource management with context managers:
- `initialize()` - Set up resources
- `cleanup()` - Clean up resources
- `is_initialized()` - Check initialization status

### RetryableOperation
Adds retry logic to operations:
- `execute_with_retry()` - Execute with automatic retry
- Configurable retry count and backoff

## Examples

See the `examples/` directory for comprehensive usage examples.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/davidvupham/snowflake.git
cd snowflake/gds_database

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check .
black --check .
mypy .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gds_database --cov-report=html

# Run specific test
pytest tests/test_base.py::TestDatabaseConnection
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Core abstract base classes
- Configuration management
- Resource management
- Retry mechanisms
- Full type hint support