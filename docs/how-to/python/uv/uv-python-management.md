# How to Manage Python Versions with UV

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Environment-green)

> [!IMPORTANT]
> **Related Docs:** [Interactive Python](./uv-interactive-python.md) | [Tool Management](./uv-tool-management.md) | [UV Reference](../../../reference/python/uv/uv-reference.md)

`uv` simplifies installing and managing Python versions, replacing tools like `pyenv`.

## Table of contents

- [Quick start (recommended workflow)](#quick-start-recommended-workflow)
- [Install Python versions](#install-python-versions)
- [List available versions](#list-available-versions)
- [Pin a project to a specific version](#pin-a-project-to-a-specific-version)
- [Make Python globally available](#make-python-globally-available)
- [Upgrade Python versions](#upgrade-python-versions)
- [Uninstall Python versions](#uninstall-python-versions)
- [Free-threaded Python (no-GIL)](#free-threaded-python-no-gil)
- [Best practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

---

## Quick start (recommended workflow)

For most users, this is the recommended approach:

```bash
# 1. Update uv to get the latest Python version support
uv self update

# 2. Install the Python version you need
uv python install 3.14

# 3. Pin it to your project
uv python pin 3.14

# 4. Sync your environment
uv sync

# 5. Run commands through uv (always use this pattern)
uv run python --version
uv run pytest
```

**Why this approach?**

- **Reproducible**: The `.python-version` file is committed to git, ensuring all contributors use the same version
- **Isolated**: Doesn't affect other projects or system Python
- **No PATH manipulation**: Works immediately without shell configuration changes
- **Consistent**: Aligns with uv's philosophy of managing everything (Python + dependencies)

---

## Install Python versions

### Install a specific version

Download and install a managed Python version:

```bash
uv python install 3.14
```

### Install multiple versions

Install multiple versions side-by-side:

```bash
uv python install 3.12 3.13 3.14
```

### Install an exact patch version

```bash
uv python install 3.14.0
```

### Install preview/beta versions

For alpha, beta, or release candidate versions:

```bash
uv python install --preview 3.15
```

### Compile bytecode during installation

For faster startup times (larger disk usage):

```bash
uv python install 3.14 --compile-bytecode
```

---

## List available versions

### See installed versions

```bash
uv python list --only-installed
```

### See all available versions

```bash
uv python list
```

Example output:

```
cpython-3.14.0-linux-x86_64-gnu                 /home/user/.local/share/uv/python/cpython-3.14.0-linux-x86_64-gnu/bin/python
cpython-3.13.1-linux-x86_64-gnu                 /home/user/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/bin/python
cpython-3.14.0+freethreaded-linux-x86_64-gnu    <download available>
```

### Filter by version

```bash
uv python list | grep 3.14
```

---

## Pin a project to a specific version

Pinning creates a `.python-version` file that tells uv which Python to use for this project.

### Pin for the current project

```bash
uv python pin 3.14
```

This creates a `.python-version` file containing `3.14`. Commit this file to git.

### Verify the pinned version

```bash
cat .python-version
# Output: 3.14
```

### How pinning works

When you run `uv sync` or `uv run`, uv:

1. Reads `.python-version`
2. Uses the specified Python version
3. If not installed, prompts to install it

---

## Make Python globally available

By default, uv installs Python to its managed cache but doesn't create global `python` or `python3` commands. Here are your options:

### Option A: Use `uv run` everywhere (recommended)

The cleanest approach—always prefix commands with `uv run`:

```bash
uv run python script.py
uv run python -c "print('Hello')"
```

### Option B: Install with `--default` flag

Creates symlinks (`python`, `python3`, `python3.14`) in `~/.local/bin`:

```bash
uv python install 3.14 --default
```

> [!NOTE]
> The `--default` option requires `--preview` on some uv versions:
> ```bash
> uv python install 3.14 --default --preview
> ```

### Option C: Create a global pin

Set a global default Python version:

```bash
uv python pin --global 3.14
```

This creates `~/.python-version`, which uv uses as fallback when no project-level pin exists.

### Option D: Manual PATH configuration

Add uv's Python directory to your PATH in `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/share/uv/python/cpython-3.14.0-linux-x86_64-gnu/bin:$PATH"
```

---

## Upgrade Python versions

### Upgrade to latest patch version

When a new patch release is available (e.g., 3.14.0 → 3.14.1):

```bash
uv python upgrade 3.14
```

> [!NOTE]
> The upgrade command is in preview. Enable it with:
> ```bash
> uv python upgrade 3.14 --preview
> ```

### Upgrade with bytecode compilation

```bash
uv python upgrade 3.14 --compile-bytecode
```

---

## Uninstall Python versions

### Remove a specific version

```bash
uv python uninstall 3.12
```

### Remove all managed Python versions

```bash
uv python uninstall --all
```

---

## Free-threaded Python (no-GIL)

Python 3.13+ includes experimental free-threaded builds that disable the Global Interpreter Lock (GIL), enabling true multi-threaded parallelism.

### Understanding free-threaded Python

- **Python 3.13**: Free-threaded is experimental, requires explicit opt-in
- **Python 3.14+**: Free-threaded is no longer experimental, though GIL-enabled is still preferred by default

### Install free-threaded Python

Append `t` to the version number:

```bash
# Install free-threaded Python 3.14
uv python install 3.14t

# Or use the full specifier
uv python install cpython-3.14.0+freethreaded-linux-x86_64-gnu
```

### Run with free-threaded Python

```bash
# Using uvx
uvx [email protected] script.py

# Or pin to free-threaded version
uv python pin 3.14t
uv run python script.py
```

### When to use free-threaded Python

- CPU-bound parallel workloads
- Testing library compatibility with no-GIL Python
- Benchmarking multi-threaded performance

> [!WARNING]
> Many packages don't yet support free-threaded Python. Check compatibility before using in production.

---

## Best practices

### 1. Always use `uv run` for project commands

```bash
# Good: Uses project's pinned Python and dependencies
uv run python script.py
uv run pytest

# Avoid: May use wrong Python or miss dependencies
python script.py
pytest
```

### 2. Pin Python version in projects

```bash
uv python pin 3.14
git add .python-version
git commit -m "Pin Python 3.14"
```

### 3. Keep uv updated

New Python releases require updated uv:

```bash
uv self update
```

### 4. Use `uv sync` after cloning

When joining a project or cloning a repo:

```bash
git clone https://github.com/org/repo
cd repo
uv sync  # Creates .venv and installs pinned Python + dependencies
```

### 5. Specify Python version in `pyproject.toml`

```toml
[project]
requires-python = ">=3.12"
```

### 6. Create projects with explicit Python version

```bash
uv init my-project --python 3.14
```

---

## Troubleshooting

### "Command 'python' not found"

**Cause**: uv doesn't create global `python` symlinks by default.

**Solutions**:

1. Use `uv run python` instead of `python`
2. Install with `--default`: `uv python install 3.14 --default`
3. Pin globally: `uv python pin --global 3.14`

### "No Python found matching version X.Y"

**Cause**: The version isn't installed.

**Solution**:

```bash
uv python install 3.14
```

### "Python version not available"

**Cause**: uv is outdated.

**Solution**:

```bash
uv self update
uv python list  # Verify version is available
```

### Virtual environment uses wrong Python

**Cause**: `.python-version` doesn't match or is missing.

**Solution**:

```bash
uv python pin 3.14
rm -rf .venv
uv sync
```

### Can't find free-threaded Python

**Cause**: Free-threaded builds require explicit suffix.

**Solution**:

```bash
uv python install 3.14t  # Note the 't' suffix
```

---

## Reference

### Command summary

| Command | Description |
|---------|-------------|
| `uv python install 3.14` | Install Python 3.14 |
| `uv python install 3.14 --default` | Install and make globally available |
| `uv python install 3.14t` | Install free-threaded build |
| `uv python list` | List available Python versions |
| `uv python list --only-installed` | List installed versions only |
| `uv python pin 3.14` | Pin project to Python 3.14 |
| `uv python pin --global 3.14` | Set global default |
| `uv python upgrade 3.14` | Upgrade to latest patch |
| `uv python uninstall 3.14` | Remove Python 3.14 |
| `uv python find` | Find Python interpreter |

### Related documentation

- [Official UV Python Documentation](https://docs.astral.sh/uv/guides/install-python/)
- [Python Versions Concept](https://docs.astral.sh/uv/concepts/python-versions/)
- [Astral Blog: Python 3.14](https://astral.sh/blog/python-3.14)

---

## Further reading

- [Real Python: Managing Python Projects With uv](https://realpython.com/python-uv/)
- [DataCamp: Python UV Ultimate Guide](https://www.datacamp.com/tutorial/python-uv)
- [SaaS Pegasus: uv Deep Dive](https://www.saaspegasus.com/guides/uv-deep-dive/)
- [Python Developer Tooling Handbook](https://pydevtools.com/handbook/reference/uv/)
