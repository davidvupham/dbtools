# Dependency Management

This guide covers managing Python dependencies in the repository using UV and pyproject.toml.

## Overview

This repository uses:

- **UV** as the package manager
- **pyproject.toml** for package configuration (PEP 517/518)
- **uv.lock** for reproducible installs
- **Workspace** configuration for monorepo support

---

## Dependency Types

### Runtime Dependencies

Dependencies required for your package to function:

```toml
[project]
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]
```

**Guidelines**:
- Use minimum version constraints (`>=`) for libraries
- Use compatible release (`~=`) for tight coupling: `~=2.0.0` allows `2.0.x`
- Avoid upper bounds unless there's a known incompatibility

### Optional Dependencies (Extras)

Feature-specific dependencies users can opt into:

```toml
[project.optional-dependencies]
postgres = ["psycopg2-binary>=2.9"]
mysql = ["mysqlclient>=2.1"]
all = ["psycopg2-binary>=2.9", "mysqlclient>=2.1"]
```

**Usage**:
```bash
pip install gds-database[postgres]
pip install gds-database[all]
```

### Development Dependencies (PEP 735)

Dependencies for development only, not included in distributions:

```toml
[dependency-groups]
dev = [
    "ruff>=0.1.0",
    "pyright>=1.1",
    "pre-commit>=3.0",
]

test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
]

docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
]
```

**Usage**:
```bash
uv sync --group dev
uv sync --group test
uv sync --all-groups
```

---

## Workspace Dependencies

### Declaring Workspace Dependencies

When one package depends on another in the workspace:

```toml
# In gds_postgres/pyproject.toml
[project]
dependencies = [
    "gds-database>=1.0.0",
]

[tool.uv.sources]
gds-database = { workspace = true }
```

The `workspace = true` tells UV to use the local workspace version instead of fetching from PyPI.

### Root Workspace Configuration

The root `pyproject.toml` defines workspace membership:

```toml
[tool.uv.workspace]
members = ["python/gds_*"]

[dependency-groups]
dev = [
    "pytest",
    "ruff",
    "pyright",
]
```

---

## Version Policies

### Semantic Versioning

All packages follow [Semantic Versioning](https://semver.org/):

| Version | When to Increment |
|---------|-------------------|
| MAJOR (1.x.x) | Breaking API changes |
| MINOR (x.1.x) | New features, backward compatible |
| PATCH (x.x.1) | Bug fixes, backward compatible |

### Version Constraints

| Constraint | Meaning | Example |
|------------|---------|---------|
| `>=1.0.0` | Minimum version | Any 1.x or higher |
| `~=1.0.0` | Compatible release | 1.0.x only |
| `>=1.0.0,<2.0.0` | Range | 1.x only |
| `==1.0.0` | Exact (avoid) | Only 1.0.0 |

**Recommendations**:
- Use `>=` for most dependencies
- Use `~=` when you need a specific minor version
- Avoid `==` except in lock files
- Avoid upper bounds unless necessary

### Lockfile Management

The `uv.lock` file ensures reproducible installs:

```bash
# Update lockfile after changing dependencies
uv lock

# Sync environment to match lockfile
uv sync

# Update a specific package
uv lock --upgrade-package requests
```

**Commit the lockfile** to ensure all developers use identical versions.

---

## Adding Dependencies

### To a Package

```bash
# Add runtime dependency
cd python/gds_vault
uv add requests

# Add with version constraint
uv add "pydantic>=2.0.0"
```

### To Root Workspace

```bash
# Add to a dependency group
uv add --group dev ruff
```

### Workspace Dependencies

Edit `pyproject.toml` directly:

```toml
[project]
dependencies = [
    "gds-database>=1.0.0",
]

[tool.uv.sources]
gds-database = { workspace = true }
```

Then sync:
```bash
uv lock
uv sync
```

---

## Removing Dependencies

```bash
# Remove from package
cd python/gds_vault
uv remove requests

# Or edit pyproject.toml and re-sync
uv lock
uv sync
```

---

## Updating Dependencies

### Update All

```bash
uv lock --upgrade
uv sync
```

### Update Specific Package

```bash
uv lock --upgrade-package requests
uv sync
```

### Check for Updates

```bash
# See outdated packages
uv pip list --outdated
```

---

## Security

### Vulnerability Scanning

```bash
# Install pip-audit
uv add --group dev pip-audit

# Scan for vulnerabilities
pip-audit
```

### Trusted Sources

Only use packages from:
- PyPI (default)
- Internal package repositories (if configured)

Never install from:
- Arbitrary URLs
- Untrusted Git repositories
- Local paths outside the workspace

---

## Common Patterns

### Optional Database Drivers

```toml
[project]
dependencies = []

[project.optional-dependencies]
postgres = ["psycopg2-binary>=2.9"]
mysql = ["mysqlclient>=2.1"]
mssql = ["pyodbc>=4.0"]
all = [
    "psycopg2-binary>=2.9",
    "mysqlclient>=2.1",
    "pyodbc>=4.0",
]
```

### Async Support

```toml
[project.optional-dependencies]
async = [
    "aiohttp>=3.8",
    "asyncpg>=0.27",
]
```

### Development Tools

```toml
[dependency-groups]
dev = [
    "ruff>=0.1.0",
    "pyright>=1.1",
    "pre-commit>=3.0",
]

test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
    "pytest-mock>=3.10",
]

typing = [
    "mypy>=1.0",
    "types-requests>=2.28",
]

all = [
    {include-group = "dev"},
    {include-group = "test"},
    {include-group = "typing"},
]
```

---

## Troubleshooting

### Conflicting Dependencies

**Problem**: UV reports version conflicts

**Solution**:
1. Check which packages require conflicting versions
2. Update the more flexible package
3. Consider if both packages are necessary

```bash
# See dependency tree
uv pip tree
```

### Missing Workspace Package

**Problem**: `Package 'gds-database' not found`

**Solution**: Ensure `[tool.uv.sources]` is configured:

```toml
[tool.uv.sources]
gds-database = { workspace = true }
```

### Lockfile Out of Sync

**Problem**: `uv sync` fails with lockfile errors

**Solution**:
```bash
uv lock
uv sync
```

### Editable Install Issues

**Problem**: Changes not reflected after editing code

**Solution**: UV uses editable installs by default. If issues persist:
```bash
uv sync --reinstall
```

---

## Best Practices Summary

1. **Use dependency groups** for dev/test/docs dependencies
2. **Use optional dependencies** for feature extras users install
3. **Commit uv.lock** for reproducible builds
4. **Use minimum versions** (`>=`) not exact pins
5. **Avoid upper bounds** unless there's a known incompatibility
6. **Scan for vulnerabilities** regularly with `pip-audit`
7. **Update dependencies** periodically to get security fixes
8. **Use workspace sources** for inter-package dependencies
