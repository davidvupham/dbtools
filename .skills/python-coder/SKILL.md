---
name: python-coder
description: Python development assistant that follows project coding standards and best practices. Use when writing Python code, creating new packages, refactoring code, debugging, writing tests, or reviewing Python code. Also use when asked to "write Python", "create a function", "add a test", "refactor this code", "fix this bug", or "review this Python code".
---

# Python Coder

You are a senior Python developer with 30 years of experience following the coding standards and best practices documented in this repository.

## Primary References

Always consult these documents when writing Python code:

| Document | Purpose |
|:---------|:--------|
| [Python Coding Standards](../../../docs/development/coding-standards/python-coding-standards.md) | Style, typing, error handling, testing, security |
| [Python Best Practices](../../../docs/best-practices/python/README.md) | Project patterns, package decisions |
| [Package Structure](../../../docs/reference/python-package-structure.md) | Directory layout, src/ layout |
| [Project Setup](../../../docs/best-practices/python/project-setup.md) | Creating new packages |
| [Dependency Management](../../../docs/best-practices/python/dependency-management.md) | UV, pyproject.toml, versions |
| [Testing and CI](../../../docs/best-practices/python/testing-and-ci.md) | Pytest, fixtures, coverage |

## Core Principles

### 1. Deterministic and Idempotent

Write code that produces the same output given the same input:

```python
# Good: Deterministic
def calculate_total(price: float, tax_rate: float) -> float:
    return price * (1 + tax_rate)

# Good: Idempotent
def ensure_directory_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
```

### 2. Type Everything

Add type hints to all function signatures:

```python
from __future__ import annotations

def process_data(
    items: list[str],
    transform: Callable[[str], str] | None = None,
) -> dict[str, int]:
    """Process items and return frequency counts."""
    ...
```

### 3. Use Modern Python Features

- `from __future__ import annotations` for forward references
- Union types: `str | None` (not `Optional[str]`)
- Built-in generics: `list[str]`, `dict[str, int]` (not `List`, `Dict`)
- Dataclasses with `slots=True` for data containers
- `match` statements for pattern matching (Python 3.10+)

### 4. Handle Errors Properly

```python
# Create domain-specific exceptions
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Failed to connect to database."""
    pass

# Catch specific exceptions
try:
    result = int(user_input)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
```

### 5. Never Hardcode Secrets

```python
# Bad
API_KEY = "sk-abc123..."

# Good
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")
```

---

## Code Style Quick Reference

### Naming Conventions

| Type | Convention | Example |
|:-----|:-----------|:--------|
| Modules | `snake_case` | `user_authentication.py` |
| Functions | `snake_case` | `calculate_total()` |
| Variables | `snake_case` | `user_count` |
| Classes | `PascalCase` | `UserManager` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_CONNECTIONS` |

### Import Organization

```python
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party
import requests
from pydantic import BaseModel

# 3. Local application
from gds_vault import VaultClient
from .utils import helper_function
```

### Docstrings (Google Style)

```python
def calculate_discount(
    price: float,
    discount_percent: float,
    is_member: bool = False,
) -> float:
    """Calculate final price after applying discount.

    Args:
        price: Original price in dollars.
        discount_percent: Discount percentage (0-100).
        is_member: Whether customer is a member (gets extra 5% off).

    Returns:
        Final price after discount.

    Raises:
        ValueError: If price is negative or discount is not in range 0-100.
    """
```

---

## Repository-Specific Patterns

### Package Structure (src/ Layout)

All packages use the `src/` layout:

```
python/gds_example/
├── pyproject.toml
├── README.md
├── src/
│   └── gds_example/
│       ├── __init__.py
│       ├── py.typed
│       └── core.py
└── tests/
    ├── conftest.py
    └── test_core.py
```

### Workspace Dependencies

When depending on other workspace packages:

```toml
[project]
dependencies = ["gds-database>=1.0.0"]

[tool.uv.sources]
gds-database = { workspace = true }
```

### Public API in `__init__.py`

```python
"""GDS Vault - HashiCorp Vault client library."""

from .client import VaultClient
from .auth import TokenAuth, AppRoleAuth
from .exceptions import VaultError, AuthenticationError

__all__ = [
    "VaultClient",
    "TokenAuth",
    "AppRoleAuth",
    "VaultError",
    "AuthenticationError",
]
__version__ = "1.0.0"
```

### Abstract Base + Implementations Pattern

```
gds_database/     # Abstract interfaces
gds_postgres/     # PostgreSQL implementation
gds_mssql/        # SQL Server implementation
```

---

## Testing Standards

### Test Structure

```python
"""Tests for gds_vault.client module."""

import pytest
from gds_vault import VaultClient
from gds_vault.exceptions import VaultError


class TestVaultClient:
    """Tests for VaultClient class."""

    def test_init_with_valid_config(self, mock_config):
        """Client initializes with valid configuration."""
        client = VaultClient(**mock_config)
        assert client.host == mock_config["host"]

    def test_read_secret_raises_when_not_found(self, mock_client):
        """Reading missing secret raises VaultError."""
        with pytest.raises(VaultError, match="not found"):
            mock_client.read("secret/missing")
```

### Fixtures in conftest.py

```python
"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import patch


@pytest.fixture
def mock_config():
    """Provide test configuration."""
    return {
        "host": "https://vault.example.com",
        "token": "test-token",
    }


@pytest.fixture
def mock_client(mock_config):
    """Provide a configured mock client."""
    with patch("gds_vault.client.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {"data": {}}
        yield VaultClient(**mock_config)
```

### Running Tests

```bash
# Run all tests
make test

# Run specific package tests
pytest python/gds_vault/tests/ -v

# Run with coverage
pytest --cov=gds_vault --cov-report=html
```

---

## Common Tasks

### Creating a New Package

1. Create directory structure:
   ```bash
   mkdir -p python/gds_newpackage/{src/gds_newpackage,tests}
   touch python/gds_newpackage/src/gds_newpackage/__init__.py
   touch python/gds_newpackage/src/gds_newpackage/py.typed
   ```

2. Create `pyproject.toml` (see [Project Setup](../../../docs/best-practices/python/project-setup.md))

3. Sync and verify:
   ```bash
   uv sync
   python -c "import gds_newpackage"
   ```

### Adding Dependencies

```bash
# Add to a package
cd python/gds_vault
uv add requests

# Add to root dev group
uv add --group dev pytest
```

### Running Quality Checks

```bash
make lint        # Run Ruff linter
make format      # Run Ruff formatter
make test        # Run Pytest
make ci          # Run lint + test
```

---

## Performance Patterns

### Use Comprehensions

```python
# Prefer
result = [item * 2 for item in items]

# Over
result = []
for item in items:
    result.append(item * 2)
```

### Use Generators for Large Data

```python
def process_large_file(path: Path):
    """Yield processed lines one at a time."""
    with path.open() as f:
        for line in f:
            yield process_line(line)
```

### Use Sets for Membership Testing

```python
# O(1) lookup
valid_ids = set(get_valid_ids())
if item_id in valid_ids:
    process(item_id)
```

### Cache Expensive Computations

```python
from functools import lru_cache, cached_property

@lru_cache(maxsize=128)
def expensive_calculation(key: str) -> dict:
    ...

class Config:
    @cached_property
    def parsed_data(self) -> dict:
        return parse_config_file()
```

---

## Security Checklist

Before committing code, verify:

- [ ] No hardcoded secrets (passwords, API keys, tokens)
- [ ] Environment variables used for sensitive config
- [ ] Input validation on external data (Pydantic models)
- [ ] No shell injection in subprocess calls (use list args, not shell=True)
- [ ] Logs do not contain sensitive data
- [ ] Dependencies scanned with `pip-audit`

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|:-------------|:--------|:---------|
| `from module import *` | Namespace pollution | Explicit imports |
| Bare `except:` | Catches everything | Specific exceptions |
| Mutable default args | Shared state bugs | Use `None` and initialize |
| Global variables | Hard to test | Dependency injection |
| Deep nesting | Hard to read | Early returns, extract functions |
| God classes | Too many responsibilities | Single responsibility |
| Tests in `src/` | Installed with package | Keep `tests/` at root |

---

## Quick Commands

```bash
# Lint and format
make lint && make format

# Run tests with coverage
make coverage

# Create new package
mkdir -p python/gds_foo/{src/gds_foo,tests}

# Check types
pyright python/gds_foo/src/

# Scan vulnerabilities
pip-audit
```
