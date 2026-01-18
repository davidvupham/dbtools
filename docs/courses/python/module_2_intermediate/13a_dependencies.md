# Dependencies Management

## Why Dependency Management Matters

Python projects rely on external packages. Proper dependency management ensures:
- Reproducible builds across environments
- Isolation between projects (no version conflicts)
- Clear documentation of what your project needs

## UV - Modern Python Package Manager

[UV](https://docs.astral.sh/uv/) is a fast, modern Python package and project manager built in Rust. It replaces pip, pip-tools, pipx, poetry, pyenv, and virtualenv.

### Installing UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Creating a New Project

```bash
# Create new project with pyproject.toml
uv init my-project
cd my-project

# Project structure created:
# my-project/
#   pyproject.toml
#   src/my_project/__init__.py
#   README.md
```

### Managing Dependencies

```bash
# Add a dependency
uv add requests
uv add pandas numpy

# Add dev dependencies
uv add --dev pytest ruff

# Remove a dependency
uv remove requests

# Sync environment with lockfile
uv sync
```

### The `pyproject.toml` File

UV uses the standard `pyproject.toml` for configuration:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "requests>=2.28",
    "pandas>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```

### Running Commands

```bash
# Run a script in the project environment
uv run python script.py

# Run a module
uv run -m pytest

# Run with additional dependencies (without adding to project)
uv run --with rich python -c "from rich import print; print('[green]Hello![/green]')"
```

### Virtual Environments

UV automatically manages virtual environments:

```bash
# Create venv explicitly (usually automatic)
uv venv

# Activate (if needed for shell integration)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install from lockfile
uv sync
```

### The Lockfile (`uv.lock`)

UV generates a lockfile that pins exact versions for reproducibility:

```bash
# Lockfile is auto-generated when you add/remove deps
uv add requests  # Updates uv.lock

# Sync environment to match lockfile exactly
uv sync

# Update all dependencies to latest compatible versions
uv lock --upgrade
```

## Traditional Tools (Reference)

### pip and requirements.txt

```bash
# Install packages
pip install requests pandas

# Freeze current environment
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

### Virtual Environments (venv)

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

## Best Practices

1. **Use UV for new projects** - faster, simpler, and handles Python versions
2. **Always use virtual environments** - isolate project dependencies
3. **Commit lockfiles** - ensures reproducible builds (`uv.lock`)
4. **Pin versions in production** - use `>=` for libraries, exact pins for apps
5. **Separate dev dependencies** - keep test/lint tools out of production
