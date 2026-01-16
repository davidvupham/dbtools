# How to Migrate from pip/Poetry to UV

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Migration-purple)

> [!IMPORTANT]
> **Related Docs:** [Migrate from Distributions](./uv-migrate-from-distributions.md) | [Dependency Management](./uv-dependency-management.md) | [Workspaces](./uv-workspaces.md)

This guide walks you through migrating existing Python projects to UV from traditional tools like pip, pip-tools, Poetry, or Pipenv.

> [!NOTE]
> For migrating from Anaconda, python.org, Microsoft Store Python, or system Python, see [Migrate from Python Distributions](./uv-migrate-from-distributions.md).

## Table of contents

- [Prerequisites](#prerequisites)
- [Migrating from `pip` + `requirements.txt`](#migrating-from-pip--requirementstxt)
    - [Step 1: Initialize UV in Your Project](#step-1-initialize-uv-in-your-project)
    - [Step 2: Import Dependencies from requirements.txt](#step-2-import-dependencies-from-requirementstxt)
    - [Step 3: Handle Development Requirements](#step-3-handle-development-requirements)
    - [Step 4: Update Your Workflow](#step-4-update-your-workflow)
    - [Step 5: Clean Up (Optional)](#step-5-clean-up-optional)
- [Migrating from Poetry](#migrating-from-poetry)
    - [Step 1: Export Poetry Dependencies](#step-1-export-poetry-dependencies)
    - [Step 2: Initialize UV](#step-2-initialize-uv)
    - [Step 3: Convert Poetry-Specific Sections](#step-3-convert-poetry-specific-sections)
    - [Step 4: Generate Lock File](#step-4-generate-lock-file)
    - [Step 5: Install Dependencies](#step-5-install-dependencies)
    - [Step 6: Update Your Workflow](#step-6-update-your-workflow)
    - [Step 7: Clean Up](#step-7-clean-up)
- [Migrating from Pipenv](#migrating-from-pipenv)
    - [Step 1: Export Current Dependencies](#step-1-export-current-dependencies)
    - [Step 2: Initialize UV](#step-2-initialize-uv-1)
    - [Step 3: Import Dependencies](#step-3-import-dependencies)
    - [Step 4: Generate Lock File](#step-4-generate-lock-file-1)
    - [Step 5: Update Your Workflow](#step-5-update-your-workflow-1)
    - [Step 6: Clean Up](#step-6-clean-up)
- [Migrating from pip-tools](#migrating-from-pip-tools)
    - [Step 1: Understand Your Current Setup](#step-1-understand-your-current-setup)
    - [Step 2: Initialize UV](#step-2-initialize-uv-2)
    - [Step 3: Import from .in Files](#step-3-import-from-in-files)
    - [Step 4: Update Your Workflow](#step-4-update-your-workflow-1)
- [Handling Special Cases](#handling-special-cases)
    - [Private Package Indexes](#private-package-indexes)
    - [Git Dependencies](#git-dependencies)
    - [Local/Editable Dependencies](#localeditable-dependencies)
- [Updating CI/CD Pipelines](#updating-cicd-pipelines)
    - [GitHub Actions](#github-actions)
    - [Docker](#docker)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)
    - ["Package not found" errors](#package-not-found-errors)
    - [Version conflicts](#version-conflicts)
    - [Missing system dependencies](#missing-system-dependencies)
- [Related Guides](#related-guides)

## Prerequisites

- UV installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An existing Python project

---

## Migrating from `pip` + `requirements.txt`

### Step 1: Initialize UV in Your Project

Navigate to your project and initialize UV:

```bash
cd your-project
uv init
```

If you already have a `pyproject.toml`, UV will use it. Otherwise, it creates one.

### Step 2: Import Dependencies from requirements.txt

#### Option A: Add to pyproject.toml (Recommended)

```bash
uv add -r requirements.txt
```

This adds all dependencies to `pyproject.toml` and creates a lock file.

#### Option B: Use Legacy pip Interface

If you want to keep using requirements.txt for now:

```bash
uv pip install -r requirements.txt
```

### Step 3: Handle Development Requirements

If you have `requirements-dev.txt`:

```bash
uv add --dev -r requirements-dev.txt
```

### Step 4: Update Your Workflow

| Old Command | New Command |
|-------------|-------------|
| `pip install -r requirements.txt` | `uv sync` |
| `pip install package` | `uv add package` |
| `pip uninstall package` | `uv remove package` |
| `pip freeze > requirements.txt` | `uv export > requirements.txt` |
| `python script.py` | `uv run python script.py` |

### Step 5: Clean Up (Optional)

Once migrated, you can remove:

- `requirements.txt` (optional - keep for legacy systems)
- `requirements-dev.txt`
- Old virtual environment folders

---

## Migrating from Poetry

### Step 1: Export Poetry Dependencies

First, understand your current state:

```bash
poetry show --tree
```

### Step 2: Initialize UV

```bash
uv init
```

If you have a `pyproject.toml` from Poetry, UV can work with it directly.

### Step 3: Convert Poetry-Specific Sections

UV uses standard `pyproject.toml` format. Convert Poetry sections:

**Before (Poetry):**

```toml
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
```

**After (UV-compatible):**

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
]
```

### Step 4: Generate Lock File

```bash
uv lock
```

### Step 5: Install Dependencies

```bash
uv sync
```

### Step 6: Update Your Workflow

| Poetry Command | UV Command |
|----------------|------------|
| `poetry install` | `uv sync` |
| `poetry add package` | `uv add package` |
| `poetry add --group dev package` | `uv add --dev package` |
| `poetry remove package` | `uv remove package` |
| `poetry run python script.py` | `uv run python script.py` |
| `poetry lock` | `uv lock` |
| `poetry shell` | Not needed - use `uv run` |

### Step 7: Clean Up

Remove Poetry-specific files:

- `poetry.lock` (replaced by `uv.lock`)
- Poetry virtual environment

---

## Migrating from Pipenv

### Step 1: Export Current Dependencies

```bash
pipenv requirements > requirements.txt
pipenv requirements --dev > requirements-dev.txt
```

### Step 2: Initialize UV

```bash
uv init
```

### Step 3: Import Dependencies

```bash
uv add -r requirements.txt
uv add --dev -r requirements-dev.txt
```

### Step 4: Generate Lock File

```bash
uv lock
```

### Step 5: Update Your Workflow

| Pipenv Command | UV Command |
|----------------|------------|
| `pipenv install` | `uv sync` |
| `pipenv install package` | `uv add package` |
| `pipenv install --dev package` | `uv add --dev package` |
| `pipenv uninstall package` | `uv remove package` |
| `pipenv run python script.py` | `uv run python script.py` |
| `pipenv lock` | `uv lock` |
| `pipenv shell` | Not needed - use `uv run` |

### Step 6: Clean Up

Remove Pipenv files:

- `Pipfile`
- `Pipfile.lock`

---

## Migrating from pip-tools

### Step 1: Understand Your Current Setup

You likely have:

- `requirements.in` (direct dependencies)
- `requirements.txt` (compiled/locked dependencies)
- Possibly `requirements-dev.in` and `requirements-dev.txt`

### Step 2: Initialize UV

```bash
uv init
```

### Step 3: Import from .in Files

```bash
uv add -r requirements.in
uv add --dev -r requirements-dev.in
```

### Step 4: Update Your Workflow

| pip-tools Command | UV Command |
|-------------------|------------|
| `pip-compile requirements.in` | `uv lock` |
| `pip-sync requirements.txt` | `uv sync` |
| Add to requirements.in + compile | `uv add package` |

---

## Handling Special Cases

### Private Package Indexes

**Old pip.conf or pip config:**

```ini
[global]
extra-index-url = https://pypi.company.com/simple/
```

**UV configuration in pyproject.toml:**

```toml
[tool.uv]
index-url = "https://pypi.org/simple"
extra-index-url = ["https://pypi.company.com/simple/"]
```

Or use environment variables:

```bash
export UV_EXTRA_INDEX_URL="https://pypi.company.com/simple/"
```

### Git Dependencies

**Poetry:**

```toml
[tool.poetry.dependencies]
my-package = { git = "https://github.com/org/repo.git", branch = "main" }
```

**UV:**

```toml
dependencies = [
    "my-package",
]

[tool.uv.sources]
my-package = { git = "https://github.com/org/repo.git", branch = "main" }
```

### Local/Editable Dependencies

**pip:**

```bash
pip install -e ./my-local-package
```

**UV:**

```bash
uv add --editable ./my-local-package
```

Or in pyproject.toml:

```toml
[tool.uv.sources]
my-package = { path = "./my-local-package", editable = true }
```

---

## Updating CI/CD Pipelines

### GitHub Actions

**Before (pip):**

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
- run: pip install -r requirements.txt
- run: pytest
```

**After (UV):**

```yaml
- uses: astral-sh/setup-uv@v4
- run: uv sync
- run: uv run pytest
```

### Docker

**Before:**

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
```

**After:**

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
```

---

## Verification Checklist

After migration, verify:

- [ ] `uv sync` runs without errors
- [ ] `uv run python -c "import your_package"` works
- [ ] All tests pass with `uv run pytest`
- [ ] CI/CD pipeline succeeds
- [ ] Docker builds work

---

## Troubleshooting

### "Package not found" errors

Check if the package name differs between PyPI and your requirements:

```bash
uv add package-name  # Try the official PyPI name
```

### Version conflicts

UV's resolver is stricter. If you get conflicts:

```bash
uv add package --resolution lowest  # Try lowest compatible versions
```

Or check the error message for conflicting requirements.

### Missing system dependencies

Some packages need system libraries. Check the package documentation for requirements like `libpq-dev` for `psycopg2`.

---

## Related Guides

- [UV Adoption Rationale (ROI & Business Case)](../../../explanation/python/uv/README.md)
- [UV Getting Started Tutorial](../../../tutorials/python/uv/uv-getting-started.md)
- [UV Docker Integration](./uv-docker-integration.md)
- [UV CI/CD Integration](./uv-ci-cd-integration.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
