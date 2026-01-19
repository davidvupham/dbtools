# Python Packages

This directory contains all Python packages (`gds_*`) in the UV workspace.

## Before You Start

**Creating a new package?** Read these first:
- `docs/best-practices/python/README.md` - Checklist and decision framework
- `docs/best-practices/python/project-setup.md` - Directory structure and templates
- `docs/reference/python-package-structure.md` - src-layout specification

**Adding dependencies?** Read:
- `docs/best-practices/python/dependency-management.md` - UV, pyproject.toml, PEP 735

**Writing tests?** Read:
- `docs/best-practices/python/testing-and-ci.md` - Pytest patterns and coverage

## Package Requirements

All packages in this directory must:

1. **Use src-layout**: `gds_<name>/src/gds_<name>/`
2. **Include type hints**: Add `py.typed` marker file
3. **Define public API**: Use `__all__` in `__init__.py`
4. **Declare workspace deps**: Use `[tool.uv.sources]` with `workspace = true`
5. **Have tests**: Minimum 70% coverage, tests in `gds_<name>/tests/`

## Quick Commands

```bash
# Sync all packages
uv sync

# Run tests for a specific package
pytest python/gds_vault/tests/ -v

# Run linter
ruff check python/gds_vault/

# Check types
pyright python/gds_vault/src/
```

## Package Structure Template

```
gds_newpackage/
├── pyproject.toml
├── README.md
├── src/
│   └── gds_newpackage/
│       ├── __init__.py      # Public API with __all__
│       ├── __main__.py      # Optional: for python -m
│       ├── py.typed         # Type hints marker
│       └── core.py
└── tests/
    ├── conftest.py
    └── test_core.py
```

## Common Patterns

### Workspace Dependency

```toml
[project]
dependencies = ["gds-database>=1.0.0"]

[tool.uv.sources]
gds-database = { workspace = true }
```

### Public API Definition

```python
# __init__.py
from .client import Client
from .exceptions import ClientError

__all__ = ["Client", "ClientError"]
__version__ = "1.0.0"
```
