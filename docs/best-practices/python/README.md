# Python Best Practices

This section provides prescriptive guidance for Python projects and packages in this repository.

## Quick Reference

| Document | Purpose |
|----------|---------|
| [Project Setup](project-setup.md) | Creating new packages and projects |
| [Dependency Management](dependency-management.md) | UV, pyproject.toml, version policies |
| [Testing and CI](testing-and-ci.md) | Testing requirements and CI integration |

## Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| Python Coding Standards | [development/coding-standards/](../../development/coding-standards/python-coding-standards.md) | Code style, typing, error handling |
| Package Structure Reference | [reference/python-package-structure.md](../../reference/python-package-structure.md) | Directory layout specification |
| Modules and Packages Course | [courses/python/module_2_intermediate/](../../courses/python/module_2_intermediate/13_modules_packages.md) | Learning-oriented tutorial |

---

## New Package Checklist

Use this checklist when creating a new Python package in the repository.

### Required Files

- [ ] `pyproject.toml` with complete metadata
- [ ] `README.md` with package description and usage
- [ ] `src/<package_name>/__init__.py` with public API exports
- [ ] `src/<package_name>/py.typed` (if using type hints)
- [ ] `tests/` directory with at least one test file
- [ ] `tests/conftest.py` for shared fixtures

### pyproject.toml Essentials

- [ ] `[build-system]` with setuptools backend
- [ ] `[project]` with name, version, description, requires-python
- [ ] `[project.dependencies]` for runtime dependencies
- [ ] `[tool.setuptools.packages.find]` with `where = ["src"]`
- [ ] `[tool.uv.sources]` for workspace dependencies (if applicable)

### Before First Commit

- [ ] Package added to workspace in root `pyproject.toml` (if in `python/`)
- [ ] `uv sync` runs without errors
- [ ] `make lint` passes
- [ ] `make test` passes (or package-specific tests pass)
- [ ] Imports work: `python -c "import <package_name>"`

---

## Decision Framework

### When to Create a New Package

Create a new package when:

- **Distinct domain**: The functionality represents a separate concern (e.g., `gds_vault` vs `gds_database`)
- **Independent deployment**: The code could be published to PyPI separately
- **Different dependencies**: The functionality needs dependencies that other packages don't
- **Team ownership**: A different team will maintain this code

### When to Extend an Existing Package

Extend an existing package when:

- **Same domain**: The functionality is closely related to existing code
- **Shared dependencies**: Uses the same core dependencies
- **Common patterns**: Follows the same architectural patterns
- **Tight coupling**: The new code frequently imports from the existing package

### Package Naming

| Convention | Example | Usage |
|------------|---------|-------|
| Prefix | `gds_*` | All packages in this repo use `gds_` prefix |
| Snake case | `gds_database` | Directory and import names |
| Kebab case | `gds-database` | PyPI package name in pyproject.toml |

---

## Architecture Patterns

### Abstract Base + Implementations

Used extensively in this repository:

```
gds_database/          # Abstract interfaces
gds_postgres/          # PostgreSQL implementation
gds_mssql/             # SQL Server implementation
gds_mongodb/           # MongoDB implementation
```

**When to use**: Multiple implementations of the same interface, dependency inversion needed.

### Service Layer

```
src/gds_notification/
├── __init__.py
├── service.py         # Business logic
├── providers/         # External integrations
│   ├── base.py
│   ├── email.py
│   └── slack.py
└── models.py          # Data structures
```

**When to use**: Complex business logic with multiple external dependencies.

### Simple Library

```
src/gds_certs/
├── __init__.py
├── loader.py
└── validator.py
```

**When to use**: Utility functions, simple transformations, no complex state.

---

## Common Pitfalls

### Avoid These Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Flat layout | Import conflicts in monorepo | Use `src/` layout |
| `import *` in `__init__.py` | Namespace pollution | Explicit imports with `__all__` |
| Circular imports | Runtime errors | Use `core/` layer or `TYPE_CHECKING` |
| Missing `py.typed` | No IDE type support | Add marker file |
| Hardcoded versions | Reproducibility issues | Use `uv.lock` |
| Tests in `src/` | Tests installed with package | Keep `tests/` at project root |

### Anti-Patterns

```python
# Bad: God module with everything
from .utils import *
from .helpers import *
from .common import *

# Good: Explicit public API
from .client import VaultClient
from .auth import TokenAuth, AppRoleAuth
from .exceptions import VaultError, AuthenticationError

__all__ = ["VaultClient", "TokenAuth", "AppRoleAuth", "VaultError", "AuthenticationError"]
```

---

## Maintenance

This documentation should be updated when:

- New architectural patterns are established
- Tooling changes (e.g., UV updates)
- Repository structure evolves
- Common issues are identified

Last updated: 2026-01-18
