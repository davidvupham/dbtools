# Python Package Directory Structure

This document describes the standard directory structure for Python packages used in this project.

## Overview

We use the **Src Layout** pattern, which is the recommended best practice layout by the Python Packaging Authority (PyPA) for avoiding import ambiguity.

## Directory Structure

```
gds_example/                    # Project root
├── pyproject.toml              # Build configuration
├── README.md                   # Package documentation
├── MANIFEST.in                 # Optional: file inclusion rules
├── src/                        # Source root (prevents import conflicts)
│   └── gds_example/            # Python package (importable code)
│       ├── __init__.py
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
| `src/` | Source root containing installable packages |
| `tests/` | Test suite (not installed with package) |
| `examples/` | Usage examples (not installed with package) |

### Package Directory (Inside src/)

The package directory inside `src/` contains the installable Python code:

| File | Purpose |
|------|---------|
| `__init__.py` | Makes directory a package, defines public API |
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
requires-python = ">=3.9"
dependencies = [
    "gds-database>=1.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]
include = ["gds_example*"]

[tool.setuptools.package-data]
gds_example = ["py.typed"]
```

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

# With optional dependencies
pip install -e ".[dev]"
```

## References

- [PyPA Packaging User Guide](https://packaging.python.org/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [PEP 561 - py.typed](https://peps.python.org/pep-0561/)
