# GDS Database Architecture Guide

## Overview

The `gds_database` package is designed using **Object-Oriented Programming (OOP)** principles to provide reusable, extensible patterns for building database libraries. This guide explains the architecture for those new to Python and OOP.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Package Structure](#package-structure)
3. [Design Patterns](#design-patterns)
4. [Class Hierarchy](#class-hierarchy)
5. [Key Components](#key-components)
6. [Extension Points](#extension-points)

---

## Core Concepts

### What is Object-Oriented Programming?

**Object-Oriented Programming (OOP)** is a programming paradigm that organizes code around "objects" - bundles of data (attributes) and behavior (methods). Think of it like building with LEGO blocks where each block has specific properties and can do specific things.

#### Key OOP Principles in This Package:

1. **Encapsulation**: Bundling data and methods that operate on that data
   - Example: `DatabaseConnection` bundles connection data and connection methods

2. **Abstraction**: Hiding complex implementation details
   - Example: `execute_query()` hides the complexity of database protocols

3. **Inheritance**: Creating new classes based on existing ones
   - Example: `TransactionalConnection` extends `DatabaseConnection`

4. **Polymorphism**: Different classes can be used interchangeably if they share an interface
   - Example: Any class implementing `DatabaseConnection` can be used the same way

### What are Abstract Base Classes (ABCs)?

An **Abstract Base Class** is like a blueprint or contract. It defines WHAT methods a class must have, but not HOW they work.

```python
from abc import ABC, abstractmethod

class Animal(ABC):  # ABC means "Abstract Base Class"
    @abstractmethod  # This decorator means "subclasses MUST implement this"
    def make_sound(self):
        pass  # No implementation - just a placeholder

# You CANNOT create an Animal directly:
# animal = Animal()  # ❌ This raises TypeError

# You MUST create a specific animal:
class Dog(Animal):
    def make_sound(self):
        return "Woof!"

dog = Dog()  # ✅ This works
print(dog.make_sound())  # Prints: Woof!
```

---

## Package Structure

```
gds_database/
├── gds_database/           # Main package code
│   ├── __init__.py        # Package exports
│   ├── base.py            # Core abstract classes
│   └── py.typed           # Type checking marker
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_base.py       # Tests for base classes
├── docs/                  # Documentation (you are here!)
│   ├── ARCHITECTURE.md    # This file
│   ├── BUILD_GUIDE.md     # How to build/install
│   └── DEVELOPER_GUIDE.md # How to develop
├── pyproject.toml         # Package configuration
├── setup.py               # Installation script
└── README.md              # Quick start guide
```

### Why This Structure?

- **Separation of Concerns**: Code, tests, and docs are separate
- **Standard Layout**: Follows Python packaging best practices
- **Easy Navigation**: Clear hierarchy makes finding things easy

---

## Design Patterns

### 1. Template Method Pattern

**What it is**: Define the skeleton of an algorithm, letting subclasses fill in the details.

**Where we use it**: All abstract classes

```python
# In gds_database/base.py
class DatabaseConnection(ABC):
    """The TEMPLATE - defines WHAT to do"""

    @abstractmethod
    def connect(self):
        """Subclasses define HOW to connect"""
        pass

# Your implementation
class PostgresConnection(DatabaseConnection):
    """Fill in the HOW"""

    def connect(self):
        # Specific PostgreSQL connection logic
        import psycopg2
        self.conn = psycopg2.connect(
            host="localhost",
            database="mydb"
        )
```

### 2. Context Manager Pattern

**What it is**: Automatically manage resources (open/close, acquire/release)

**Where we use it**: `ResourceManager`, `AsyncResourceManager`

```python
# Using context manager (the 'with' statement)
with ResourceManager() as manager:
    # Resource is automatically initialized
    manager.do_something()
# Resource is automatically cleaned up (even if error occurs!)

# Without context manager (manual cleanup - easy to forget!)
manager = ResourceManager()
manager.initialize()
try:
    manager.do_something()
finally:
    manager.cleanup()  # Must remember to do this!
```

**How it works**:
- `__enter__()` is called when entering the `with` block
- `__exit__()` is called when leaving (even if there's an error)

### 3. Strategy Pattern (via Protocols)

**What it is**: Define a family of algorithms and make them interchangeable

**Where we use it**: `Connectable`, `Queryable` protocols

```python
# Define the strategy interface
from typing import Protocol

class Connectable(Protocol):
    def connect(self) -> Any: ...
    def disconnect(self) -> None: ...

# Now ANY class with these methods works
def connect_to_service(service: Connectable):
    if not service.is_connected():
        service.connect()
    # Works with database, API client, file handler, etc.
```

### 4. Retry Pattern with Exponential Backoff

**What it is**: Automatically retry failed operations with increasing delays

**Where we use it**: `RetryableOperation`

```python
class RetryableOperation(ABC):
    def execute_with_retry(self):
        for attempt in range(self.max_retries + 1):
            try:
                return self._execute()
            except Exception:
                # Wait longer each time: 1s, 2s, 4s, 8s, ...
                delay = self.backoff_factor ** attempt
                time.sleep(delay)
```

**Why exponential backoff?**
- Gives temporary problems time to resolve
- Reduces load on overloaded services
- Common in distributed systems

### 5. Factory Method Pattern

**What it is**: Create objects without specifying their exact class

**Where we use it**: `OperationResult.success_result()`, `OperationResult.failure_result()`

```python
# Instead of:
result = OperationResult(
    success=True,
    message="Done",
    data={"count": 5},
    error=None,
    duration_ms=0.0,
    timestamp=datetime.now()
)

# Use factory method:
result = OperationResult.success_result("Done", {"count": 5})
# Cleaner, less error-prone!
```

---

## Class Hierarchy

### Visual Hierarchy

```
ABC (Abstract Base Class)
│
├── DatabaseConnection
│   └── TransactionalConnection (extends DatabaseConnection)
│       └── (Your implementations: PostgresConnection, MySQLConnection, etc.)
│
├── AsyncDatabaseConnection
│   └── (Your async implementations)
│
├── ConfigurableComponent
│   └── (Your configurable classes)
│
├── ResourceManager
│   └── (Your resource managers)
│
├── AsyncResourceManager
│   └── (Your async resource managers)
│
├── RetryableOperation
│   └── (Your retryable operations)
│
├── ConnectionPool
│   └── (Your connection pool implementations)
│
└── PerformanceMonitored (Mixin)
    └── (Mix into any class for monitoring)

Protocols (Duck Typing)
├── Connectable
└── Queryable

Data Classes
└── OperationResult
```

### Inheritance Relationships

```python
# Simple Inheritance
class TransactionalConnection(DatabaseConnection):
    """Adds transaction methods to DatabaseConnection"""
    pass

# Multiple Inheritance (Mixin)
class MonitoredDatabase(PerformanceMonitored, DatabaseConnection):
    """Combines performance monitoring with database connection"""
    pass

# Protocol (Duck Typing)
def process(obj: Connectable):
    """Works with ANY object that has connect/disconnect methods"""
    pass
```

---

## Key Components

### 1. DatabaseConnection (Abstract Base Class)

**Purpose**: Define the standard interface for all database connections

**Core Methods**:
```python
class DatabaseConnection(ABC):
    @abstractmethod
    def connect(self) -> Any:
        """Establish connection"""

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection"""

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[Any]:
        """Execute SQL and return results"""

    @abstractmethod
    def is_connected(self) -> bool:
        """Check connection status"""

    @abstractmethod
    def get_connection_info(self) -> dict[str, Any]:
        """Get connection metadata"""
```

**Why abstract?** Different databases (PostgreSQL, MySQL, SQLite) connect differently, but all need these operations.

### 2. ConfigurableComponent

**Purpose**: Provide standard configuration management

**Key Concept**: **Configuration Validation**

```python
class ConfigurableComponent(ABC):
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.validate_config()  # Validate on creation

    @abstractmethod
    def validate_config(self) -> bool:
        """Check if configuration is valid"""
        pass

    def set_config(self, key: str, value: Any) -> None:
        """Set value and re-validate"""
        self.config[key] = value
        self.validate_config()  # Re-validate after change
```

**Pattern**: Validate early, fail fast

### 3. ResourceManager

**Purpose**: Manage resource lifecycle (creation, use, cleanup)

**Key Methods**:
```python
class ResourceManager(ABC):
    def __enter__(self) -> "ResourceManager":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        self.cleanup()
        return False  # Don't suppress exceptions
```

**Magic Methods**: `__enter__` and `__exit__` enable the `with` statement

### 4. RetryableOperation

**Purpose**: Add automatic retry logic to operations

**Algorithm**:
```
1. Try operation
2. If succeeds → return result
3. If fails → wait (exponentially longer each time)
4. Retry up to max_retries times
5. If all retries fail → raise last exception
```

**Configuration**:
- `max_retries`: How many times to retry (default: 3)
- `backoff_factor`: How much to increase delay (default: 2.0)
  - Attempt 1: wait 1 second
  - Attempt 2: wait 2 seconds
  - Attempt 3: wait 4 seconds
  - Attempt 4: wait 8 seconds

### 5. OperationResult

**Purpose**: Standardize how operations report results

**Structure**:
```python
@dataclass
class OperationResult:
    success: bool              # Did it work?
    message: str               # Human-readable message
    data: Optional[dict]       # Result data
    error: Optional[str]       # Error details (if failed)
    duration_ms: float         # How long it took
    timestamp: datetime        # When it happened
    metadata: Optional[dict]   # Extra information
```

**Why dataclass?** Automatically generates `__init__`, `__repr__`, etc.

### 6. Protocols (Connectable, Queryable)

**Purpose**: Enable duck typing with type checking

**Duck Typing**: "If it walks like a duck and quacks like a duck, it's a duck"

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Connectable(Protocol):
    def connect(self) -> Any: ...
    def disconnect(self) -> None: ...
    def is_connected(self) -> bool: ...

# Now you can check at runtime:
class MyService:
    def connect(self): return "connected"
    def disconnect(self): pass
    def is_connected(self): return True

service = MyService()
print(isinstance(service, Connectable))  # True!
```

**Benefits**:
- Type safety without inheritance
- Works with any compatible object
- Flexible and loosely coupled

---

## Extension Points

### How to Extend This Package

#### 1. Creating a Database-Specific Implementation

```python
from gds_database import DatabaseConnection

class MyDatabaseConnection(DatabaseConnection):
    """Implement all abstract methods"""

    def connect(self):
        # Your database connection code
        self._conn = my_db_library.connect(...)
        return self._conn

    def disconnect(self):
        if hasattr(self, '_conn'):
            self._conn.close()

    def execute_query(self, query, params=None):
        cursor = self._conn.cursor()
        cursor.execute(query, params or ())
        return cursor.fetchall()

    def is_connected(self):
        return hasattr(self, '_conn') and self._conn.is_open

    def get_connection_info(self):
        return {
            'database': self._conn.database_name,
            'host': self._conn.host,
            'status': 'connected' if self.is_connected() else 'disconnected'
        }
```

#### 2. Adding Transaction Support

```python
from gds_database import TransactionalConnection

class MyTransactionalDB(TransactionalConnection):
    """Extend DatabaseConnection with transactions"""

    def __init__(self):
        super().__init__()
        self._in_transaction = False

    # Implement all DatabaseConnection methods...
    # Plus transaction methods:

    def begin_transaction(self):
        self._conn.execute("BEGIN")
        self._in_transaction = True

    def commit(self):
        self._conn.execute("COMMIT")
        self._in_transaction = False

    def rollback(self):
        self._conn.execute("ROLLBACK")
        self._in_transaction = False

    def in_transaction(self):
        return self._in_transaction
```

#### 3. Adding Connection Pooling

```python
from gds_database import ConnectionPool
from queue import Queue

class MyConnectionPool(ConnectionPool):
    """Manage a pool of database connections"""

    def __init__(self, size=10):
        self._pool = Queue(maxsize=size)
        self._size = size
        # Pre-create connections
        for _ in range(size):
            self._pool.put(MyDatabaseConnection())

    def get_connection(self):
        return self._pool.get()  # Block if none available

    def release_connection(self, conn):
        self._pool.put(conn)

    def close_all(self):
        while not self._pool.empty():
            conn = self._pool.get()
            conn.disconnect()

    def get_pool_status(self):
        return {
            'size': self._size,
            'available': self._pool.qsize(),
            'in_use': self._size - self._pool.qsize()
        }
```

#### 4. Adding Performance Monitoring

```python
from gds_database import PerformanceMonitored, DatabaseConnection

class MonitoredConnection(PerformanceMonitored, DatabaseConnection):
    """Database connection with automatic timing"""

    def execute_query(self, query, params=None):
        with self._measure_time("execute_query"):
            # Your query execution code
            return self._do_query(query, params)

    # The _measure_time context manager automatically logs:
    # "execute_query took 45.23ms"
```

#### 5. Adding Async Support

```python
from gds_database import AsyncDatabaseConnection

class MyAsyncDB(AsyncDatabaseConnection):
    """Async/await database operations"""

    async def connect(self):
        self._conn = await asyncpg.connect(...)
        return self._conn

    async def disconnect(self):
        await self._conn.close()

    async def execute_query(self, query, params=None):
        return await self._conn.fetch(query, *(params or ()))

    async def is_connected(self):
        return self._conn and not self._conn.is_closed()

    def get_connection_info(self):
        return {'database': self._conn.get_dsn_parameters()}

# Usage:
async def main():
    async with MyAsyncDB() as db:
        results = await db.execute_query("SELECT * FROM users")
```

---

## SOLID Principles Applied

### S - Single Responsibility Principle
Each class has one reason to change:
- `DatabaseConnection` → Database connectivity
- `ConfigurableComponent` → Configuration management
- `RetryableOperation` → Retry logic

### O - Open/Closed Principle
Classes are open for extension, closed for modification:
- Extend `DatabaseConnection` for new databases
- Don't modify the base class

### L - Liskov Substitution Principle
Subclasses can replace parent classes:
```python
def process_data(db: DatabaseConnection):
    db.connect()
    results = db.execute_query("SELECT * FROM data")
    db.disconnect()

# Works with ANY DatabaseConnection implementation
process_data(PostgresConnection())
process_data(MySQLConnection())
process_data(SQLiteConnection())
```

### I - Interface Segregation Principle
Small, focused interfaces:
- `Connectable` → Just connection methods
- `Queryable` → Just query methods
- Don't force classes to implement methods they don't need

### D - Dependency Inversion Principle
Depend on abstractions, not concrete classes:
```python
# Good: Depends on abstract DatabaseConnection
def backup_database(db: DatabaseConnection):
    data = db.execute_query("SELECT * FROM all_tables")
    save_to_backup(data)

# Bad: Depends on specific PostgresConnection
def backup_database(db: PostgresConnection):  # Too specific!
    pass
```

---

## Best Practices

### 1. Always Validate Configuration
```python
class MyComponent(ConfigurableComponent):
    def validate_config(self):
        required = ['host', 'port', 'database']
        for key in required:
            if key not in self.config:
                raise ConfigurationError(f"Missing: {key}")

        if not isinstance(self.config['port'], int):
            raise ConfigurationError("Port must be integer")

        return True
```

### 2. Use Context Managers
```python
# Good: Automatic cleanup
with MyResourceManager() as manager:
    manager.do_work()

# Bad: Manual cleanup (can forget)
manager = MyResourceManager()
manager.initialize()
manager.do_work()
manager.cleanup()  # What if do_work() raises exception?
```

### 3. Handle Errors Gracefully
```python
def execute_query(self, query, params=None):
    try:
        return self._conn.execute(query, params)
    except DatabaseError as e:
        raise QueryError(f"Query failed: {e}")
    except Exception as e:
        raise ConnectionError(f"Connection lost: {e}")
```

### 4. Provide Clear Error Messages
```python
# Bad
raise ValueError("Invalid config")

# Good
raise ConfigurationError(
    f"Invalid configuration: missing required key 'host'. "
    f"Provided keys: {list(self.config.keys())}"
)
```

### 5. Document with Examples
```python
def execute_query(self, query: str, params: Optional[tuple] = None):
    """
    Execute a SQL query.

    Args:
        query: SQL query string
        params: Optional query parameters

    Returns:
        List of result rows

    Example:
        >>> db = MyDatabase()
        >>> results = db.execute_query(
        ...     "SELECT * FROM users WHERE age > ?",
        ...     (18,)
        ... )
        >>> print(results)
        [{'name': 'Alice', 'age': 25}, ...]
    """
```

---

## Summary

The `gds_database` architecture provides:

✅ **Reusable patterns** for common database operations
✅ **Type-safe interfaces** with full type hints
✅ **Extensible design** following SOLID principles
✅ **Modern Python features** (async, protocols, dataclasses)
✅ **Production-ready patterns** (retry, pooling, monitoring)

**Next Steps**:
- Read [BUILD_GUIDE.md](BUILD_GUIDE.md) to learn how to install and build
- Read [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) to learn how to contribute
- Study the [test files](../tests/) to see usage examples
