# Python Package Directory Structure

This document describes the standard directory structure for Python packages used in this project.

## Overview

We use the **Src Layout** pattern, which is the recommended best practice layout by the Python Packaging Authority (PyPA) for avoiding import ambiguity.

## Directory Structure

```
gds_example/                    # Project root
├── pyproject.toml              # Build configuration
├── README.md                   # Package documentation
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # License file
├── MANIFEST.in                 # Optional: file inclusion rules
├── src/                        # Source root (prevents import conflicts)
│   └── gds_example/            # Python package (importable code)
│       ├── __init__.py
│       ├── __main__.py         # Entry point for python -m gds_example
│       ├── py.typed            # Optional: PEP 561 marker
│       ├── module.py
│       └── subpackage/
│           ├── __init__.py
│           └── helper.py
├── tests/                      # Test files
│   ├── conftest.py             # Pytest shared fixtures
│   └── test_module.py
└── examples/                   # Optional: usage examples
    └── example.py
```

## Key Components

### Project Root (Outer Directory)

The outer directory contains project-level files:

| File | Purpose |
|------|---------|
| `pyproject.toml` | Build system and project metadata (PEP 517/518) |
| `README.md` | Package documentation, displayed on PyPI |
| `CHANGELOG.md` | Version history and release notes |
| `CONTRIBUTING.md` | Contribution guidelines for developers |
| `LICENSE` | License file (use SPDX identifier in pyproject.toml) |
| `src/` | Source root containing installable packages |
| `tests/` | Test suite (not installed with package) |
| `examples/` | Usage examples (not installed with package) |

### Package Directory (Inside src/)

The package directory inside `src/` contains the installable Python code:

| File | Purpose |
|------|---------|
| `__init__.py` | Makes directory a package, defines public API |
| `__main__.py` | Entry point for `python -m package_name` execution |
| `py.typed` | Signals that package includes type hints (PEP 561) |
| `*.py` | Module files |

## Why the src/ Layout?

The `src/` directory provides critical benefits:

1. **Import Safety**: Impossible to accidentally import uninstalled source code
2. **Test Isolation**: Tests always run against the *installed* package, not source
3. **Clean Installs**: Only `src/gds_example/` is installed to `site-packages`
4. **Monorepo Friendly**: Prevents namespace conflicts in repositories with multiple packages
5. **Industry Standard**: Recommended by PyPA and major Python projects

## Layout Comparison

### Src Layout (Our Choice) ✓

```
project/
├── pyproject.toml
└── src/
    └── package/
        └── __init__.py
```

**Pros**: Impossible to import uninstalled code, prevents namespace conflicts, best for monorepos
**Cons**: Extra directory level

### Flat Layout (Alternative)

```
project/
├── pyproject.toml
└── package/
    └── __init__.py
```

**Pros**: Simple, familiar
**Cons**: Possible to accidentally import source instead of installed package, causes conflicts in monorepos

## pyproject.toml Configuration

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "gds-example"
version = "1.0.0"
description = "Package description"
readme = "README.md"
license = "MIT"                    # SPDX identifier (PEP 639)
requires-python = ">=3.9"
dependencies = [
    "gds-database>=1.0.0",
]

[project.optional-dependencies]
# Feature-specific dependencies (installed with pip install pkg[feature])
postgres = ["psycopg2-binary>=2.9"]

[tool.setuptools.packages.find]
where = ["src"]
include = ["gds_example*"]

[tool.setuptools.package-data]
gds_example = ["py.typed"]
```

## Dependency Groups (PEP 735)

PEP 735 (finalized October 2024) introduces **dependency groups** for development dependencies. Unlike `[project.optional-dependencies]`, these are not included in built distributions.

```toml
[dependency-groups]
# Development tools
dev = [
    "ruff>=0.1.0",
    "pyright>=1.1",
    "pre-commit>=3.0",
]

# Testing dependencies
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
]

# Documentation tools
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]

# Combined group using include
all = [
    {include-group = "dev"},
    {include-group = "test"},
    {include-group = "docs"},
]
```

### When to Use Each

| Type | Use Case | Installed With |
|------|----------|----------------|
| `[project.dependencies]` | Runtime requirements | `pip install pkg` |
| `[project.optional-dependencies]` | Feature extras (e.g., database drivers) | `pip install pkg[feature]` |
| `[dependency-groups]` | Development-only tools | `uv sync --group dev` |

## Package Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Directory name | `snake_case` | `gds_example` |
| Package name (PyPI) | `kebab-case` | `gds-example` |
| Import statement | `snake_case` | `import gds_example` |

## Installation Methods

```bash
# Development install (editable)
pip install -e .

# Production install
pip install .

# With optional dependencies (feature extras)
pip install -e ".[postgres]"

# With UV (recommended)
uv sync                    # Install all dependencies
uv sync --group dev        # Include dev dependency group
uv sync --all-groups       # Include all dependency groups
```

## UV Workspaces (Monorepos)

For projects with multiple related packages, UV workspaces provide a unified development experience with a shared lockfile.

### Workspace Structure

```
project-root/
├── pyproject.toml              # Root workspace configuration
├── uv.lock                     # Shared lockfile for all packages
├── python/
│   ├── gds_database/
│   │   ├── pyproject.toml
│   │   └── src/gds_database/
│   ├── gds_postgres/
│   │   ├── pyproject.toml
│   │   └── src/gds_postgres/
│   └── gds_vault/
│       ├── pyproject.toml
│       └── src/gds_vault/
└── tests/
```

### Root pyproject.toml

```toml
[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.9"

[tool.uv]
package = true
python-preference = "managed"

[tool.uv.workspace]
members = ["python/gds_*"]

[dependency-groups]
dev = ["pytest", "ruff", "pyright"]
```

### Inter-Package Dependencies

Workspace members can depend on each other:

```toml
# In gds_postgres/pyproject.toml
[project]
dependencies = ["gds-database>=1.0.0"]

[tool.uv.sources]
gds-database = { workspace = true }
```

### Workspace Commands

```bash
uv sync                          # Sync root package
uv sync --package gds-postgres   # Sync specific package
uv run --package gds-vault pytest  # Run command in package context
uv lock                          # Update shared lockfile
```

## References

- [PyPA Packaging User Guide](https://packaging.python.org/)
- [PyPA: src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [PEP 561 - py.typed](https://peps.python.org/pep-0561/)
- [PEP 639 - SPDX License Expressions](https://peps.python.org/pep-0639/)
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
