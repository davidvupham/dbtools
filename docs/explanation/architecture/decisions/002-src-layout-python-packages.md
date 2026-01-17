# ADR-002: Use src layout for Python packages

## Status

Accepted

## Context

Python packages can be organized in two primary layouts:

**Flat layout:**
```
gds_database/
├── gds_database/
│   └── __init__.py
├── tests/
└── pyproject.toml
```

**Src layout:**
```
gds_database/
├── src/
│   └── gds_database/
│       └── __init__.py
├── tests/
└── pyproject.toml
```

The choice affects import behavior during development and testing.

## Decision

We use the **src layout** for all Python packages in this repository.

Directory structure:
```
python/gds_database/
├── src/
│   └── gds_database/
│       ├── __init__.py
│       └── [modules].py
├── tests/
│   ├── conftest.py
│   └── test_*.py
└── pyproject.toml
```

## Consequences

### Benefits

- **Prevents accidental imports**: The package must be installed to be imported; you cannot accidentally import from the local directory
- **Tests match production**: Tests run against the installed package, not source files, catching packaging issues early
- **Clear separation**: Source code, tests, and configuration are clearly separated
- **Industry standard**: Recommended by the Python Packaging Authority (PyPA)

### Trade-offs

- **Slightly deeper nesting**: One extra directory level
- **Must install to test**: Requires `pip install -e .` or `uv sync` before running tests

### Configuration

In `pyproject.toml`:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```

Or with UV:
```toml
[project]
name = "gds-database"

[tool.uv]
package = true
```
