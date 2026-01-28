# The complete guide to UV: Python's modern package manager

**[← Back to UV Documentation Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Tutorial-blue)

> [!IMPORTANT]
> **Related Docs:** [Getting Started (Beginner)](./uv-getting-started.md) | [Architecture](../../../../explanation/python/uv/uv-architecture.md) | [How-to Guides](../../../../how-to/python/uv/README.md) | [Reference](../../../../reference/python/uv/uv-reference.md)

A progressive tutorial that takes you from first principles to production-grade mastery of `uv`, the modern Python package manager. By the end, you will know how to manage projects, dependencies, workspaces, private registries, Docker builds, CI/CD pipelines, and how to troubleshoot every common issue.

> [!TIP]
> **New to UV?** If you have never used `uv` before, start with the [Getting Started guide](./uv-getting-started.md) first, then return here for the deep dive.

## Table of contents

- [Part I — Fundamentals](#part-i--fundamentals)
  - [1. What is UV and why does it exist?](#1-what-is-uv-and-why-does-it-exist)
  - [2. Core concepts](#2-core-concepts)
  - [3. Installation](#3-installation)
  - [4. Your first project](#4-your-first-project)
  - [5. Managing dependencies](#5-managing-dependencies)
  - [6. Running code with `uv run`](#6-running-code-with-uv-run)
  - [7. The lock file explained](#7-the-lock-file-explained)
  - [8. Python version management](#8-python-version-management)
- [Part II — Intermediate](#part-ii--intermediate)
  - [9. Dependency groups and optional extras](#9-dependency-groups-and-optional-extras)
  - [10. Tool management with `uvx`](#10-tool-management-with-uvx)
  - [11. Inline script metadata (PEP 723)](#11-inline-script-metadata-pep-723)
  - [12. Private registries and custom indexes](#12-private-registries-and-custom-indexes)
  - [13. Platform-specific dependencies](#13-platform-specific-dependencies)
  - [14. Cache management](#14-cache-management)
  - [15. Configuration reference](#15-configuration-reference)
- [Part III — Advanced](#part-iii--advanced)
  - [16. Workspaces and monorepos](#16-workspaces-and-monorepos)
  - [17. Overrides and constraints](#17-overrides-and-constraints)
  - [18. Resolution strategies](#18-resolution-strategies)
  - [19. Building and publishing packages](#19-building-and-publishing-packages)
  - [20. Docker integration](#20-docker-integration)
  - [21. CI/CD integration](#21-cicd-integration)
  - [22. Pre-commit hooks](#22-pre-commit-hooks)
  - [23. Exporting and software bill of materials](#23-exporting-and-software-bill-of-materials)
- [Part IV — Troubleshooting](#part-iv--troubleshooting)
  - [24. Common errors and solutions](#24-common-errors-and-solutions)
  - [25. Debug logging](#25-debug-logging)
  - [26. Environment variables reference](#26-environment-variables-reference)
- [Part V — Best practices and exercises](#part-v--best-practices-and-exercises)
  - [27. Best practices summary](#27-best-practices-summary)
  - [28. Exercises](#28-exercises)
  - [29. Quick reference cheatsheet](#29-quick-reference-cheatsheet)
- [Further reading](#further-reading)

---

# Part I — Fundamentals

## 1. What is UV and why does it exist?

[↑ Back to table of contents](#table-of-contents)

[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package installer and project manager written in Rust. It replaces the following tools with a single binary:

| Traditional tool | What it does | UV equivalent |
|:---|:---|:---|
| `pip` | Install packages | `uv pip install` or `uv add` |
| `pip-tools` | Lock dependencies | `uv lock` |
| `virtualenv` / `venv` | Create environments | `uv venv` (automatic with `uv sync`) |
| `pyenv` | Manage Python versions | `uv python install` |
| `pipx` | Run CLI tools in isolation | `uvx` / `uv tool run` |
| `pip` + `pip-tools` | Dependency compilation and sync | `uv add`, `uv lock`, `uv sync` |
| `twine` | Publish to PyPI | `uv publish` |

### Why UV is fast

UV achieves **10–100x speedups** over pip because:

- **Rust**: The entire resolver, installer, and downloader are native code — no Python runtime overhead.
- **Parallel I/O**: Downloads, builds, and installs happen concurrently.
- **Global cache**: Packages are downloaded once and hardlinked into each project, saving disk space and network bandwidth.
- **PubGrub solver**: A state-of-the-art dependency resolver (the same algorithm used by Dart/Pub) that avoids backtracking in most cases.

### Who builds UV?

**Astral** is the company behind UV. They also created **Ruff**, the Python linter/formatter that achieved similar 100x speedups. Astral is venture-backed and dedicated to high-performance, open-source Python tooling.

---

## 2. Core concepts

[↑ Back to table of contents](#table-of-contents)

Before working with UV, you need to understand four concepts. If you are already familiar with these, skip to [section 3](#3-installation).

### Dependencies

A **dependency** is a library your project needs. When you write `import requests`, the `requests` package is a dependency.

- **Direct dependency**: A package you explicitly add (`uv add requests`).
- **Transitive dependency**: A package your dependency needs (`requests` depends on `urllib3`, `certifi`, and others). UV resolves these automatically.

### Virtual environments

A **virtual environment** is an isolated directory (`.venv/`) containing Python and your project's packages. Each project gets its own environment so dependencies never conflict between projects.

UV creates and manages virtual environments automatically — you rarely need to think about them.

### The lock file

When you add dependencies, UV solves the entire dependency graph and writes exact versions to `uv.lock`. This file guarantees that every developer, CI runner, and production server uses identical packages.

The UV lock file is **universal** — it resolves for all platforms and Python versions simultaneously using environment markers. A single `uv.lock` works on macOS, Linux, and Windows.

### The project file

`pyproject.toml` is the standard Python project configuration file (defined by PEP 621). It stores your project name, version, Python requirement, and dependency list. UV reads and writes this file — you rarely edit it by hand.

---

## 3. Installation

[↑ Back to table of contents](#table-of-contents)

### Install UV

Choose your platform:

**macOS / Linux / WSL:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative methods:**

```bash
# Homebrew (macOS)
brew install uv

# pip (any platform)
pip install uv

# Cargo (Rust toolchain)
cargo install --locked uv

# WinGet (Windows)
winget install --id=astral-sh.uv -e
```

### Verify installation

Restart your terminal, then:

```bash
uv --version
```

Expected output (version may vary):

```text
uv 0.9.27 (Homebrew 2026-01-26)
```

### Enable shell completion

Tab-completion saves time. Add the appropriate line to your shell profile:

```bash
# Bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
uv generate-shell-completion fish > ~/.config/fish/completions/uv.fish
```

Reload your shell (`source ~/.bashrc` or restart the terminal).

### Update UV

If you used the standalone installer:

```bash
uv self update
```

For Homebrew: `brew upgrade uv`. For pip: `pip install --upgrade uv`.

---

## 4. Your first project

[↑ Back to table of contents](#table-of-contents)

### Initialize

```bash
uv init my-app
cd my-app
```

UV creates:

```text
my-app/
├── .gitignore          # Ignores .venv/ and other generated files
├── .python-version     # Pinned Python version (e.g., "3.12")
├── main.py             # Starter script
├── pyproject.toml      # Project configuration
└── README.md           # Project README
```

### Explore `pyproject.toml`

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```

This is the standard Python project format (PEP 621). UV manages it for you.

### Project types

UV supports different project layouts depending on your use case:

```bash
# Application (default) — a script or service you deploy
uv init my-app

# Library with src/ layout — a reusable package others install
uv init --lib my-library

# Packaged application — an app with entry points and src/ layout
uv init --package my-cli-tool

# Minimal — just pyproject.toml, no starter files
uv init --bare my-project
```

### Run the starter script

```bash
uv run main.py
```

Output:

```text
Hello from my-app!
```

The first time you run `uv run`, UV:

1. Downloads the pinned Python version (if not cached)
2. Creates a `.venv/` virtual environment
3. Installs any declared dependencies
4. Runs your script inside that environment

Subsequent runs are nearly instant because everything is cached.

---

## 5. Managing dependencies

[↑ Back to table of contents](#table-of-contents)

### Add a dependency

```bash
uv add requests
```

This single command:

1. Resolves the full dependency graph (finds compatible versions of `requests` and all its transitive dependencies)
2. Updates `pyproject.toml` with the new dependency
3. Creates or updates `uv.lock` with exact pinned versions
4. Installs everything into `.venv/`

Your `pyproject.toml` now contains:

```toml
dependencies = [
    "requests>=2.32.3",
]
```

### Add with version constraints

```bash
uv add "requests>=2.31,<3"       # Range
uv add "flask==3.0.0"            # Exact pin
uv add "pandas~=2.1"             # Compatible release (>=2.1, <3.0)
```

### Add multiple packages

```bash
uv add httpx rich typer
```

### Remove a dependency

```bash
uv remove requests
```

This removes it from `pyproject.toml`, re-resolves the lock file, and uninstalls it from `.venv/`.

### Import from `requirements.txt`

If you are migrating an existing project:

```bash
uv add -r requirements.txt
```

This reads every line in `requirements.txt` and adds them to `pyproject.toml` as proper dependencies.

### Sync the environment

When you clone a project or switch branches:

```bash
uv sync
```

This reads `uv.lock` and makes `.venv/` match it exactly — adding missing packages and removing extras. It also installs your project in editable mode.

---

## 6. Running code with `uv run`

[↑ Back to table of contents](#table-of-contents)

Always use `uv run` to execute code. It ensures the correct Python version and virtual environment are active:

```bash
# Run a script
uv run main.py

# Run Python directly
uv run python -c "import sys; print(sys.version)"

# Run a module
uv run python -m pytest

# Run an installed CLI tool
uv run ruff check .

# Pass arguments after --
uv run -- flask run --port 8080
```

### Why not `python main.py`?

Running `python` directly may use the wrong version, a global installation without your project's packages, or an outdated `.venv/`. `uv run` always verifies the environment is synced before executing.

### Temporary dependencies with `--with`

You can inject extra packages for a single run without adding them to your project:

```bash
uv run --with rich python -c "from rich import print; print('[bold green]Hello![/]')"
```

The `rich` package is available for that run only and does not modify `pyproject.toml`.

### Run with a different Python version

```bash
uv run --python 3.11 main.py
```

UV downloads Python 3.11 if necessary, creates a temporary environment, and runs your script.

---

## 7. The lock file explained

[↑ Back to table of contents](#table-of-contents)

### What `uv.lock` contains

The lock file is a TOML file that records:

- The exact version of every package (direct and transitive)
- The hash of every downloaded artifact
- Platform markers indicating which version applies on which OS/architecture
- The Python version range each resolution applies to

### Why it matters

Without a lock file, `uv add requests` installs the latest compatible version *today*, but a different version *tomorrow*. The lock file freezes the resolution so every environment is identical.

### Lock file commands

```bash
# Create or update the lock file
uv lock

# Upgrade all packages to their latest compatible versions
uv lock --upgrade

# Upgrade a single package
uv lock --upgrade-package requests

# Verify the lock file matches pyproject.toml (useful in CI)
uv lock --check
```

### What to commit

| File | Commit? | Why |
|:---|:---|:---|
| `pyproject.toml` | Yes | Defines your project and dependencies |
| `uv.lock` | Yes | Freezes exact versions for reproducibility |
| `.python-version` | Yes | Ensures consistent Python version |
| `.venv/` | No | Generated locally by `uv sync` |

---

## 8. Python version management

[↑ Back to table of contents](#table-of-contents)

UV can install and manage Python versions — you do not need `pyenv` or system-level installers.

### Install Python

```bash
uv python install 3.12             # Latest 3.12.x
uv python install 3.12.8           # Specific patch
uv python install 3.9 3.10 3.11   # Multiple versions at once
uv python install pypy             # PyPy interpreter
```

### List available versions

```bash
uv python list                     # Installed + available
uv python list --only-installed    # Only what you have
```

### Pin a version for your project

```bash
uv python pin 3.12
```

This writes `3.12` to `.python-version`. When anyone runs `uv sync` or `uv run` in this project, UV uses Python 3.12.

### How Python is stored

UV downloads Python builds to a central cache (`~/.local/share/uv/python/` on Linux). If ten projects all pin Python 3.12, UV stores it once and links to it from each project's `.venv/`. This saves significant disk space.

### Python preference

Control how UV discovers Python via `pyproject.toml`:

```toml
[tool.uv]
python-preference = "managed"         # Default: prefer UV-managed, allow system
# "only-managed"                      # Ignore system Python entirely
# "system"                            # Prefer system Python
# "only-system"                       # Reject UV-managed downloads
```

---

# Part II — Intermediate

## 9. Dependency groups and optional extras

[↑ Back to table of contents](#table-of-contents)

### Development dependencies

Development dependencies (testing, linting, type checking) are packages you need during development but not in production:

```bash
uv add --dev pytest ruff mypy
```

This adds them to the `[dependency-groups]` section:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]
```

### Custom dependency groups (PEP 735)

You can create named groups beyond `dev`:

```bash
uv add --group test pytest coverage
uv add --group lint ruff
uv add --group docs sphinx furo
```

Result in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    { include-group = "test" },
    { include-group = "lint" },
]
test = ["pytest>=8.0", "coverage>=7.0"]
lint = ["ruff>=0.8.0"]
docs = ["sphinx>=7.0", "furo>=2024.0"]
```

### Control what gets installed

```bash
uv sync                             # Installs default groups (dev)
uv sync --all-groups                 # Installs all groups
uv sync --group docs                 # Installs only docs group
uv sync --no-dev                     # Skips dev group
uv sync --no-group docs              # Skips specific group
```

### Configure default groups

By default, `uv sync` installs the `dev` group. You can change this:

```toml
[tool.uv]
default-groups = ["dev", "docs"]     # Sync these by default
# default-groups = "all"             # Sync everything by default
```

### Optional dependencies (extras)

Optional dependencies are features your *users* opt into when installing your package:

```toml
[project.optional-dependencies]
network = ["httpx", "aiohttp"]
database = ["sqlalchemy>=2.0", "asyncpg"]
all = ["my-app[network]", "my-app[database]"]
```

Install extras:

```bash
uv sync --extra network              # Install network extras
uv sync --all-extras                 # Install all extras
```

> [!NOTE]
> **Groups vs. extras**: Use **dependency groups** for development tooling (test, lint, docs). Use **optional extras** for features your package exposes to end users.

---

## 10. Tool management with `uvx`

[↑ Back to table of contents](#table-of-contents)

`uvx` (alias for `uv tool run`) runs Python CLI tools in isolated temporary environments — like `npx` for Python. This replaces `pipx`.

### Run a tool without installing it

```bash
uvx ruff check .                     # Run ruff linter
uvx black .                          # Run black formatter
uvx mypy src/                        # Run type checker
uvx pycowsay "Hello UV!"            # Fun example
```

Each invocation creates a temporary environment, installs the tool, runs it, then cleans up. Subsequent runs reuse a cached environment.

### Specify a version

```bash
uvx ruff@0.8.0 check .              # Exact version
uvx ruff@latest check .             # Force latest
```

### When package name differs from command

```bash
uvx --from httpie http GET https://httpbin.org/get
uvx --from 'ruff>=0.8,<0.9' ruff check .
```

### Install tools persistently

If you use a tool frequently, install it permanently:

```bash
uv tool install ruff
uv tool install --python 3.12 mypy   # Pin to specific Python
uv tool upgrade ruff                  # Upgrade
uv tool upgrade --all                 # Upgrade all tools
uv tool list                          # List installed tools
uv tool uninstall ruff                # Remove
```

Installed tools are placed on your `PATH` (in `~/.local/bin/` by default).

---

## 11. Inline script metadata (PEP 723)

[↑ Back to table of contents](#table-of-contents)

PEP 723 allows you to declare dependencies directly inside a Python script. This is ideal for single-file utilities, quick experiments, and shareable scripts.

### Create a script with inline metadata

```bash
uv init --script weather.py --python 3.12
uv add --script weather.py httpx rich
```

This generates:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "rich",
# ]
# ///

import httpx
from rich import print

def main():
    response = httpx.get("https://wttr.in/London?format=j1")
    data = response.json()
    temp = data["current_condition"][0]["temp_C"]
    desc = data["current_condition"][0]["weatherDesc"][0]["value"]
    print(f"[bold blue]London[/]: {temp}C, {desc}")

if __name__ == "__main__":
    main()
```

### Run the script

```bash
uv run weather.py
```

UV reads the `# /// script` block, creates a temporary environment with the declared dependencies, and runs the script. No `pyproject.toml` or `uv.lock` needed.

### Lock a script for reproducibility

```bash
uv lock --script weather.py
```

This creates `weather.py.lock` alongside the script, pinning exact versions.

### Make a script executable (shebang)

Add this as the first line of your script:

```python
#!/usr/bin/env -S uv run --script
```

Then:

```bash
chmod +x weather.py
./weather.py
```

---

## 12. Private registries and custom indexes

[↑ Back to table of contents](#table-of-contents)

Enterprise environments often host internal Python packages on private registries.

### Configure a private index

Add to `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://pypi.internal.company.com/simple/"
```

UV searches this index *in addition to* PyPI when resolving dependencies.

### Pin a package to a specific index

Use `explicit = true` to restrict an index to packages that explicitly reference it:

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch" }
```

Now `torch` only resolves from the PyTorch index, while all other packages resolve from PyPI.

### Replace PyPI as the default

```toml
[[tool.uv.index]]
name = "company-pypi"
url = "https://pypi.company.com/simple/"
default = true
```

### Authentication

**Environment variables** (recommended for CI):

```bash
export UV_INDEX_INTERNAL_USERNAME=myuser
export UV_INDEX_INTERNAL_PASSWORD=mytoken
```

**Keyring integration** (for local development):

```bash
uv sync --keyring-provider auto
```

**Always authenticate** (skip anonymous attempt):

```toml
[[tool.uv.index]]
name = "private"
url = "https://private.company.com/simple/"
authenticate = "always"
```

> [!WARNING]
> Credentials are **never** stored in `uv.lock`. Use environment variables or a keyring — never embed passwords in `pyproject.toml`.

### Index strategy

The default strategy (`first-index`) stops searching once the first index returns a package. This prevents **dependency confusion attacks** where a malicious package on PyPI has the same name as your internal package.

```bash
# Default: safest — use first index that has the package
uv sync --index-strategy first-index

# Search all indexes for the best version (less safe)
uv sync --index-strategy unsafe-best-match
```

---

## 13. Platform-specific dependencies

[↑ Back to table of contents](#table-of-contents)

UV supports PEP 508 environment markers to declare dependencies that only apply on certain platforms:

```bash
uv add "pywin32; sys_platform == 'win32'"
uv add "uvloop; sys_platform == 'linux'"
uv add "numpy; python_version >= '3.11'"
```

In `pyproject.toml`, these appear as:

```toml
dependencies = [
    "pywin32; sys_platform == 'win32'",
    "uvloop; sys_platform == 'linux'",
    "numpy; python_version >= '3.11'",
]
```

### Restrict resolution to specific platforms

If your project only runs on Linux and macOS, you can tell UV to skip Windows resolution entirely:

```toml
[tool.uv]
environments = [
    "sys_platform == 'linux'",
    "sys_platform == 'darwin'",
]
```

This makes `uv lock` faster and `uv.lock` smaller because it skips Windows-only variants.

---

## 14. Cache management

[↑ Back to table of contents](#table-of-contents)

UV uses a global cache to avoid re-downloading and re-building packages. Understanding the cache helps you troubleshoot and optimize.

### Cache location

| Platform | Default location |
|:---|:---|
| Linux | `~/.cache/uv/` |
| macOS | `~/Library/Caches/uv/` |
| Windows | `%LOCALAPPDATA%\uv\cache` |

Override with `UV_CACHE_DIR` or `--cache-dir`.

### Cache commands

```bash
uv cache dir                         # Show cache location
uv cache clean                       # Remove ALL cached packages
uv cache clean requests              # Remove cache for one package
uv cache prune                       # Remove outdated entries only
uv cache prune --ci                  # Aggressive prune for CI (keeps locally-built wheels)
```

### Force revalidation

When you suspect a cached package is stale:

```bash
uv sync --refresh                    # Revalidate all cached packages
uv sync --refresh-package requests   # Revalidate one package
```

> [!TIP]
> The cache is thread-safe and supports concurrent access from multiple UV processes. You can safely run `uv sync` in parallel across multiple projects.

---

## 15. Configuration reference

[↑ Back to table of contents](#table-of-contents)

UV reads configuration from three places, in order of precedence:

1. **Command-line flags** (highest priority)
2. **Environment variables** (e.g., `UV_CACHE_DIR`)
3. **Project config** (`pyproject.toml` `[tool.uv]` section or `uv.toml` in project root)
4. **User config** (`~/.config/uv/uv.toml`)
5. **System config** (`/etc/uv/uv.toml`)

### Example `[tool.uv]` configuration

```toml
[tool.uv]
# Python management
python-preference = "managed"
python-downloads = "automatic"

# Resolution behavior
resolution = "latest"
exclude-newer = "2026-01-15T00:00:00Z"    # Reproducibility cutoff

# Default groups to sync
default-groups = ["dev"]

# Platform restrictions
environments = [
    "sys_platform == 'linux'",
    "sys_platform == 'darwin'",
]

# Workspace configuration
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]

# Package indexes
[[tool.uv.index]]
name = "internal"
url = "https://pypi.company.com/simple/"
```

### Standalone `uv.toml`

You can use a `uv.toml` file instead of `[tool.uv]` in `pyproject.toml`. The syntax is the same but without the `tool.uv` prefix:

```toml
python-preference = "managed"
default-groups = ["dev"]

[[index]]
name = "internal"
url = "https://pypi.company.com/simple/"
```

> [!NOTE]
> When both `uv.toml` and `pyproject.toml` `[tool.uv]` exist, `uv.toml` takes precedence.

---

# Part III — Advanced

## 16. Workspaces and monorepos

[↑ Back to table of contents](#table-of-contents)

Workspaces let you manage multiple related packages in a single repository with a shared lock file. This is the pattern used by this repository (`dbtools`).

### Set up a workspace

In your root `pyproject.toml`:

```toml
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["packages/*", "libs/*"]
exclude = ["packages/experimental"]
```

Every directory matched by `members` must contain its own `pyproject.toml`.

### Directory structure

```text
my-monorepo/
├── pyproject.toml          # Root workspace config
├── uv.lock                 # Single lock file for all members
├── packages/
│   ├── api-server/
│   │   ├── pyproject.toml  # Member: depends on shared-lib
│   │   └── src/
│   └── worker/
│       ├── pyproject.toml  # Member: depends on shared-lib
│       └── src/
└── libs/
    └── shared-lib/
        ├── pyproject.toml  # Member: reusable library
        └── src/
```

### Declare inter-member dependencies

In `packages/api-server/pyproject.toml`:

```toml
[project]
name = "api-server"
dependencies = ["shared-lib"]

[tool.uv.sources]
shared-lib = { workspace = true }
```

The `workspace = true` source tells UV to resolve `shared-lib` from the workspace instead of PyPI. Workspace members are always installed in editable mode.

### Workspace commands

```bash
# Lock the entire workspace (single uv.lock)
uv lock

# Sync the entire workspace
uv sync

# Sync only a specific member
uv sync --package api-server

# Run a command in a specific member's context
uv run --package api-server python -m api_server

# Build a specific member
uv build --package shared-lib
```

### Key characteristics

- A single `uv.lock` covers the entire workspace.
- `requires-python` for the workspace is the intersection of all members.
- Root-level `[tool.uv.sources]` apply to all members unless overridden.
- Workspaces are not suited for members with fundamentally conflicting requirements — use separate lock files or path dependencies instead.

---

## 17. Overrides and constraints

[↑ Back to table of contents](#table-of-contents)

### Constraints

Constraints narrow the acceptable versions of a package *without* adding it as a dependency. Use them when a transitive dependency has a known bug in certain versions:

```toml
[tool.uv]
constraint-dependencies = [
    "grpcio<1.65",
    "numpy>=1.24,<2.0",
]
```

If nothing in your project depends on `grpcio`, the constraint has no effect. If something does, UV respects the narrower range.

### Overrides

Overrides replace a package's declared dependencies entirely. This is an escape hatch for upstream packages with incorrect metadata (e.g., unnecessarily restrictive upper bounds):

```toml
[tool.uv]
override-dependencies = [
    "werkzeug==2.3.0",
    "pydantic>=1.0,<3",
]
```

> [!CAUTION]
> Overrides bypass the solver's safety checks. Use them only when you are certain the override is compatible. Document why each override exists.

### When to use each

| Scenario | Use |
|:---|:---|
| Avoid a broken version of a transitive dependency | Constraint |
| Force an older version for security patching | Constraint |
| Work around an upstream package with a too-tight upper bound | Override |
| Pin a shared dependency across the workspace | Constraint |

---

## 18. Resolution strategies

[↑ Back to table of contents](#table-of-contents)

### Resolution modes

```bash
uv lock --resolution latest          # Default: newest compatible versions
uv lock --resolution lowest          # Oldest compatible versions
uv lock --resolution lowest-direct   # Oldest for direct deps, newest for transitive
```

**When to use `lowest`**: If you maintain a library and want to test that your declared minimum versions actually work, `lowest` forces the resolver to select the lowest compatible version of every dependency.

### Reproducibility with `exclude-newer`

Lock only packages published before a given date:

```bash
uv lock --exclude-newer 2026-01-01
```

Or in `pyproject.toml`:

```toml
[tool.uv]
exclude-newer = "2026-01-01T00:00:00Z"
```

This is useful for auditable builds where you need to guarantee no package published after a cutoff date enters the lock file.

### Declaring conflicts

If your project has mutually exclusive extras (e.g., CPU vs. GPU), declare them:

```toml
[tool.uv]
conflicts = [
    [
        { extra = "cpu" },
        { extra = "gpu" },
    ],
]
```

This prevents UV from trying to resolve both simultaneously.

---

## 19. Building and publishing packages

[↑ Back to table of contents](#table-of-contents)

### Build your package

```bash
uv build                             # Build both sdist and wheel to dist/
uv build --sdist                     # Source distribution only
uv build --wheel                     # Wheel only
uv build --package my-lib            # Build a specific workspace member
```

### Publish to PyPI

```bash
uv publish                           # Publish to PyPI
uv publish --token "$PYPI_TOKEN"     # Explicit token
uv publish --index testpypi          # Publish to TestPyPI
```

### Configure publishing indexes

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

### Prevent accidental public publishing

For internal packages that should never be uploaded to PyPI:

```toml
[project]
classifiers = ["Private :: Do Not Upload"]
```

### Test the built package

```bash
uv run --with dist/my_lib-1.0.0-py3-none-any.whl --no-project -- python -c "import my_lib; print(my_lib.__version__)"
```

---

## 20. Docker integration

[↑ Back to table of contents](#table-of-contents)

UV's speed makes Docker builds significantly faster. The key technique is **layer caching** — install dependencies in an early layer (cached when only source code changes) and copy source code in a later layer.

### Optimized Dockerfile

```dockerfile
FROM python:3.12-slim-bookworm

# Install UV from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /uvx /bin/

WORKDIR /app

# Configure UV for Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Layer 1: Install dependencies (cached when only source code changes)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Layer 2: Copy source and install the project itself
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Activate the virtual environment via PATH
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "my_app"]
```

### Multi-stage build (smaller final image)

For production, use a multi-stage build so UV is not included in the final image:

```dockerfile
# --- Builder stage ---
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

# --- Runtime stage ---
FROM python:3.12-slim-bookworm
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY . /app
CMD ["python", "-m", "my_app"]
```

### Key environment variables for Docker

| Variable | Value | Purpose |
|:---|:---|:---|
| `UV_COMPILE_BYTECODE` | `1` | Compiles `.pyc` files for faster startup |
| `UV_LINK_MODE` | `copy` | Required when using cache mounts (separate filesystem) |

> [!IMPORTANT]
> Add `.venv` to your `.dockerignore` file so local environments are not copied into the build context.

---

## 21. CI/CD integration

[↑ Back to table of contents](#table-of-contents)

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v7
        with:
          version: "0.9.27"
          python-version: ${{ matrix.python-version }}
          enable-cache: true

      - run: uv sync --locked --all-extras --dev
      - run: uv run pytest tests/
      - run: uv run ruff check .

  publish:
    runs-on: ubuntu-latest
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - run: uv publish
```

### GitLab CI

```yaml
variables:
  UV_VERSION: "0.9.27"
  UV_CACHE_DIR: .uv-cache
  UV_LINK_MODE: copy

image: ghcr.io/astral-sh/uv:${UV_VERSION}-python3.12-bookworm-slim

cache:
  key:
    files:
      - uv.lock
  paths:
    - $UV_CACHE_DIR

stages:
  - test
  - lint

test:
  stage: test
  script:
    - uv sync --locked --all-extras --dev
    - uv run pytest tests/
    - uv cache prune --ci

lint:
  stage: lint
  script:
    - uv sync --locked --group lint
    - uv run ruff check .
```

### Key CI patterns

- **Always use `--locked`** in CI. This fails the build if the lock file is outdated, catching the mistake immediately.
- **Cache `uv.lock`-keyed caches**. Use the lock file as the cache key so the cache invalidates when dependencies change.
- **Use `uv cache prune --ci`** at the end of jobs to reduce cache size (removes pre-built wheels, keeps locally-built ones).

---

## 22. Pre-commit hooks

[↑ Back to table of contents](#table-of-contents)

UV provides official pre-commit hooks to keep your lock file and exports in sync:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.9.27
    hooks:
      # Verify uv.lock is up-to-date
      - id: uv-lock

      # Export requirements.txt from the lock file
      - id: uv-export
        args: [
          "--format", "requirements-txt",
          "--no-hashes",
          "-o", "requirements.txt"
        ]
```

The `uv-lock` hook ensures that every commit has a valid lock file — if someone edits `pyproject.toml` without running `uv lock`, the hook catches it.

---

## 23. Exporting and software bill of materials

[↑ Back to table of contents](#table-of-contents)

### Export to `requirements.txt`

For tools or environments that require the traditional format:

```bash
uv export --format requirements-txt > requirements.txt
uv export --format requirements-txt --no-hashes > requirements.txt
```

### Export to PEP 751 (`pylock.toml`)

```bash
uv export --format pylock.toml --output-file pylock.toml
```

### Generate a CycloneDX SBOM

For security and compliance audits:

```bash
uv export --format cyclonedx1.5 > sbom.json
```

This produces a Software Bill of Materials (SBOM) in the CycloneDX format listing every dependency with version and hash.

---

# Part IV — Troubleshooting

## 24. Common errors and solutions

[↑ Back to table of contents](#table-of-contents)

### "No `pyproject.toml` found"

**Cause**: You ran a UV command outside a project directory.

**Solution**: Navigate to your project root or initialize one:

```bash
cd /path/to/your/project
# or
uv init
```

### "No solution found" (dependency conflict)

**Cause**: Two or more packages require incompatible versions of a shared dependency.

**Solution**:

1. Read the error message — UV shows exactly which packages conflict.
2. Try relaxing version constraints in `pyproject.toml`.
3. Use `uv lock --resolution lowest` to see if floor versions work.
4. As a last resort, add an override:

```toml
[tool.uv]
override-dependencies = [
    "conflicting-package>=1.0,<3.0",
]
```

### "Locked versions are not up to date"

**Cause**: Someone edited `pyproject.toml` without running `uv lock`.

**Solution**:

```bash
uv lock
```

Then commit the updated `uv.lock`.

### Python version mismatch

**Cause**: `.python-version` specifies a version not matching `requires-python` in `pyproject.toml`.

**Solution**:

```bash
# Check what's pinned
cat .python-version

# Update the pin
uv python pin 3.12
```

### Missing `.venv` after cloning

**Cause**: `.venv/` is (correctly) not committed to Git.

**Solution**:

```bash
uv sync
```

This recreates the environment from the lock file.

### Package builds fail on your platform

**Cause**: A source distribution requires a C compiler or system library you don't have.

**Solution**:

1. Install the system dependency (e.g., `libpq-dev` for `psycopg2`).
2. Use a binary-only package (e.g., `psycopg2-binary` instead of `psycopg2`).
3. Provide pre-built metadata to skip the build:

```toml
[tool.uv]
no-build-package = ["problematic-package"]
```

### Cache seems stale

**Cause**: A cached package is outdated or corrupted.

**Solution**:

```bash
# Refresh one package
uv sync --refresh-package requests

# Refresh everything
uv sync --refresh

# Nuclear option: clear all cache
uv cache clean
```

### Proxy or network issues

**Cause**: Corporate proxy or firewall blocking downloads.

**Solution**:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
uv sync
```

For fully offline environments:

```bash
UV_OFFLINE=1 uv sync --frozen
```

### Lock file keeps changing across platforms

**Cause**: This is expected behavior. The lock file is universal but records platform-specific variants. If a contributor on macOS and another on Linux both run `uv lock`, the file may differ in marker ordering.

**Solution**: Designate one platform (or CI) as the canonical lock source. Run `uv lock` in CI and commit the result, or agree on a single platform for locking.

---

## 25. Debug logging

[↑ Back to table of contents](#table-of-contents)

When standard error messages are not enough:

```bash
# Verbose output (shows resolution steps)
uv sync -v

# Very verbose (shows HTTP requests)
uv sync -vv

# Rust-level debug logging (maximum detail)
RUST_LOG=debug uv sync
```

The `RUST_LOG=debug` output includes the PubGrub solver's decision tree, which is invaluable when diagnosing resolution failures.

---

## 26. Environment variables reference

[↑ Back to table of contents](#table-of-contents)

The most commonly used environment variables:

| Variable | Purpose | Example |
|:---|:---|:---|
| `UV_CACHE_DIR` | Override cache location | `/tmp/uv-cache` |
| `UV_LINK_MODE` | Package linking mode | `copy` (required in Docker) |
| `UV_COMPILE_BYTECODE` | Compile `.pyc` files on install | `1` |
| `UV_PYTHON` | Default Python interpreter | `3.12` |
| `UV_SYSTEM_PYTHON` | Use system Python for `uv pip` | `1` |
| `UV_PROJECT_ENVIRONMENT` | Custom `.venv` path | `/opt/venv` |
| `UV_FROZEN` | Use lockfile without checking | `1` |
| `UV_LOCKED` | Fail if lockfile is outdated | `1` |
| `UV_NO_SYNC` | Skip auto-sync on `uv run` | `1` |
| `UV_NO_DEV` | Exclude dev dependencies | `1` |
| `UV_OFFLINE` | Disable all network access | `1` |
| `UV_DEFAULT_INDEX` | Default package index URL | `https://pypi.company.com/simple/` |
| `UV_INDEX` | Additional index URLs | `https://extra.index.com/simple/` |
| `UV_EXCLUDE_NEWER` | Package date cutoff | `2026-01-01T00:00:00Z` |
| `UV_HTTP_TIMEOUT` | HTTP request timeout (seconds) | `60` |
| `UV_CONCURRENT_DOWNLOADS` | Max parallel downloads | `8` |
| `UV_PUBLISH_TOKEN` | PyPI publish token | `pypi-AgEI...` |
| `UV_TORCH_BACKEND` | PyTorch accelerator backend | `auto`, `cpu`, `cu126` |
| `UV_NO_PROGRESS` | Suppress progress bars | `1` |
| `UV_ENV_FILE` | `.env` file paths for `uv run` | `.env.local` |
| `UV_NATIVE_TLS` | Use system TLS certificates | `1` |

UV also reads `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `SSL_CERT_FILE`, and `SSL_CERT_DIR` from the environment.

---

# Part V — Best practices and exercises

## 27. Best practices summary

[↑ Back to table of contents](#table-of-contents)

### Project setup

1. **Always use `uv init`** for new projects. It generates the correct structure (`pyproject.toml`, `.python-version`, `.gitignore`).
2. **Pin your Python version** with `uv python pin`. This prevents accidental upgrades.
3. **Choose the right project type**: `--lib` for libraries, `--package` for CLIs, default for applications.

### Dependencies

4. **Always commit `uv.lock`**. This is the single most important practice for reproducible builds.
5. **Use dependency groups** for development tools (`--group test`, `--group lint`, `--group docs`). Keep production dependencies minimal.
6. **Use `uv add`, not manual edits**. Let UV manage `pyproject.toml` to avoid syntax mistakes and ensure the lock file stays in sync.

### Daily workflow

7. **Use `uv run` for everything**. Never manually activate `.venv/`. `uv run` guarantees the environment is synced.
8. **Use `uvx` for CLI tools** like `ruff`, `black`, `mypy`. This keeps them isolated from your project.
9. **Run `uv sync` after pulling** from Git to pick up dependency changes.

### Team and CI

10. **Use `--locked` in CI**. This fails the build if the lock file is outdated, catching mistakes immediately.
11. **Use `--frozen` in Docker**. This uses the lock file without checking `pyproject.toml`, which is faster and more predictable.
12. **Cache aggressively**. Use `uv cache prune --ci` to keep CI caches lean.

### Security

13. **Use the default `first-index` strategy** to prevent dependency confusion attacks.
14. **Use `exclude-newer`** for auditable builds where you need a date cutoff.
15. **Generate SBOMs** with `uv export --format cyclonedx1.5` for compliance reporting.

---

## 28. Exercises

[↑ Back to table of contents](#table-of-contents)

### Exercise 1: Build a CLI tool

Create a project that uses `typer` to build a command-line greeting tool.

**Requirements:**

1. Initialize a packaged project with `uv init --package greeter`
2. Add `typer` as a dependency and `pytest` as a dev dependency
3. Write a `greet` command that accepts a `--name` flag
4. Write a test that verifies the output
5. Run the tool and tests with `uv run`

<details>
<summary>Solution</summary>

```bash
uv init --package greeter
cd greeter
uv add typer
uv add --dev pytest
```

Edit `src/greeter/__init__.py`:

```python
import typer

app = typer.Typer()

@app.command()
def greet(name: str = "World"):
    """Greet someone by name."""
    print(f"Hello, {name}!")

def main():
    app()
```

Edit `tests/test_greeter.py`:

```python
from typer.testing import CliRunner
from greeter import app

runner = CliRunner()

def test_greet_default():
    result = runner.invoke(app, [])
    assert "Hello, World!" in result.stdout

def test_greet_name():
    result = runner.invoke(app, ["--name", "Alice"])
    assert "Hello, Alice!" in result.stdout
```

Run:

```bash
uv run greeter greet --name Alice
uv run pytest
```

</details>

### Exercise 2: Set up a workspace

Create a monorepo with two packages: a shared library and an application that uses it.

**Requirements:**

1. Create a root project with a workspace containing `libs/mathlib` and `apps/calculator`
2. `mathlib` exports an `add(a, b)` function
3. `calculator` depends on `mathlib` (workspace source) and uses it
4. Run the calculator with `uv run --package calculator`

<details>
<summary>Solution</summary>

```bash
mkdir my-workspace && cd my-workspace
uv init
mkdir -p libs/mathlib/src/mathlib apps/calculator/src/calculator
```

Edit root `pyproject.toml`:

```toml
[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["libs/*", "apps/*"]
```

Create `libs/mathlib/pyproject.toml`:

```toml
[project]
name = "mathlib"
version = "0.1.0"
requires-python = ">=3.12"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Create `libs/mathlib/src/mathlib/__init__.py`:

```python
def add(a: float, b: float) -> float:
    return a + b
```

Create `apps/calculator/pyproject.toml`:

```toml
[project]
name = "calculator"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["mathlib"]

[tool.uv.sources]
mathlib = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Create `apps/calculator/src/calculator/__init__.py`:

```python
from mathlib import add

def main():
    result = add(2, 3)
    print(f"2 + 3 = {result}")

if __name__ == "__main__":
    main()
```

Run:

```bash
uv sync
uv run --package calculator python -m calculator
```

Output: `2 + 3 = 5`

</details>

### Exercise 3: Inline script with PEP 723

Write a single-file script that fetches a random joke from an API and prints it with colored output — using only inline script metadata (no `pyproject.toml`).

<details>
<summary>Solution</summary>

```bash
uv init --script joke.py --python 3.12
uv add --script joke.py httpx rich
```

Edit `joke.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "rich",
# ]
# ///

import httpx
from rich.console import Console

console = Console()

def main():
    response = httpx.get(
        "https://official-joke-api.appspot.com/random_joke"
    )
    joke = response.json()
    console.print(f"[bold cyan]{joke['setup']}[/]")
    console.print(f"[bold green]{joke['punchline']}[/]")

if __name__ == "__main__":
    main()
```

Run:

```bash
uv run joke.py
```

</details>

---

## 29. Quick reference cheatsheet

[↑ Back to table of contents](#table-of-contents)

### Project lifecycle

| Command | Description |
|:---|:---|
| `uv init` | Create a new project |
| `uv init --lib` | Create a library (src/ layout) |
| `uv init --package` | Create a packaged application |
| `uv add <pkg>` | Add a dependency |
| `uv add --dev <pkg>` | Add a development dependency |
| `uv add --group <name> <pkg>` | Add to a named group |
| `uv remove <pkg>` | Remove a dependency |
| `uv sync` | Sync `.venv/` with lock file |
| `uv sync --locked` | Sync (fail if lock file outdated) |
| `uv sync --frozen` | Sync (skip lock file check) |
| `uv lock` | Create or update the lock file |
| `uv lock --upgrade` | Upgrade all packages |
| `uv lock --check` | Verify lock file is current |
| `uv run <cmd>` | Run a command in the project environment |
| `uv run --with <pkg> <cmd>` | Run with a temporary extra dependency |
| `uv version` | Show project version |
| `uv version --bump minor` | Bump the project version |

### Python management

| Command | Description |
|:---|:---|
| `uv python install <ver>` | Install a Python version |
| `uv python list` | List installed and available versions |
| `uv python pin <ver>` | Pin project to a Python version |
| `uv python find <constraint>` | Find a matching interpreter |

### Tools

| Command | Description |
|:---|:---|
| `uvx <tool>` | Run a tool in a temporary environment |
| `uv tool install <tool>` | Install a tool persistently |
| `uv tool upgrade <tool>` | Upgrade a tool |
| `uv tool list` | List installed tools |

### Building and publishing

| Command | Description |
|:---|:---|
| `uv build` | Build sdist + wheel |
| `uv publish` | Publish to PyPI |
| `uv export --format requirements-txt` | Export lock file to requirements.txt |
| `uv export --format cyclonedx1.5` | Generate SBOM |

### Cache and maintenance

| Command | Description |
|:---|:---|
| `uv cache dir` | Show cache location |
| `uv cache clean` | Clear all cache |
| `uv cache prune` | Remove stale entries |
| `uv self update` | Update UV itself |

---

## Further reading

[↑ Back to table of contents](#table-of-contents)

| Resource | Description |
|:---|:---|
| [Official UV documentation](https://docs.astral.sh/uv/) | Complete reference from Astral |
| [UV GitHub repository](https://github.com/astral-sh/uv) | Source code, issues, and changelog |
| [UV changelog](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md) | Detailed version history |
| [Getting Started guide](./uv-getting-started.md) | Beginner-focused first steps |
| [UV Architecture](../../../../explanation/python/uv/uv-architecture.md) | How UV works internally |
| [Migration Guide](../../../../how-to/python/uv/uv-migrate-from-pip.md) | Move from pip to UV |
| [Docker Integration](../../../../how-to/python/uv/uv-docker-integration.md) | Detailed Docker patterns |
| [CI/CD Integration](../../../../how-to/python/uv/uv-ci-cd-integration.md) | Pipeline recipes |
| [Command Reference](../../../../reference/python/uv/uv-reference.md) | Full command documentation |
