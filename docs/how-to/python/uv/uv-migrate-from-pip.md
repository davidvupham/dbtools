# How to migrate from pip to UV

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Migration-purple)

> [!IMPORTANT]
> **Related Docs:** [Migrate from Distributions](./uv-migrate-from-distributions.md) | [Dependency Management](./uv-dependency-management.md) | [Workspaces](./uv-workspaces.md)

This guide walks you through migrating existing Python projects from pip (and pip-tools) to UV.

> [!NOTE]
> For migrating from Anaconda, python.org, Microsoft Store Python, or system Python, see [Migrate from Python Distributions](./uv-migrate-from-distributions.md).

## Table of contents

- [Why migrate from pip to UV?](#why-migrate-from-pip-to-uv)
- [Prerequisites](#prerequisites)
- [Migrating from pip + requirements.txt](#migrating-from-pip--requirementstxt)
  - [Step 1: Initialize UV in your project](#step-1-initialize-uv-in-your-project)
  - [Step 2: Import dependencies from requirements.txt](#step-2-import-dependencies-from-requirementstxt)
  - [Step 3: Handle development requirements](#step-3-handle-development-requirements)
  - [Step 4: Update your workflow](#step-4-update-your-workflow)
  - [Step 5: Clean up (optional)](#step-5-clean-up-optional)
- [Migrating from pip-tools](#migrating-from-pip-tools)
  - [Step 1: Understand your current setup](#step-1-understand-your-current-setup)
  - [Step 2: Initialize UV](#step-2-initialize-uv)
  - [Step 3: Import from .in files](#step-3-import-from-in-files)
  - [Step 4: Update your workflow](#step-4-update-your-workflow-1)
- [Handling special cases](#handling-special-cases)
  - [Private package indexes](#private-package-indexes)
  - [Git dependencies](#git-dependencies)
  - [Local/editable dependencies](#localeditable-dependencies)
- [Updating CI/CD pipelines](#updating-cicd-pipelines)
  - [GitHub Actions](#github-actions)
  - [Docker](#docker)
- [Verification checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)
  - ["Package not found" errors](#package-not-found-errors)
  - [Version conflicts](#version-conflicts)
  - [Missing system dependencies](#missing-system-dependencies)
- [Related guides](#related-guides)

---

## Why migrate from pip to UV?

[↑ Back to table of contents](#table-of-contents)

Understanding the trade-offs helps you make an informed decision.

### Advantages of UV over pip

| Area | pip | UV |
|:---|:---|:---|
| **Speed** | Installs packages sequentially; resolution can take minutes on large dependency trees | 10-100x faster; Rust-based with parallel downloads and installs |
| **Reproducibility** | No built-in lock file; `pip freeze` captures state but doesn't guarantee reproducibility across platforms | Universal `uv.lock` resolves for all platforms simultaneously |
| **Environment management** | Requires separate `python -m venv` step; manual activation | Automatic `.venv` creation and management; `uv run` handles everything |
| **Python version management** | Not supported; requires separate tool like `pyenv` | Built-in `uv python install` with pre-compiled binaries |
| **Dependency resolution** | Backtracking resolver; can be slow or fail on complex trees | PubGrub algorithm with human-readable conflict messages |
| **Disk usage** | Each venv gets its own copy of every package | Global cache with hardlinks; venvs share cached packages |
| **Cross-platform locking** | Not supported; lock files are platform-specific | Lock file resolves for Linux, macOS, and Windows simultaneously |
| **Tool running** | Requires `pipx` as a separate tool | Built-in `uvx` command for running CLI tools |

### When pip is sufficient

- Small scripts with few dependencies
- Environments where you cannot install additional tooling
- Legacy systems that require pip-based workflows
- Docker images where you need the smallest possible toolchain

### What you keep with UV

- **Standard `pyproject.toml`**: UV uses PEP 621 project metadata — no proprietary config format
- **Standard virtual environments**: `.venv` is a regular Python venv; `pip` can still read it
- **Standard wheels from PyPI**: UV installs the same packages from the same index
- **No vendor lock-in**: You can stop using UV at any time and switch back to `pip install .`

[↑ Back to table of contents](#table-of-contents)

---

## Prerequisites

- UV installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An existing Python project using pip

---

## Migrating from pip + requirements.txt

[↑ Back to table of contents](#table-of-contents)

### Step 1: Initialize UV in your project

Navigate to your project and initialize UV:

```bash
cd your-project
uv init
```

If you already have a `pyproject.toml`, UV uses it. Otherwise, it creates one.

### Step 2: Import dependencies from requirements.txt

#### Option A: Add to pyproject.toml (recommended)

```bash
uv add -r requirements.txt
```

This adds all dependencies to `pyproject.toml` and creates a lock file.

#### Option B: Use legacy pip interface

If you want to keep using requirements.txt temporarily:

```bash
uv pip install -r requirements.txt
```

### Step 3: Handle development requirements

If you have `requirements-dev.txt`:

```bash
uv add --dev -r requirements-dev.txt
```

### Step 4: Update your workflow

| pip command | UV command |
|:---|:---|
| `pip install -r requirements.txt` | `uv sync` |
| `pip install package` | `uv add package` |
| `pip uninstall package` | `uv remove package` |
| `pip freeze > requirements.txt` | `uv export -o requirements.txt` |
| `python script.py` | `uv run python script.py` |
| `python -m venv .venv` | Not needed — `uv sync` creates `.venv` automatically |
| `source .venv/bin/activate` | Not needed — `uv run` activates automatically |
| `pip install -e .` | Not needed — `uv sync` installs in editable mode |

### Step 5: Clean up (optional)

Once migrated, you can remove:

- `requirements.txt` (optional — keep for legacy systems that need it)
- `requirements-dev.txt`
- Old virtual environment folders

> [!TIP]
> If you still need a `requirements.txt` for legacy consumers, generate it from your lock file:
> ```bash
> uv export --no-dev -o requirements.txt
> ```

[↑ Back to table of contents](#table-of-contents)

---

## Migrating from pip-tools

[↑ Back to table of contents](#table-of-contents)

### Step 1: Understand your current setup

You likely have:

- `requirements.in` (direct dependencies)
- `requirements.txt` (compiled/locked dependencies)
- Possibly `requirements-dev.in` and `requirements-dev.txt`

### Step 2: Initialize UV

```bash
uv init
```

### Step 3: Import from .in files

```bash
uv add -r requirements.in
uv add --dev -r requirements-dev.in
```

### Step 4: Update your workflow

| pip-tools command | UV command |
|:---|:---|
| `pip-compile requirements.in` | `uv lock` |
| `pip-sync requirements.txt` | `uv sync` |
| Add to requirements.in + compile | `uv add package` |

[↑ Back to table of contents](#table-of-contents)

---

## Handling special cases

[↑ Back to table of contents](#table-of-contents)

### Private package indexes

**Old pip.conf or pip config:**

```ini
[global]
extra-index-url = https://pypi.company.com/simple/
```

**UV configuration in pyproject.toml:**

```toml
[[tool.uv.index]]
name = "company"
url = "https://pypi.company.com/simple/"
```

Or use environment variables:

```bash
export UV_EXTRA_INDEX_URL="https://pypi.company.com/simple/"
```

### Git dependencies

**pip (requirements.txt):**

```text
my-package @ git+https://github.com/org/repo.git@main
```

**UV (pyproject.toml):**

```toml
dependencies = [
    "my-package",
]

[tool.uv.sources]
my-package = { git = "https://github.com/org/repo.git", branch = "main" }
```

### Local/editable dependencies

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

[↑ Back to table of contents](#table-of-contents)

---

## Updating CI/CD pipelines

[↑ Back to table of contents](#table-of-contents)

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
- uses: astral-sh/setup-uv@v7
- run: uv sync --locked
- run: uv run pytest
```

> [!NOTE]
> `--locked` ensures the lock file is up to date with `pyproject.toml`. If it is not, the command fails — preventing CI from silently using stale dependencies.

### Docker

**Before (pip):**

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**After (UV):**

```dockerfile
FROM ghcr.io/astral-sh/uv:0.6-python3.12-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY . .

CMD ["python", "app.py"]
```

> [!TIP]
> Pin UV to a specific version tag (e.g., `0.6`) in Docker images for reproducible builds. Avoid `:latest`.

[↑ Back to table of contents](#table-of-contents)

---

## Verification checklist

After migration, verify:

- [ ] `uv sync` runs without errors
- [ ] `uv run python -c "import your_package"` works
- [ ] All tests pass with `uv run pytest`
- [ ] CI/CD pipeline succeeds
- [ ] Docker builds work
- [ ] `uv.lock` is committed to version control

---

## Troubleshooting

[↑ Back to table of contents](#table-of-contents)

### "Package not found" errors

Check if the package name differs between PyPI and your requirements:

```bash
uv add package-name  # Try the official PyPI name
```

### Version conflicts

UV's resolver is stricter than pip's. If you get conflicts:

```bash
# See the full dependency tree to understand conflicts
uv tree

# Check what requires a specific package
uv tree --invert --package conflicting-package
```

### Missing system dependencies

Some packages need system libraries. Check the package documentation for requirements like `libpq-dev` for `psycopg2`.

[↑ Back to table of contents](#table-of-contents)

---

## Related guides

- [UV Getting Started Tutorial](../../../tutorials/languages/python/uv/uv-getting-started.md)
- [UV Adoption Rationale](../../../explanation/python/uv/README.md)
- [UV Docker Integration](./uv-docker-integration.md)
- [UV CI/CD Integration](./uv-ci-cd-integration.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
