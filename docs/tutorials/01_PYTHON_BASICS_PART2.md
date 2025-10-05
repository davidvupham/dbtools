# Complete Python Tutorial for Beginners - Part 2
## Advanced Concepts: Decorators, Context Managers, and Design Patterns

This is Part 2 of the Python tutorial. Make sure you've completed [Part 1](01_PYTHON_BASICS_FOR_THIS_PROJECT.md) first!

---

## Table of Contents

1. [Decorators](#decorators)
2. [Context Managers](#context-managers)
3. [Logging](#logging)
4. [Modules and Packages](#modules-and-packages)
5. [Design Patterns](#design-patterns)
6. [Putting It All Together](#putting-it-all-together)

---

## Decorators

### What is a Decorator?

A **decorator** is a function that modifies another function's behavior. Think of it like gift wrapping - the gift (function) stays the same, but you add something around it.

### Simple Example

```python
# A simple decorator
def make_bold(func):
    """Decorator that adds bold tags."""
    def wrapper():
        result = func()
        return f"<b>{result}</b>"
    return wrapper

# Without decorator
def say_hello():
    return "Hello!"

print(say_hello())  # "Hello!"

# With decorator
@make_bold
def say_hello():
    return "Hello!"

print(say_hello())  # "<b>Hello!</b>"
```

**What happened?**
1. `@make_bold` is decorator syntax
2. It wraps `say_hello()` with the `wrapper()` function
3. When you call `say_hello()`, you're actually calling `wrapper()`
4. `wrapper()` calls the original function and modifies its output

### Decorator with Arguments

```python
def repeat(times):
    """Decorator that repeats a function multiple times."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    return f"Hello {name}!"

print(greet("Alice"))
# ["Hello Alice!", "Hello Alice!", "Hello Alice!"]
```

**Understanding the layers:**
1. `repeat(3)` returns `decorator`
2. `decorator` wraps the function
3. `wrapper` does the actual work

### Practical Example: Timing Decorator

```python
import time

def timer(func):
    """Decorator that times function execution."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(2)
    return "Done!"

result = slow_function()
# Output: slow_function took 2.00 seconds
print(result)  # "Done!"
```

### Example from Our Code

From `vault.py`:
```python
def with_retry(max_attempts=3, backoff_factor=2.0):
    """
    Decorator that retries a function if it fails.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
    """
    def decorator(func):
        @wraps(func)  # Preserves original function's metadata
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    # Try to execute the function
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed, give up
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(backoff_factor ** attempt, 60)
                    logger.warning(
                        "Attempt %d/%d failed: %s. Retrying in %.1fs...",
                        attempt + 1, max_attempts, e, delay
                    )
                    time.sleep(delay)
            
            # All attempts failed
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@with_retry(max_attempts=3, backoff_factor=2.0)
def fetch_secret_from_vault(secret_path):
    """Fetch secret with automatic retry on failure."""
    response = requests.get(f"{vault_url}/{secret_path}")
    if not response.ok:
        raise VaultError("Failed to fetch secret")
    return response.json()
```

**Why this design?**
- **Automatic retry**: Don't need to write retry logic everywhere
- **Configurable**: Can set max attempts and backoff
- **Reusable**: Can apply to any function
- **Clean code**: Function logic separate from retry logic

### @property Decorator

```python
class Temperature:
    """Temperature with automatic conversion."""
    
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Get temperature in Celsius."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set temperature in Celsius."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get temperature in Fahrenheit."""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set temperature in Fahrenheit."""
        self.celsius = (value - 32) * 5/9

# Usage
temp = Temperature(25)
print(temp.celsius)     # 25
print(temp.fahrenheit)  # 77.0

temp.fahrenheit = 32    # Set using Fahrenheit
print(temp.celsius)     # 0.0
```

**Why @property?**
- Access like an attribute: `temp.celsius` instead of `temp.get_celsius()`
- Can add validation when setting
- Can compute values on-the-fly
- Cleaner API

---

## Context Managers

### What is a Context Manager?

A **context manager** handles setup and cleanup automatically. It's perfect for resources that need to be opened and closed (files, connections, locks).

### The Problem Without Context Managers

```python
# Without context manager - easy to forget cleanup
file = open("data.txt", "r")
try:
    data = file.read()
    process_data(data)
finally:
    file.close()  # Must remember to close!

# If you forget to close:
file = open("data.txt", "r")
data = file.read()
# File never closed! Resource leak!
```

### With Context Manager

```python
# With context manager - automatic cleanup
with open("data.txt", "r") as file:
    data = file.read()
    process_data(data)
    # File automatically closed when done!
```

### How It Works

```python
class MyFile:
    """Simple file context manager."""
    
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """Called when entering 'with' block."""
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file  # This is what 'as' gets
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block."""
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

# Usage
with MyFile("data.txt", "r") as file:
    data = file.read()
    # __exit__ automatically called here
```

**The magic methods:**
- `__enter__`: Runs when entering the `with` block
- `__exit__`: Runs when leaving the `with` block (even if error!)

### Example from Our Code

From `connection.py`:
```python
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """Snowflake connection with context manager support."""
    
    def __enter__(self):
        """Context manager entry - establish connection."""
        self.initialize()  # Setup
        self.connect()     # Connect to Snowflake
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.cleanup()  # Close connection and cleanup
        return False    # Don't suppress exceptions

# Usage
with SnowflakeConnection(account="prod", user="admin") as conn:
    # Connection automatically established
    results = conn.execute_query("SELECT * FROM users")
    process_results(results)
    # Connection automatically closed when done!

# Even if there's an error, connection is still closed:
try:
    with SnowflakeConnection(account="prod", user="admin") as conn:
        results = conn.execute_query("INVALID SQL")  # Error!
except Exception as e:
    print(f"Error: {e}")
    # Connection was still closed properly!
```

**Why context managers?**
- **Automatic cleanup**: Never forget to close resources
- **Exception safe**: Cleanup happens even if there's an error
- **Cleaner code**: No try/finally blocks everywhere
- **Best practice**: Recommended for all resources

### Creating Context Managers with contextlib

```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    """Context manager to time code execution."""
    start = time.time()
    print(f"Starting {name}...")
    
    try:
        yield  # Code in 'with' block runs here
    finally:
        end = time.time()
        print(f"{name} took {end - start:.2f} seconds")

# Usage
with timer("Data processing"):
    # Your code here
    time.sleep(2)
    process_data()
    # Timing printed automatically
```

### Multiple Context Managers

```python
# Can use multiple context managers
with open("input.txt", "r") as infile, open("output.txt", "w") as outfile:
    data = infile.read()
    processed = process_data(data)
    outfile.write(processed)
    # Both files automatically closed
```

---

## Logging

### Why Logging?

**Logging** records what your program is doing. It's essential for:
- **Debugging**: Find out what went wrong
- **Monitoring**: Track program behavior in production
- **Auditing**: Record important events

### Print vs Logging

```python
# Bad: Using print
def process_user(user_id):
    print(f"Processing user {user_id}")  # Goes to console
    # Can't control output
    # Can't filter by severity
    # Can't send to files/services

# Good: Using logging
import logging

logger = logging.getLogger(__name__)

def process_user(user_id):
    logger.info("Processing user %s", user_id)  # Flexible output
    # Can control where it goes
    # Can filter by level
    # Can format differently
```

### Logging Levels

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Different severity levels (from lowest to highest)
logger.debug("Detailed info for debugging")      # Only during development
logger.info("General information")                # Normal operation
logger.warning("Something unexpected")            # Potential problem
logger.error("Something failed")                  # Definite problem
logger.critical("Serious error")                  # Program might crash
```

**When to use each level:**
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working
- **WARNING**: Something unexpected, but program continues
- **ERROR**: Something failed, but program continues
- **CRITICAL**: Serious error, program might stop

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

def connect_to_database(server, port):
    """Connect to database with proper logging."""
    
    # Log start of operation
    logger.info("Attempting to connect to %s:%d", server, port)
    
    try:
        # Log detailed debug info
        logger.debug("Connection parameters: server=%s, port=%d, timeout=30", server, port)
        
        connection = establish_connection(server, port)
        
        # Log success
        logger.info("Successfully connected to %s:%d", server, port)
        return connection
        
    except ConnectionError as e:
        # Log error with details
        logger.error("Failed to connect to %s:%d: %s", server, port, e)
        raise
    except Exception as e:
        # Log unexpected errors
        logger.critical("Unexpected error connecting to %s:%d: %s", server, port, e)
        raise
```

### Lazy Logging (Important!)

```python
# BAD: String always created (even if not logged)
logger.debug(f"User {user_id} data: {expensive_function()}")
# expensive_function() runs even if DEBUG is disabled!

# GOOD: Lazy evaluation (string only created if logged)
logger.debug("User %s data: %s", user_id, expensive_function())
# expensive_function() only runs if DEBUG is enabled!
```

### Example from Our Code

From `connection.py`:
```python
import logging

logger = logging.getLogger(__name__)

class SnowflakeConnection:
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        # Log start of operation
        logger.info("Connecting to Snowflake account: %s", self.account)
        
        try:
            # Log debug details
            logger.debug(
                "Connection parameters: account=%s, user=%s, warehouse=%s",
                self.account, self.user, self.warehouse
            )
            
            # Attempt connection
            self.connection = snowflake.connector.connect(**connection_params)
            
            # Log success
            logger.info("Successfully connected to Snowflake account: %s", self.account)
            return self.connection
            
        except Exception as e:
            # Log error
            logger.error(
                "Failed to connect to Snowflake account %s: %s",
                self.account, str(e)
            )
            raise SnowflakeConnectionError(
                f"Failed to connect to Snowflake account {self.account}: {str(e)}"
            ) from e
    
    def close(self):
        """Close connection."""
        if self.connection is not None:
            try:
                self.connection.close()
                logger.info("Closed connection to Snowflake account: %s", self.account)
            except Exception as e:
                logger.error("Error closing connection: %s", str(e))
```

**Why this logging strategy?**
- **INFO level**: Track major operations (connect, close)
- **DEBUG level**: Detailed information for troubleshooting
- **ERROR level**: Problems that need attention
- **Lazy logging**: Use `%s` placeholders, not f-strings
- **Context**: Always include relevant details (account, user, etc.)

### Configuring Logging

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,                          # Minimum level to log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),          # Log to file
        logging.StreamHandler()                  # Log to console
    ]
)

# Output format:
# 2025-01-15 10:30:45,123 - myapp.database - INFO - Connected to database
```

---

## Modules and Packages

### What is a Module?

A **module** is a Python file containing code. A **package** is a directory containing multiple modules.

### Importing Modules

```python
# Import entire module
import math
print(math.sqrt(16))  # 4.0
print(math.pi)        # 3.14159...

# Import specific items
from math import sqrt, pi
print(sqrt(16))  # 4.0
print(pi)        # 3.14159...

# Import with alias
import pandas as pd
df = pd.DataFrame()

# Import everything (discouraged!)
from math import *  # Don't do this - unclear where things come from
```

### Creating a Module

```python
# File: my_utils.py
"""Utility functions for my project."""

def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

def add(a, b):
    """Add two numbers."""
    return a + b

PI = 3.14159

# File: main.py
from my_utils import greet, add, PI

print(greet("Alice"))  # "Hello, Alice!"
print(add(5, 3))       # 8
print(PI)              # 3.14159
```

### Package Structure

```
my_project/
├── my_package/
│   ├── __init__.py       # Makes it a package
│   ├── core.py           # Core functionality
│   ├── utils.py          # Utility functions
│   └── database.py       # Database code
└── main.py               # Main script
```

### The `__init__.py` File

```python
# File: my_package/__init__.py
"""My package for doing cool things."""

# Import key items to make them easily accessible
from .core import MainClass
from .utils import helper_function
from .database import Database

# Define what gets imported with "from my_package import *"
__all__ = ['MainClass', 'helper_function', 'Database']

# Package version
__version__ = '1.0.0'

# Now users can do:
# from my_package import MainClass
# instead of:
# from my_package.core import MainClass
```

### Example from Our Code

From `gds_snowflake/__init__.py`:
```python
"""
GDS Snowflake Package

Provides classes for connecting to Snowflake, managing databases and tables,
and monitoring replication status for failover groups.
"""

# Import main classes
from .connection import SnowflakeConnection
from .database import SnowflakeDatabase
from .table import SnowflakeTable
from .replication import SnowflakeReplication, FailoverGroup
from .monitor import (
    SnowflakeMonitor,
    AlertSeverity,
    MonitoringResult,
    ConnectivityResult,
    ReplicationResult
)
from .base import (
    BaseMonitor,
    DatabaseConnection,
    SecretProvider,
    ConfigurableComponent,
    ResourceManager,
    RetryableOperation,
    OperationResult
)

# Package metadata
__version__ = "1.0.0"

# Define public API
__all__ = [
    "SnowflakeConnection",
    "SnowflakeDatabase",
    "SnowflakeTable",
    "SnowflakeReplication",
    "FailoverGroup",
    "SnowflakeMonitor",
    "AlertSeverity",
    "MonitoringResult",
    "ConnectivityResult",
    "ReplicationResult",
    "BaseMonitor",
    "DatabaseConnection",
    "SecretProvider",
    "ConfigurableComponent",
    "ResourceManager",
    "RetryableOperation",
    "OperationResult"
]

# Now users can do:
# from gds_snowflake import SnowflakeConnection, SnowflakeMonitor
```

**Why this structure?**
- **Clean imports**: Users don't need to know internal structure
- **Public API**: `__all__` defines what's public
- **Version tracking**: `__version__` for package version
- **Documentation**: Docstring explains the package

### Relative Imports

```python
# Within a package, use relative imports
# File: my_package/database.py
from .utils import helper_function      # Same package
from .core import MainClass             # Same package
from ..other_package import something   # Parent package

# Absolute imports (also fine)
from my_package.utils import helper_function
from my_package.core import MainClass
```

---

## Design Patterns

### What are Design Patterns?

**Design patterns** are proven solutions to common programming problems. They're like recipes for organizing code.

### 1. Factory Pattern

**Problem**: Creating objects is complex or you want to hide the creation logic.

**Solution**: Use a factory function/class to create objects.

```python
# Without factory - complex creation logic everywhere
if database_type == "postgres":
    conn = PostgreSQLConnection(host, port, user, password)
elif database_type == "mysql":
    conn = MySQLConnection(host, port, user, password)
elif database_type == "snowflake":
    conn = SnowflakeConnection(account, user, private_key)

# With factory - creation logic in one place
def create_database_connection(database_type, **kwargs):
    """Factory function to create database connections."""
    if database_type == "postgres":
        return PostgreSQLConnection(**kwargs)
    elif database_type == "mysql":
        return MySQLConnection(**kwargs)
    elif database_type == "snowflake":
        return SnowflakeConnection(**kwargs)
    else:
        raise ValueError(f"Unknown database type: {database_type}")

# Usage
conn = create_database_connection("snowflake", account="prod", user="admin")
```

**Example from Our Code** (`enhanced_vault.py`):
```python
def create_vault_client(
    vault_addr: Optional[str] = None,
    role_id: Optional[str] = None,
    secret_id: Optional[str] = None,
    enhanced: bool = True
) -> Any:
    """
    Factory function to create Vault client.
    
    Args:
        vault_addr: Vault server address
        role_id: AppRole role_id
        secret_id: AppRole secret_id
        enhanced: Whether to use enhanced client with OOP features
    
    Returns:
        Vault client instance
    """
    if enhanced:
        return EnhancedVaultClient(
            vault_addr=vault_addr,
            role_id=role_id,
            secret_id=secret_id
        )
    else:
        from .vault import VaultClient
        return VaultClient(
            vault_addr=vault_addr,
            role_id=role_id,
            secret_id=secret_id
        )

# Usage
client = create_vault_client(enhanced=True)  # Get enhanced version
client = create_vault_client(enhanced=False)  # Get basic version
```

**Why factory pattern?**
- **Centralized creation**: All creation logic in one place
- **Flexibility**: Easy to change what gets created
- **Abstraction**: Users don't need to know implementation details

### 2. Singleton Pattern

**Problem**: Need exactly one instance of a class (e.g., database connection pool, logger).

**Solution**: Ensure only one instance can be created.

```python
class DatabasePool:
    """Singleton database connection pool."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = []
        return cls._instance
    
    def get_connection(self):
        # Return a connection from the pool
        pass

# Usage
pool1 = DatabasePool()
pool2 = DatabasePool()

print(pool1 is pool2)  # True - same instance!
```

### 3. Strategy Pattern

**Problem**: Need different algorithms/behaviors that can be swapped.

**Solution**: Define a family of algorithms and make them interchangeable.

```python
# Strategy interface
class CompressionStrategy:
    def compress(self, data):
        pass

# Concrete strategies
class ZipCompression(CompressionStrategy):
    def compress(self, data):
        return f"ZIP compressed: {data}"

class GzipCompression(CompressionStrategy):
    def compress(self, data):
        return f"GZIP compressed: {data}"

# Context that uses strategy
class FileCompressor:
    def __init__(self, strategy: CompressionStrategy):
        self.strategy = strategy
    
    def compress_file(self, filename):
        data = read_file(filename)
        return self.strategy.compress(data)

# Usage
compressor = FileCompressor(ZipCompression())
result = compressor.compress_file("data.txt")

# Change strategy
compressor.strategy = GzipCompression()
result = compressor.compress_file("data.txt")
```

### 4. Observer Pattern

**Problem**: Need to notify multiple objects when something changes.

**Solution**: Objects subscribe to events and get notified automatically.

```python
class Subject:
    """Object being observed."""
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        """Subscribe an observer."""
        self._observers.append(observer)
    
    def notify(self, event):
        """Notify all observers."""
        for observer in self._observers:
            observer.update(event)

class Observer:
    """Object that observes."""
    def update(self, event):
        print(f"Received event: {event}")

# Usage
subject = Subject()
observer1 = Observer()
observer2 = Observer()

subject.attach(observer1)
subject.attach(observer2)

subject.notify("Something happened!")
# Both observers get notified
```

### 5. Template Method Pattern

**Problem**: Multiple classes share similar algorithms but differ in some steps.

**Solution**: Define algorithm structure in base class, let subclasses implement specific steps.

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """Template for processing data."""
    
    def process(self):
        """Template method - defines the algorithm."""
        data = self.read_data()
        validated = self.validate_data(data)
        processed = self.process_data(validated)
        self.save_data(processed)
    
    @abstractmethod
    def read_data(self):
        """Subclasses must implement."""
        pass
    
    def validate_data(self, data):
        """Default validation."""
        return data
    
    @abstractmethod
    def process_data(self, data):
        """Subclasses must implement."""
        pass
    
    @abstractmethod
    def save_data(self, data):
        """Subclasses must implement."""
        pass

class CSVProcessor(DataProcessor):
    """Process CSV files."""
    def read_data(self):
        return read_csv("data.csv")
    
    def process_data(self, data):
        return transform_csv(data)
    
    def save_data(self, data):
        write_csv("output.csv", data)

# Usage
processor = CSVProcessor()
processor.process()  # Follows the template!
```

**Example from Our Code** (`base.py`):
```python
class BaseMonitor(ABC):
    """Template for all monitors."""
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """Subclasses must implement the check logic."""
        pass
    
    def _log_result(self, result: Dict[str, Any]) -> None:
        """Template method - logs results (same for all monitors)."""
        status = "SUCCESS" if result.get('success', False) else "FAILED"
        duration = result.get('duration_ms', 0)
        
        self.logger.info(
            "%s check %s in %dms - %s",
            self.name,
            status,
            duration,
            result.get('message', 'No message')
        )
    
    def _record_check(self, result: Dict[str, Any]) -> None:
        """Template method - records statistics (same for all monitors)."""
        self._check_count += 1
        self._last_check = datetime.now()

# Subclass implements specific check logic
class SnowflakeMonitor(BaseMonitor):
    def check(self) -> Dict[str, Any]:
        """Snowflake-specific monitoring."""
        start_time = time.time()
        
        try:
            results = self.monitor_all()  # Snowflake-specific
            
            duration_ms = (time.time() - start_time) * 1000
            
            result = {
                'success': results['summary']['connectivity_ok'],
                'message': f"Monitoring completed for {self.account}",
                'duration_ms': duration_ms,
                'data': results
            }
            
            # Use inherited template methods
            self._log_result(result)
            self._record_check(result)
            
            return result
        except Exception as e:
            # Handle error...
            pass
```

**Why template method?**
- **Code reuse**: Common logic in base class
- **Consistency**: All subclasses follow same structure
- **Flexibility**: Subclasses customize specific steps
- **Maintainability**: Change common logic in one place

---

## Putting It All Together

Let's see how all these concepts work together in a real example from our codebase.

### Complete Example: SnowflakeConnection

```python
# File: gds_snowflake/connection.py

import logging
import os
from typing import Optional, List, Any, Dict
import snowflake.connector

# Imports from our package
from .base import DatabaseConnection, ConfigurableComponent, ResourceManager
from .exceptions import SnowflakeConnectionError

# Set up logging
logger = logging.getLogger(__name__)

class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    Manages Snowflake database connections.
    
    This class demonstrates:
    - Multiple inheritance (3 base classes)
    - Type hints
    - Error handling
    - Logging
    - Context manager
    - Encapsulation
    """
    
    def __init__(
        self,
        account: str,                      # Type hints
        user: Optional[str] = None,        # Optional parameters
        warehouse: Optional[str] = None,
        role: Optional[str] = None,
        database: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize connection.
        
        Args:
            account: Snowflake account name
            user: Username (optional)
            warehouse: Warehouse name (optional)
            role: Role name (optional)
            database: Database name (optional)
            config: Configuration dictionary (optional)
        """
        # Initialize base classes
        ConfigurableComponent.__init__(self, config)
        
        # Public attributes
        self.account = account
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.warehouse = warehouse
        self.role = role
        self.database = database
        self.connection = None
        
        # Private attributes (convention)
        self._initialized = False
        
        # Log initialization
        logger.debug("Initialized SnowflakeConnection for account: %s", account)
    
    # Implement abstract methods from DatabaseConnection
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """
        Establish connection to Snowflake.
        
        Returns:
            Snowflake connection object
            
        Raises:
            SnowflakeConnectionError: If connection fails
        """
        logger.info("Connecting to Snowflake account: %s", self.account)
        
        try:
            # Build connection parameters
            connection_params = {
                "account": self.account,
                "user": self.user,
                "private_key": self.private_key,
            }
            
            # Add optional parameters
            if self.warehouse:
                connection_params["warehouse"] = self.warehouse
            if self.role:
                connection_params["role"] = self.role
            if self.database:
                connection_params["database"] = self.database
            
            # Establish connection
            self.connection = snowflake.connector.connect(**connection_params)
            
            logger.info("Successfully connected to Snowflake account: %s", self.account)
            return self.connection
            
        except Exception as e:
            # Log error
            logger.error(
                "Failed to connect to Snowflake account %s: %s",
                self.account, str(e)
            )
            # Raise custom exception with context
            raise SnowflakeConnectionError(
                f"Failed to connect to Snowflake account {self.account}: {str(e)}"
            ) from e
    
    def disconnect(self) -> None:
        """Close database connection."""
        self.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Any]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            List of query results
        """
        logger.debug("Executing query: %s", query[:100])  # Log first 100 chars
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                
            logger.debug("Query returned %d rows", len(results))
            return results
            
        except Exception as e:
            logger.error("Query execution failed: %s", e)
            raise
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connection is not None and not self.connection.is_closed()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'account': self.account,
            'user': self.user,
            'warehouse': self.warehouse,
            'role': self.role,
            'database': self.database,
            'connected': self.is_connected()
        }
    
    # Implement abstract methods from ConfigurableComponent
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        required_fields = ['account']
        for field in required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                return False
        return True
    
    # Implement abstract methods from ResourceManager
    def initialize(self) -> None:
        """Initialize resources."""
        self._initialized = True
        logger.debug("Resources initialized")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.close()
        self._initialized = False
        logger.debug("Resources cleaned up")
    
    def is_initialized(self) -> bool:
        """Check if resources are initialized."""
        return self._initialized
    
    # Context manager methods (from ResourceManager)
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False  # Don't suppress exceptions
    
    def close(self):
        """Close the connection."""
        if self.connection is not None:
            try:
                self.connection.close()
                logger.info("Closed connection to Snowflake account: %s", self.account)
            except Exception as e:
                logger.error("Error closing connection: %s", str(e))

# Usage examples
if __name__ == "__main__":
    # Example 1: Basic usage
    conn = SnowflakeConnection(account="prod", user="admin")
    conn.connect()
    results = conn.execute_query("SELECT * FROM users LIMIT 10")
    conn.close()
    
    # Example 2: Context manager (recommended)
    with SnowflakeConnection(account="prod", user="admin") as conn:
        results = conn.execute_query("SELECT * FROM users LIMIT 10")
        # Connection automatically closed
    
    # Example 3: Error handling
    try:
        with SnowflakeConnection(account="invalid") as conn:
            results = conn.execute_query("SELECT * FROM users")
    except SnowflakeConnectionError as e:
        print(f"Connection failed: {e}")
```

### What This Example Demonstrates

1. **Multiple Inheritance**: Inherits from 3 base classes
2. **Abstract Base Classes**: Implements required methods
3. **Type Hints**: Clear parameter and return types
4. **Error Handling**: Try-except with custom exceptions
5. **Logging**: Comprehensive logging at different levels
6. **Context Manager**: Automatic resource management
7. **Encapsulation**: Public and private attributes
8. **Documentation**: Docstrings explain everything
9. **Design Patterns**: Template method, resource manager
10. **Best Practices**: Follows Python conventions

---

## Summary

Congratulations! You've learned:

✅ **Decorators**: Modify function behavior
✅ **Context Managers**: Automatic resource management
✅ **Logging**: Track program execution
✅ **Modules & Packages**: Organize code
✅ **Design Patterns**: Proven solutions to common problems

### Key Takeaways

1. **Decorators** wrap functions to add functionality
2. **Context managers** ensure cleanup with `with` statements
3. **Logging** is better than `print()` for production code
4. **Modules** organize code into reusable files
5. **Design patterns** provide proven solutions

### Next Steps

Now that you understand Python fundamentals, continue with:

1. **[Vault Module Tutorial](02_VAULT_MODULE_TUTORIAL.md)** - HashiCorp Vault integration
2. **[Connection Module Tutorial](03_CONNECTION_MODULE_TUTORIAL.md)** - Snowflake connections
3. **[Replication Module Tutorial](04_REPLICATION_MODULE_TUTORIAL.md)** - Replication monitoring

### Practice Exercises

Try these to reinforce your learning:

**Exercise 1: Create a Decorator**
```python
# Create a decorator that logs function calls
def log_calls(func):
    # Your code here
    pass

@log_calls
def add(a, b):
    return a + b

result = add(5, 3)  # Should log "Calling add with args: (5, 3)"
```

**Exercise 2: Create a Context Manager**
```python
# Create a context manager that times code execution
class Timer:
    # Your code here
    pass

with Timer():
    # Code to time
    time.sleep(1)
# Should print elapsed time
```

**Exercise 3: Use Design Patterns**
```python
# Create a factory function for different types of loggers
def create_logger(logger_type, name):
    # Your code here
    pass

logger = create_logger("file", "myapp")
logger = create_logger("console", "myapp")
```

---

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [Real Python Tutorials](https://realpython.com/)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)
- [Python Type Checking](https://realpython.com/python-type-checking/)

Happy coding! 🐍
