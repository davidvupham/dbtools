# How to Use UV Workspaces for Monorepos

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Structure-purple)

> [!IMPORTANT]
> **Related Docs:** [Dependency Management](./uv-dependency-management.md) | [CI/CD Integration](./uv-ci-cd-integration.md)

This guide covers setting up and managing UV workspaces for monorepo projects with multiple Python packages.

## Table of contents

- [What Are Workspaces?](#what-are-workspaces)
- [When to Use Workspaces](#when-to-use-workspaces)
- [Quick Start](#quick-start)
  - [Project Structure](#project-structure)
  - [Step 1: Create the Workspace Root](#step-1-create-the-workspace-root)
  - [Step 2: Create Member Packages](#step-2-create-member-packages)
  - [Step 3: Initialize and Sync](#step-3-initialize-and-sync)
- [Importing Workspace Packages](#importing-workspace-packages)
  - [How It Works](#how-it-works)
  - [Verifying Package Installation](#verifying-package-installation)
  - [Key Difference from pip](#key-difference-from-pip)
- [Working with Workspaces](#working-with-workspaces)
  - [Running Commands in Specific Packages](#running-commands-in-specific-packages)
  - [Adding Dependencies](#adding-dependencies)
  - [Syncing Dependencies](#syncing-dependencies)
- [Workspace Configuration](#workspace-configuration)
  - [Include/Exclude Members](#includeexclude-members)
  - [Workspace Sources](#workspace-sources)
- [Common Patterns](#common-patterns)
  - [Shared Development Dependencies](#shared-development-dependencies)
  - [Per-Package Dev Dependencies](#per-package-dev-dependencies)
  - [Publishable vs Non-Publishable Members](#publishable-vs-non-publishable-members)
- [CI/CD for Workspaces](#cicd-for-workspaces)
  - [Testing All Packages](#testing-all-packages)
  - [Matrix Testing](#matrix-testing)
  - [Only Test Changed Packages](#only-test-changed-packages)
- [Building and Publishing](#building-and-publishing)
  - [Build a Single Package](#build-a-single-package)
  - [Publish a Package](#publish-a-package)
  - [Build All Packages](#build-all-packages)
- [Docker with Workspaces](#docker-with-workspaces)
  - [Multi-Package Dockerfile](#multi-package-dockerfile)
- [Troubleshooting](#troubleshooting)
  - ["Package not found in workspace"](#package-not-found-in-workspace)
  - [Circular dependencies](#circular-dependencies)
  - [Lock file conflicts](#lock-file-conflicts)
  - [Import errors in development](#import-errors-in-development)
- [Migration from Other Tools](#migration-from-other-tools)
  - [From Poetry Workspaces](#from-poetry-workspaces)
  - [From npm/yarn Workspaces](#from-npmyarn-workspaces)
- [Related Guides](#related-guides)

## What Are Workspaces?

UV workspaces allow you to manage multiple related Python packages in a single repository with:

- **Shared lock file**: One `uv.lock` for all packages
- **Unified dependency resolution**: No version conflicts between packages
- **Easy local development**: Packages automatically reference each other
- **Efficient CI**: Build and test related packages together

---

## When to Use Workspaces

✅ **Good use cases:**

- Monorepo with multiple related packages
- Libraries with separate CLI/API/Core components
- Microservices sharing common utilities
- Projects with internal dependencies

❌ **Not needed for:**

- Single package projects
- Unrelated packages that happen to be in the same repo
- Projects where packages need different Python versions

---

## Quick Start

### Project Structure

```
my-monorepo/
├── pyproject.toml           # Workspace root
├── uv.lock                  # Shared lock file
├── packages/
│   ├── core/
│   │   ├── pyproject.toml   # Core library
│   │   └── src/core/
│   ├── api/
│   │   ├── pyproject.toml   # API package (depends on core)
│   │   └── src/api/
│   └── cli/
│       ├── pyproject.toml   # CLI package (depends on core)
│       └── src/cli/
└── apps/
    └── web/
        ├── pyproject.toml   # Web app (depends on api)
        └── src/web/
```

### Step 1: Create the Workspace Root

Create the root `pyproject.toml`:

```toml
# pyproject.toml (workspace root)
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/*", "apps/*"]
```

### Step 2: Create Member Packages

**Core library (`packages/core/pyproject.toml`):**

```toml
[project]
name = "my-core"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**API package (`packages/api/pyproject.toml`):**

```toml
[project]
name = "my-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "my-core",        # Workspace dependency
    "fastapi>=0.100",
]

[tool.uv.sources]
my-core = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Step 3: Initialize and Sync

```bash
# From workspace root
uv sync
```

This creates a single `.venv` and `uv.lock` at the workspace root.

---

## Importing Workspace Packages

After running `uv sync`, all workspace member packages are installed in **editable mode** automatically. This means you can import them in Python scripts exactly like any other installed package:

```python
# Import workspace packages just like any installed package
from my_core import BaseModel
from my_api import create_app
from my_cli import run_command

# Changes to source code are reflected immediately—no reinstall needed
```

### How It Works

When you run `uv sync`:

1. **Creates a virtual environment** at the workspace root (`.venv`)
2. **Installs all external dependencies** from `uv.lock`
3. **Installs all workspace members in editable mode** (equivalent to `pip install -e`)

This is controlled by the `package = true` setting in the root `pyproject.toml`:

```toml
[tool.uv]
package = true  # Treat workspace members as installable packages
```

### Verifying Package Installation

```bash
# Check that packages are importable
uv run python -c "from my_core import something; print('OK')"

# List installed packages
uv run pip list | grep my-
```

### Key Difference from pip

| pip workflow | UV workflow |
|--------------|-------------|
| `pip install -e ./packages/core` | `uv sync` |
| `pip install -e ./packages/api` | (installs all at once) |
| `pip install -e ./packages/cli` | |
| Repeat for each package... | |

---

## Working with Workspaces

### Running Commands in Specific Packages

```bash
# Run from workspace root, targeting a specific package
uv run --package my-api pytest
uv run --package my-cli python -m cli

# Or navigate to the package directory
cd packages/api
uv run pytest
```

### Adding Dependencies

```bash
# Add to a specific package
uv add --package my-api httpx

# Add to the workspace root
uv add requests

# Add as dev dependency
uv add --package my-core --dev pytest
```

### Syncing Dependencies

```bash
# Sync all packages
uv sync

# Sync specific package only
uv sync --package my-api
```

---

## Workspace Configuration

### Include/Exclude Members

```toml
[tool.uv.workspace]
# Include patterns
members = [
    "packages/*",
    "apps/*",
    "tools/linter",
]

# Exclude patterns
exclude = [
    "packages/deprecated-*",
    "apps/experimental",
]
```

### Workspace Sources

Reference workspace packages as dependencies:

```toml
# In packages/api/pyproject.toml
[project]
dependencies = [
    "my-core",
    "my-utils",
]

[tool.uv.sources]
my-core = { workspace = true }
my-utils = { workspace = true }
```

---

## Common Patterns

### Shared Development Dependencies

Create a `dev` group at the workspace root:

```toml
# pyproject.toml (workspace root)
[project]
name = "my-monorepo"
version = "0.1.0"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.workspace]
members = ["packages/*"]
```

Then all packages can use these tools:

```bash
uv run pytest packages/core/tests
uv run ruff check .
```

### Per-Package Dev Dependencies

```toml
# packages/api/pyproject.toml
[project]
name = "my-api"
dependencies = ["my-core", "fastapi"]

[dependency-groups]
dev = [
    "httpx",  # For testing FastAPI
]
```

### Publishable vs Non-Publishable Members

Mark packages that shouldn't be published:

```toml
# apps/web/pyproject.toml (application, not a library)
[project]
name = "my-web-app"
version = "0.1.0"

# This is an application, not meant for PyPI
[tool.uv]
package = false
```

---

## CI/CD for Workspaces

### Testing All Packages

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4

      - name: Sync all packages
        run: uv sync

      - name: Test core
        run: uv run --package my-core pytest

      - name: Test api
        run: uv run --package my-api pytest

      - name: Test cli
        run: uv run --package my-cli pytest
```

### Matrix Testing

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: [my-core, my-api, my-cli]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run --package ${{ matrix.package }} pytest
```

### Only Test Changed Packages

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            my-core:
              - 'packages/core/**'
            my-api:
              - 'packages/api/**'
              - 'packages/core/**'  # api depends on core
            my-cli:
              - 'packages/cli/**'
              - 'packages/core/**'

  test:
    needs: changes
    if: ${{ needs.changes.outputs.packages != '[]' }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: ${{ fromJson(needs.changes.outputs.packages) }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run --package ${{ matrix.package }} pytest
```

---

## Building and Publishing

### Build a Single Package

```bash
uv build --package my-core
```

Output goes to `dist/`:

```
dist/
├── my_core-0.1.0-py3-none-any.whl
└── my_core-0.1.0.tar.gz
```

### Publish a Package

```bash
uv publish --package my-core
```

### Build All Packages

```bash
for pkg in packages/*/; do
    uv build --package "$(basename $pkg)"
done
```

---

## Docker with Workspaces

### Multi-Package Dockerfile

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Copy workspace files
COPY pyproject.toml uv.lock ./
COPY packages/ packages/

# Install only the api package and its dependencies
RUN uv sync --package my-api --frozen --no-dev

FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages/api/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

---

## Troubleshooting

### "Package not found in workspace"

Ensure the package has a valid `pyproject.toml` with `[project]` section:

```toml
[project]
name = "my-package"
version = "0.1.0"
```

### Circular dependencies

UV will error on circular dependencies. Refactor to break the cycle:

```
# Bad: A depends on B, B depends on A

# Good: Extract shared code to C
# A depends on C
# B depends on C
```

### Lock file conflicts

After merging branches:

```bash
uv lock
```

### Import errors in development

Ensure packages are installed in editable mode (default for `uv sync`):

```bash
uv sync  # Installs all workspace members as editable
```

---

## Migration from Other Tools

### From Poetry Workspaces

Poetry uses a different workspace format. Convert:

**Poetry:**

```toml
[tool.poetry.packages]
include = [
    { include = "core", from = "packages" },
]
```

**UV:**

```toml
[tool.uv.workspace]
members = ["packages/core"]
```

### From npm/yarn Workspaces

Similar concept, different syntax:

**package.json:**

```json
{
  "workspaces": ["packages/*"]
}
```

**UV:**

```toml
[tool.uv.workspace]
members = ["packages/*"]
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/python/uv/uv-getting-started.md)
- [UV Reference](../../../reference/python/uv/uv-reference.md)
- [Python Package Structure](../../../reference/python-package-structure.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
