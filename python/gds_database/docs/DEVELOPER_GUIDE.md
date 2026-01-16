# GDS Database Developer Guide

## Overview

Welcome to the `gds_database` developer guide! This guide will help you understand how to contribute to the project, write clean code, and follow best practices. Whether you're new to Python or experienced, this guide provides everything you need to become a productive contributor.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Code Organization](#code-organization)
3. [Writing New Classes](#writing-new-classes)
4. [Testing Guidelines](#testing-guidelines)
5. [Documentation Standards](#documentation-standards)
6. [Code Style](#code-style)
7. [Type Hints](#type-hints)
8. [Common Patterns](#common-patterns)
9. [Contributing](#contributing)
10. [Advanced Topics](#advanced-topics)

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. Read [BUILD_GUIDE.md](BUILD_GUIDE.md) and set up your development environment
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
3. Familiarity with Python basics (classes, functions, decorators)
4. Basic understanding of Git and GitHub

### Your First Contribution

Start with something small:

1. **Fix a typo** in documentation
2. **Add a test** for existing code
3. **Improve a docstring** with better examples
4. **Add type hints** where missing

---

## Code Organization

### File Structure

```
gds_database/
├── gds_database/
│   ├── __init__.py        # Package exports (what users import)
│   └── base.py            # Core abstract classes
├── tests/
│   ├── __init__.py
│   └── test_base.py       # Tests for base.py
├── docs/
│   ├── ARCHITECTURE.md    # Design documentation
│   ├── BUILD_GUIDE.md     # Build instructions
│   └── DEVELOPER_GUIDE.md # This file
├── pyproject.toml         # Package metadata and configuration
├── setup.py               # Installation script (setuptools)
└── README.md              # User-facing documentation
```

### When to Create New Files

**Keep in base.py:**
- Core abstract classes
- Fundamental utilities
- Classes that all implementations need

**Create new files for:**
- Database-specific implementations (e.g., `postgres.py`)
- Optional features (e.g., `monitoring.py`)
- Utilities that aren't core (e.g., `helpers.py`)

**Example future structure:**
```
gds_database/
├── base.py           # Core abstractions
├── monitoring.py     # Performance monitoring
├── pooling.py        # Connection pooling implementations
└── testing.py        # Testing utilities
```

---

## Writing New Classes

### Step-by-Step: Creating an Abstract Base Class

#### Step 1: Define the Class

```python
from abc import ABC, abstractmethod
from typing import Any, Optional

class MyNewComponent(ABC):
    """
    Brief one-line description.

    Longer description explaining:
    - What this class does
    - When to use it
    - What subclasses must implement

    Example:
        class MyImpl(MyNewComponent):
            def my_method(self):
                return "Hello!"
    """
```

**Key points:**
- Inherit from `ABC` for abstract classes
- Start with a clear docstring
- Include usage example

#### Step 2: Add Abstract Methods

```python
class MyNewComponent(ABC):
    @abstractmethod
    def required_method(self, param: str) -> int:
        """
        Description of what this method should do.

        Args:
            param: What this parameter means

        Returns:
            What this method returns

        Raises:
            ValueError: When this error occurs

        Example:
            >>> obj.required_method("test")
            42
        """
        pass  # No implementation in abstract class
```

**Key points:**
- Use `@abstractmethod` decorator
- Provide complete type hints
- Document parameters, returns, and exceptions
- Include usage example

#### Step 3: Add Concrete Methods (Optional)

```python
class MyNewComponent(ABC):
    def helper_method(self, data: dict[str, Any]) -> str:
        """
        Helper method that subclasses can use.

        This is NOT abstract - it has a default implementation.
        Subclasses can override it if needed.
        """
        return f"Processing: {data}"
```

#### Step 4: Export in `__init__.py`

```python
# In gds_database/__init__.py
from .base import (
    # ... existing exports ...
    MyNewComponent,  # Add your new class
)

__all__ = [
    # ... existing exports ...
    "MyNewComponent",  # Add to __all__
]
```

### Step-by-Step: Creating a Concrete Implementation

#### Example: Implementing DatabaseConnection

```python
from gds_database import DatabaseConnection, QueryError, DatabaseConnectionError
import sqlite3
from typing import Any, Optional

class SQLiteConnection(DatabaseConnection):
    """
    SQLite database connection implementation.

    This provides a concrete implementation of DatabaseConnection
    for SQLite databases.

    Attributes:
        database_path: Path to SQLite database file
        _connection: Internal SQLite connection object

    Example:
        >>> db = SQLiteConnection('mydb.sqlite')
        >>> db.connect()
        >>> results = db.execute_query('SELECT * FROM users')
        >>> db.disconnect()
    """

    def __init__(self, database_path: str):
        """
        Initialize SQLite connection.

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to SQLite database.

        Returns:
            SQLite connection object

        Raises:
            DatabaseConnectionError: If connection fails
        """
        try:
            self._connection = sqlite3.connect(self.database_path)
            self._connection.row_factory = sqlite3.Row  # Return rows as dicts
            return self._connection
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Failed to connect: {e}")

    def disconnect(self) -> None:
        """Close SQLite connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute_query(
        self,
        query: str,
        params: Optional[tuple[Any, ...]] = None
    ) -> list[Any]:
        """
        Execute SQL query against SQLite database.

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            QueryError: If query execution fails
            DatabaseConnectionError: If not connected
        """
        if not self.is_connected():
            raise DatabaseConnectionError("Not connected to database")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())

            # Convert rows to dictionaries
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise QueryError(f"Query failed: {e}")

    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._connection is not None

    def get_connection_info(self) -> dict[str, Any]:
        """Get connection metadata."""
        return {
            'database': self.database_path,
            'type': 'sqlite',
            'connected': self.is_connected(),
        }
```

**Key implementation points:**

1. **Constructor**: Store necessary configuration
2. **Private attributes**: Use `_` prefix (e.g., `_connection`)
3. **Error handling**: Convert library-specific errors to our exceptions
4. **Type hints**: Complete annotations for all parameters/returns
5. **Docstrings**: Document behavior, not just signature

---

## Testing Guidelines

### Test Organization

Each source file should have a corresponding test file:

```
gds_database/base.py  →  tests/test_base.py
gds_database/pooling.py  →  tests/test_pooling.py
```

### Writing Test Classes

```python
import unittest
from gds_database import MyNewComponent

class TestMyNewComponent(unittest.TestCase):
    """Tests for MyNewComponent class."""

    def setUp(self):
        """Run before each test method."""
        self.component = ConcreteImplementation()

    def tearDown(self):
        """Run after each test method."""
        # Clean up resources if needed
        pass

    def test_something_works(self):
        """Test that something works correctly."""
        result = self.component.do_something()
        self.assertEqual(result, expected_value)

    def test_error_handling(self):
        """Test that errors are handled properly."""
        with self.assertRaises(ValueError):
            self.component.do_invalid_thing()
```

### Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected_result>

def test_execute_query_valid_sql_returns_results(self):
    """Test that valid SQL returns correct results."""
    pass

def test_execute_query_invalid_sql_raises_error(self):
    """Test that invalid SQL raises QueryError."""
    pass

def test_connect_with_valid_credentials_succeeds(self):
    """Test successful connection with valid credentials."""
    pass

def test_connect_with_invalid_credentials_raises_error(self):
    """Test that invalid credentials raise ConnectionError."""
    pass
```

### Testing Abstract Methods

Use `super()` to call and cover abstract method bodies:

```python
def test_abstract_method_bodies_via_super(self):
    """Test that abstract method bodies can be called via super()."""
    class TestImpl(DatabaseConnection):
        def connect(self):
            super().connect()  # Cover the abstract method's pass statement
            return "connected"

        def disconnect(self):
            super().disconnect()  # Cover abstract method

        # ... implement other methods ...

    impl = TestImpl()
    impl.connect()
    impl.disconnect()
```

### Testing Exceptions

```python
def test_query_error_raised(self):
    """Test that QueryError is raised on query failure."""
    db = BrokenConnection()

    with self.assertRaises(QueryError) as context:
        db.execute_query("INVALID SQL")

    # Check error message
    self.assertIn("Query failed", str(context.exception))
```

### Testing Async Code

```python
import asyncio
import unittest

class TestAsyncComponent(unittest.TestCase):
    """Tests for async components."""

    def test_async_operation(self):
        """Test async operation."""
        async def run_test():
            component = AsyncComponent()
            result = await component.async_method()
            self.assertEqual(result, expected)

        asyncio.run(run_test())
```

### Coverage Best Practices

**Goal: 100% coverage**

```bash
# Run tests with coverage
pytest tests/ --cov=gds_database --cov-report=term-missing

# Check HTML report
pytest tests/ --cov=gds_database --cov-report=html
open htmlcov/index.html
```

**For unreachable defensive code:**
```python
if last_exception:
    raise last_exception
# This line should never execute in normal operation
raise RuntimeError("Impossible condition")  # pragma: no cover
```

---

## Documentation Standards

### Docstring Format

We use **Google-style docstrings**:

```python
def function_name(param1: int, param2: str) -> bool:
    """
    Brief one-line description.

    Longer description that explains:
    - What the function does
    - Important behavior
    - Side effects

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When this error occurs
        TypeError: When this error occurs

    Example:
        >>> function_name(42, "hello")
        True

    Note:
        Any important notes or warnings
    """
    pass
```

### Class Docstrings

```python
class ClassName:
    """
    Brief description of the class.

    Longer description explaining:
    - What the class represents
    - When to use it
    - How it fits into the larger system

    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2

    Example:
        >>> obj = ClassName()
        >>> obj.method()
        'result'

    Note:
        Important information about usage
    """
```

### Module Docstrings

```python
"""
Module name - Brief description.

This module provides:
- Feature 1
- Feature 2
- Feature 3

Example:
    >>> from module import ClassName
    >>> obj = ClassName()
"""
```

### README Updates

When adding new features, update README.md:

```markdown
## New Feature

Brief description of what it does.

### Usage

\```python
from gds_database import NewFeature

# Example code
feature = NewFeature()
feature.do_something()
\```

### API Reference

- `method1(arg)`: Description
- `method2(arg)`: Description
```

---

## Code Style

### PEP 8 Compliance

Follow [PEP 8](https://peps.python.org/pep-0008/) Python style guide:

```python
# Good
def calculate_total(items: list[int]) -> int:
    """Calculate total of items."""
    return sum(items)

# Bad
def calculateTotal(items):  # Wrong naming
    return sum(items)  # Missing docstring, type hints
```

### Line Length

Maximum **120 characters** (configured in `pyproject.toml`):

```python
# Good
result = database.execute_query(
    "SELECT * FROM users WHERE age > ?",
    (18,)
)

# Bad - too long
result = database.execute_query("SELECT * FROM users WHERE age > ? AND status = ? AND country = ?", (18, 'active', 'USA'))
```

### Import Organization

```python
# 1. Standard library
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

# 2. Third-party packages
import numpy as np
import pandas as pd

# 3. Local imports
from .base import DatabaseConnection
from .exceptions import QueryError
```

Use `ruff` to automatically organize imports:
```bash
ruff check --fix gds_database/
```

### Naming Conventions

```python
# Classes: PascalCase
class DatabaseConnection:
    pass

# Functions/methods: snake_case
def execute_query():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private attributes: _leading_underscore
class MyClass:
    def __init__(self):
        self._private_attr = "value"

# "Protected" (internal): _single_leading_underscore
def _internal_helper():
    pass

# "Very private" (name mangling): __double_leading_underscore
class MyClass:
    def __init__(self):
        self.__very_private = "value"
```

### String Formatting

Prefer **f-strings** (Python 3.6+):

```python
# Good
message = f"User {username} logged in at {timestamp}"

# Acceptable
message = "User {} logged in at {}".format(username, timestamp)

# Avoid
message = "User " + username + " logged in at " + str(timestamp)
```

---

## Type Hints

### Why Type Hints?

```python
# Without type hints - unclear what types are expected
def process_data(data, config):
    return data * config['multiplier']

# With type hints - crystal clear
def process_data(data: list[int], config: dict[str, int]) -> list[int]:
    return [x * config['multiplier'] for x in data]
```

### Basic Types

```python
from typing import Any, Optional, Union

# Built-in types
def func(
    number: int,
    text: str,
    flag: bool,
    ratio: float,
) -> None:
    pass

# Collections
def func(
    items: list[str],              # List of strings
    mapping: dict[str, int],       # Dict with str keys, int values
    unique: set[int],              # Set of integers
    coords: tuple[float, float],   # Tuple of exactly 2 floats
) -> list[dict[str, Any]]:        # List of dicts
    pass

# Optional (can be None)
def func(value: Optional[int] = None) -> Optional[str]:
    if value is None:
        return None
    return str(value)

# Union (multiple possible types)
def func(value: Union[int, str]) -> Union[int, str]:
    return value
```

### Advanced Types

```python
from typing import Callable, Protocol, TypeVar, Generic

# Callable (functions as arguments)
def apply_func(
    func: Callable[[int], str],  # Takes int, returns str
    value: int
) -> str:
    return func(value)

# Protocol (structural typing)
class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()  # Works with ANY object that has draw()

# Generic types
T = TypeVar('T')

def first(items: list[T]) -> T:
    return items[0]

# Self-referential types
class Node:
    def __init__(self, value: int, next: Optional['Node'] = None):
        self.value = value
        self.next = next
```

### Type Checking

```bash
# Check types with mypy
mypy gds_database/

# Strict mode (recommended)
mypy --strict gds_database/
```

**Common mypy errors:**

```python
# Error: Missing return type
def func(x):  # ❌
    return x * 2

def func(x: int) -> int:  # ✅
    return x * 2

# Error: Incompatible types
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")  # ❌ mypy error

# Error: Optional not handled
def get_user(id: int) -> Optional[str]:
    if id > 0:
        return "user"
    return None

user = get_user(1)
print(user.upper())  # ❌ user might be None!

# Fix:
user = get_user(1)
if user is not None:
    print(user.upper())  # ✅
```

---

## Common Patterns

### 1. Context Manager Implementation

```python
from typing import Literal

class MyResource(ResourceManager):
    def __enter__(self) -> "MyResource":
        """Called when entering 'with' block."""
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> Literal[False]:
        """Called when exiting 'with' block."""
        self.cleanup()
        return False  # Don't suppress exceptions
```

### 2. Property Decorators

```python
class Connection:
    def __init__(self):
        self._connected = False

    @property
    def connected(self) -> bool:
        """Read-only property."""
        return self._connected

    @property
    def status(self) -> str:
        """Computed property."""
        return "connected" if self._connected else "disconnected"

    @property
    def timeout(self) -> int:
        """Property with getter and setter."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        if value < 0:
            raise ValueError("Timeout must be positive")
        self._timeout = value

# Usage
conn = Connection()
print(conn.connected)  # Access like attribute
conn.timeout = 30      # Set with validation
```

### 3. Dataclass Pattern

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Result:
    """Result with automatic __init__, __repr__, etc."""
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def is_success(self) -> bool:
        return self.success

# Usage
result = Result(True, "Done")  # Auto-generated __init__
print(result)  # Auto-generated __repr__
```

### 4. Singleton Pattern

```python
class DatabasePool:
    """Only one pool instance should exist."""
    _instance: Optional['DatabasePool'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connections = []
            self.initialized = True

# Usage
pool1 = DatabasePool()
pool2 = DatabasePool()
print(pool1 is pool2)  # True - same instance!
```

### 5. Factory Pattern

```python
class ConnectionFactory:
    """Create connections based on configuration."""

    @staticmethod
    def create(db_type: str, **kwargs) -> DatabaseConnection:
        if db_type == "postgres":
            return PostgresConnection(**kwargs)
        elif db_type == "mysql":
            return MySQLConnection(**kwargs)
        elif db_type == "sqlite":
            return SQLiteConnection(**kwargs)
        else:
            raise ValueError(f"Unknown database type: {db_type}")

# Usage
db = ConnectionFactory.create("postgres", host="localhost")
```

---

## Contributing

### Git Workflow

#### 1. Fork and Clone

```bash
# Fork on GitHub (click Fork button)

# Clone your fork
git clone https://github.com/YOUR_USERNAME/dbtools.git
cd dbtools/gds_database

# Add upstream remote
git remote add upstream https://github.com/davidvupham/dbtools.git
```

#### 2. Create Feature Branch

```bash
# Update main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

#### 3. Make Changes

```bash
# Edit files
vim gds_database/new_feature.py

# Add tests
vim tests/test_new_feature.py

# Run tests
pytest tests/ -v

# Check code quality
ruff check gds_database/ tests/
mypy gds_database/
```

#### 4. Commit Changes

```bash
# Stage changes
git add gds_database/new_feature.py tests/test_new_feature.py

# Commit with descriptive message
git commit -m "feat: Add new feature for X

- Implement X functionality
- Add tests for X
- Update documentation"
```

**Commit message format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

#### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Go to https://github.com/davidvupham/dbtools
# Click "New Pull Request"
```

### Pull Request Checklist

Before submitting:

- [ ] Tests pass locally (`pytest tests/`)
- [ ] Code is linted (`ruff check gds_database/ tests/`)
- [ ] Types are checked (`mypy gds_database/`)
- [ ] Coverage is 100% (`pytest tests/ --cov`)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Code Review Process

1. **Automated checks** run on PR (CI/CD)
2. **Maintainer reviews** code
3. **Requested changes** addressed
4. **Approval** granted
5. **Merge** to main branch

---

## Advanced Topics

### Async Programming

```python
import asyncio
from typing import Any

class AsyncDatabaseConnection(ABC):
    """Async database operations."""

    @abstractmethod
    async def connect(self) -> Any:
        """Async connection."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        params: Optional[tuple[Any, ...]] = None
    ) -> list[Any]:
        """Async query execution."""
        pass

# Implementation
class AsyncPostgres(AsyncDatabaseConnection):
    async def connect(self):
        import asyncpg
        self.conn = await asyncpg.connect(...)
        return self.conn

    async def execute_query(self, query, params=None):
        return await self.conn.fetch(query, *(params or ()))

# Usage
async def main():
    async with AsyncPostgres() as db:
        results = await db.execute_query("SELECT * FROM users")
        print(results)

asyncio.run(main())
```

### Performance Optimization

```python
import time
from functools import lru_cache

# Caching
@lru_cache(maxsize=128)
def expensive_operation(key: str) -> dict:
    """Cache results for repeated calls."""
    # Expensive computation
    time.sleep(1)
    return {"result": key}

# Profiling
import cProfile

def profile_code():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    for i in range(1000):
        expensive_operation(str(i % 10))

    profiler.disable()
    profiler.print_stats(sort='cumulative')

# Memory usage
import tracemalloc

tracemalloc.start()
# Your code
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f}MB")
print(f"Peak: {peak / 1024 / 1024:.2f}MB")
tracemalloc.stop()
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MonitoredConnection(DatabaseConnection):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_query(self, query, params=None):
        self.logger.info(f"Executing query: {query}")
        try:
            result = self._do_query(query, params)
            self.logger.info(f"Query returned {len(result)} rows")
            return result
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise
```

### Testing with Mocks

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    # Create mock
    mock_conn = Mock(spec=DatabaseConnection)
    mock_conn.execute_query.return_value = [{"id": 1}]

    # Use mock
    result = mock_conn.execute_query("SELECT * FROM users")
    assert result == [{"id": 1}]

    # Verify call
    mock_conn.execute_query.assert_called_once_with("SELECT * FROM users")

def test_with_patch():
    # Patch external dependency
    with patch('sqlite3.connect') as mock_connect:
        mock_connect.return_value = MagicMock()

        db = SQLiteConnection('test.db')
        db.connect()

        # Verify connect was called
        mock_connect.assert_called_once_with('test.db')
```

---

## Summary

You now know:

✅ How to organize code
✅ How to write new classes
✅ How to write comprehensive tests
✅ How to document code properly
✅ How to follow code style guidelines
✅ How to use type hints effectively
✅ Common patterns and practices
✅ How to contribute to the project

**Resources:**
- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [Testing with pytest](https://docs.pytest.org/)

**Happy coding!** 🚀
