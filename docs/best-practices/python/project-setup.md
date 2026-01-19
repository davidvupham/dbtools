# Project Setup

This guide covers creating new Python packages in the repository.

## Creating a New Package

### Step 1: Create Directory Structure

```bash
# From repository root
mkdir -p python/gds_newpackage/{src/gds_newpackage,tests}

# Create required files
touch python/gds_newpackage/src/gds_newpackage/__init__.py
touch python/gds_newpackage/src/gds_newpackage/py.typed
touch python/gds_newpackage/tests/__init__.py
touch python/gds_newpackage/tests/conftest.py
touch python/gds_newpackage/README.md
```

### Step 2: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gds-newpackage"
version = "1.0.0"
description = "Brief description of what this package does"
readme = "README.md"
license = "MIT"
authors = [
    {name = "GDS Team", email = "gds-team@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.9"
dependencies = []

[project.urls]
Homepage = "https://github.com/davidvupham/dbtools"
Repository = "https://github.com/davidvupham/dbtools"
Documentation = "https://github.com/davidvupham/dbtools/tree/main/python/gds_newpackage"

[tool.setuptools.packages.find]
where = ["src"]
include = ["gds_newpackage*"]

[tool.setuptools.package-data]
gds_newpackage = ["py.typed"]
```

### Step 3: Add Workspace Dependencies (If Needed)

If your package depends on other workspace packages:

```toml
[project]
dependencies = [
    "gds-database>=1.0.0",
]

[tool.uv.sources]
gds-database = { workspace = true }
```

### Step 4: Update Root pyproject.toml

The workspace glob `python/gds_*` should automatically include your package. Verify:

```bash
# Check workspace members
uv sync --dry-run
```

### Step 5: Create __init__.py

Define your public API explicitly:

```python
"""GDS New Package - Brief description.

This package provides:
- Feature 1
- Feature 2
"""

from .core import MainClass
from .utils import helper_function
from .exceptions import PackageError

__all__ = ["MainClass", "helper_function", "PackageError"]
__version__ = "1.0.0"
```

### Step 6: Verify Setup

```bash
# Sync dependencies
uv sync

# Verify import works
python -c "import gds_newpackage; print(gds_newpackage.__version__)"

# Run linter
make lint

# Run tests (should pass with no tests yet)
pytest python/gds_newpackage/tests/ -v
```

---

## Package Templates

### Library Package

For reusable code without external service dependencies:

```
python/gds_utils/
├── pyproject.toml
├── README.md
├── src/
│   └── gds_utils/
│       ├── __init__.py
│       ├── py.typed
│       ├── strings.py
│       └── dates.py
└── tests/
    ├── conftest.py
    ├── test_strings.py
    └── test_dates.py
```

### Service Client Package

For packages that interact with external services:

```
python/gds_vault/
├── pyproject.toml
├── README.md
├── src/
│   └── gds_vault/
│       ├── __init__.py
│       ├── py.typed
│       ├── client.py           # Main client class
│       ├── async_client.py     # Async variant
│       ├── auth.py             # Authentication strategies
│       ├── cache.py            # Response caching
│       ├── base.py             # Abstract base classes
│       └── exceptions.py       # Custom exceptions
└── tests/
    ├── conftest.py
    ├── test_client.py
    └── test_auth.py
```

### Abstract Interface Package

For defining interfaces that other packages implement:

```
python/gds_database/
├── pyproject.toml
├── README.md
├── src/
│   └── gds_database/
│       ├── __init__.py
│       ├── py.typed
│       ├── base.py             # Abstract base classes
│       ├── engine.py           # Connection engine interface
│       └── metadata.py         # Schema metadata interface
└── tests/
    ├── conftest.py
    └── test_base.py
```

### Implementation Package

For concrete implementations of abstract interfaces:

```
python/gds_postgres/
├── pyproject.toml              # Depends on gds-database
├── README.md
├── src/
│   └── gds_postgres/
│       ├── __init__.py
│       ├── py.typed
│       ├── connection.py       # PostgreSQL connection
│       └── engine.py           # PostgreSQL engine
└── tests/
    ├── conftest.py
    └── test_connection.py
```

---

## Required Files

### README.md Template

```markdown
# gds-newpackage

Brief description of what this package does.

## Installation

```bash
# Within the monorepo
uv sync

# Or install directly
pip install -e python/gds_newpackage
```

## Usage

```python
from gds_newpackage import MainClass

client = MainClass()
result = client.do_something()
```

## Development

```bash
# Run tests
pytest python/gds_newpackage/tests/ -v

# Run linter
ruff check python/gds_newpackage/
```

## API Reference

### MainClass

Description of the main class.

### helper_function

Description of helper function.
```

### conftest.py Template

```python
"""Pytest configuration and fixtures for gds_newpackage tests."""

import pytest


@pytest.fixture
def sample_config():
    """Provide sample configuration for tests."""
    return {
        "host": "localhost",
        "port": 8080,
    }


@pytest.fixture
def mock_client(sample_config):
    """Provide a configured mock client."""
    from gds_newpackage import MainClass
    return MainClass(**sample_config)
```

### py.typed

This file should be empty. Its presence signals that the package includes type hints (PEP 561).

```bash
touch src/gds_newpackage/py.typed
```

---

## Executable Packages

If your package should be runnable with `python -m gds_package`:

### Add __main__.py

```python
"""Entry point for python -m gds_newpackage."""

from .cli import main

if __name__ == "__main__":
    main()
```

### Add CLI Module

```python
"""Command-line interface for gds_newpackage."""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="gds-newpackage",
        description="Description of what the CLI does",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("--config", help="Path to configuration file")

    args = parser.parse_args(argv)

    # Implementation
    print(f"Running with config: {args.config}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Add Entry Point (Optional)

For installing as a command:

```toml
[project.scripts]
gds-newpackage = "gds_newpackage.cli:main"
```

---

## Validation Checklist

Before committing a new package:

```bash
# 1. Sync and verify no errors
uv sync

# 2. Import test
python -c "import gds_newpackage"

# 3. Lint passes
ruff check python/gds_newpackage/

# 4. Tests pass
pytest python/gds_newpackage/tests/ -v

# 5. Type check passes (if using types)
pyright python/gds_newpackage/src/
```

---

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'gds_newpackage'`

**Solution**: Ensure the package is in the workspace and synced:
```bash
uv sync
python -c "import gds_newpackage"
```

### Workspace Not Recognized

**Problem**: Package not included in `uv sync`

**Solution**: Check that directory matches workspace glob in root `pyproject.toml`:
```toml
[tool.uv.workspace]
members = ["python/gds_*"]  # Must match python/gds_newpackage
```

### Circular Import

**Problem**: `ImportError: cannot import name 'X' from partially initialized module`

**Solution**:
1. Move shared types to a `base.py` or `types.py` module
2. Use `TYPE_CHECKING` for type-only imports
3. Use lazy imports inside functions

See [Modules and Packages](../../courses/python/module_2_intermediate/13_modules_packages.md#avoid-circular-imports) for detailed solutions.
