# UV Command Reference
 
**🔗 [← Back to UV Reference Index](./README.md)**
 
> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production
 
![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-CLI-blue)
 
> [!IMPORTANT]
> **Related Docs:** [Getting Started](../../../tutorials/python/uv/uv-getting-started.md) | [How-to Guides](../../../how-to/python/uv/) | [Adoption Rationale](../../../explanation/python/uv/README.md)

A complete reference for UV commands, configuration options, and environment variables.

## Table of Contents

- [Commands](#commands)
  - [Project Commands](#project-commands)
  - [Dependency Commands](#dependency-commands)
  - [Python Commands](#python-commands)
  - [Tool Commands](#tool-commands)
  - [pip Interface](#pip-interface)
  - [Cache Commands](#cache-commands)
  - [Self Commands](#self-commands)
- [Configuration](#configuration)
  - [pyproject.toml Options](#pyprojecttoml-options)
  - [Environment Variables](#environment-variables)
- [File Reference](#file-reference)

---

## Commands

### Project Commands

#### `uv init`

Initialize a new Python project.

```bash
uv init [path]                    # Initialize in path (default: current dir)
uv init --name my-project         # Set project name
uv init --python 3.12             # Specify Python version
uv init --lib                     # Create as library (with src/ layout)
uv init --app                     # Create as application (default)
uv init --no-readme               # Skip README.md creation
uv init --no-pin-python           # Don't pin Python version
```

#### `uv run`

Run a command in the project environment.

```bash
uv run <command>                  # Run command
uv run python script.py           # Run Python script
uv run pytest                     # Run installed tool
uv run --package <pkg> <command>  # Run in specific package (workspaces)
uv run --with <dep> <command>     # Run with additional dependency
uv run --python 3.11 <command>    # Run with specific Python
```

#### `uv sync`

Synchronize the project environment with the lock file.

```bash
uv sync                           # Sync all dependencies
uv sync --frozen                  # Fail if lock file is outdated
uv sync --no-dev                  # Skip development dependencies
uv sync --group <name>            # Include specific dependency group
uv sync --all-groups              # Include all dependency groups
uv sync --package <pkg>           # Sync specific package (workspaces)
```

#### `uv lock`

Update the lock file.

```bash
uv lock                           # Update lock file
uv lock --check                   # Check if lock file is up to date
uv lock --upgrade                 # Upgrade all dependencies
uv lock --upgrade-package <pkg>   # Upgrade specific package
```

#### `uv build`

Build the project into distributable artifacts.

```bash
uv build                          # Build wheel and sdist
uv build --wheel                  # Build only wheel
uv build --sdist                  # Build only source distribution
uv build --package <pkg>          # Build specific package (workspaces)
uv build --out-dir <path>         # Custom output directory
```

#### `uv publish`

Publish the project to a package index.

```bash
uv publish                        # Publish to PyPI
uv publish --token <token>        # Use API token
uv publish --repository <url>     # Custom repository URL
uv publish --package <pkg>        # Publish specific package
```

#### `uv tree`

Display the project's dependency tree.

```bash
uv tree                           # Show dependency tree
uv tree --depth <n>               # Limit tree depth
uv tree --invert                  # Show reverse dependencies
uv tree --package <pkg>           # Tree for specific package
```

#### `uv export`

Export dependencies to a requirements format.

```bash
uv export                                  # Export to stdout
uv export --format requirements-txt        # Export as requirements.txt
uv export --no-dev                         # Exclude dev dependencies
uv export --frozen                         # Use exact locked versions
uv export -o requirements.txt              # Write to file
```

---

### Dependency Commands

#### `uv add`

Add a dependency to the project.

```bash
uv add <package>                  # Add package
uv add <package>==1.0.0           # Add specific version
uv add "<package>>=1.0,<2.0"      # Add with version constraint
uv add --dev <package>            # Add as development dependency
uv add --optional <group> <pkg>   # Add as optional dependency
uv add --group <name> <package>   # Add to dependency group
uv add -r requirements.txt        # Add from requirements file
uv add --editable ./path          # Add local package as editable
uv add --package <pkg> <dep>      # Add to specific package (workspaces)
uv add git+https://github.com/... # Add from git
uv add --script script.py <pkg>   # Add to inline script metadata
```

#### `uv remove`

Remove a dependency from the project.

```bash
uv remove <package>               # Remove package
uv remove --dev <package>         # Remove from dev dependencies
uv remove --package <pkg> <dep>   # Remove from specific package
```

---

### Python Commands

#### `uv python install`

Install Python versions.

```bash
uv python install                 # Install project's Python version
uv python install 3.12            # Install specific version
uv python install 3.12.1          # Install exact patch version
uv python install 3.10 3.11 3.12  # Install multiple versions
uv python install 3.13t           # Install free-threaded build
uv python install --preview       # Install preview/beta versions
```

#### `uv python list`

List available Python versions.

```bash
uv python list                    # List installed versions
uv python list --all              # Include all available versions
uv python list --only-installed   # Show only installed
```

#### `uv python pin`

Pin the Python version for the project.

```bash
uv python pin 3.12                # Pin to version (creates .python-version)
uv python pin --global 3.12       # Set global default
```

#### `uv python find`

Find a Python interpreter.

```bash
uv python find                    # Find default Python
uv python find 3.12               # Find specific version
```

#### `uv python uninstall`

Uninstall Python versions.

```bash
uv python uninstall 3.10          # Uninstall version
uv python uninstall --all         # Uninstall all managed versions
```

---

### Tool Commands

#### `uv tool run` / `uvx`

Run a tool in an isolated environment.

```bash
uvx <tool>                        # Run tool (alias for uv tool run)
uvx ruff check .                  # Run ruff
uvx --from httpie http            # Run command from different package
uvx <tool>@<version>              # Run specific version
uvx --with <dep> <tool>           # Run with additional dependencies
uvx --python 3.11 <tool>          # Run with specific Python
```

#### `uv tool install`

Install a tool globally.

```bash
uv tool install <package>         # Install tool
uv tool install ruff              # Install ruff
uv tool install --python 3.12 ... # Use specific Python
```

#### `uv tool uninstall`

Uninstall a globally installed tool.

```bash
uv tool uninstall <package>       # Uninstall tool
uv tool uninstall --all           # Uninstall all tools
```

#### `uv tool list`

List installed tools.

```bash
uv tool list                      # List all installed tools
uv tool list --show-paths         # Include installation paths
```

#### `uv tool upgrade`

Upgrade installed tools.

```bash
uv tool upgrade <package>         # Upgrade specific tool
uv tool upgrade --all             # Upgrade all tools
```

---

### pip Interface

UV provides a pip-compatible interface for legacy workflows.

#### `uv pip install`

```bash
uv pip install <package>          # Install package
uv pip install -r requirements.txt # Install from requirements
uv pip install -e ./path          # Install editable
uv pip install --upgrade <pkg>    # Upgrade package
```

#### `uv pip uninstall`

```bash
uv pip uninstall <package>        # Uninstall package
```

#### `uv pip freeze`

```bash
uv pip freeze                     # List installed packages
uv pip freeze > requirements.txt  # Export to file
```

#### `uv pip list`

```bash
uv pip list                       # List packages
uv pip list --outdated            # Show outdated packages
```

#### `uv pip compile`

```bash
uv pip compile requirements.in    # Compile requirements
uv pip compile pyproject.toml     # Compile from pyproject.toml
uv pip compile -o requirements.txt # Output to file
```

#### `uv pip sync`

```bash
uv pip sync requirements.txt      # Sync environment with requirements
```

#### `uv venv`

```bash
uv venv                           # Create .venv
uv venv /path/to/venv             # Create at specific path
uv venv --python 3.12             # Use specific Python
```

---

### Cache Commands

#### `uv cache clean`

```bash
uv cache clean                    # Clear entire cache
uv cache clean <package>          # Clear specific package cache
```

#### `uv cache prune`

```bash
uv cache prune                    # Remove unused cache entries
```

#### `uv cache dir`

```bash
uv cache dir                      # Show cache directory location
```

#### `uv cache size`

```bash
uv cache size                     # Show cache size
```

---

### Self Commands

#### `uv self update`

```bash
uv self update                    # Update UV to latest version
uv self update --preview          # Update to preview version
```

#### `uv self version`

```bash
uv self version                   # Show UV version
```

---

## Configuration

### pyproject.toml Options

#### Project Metadata

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Name", email = "email@example.com"}]
keywords = ["python", "example"]

dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]
docs = ["mkdocs>=1.5"]
```

#### Dependency Groups

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
]
test = [
    "pytest>=8.0",
    "coverage>=7.0",
]
```

#### UV Configuration

```toml
[tool.uv]
# Package type (default: true for libraries)
package = true

# Development dependencies (alternative to dependency-groups)
dev-dependencies = [
    "pytest>=8.0",
]

# Python version preference
python-preference = "managed"  # managed, system, only-managed, only-system

# Index configuration
index-url = "https://pypi.org/simple"
extra-index-url = ["https://private.pypi.org/simple"]

# Compilation options
compile-bytecode = true

# Resolution strategy
resolution = "highest"  # highest, lowest, lowest-direct
```

#### UV Sources

```toml
[tool.uv.sources]
# Workspace dependencies
my-lib = { workspace = true }

# Git dependencies
my-package = { git = "https://github.com/org/repo.git" }
my-package = { git = "https://github.com/org/repo.git", branch = "main" }
my-package = { git = "https://github.com/org/repo.git", tag = "v1.0.0" }
my-package = { git = "https://github.com/org/repo.git", rev = "abc123" }

# Local dependencies
my-local = { path = "./packages/local" }
my-local = { path = "./packages/local", editable = true }

# URL dependencies
my-package = { url = "https://example.com/package.whl" }
```

#### Workspace Configuration

```toml
[tool.uv.workspace]
members = ["packages/*", "apps/*"]
exclude = ["packages/deprecated"]
```

---

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UV_CACHE_DIR` | Cache directory location | Platform-specific |
| `UV_COMPILE_BYTECODE` | Compile .pyc files | `0` |
| `UV_CONCURRENT_DOWNLOADS` | Max parallel downloads | `50` |
| `UV_CONCURRENT_INSTALLS` | Max parallel installs | `4` |
| `UV_CONFIG_FILE` | Custom config file path | - |
| `UV_EXCLUDE_NEWER` | Exclude packages newer than date | - |
| `UV_EXTRA_INDEX_URL` | Additional package indexes | - |
| `UV_FROZEN` | Equivalent to --frozen | `0` |
| `UV_INDEX_URL` | Primary package index | PyPI |
| `UV_LINK_MODE` | Link mode (hardlink, copy, symlink) | `hardlink` |
| `UV_NO_CACHE` | Disable caching | `0` |
| `UV_NO_PROGRESS` | Disable progress bars | `0` |
| `UV_OFFLINE` | Disable network access | `0` |
| `UV_PREVIEW` | Enable preview features | `0` |
| `UV_PYTHON` | Python version to use | - |
| `UV_PYTHON_PREFERENCE` | Python preference (managed/system) | `managed` |
| `UV_SYSTEM_PYTHON` | Use system Python | `0` |

---

## File Reference

### Files Created by UV

| File | Purpose | Commit? |
|------|---------|---------|
| `.python-version` | Pinned Python version | ✅ Yes |
| `pyproject.toml` | Project configuration | ✅ Yes |
| `uv.lock` | Locked dependency versions | ✅ Yes |
| `.venv/` | Virtual environment | ❌ No |

### Lock File Format

The `uv.lock` file is a TOML file containing:

```toml
version = 1
requires-python = ">=3.11"

[[package]]
name = "requests"
version = "2.32.3"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]

# ... more packages
```

### .python-version Format

```
3.12
```

Or with patch version:

```
3.12.1
```

---

## Related Documentation

- [UV Getting Started](../../../tutorials/python/uv/uv-getting-started.md)
- [UV Comprehensive Guide](../../../tutorials/python/uv/uv_tutorial.md)
- [UV Adoption Rationale](../../../explanation/python/uv/README.md)
- [UV Architecture Deep Dive](../../../explanation/python/uv/uv-architecture.md)
- [Official UV Documentation](https://docs.astral.sh/uv/)
