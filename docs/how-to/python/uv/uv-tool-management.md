# How to run tools with UV

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 2.0
> **Last Updated:** January 27, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Tools-blue)

> [!IMPORTANT]
> **Related Docs:** [Interactive Python](./uv-interactive-python.md) | [Python Management](./uv-python-management.md) | [UV Reference](../../../reference/python/uv/uv-reference.md)

UV replaces `pipx` for running command-line tools in isolated environments. Use `uvx` (alias for `uv tool run`) for ephemeral execution, or `uv tool install` for persistent global installation.

## Table of contents

- [Run tools ephemerally with uvx](#run-tools-ephemerally-with-uvx)
  - [Basic usage](#basic-usage)
  - [Run a specific version](#run-a-specific-version)
  - [Run from a different package name](#run-from-a-different-package-name)
  - [Run with extra dependencies](#run-with-extra-dependencies)
  - [Run with a specific Python version](#run-with-a-specific-python-version)
- [Install tools globally](#install-tools-globally)
  - [Install a tool](#install-a-tool)
  - [List installed tools](#list-installed-tools)
  - [Upgrade tools](#upgrade-tools)
  - [Uninstall tools](#uninstall-tools)
- [Common tools](#common-tools)
- [Troubleshooting](#troubleshooting)
- [Related guides](#related-guides)

---

## Run tools ephemerally with uvx

[↑ Back to table of contents](#table-of-contents)

`uvx` downloads and runs a tool in a temporary, isolated environment without installing it globally. The environment is cached for reuse.

### Basic usage

```bash
# Lint code with Ruff
uvx ruff check .

# Format code with Ruff
uvx ruff format .

# Run pre-commit hooks
uvx pre-commit run --all-files

# Check types with mypy
uvx mypy src/
```

### Run a specific version

Pin to a specific version with `@`:

```bash
uvx ruff@0.8.0 check .
uvx black@24.10.0 .
```

### Run from a different package name

When the command name differs from the package name, use `--from`:

```bash
# The "http" command comes from the "httpie" package
uvx --from httpie http GET https://httpbin.org/get

# The "jupyter" command comes from "jupyterlab"
uvx --from jupyterlab jupyter lab
```

### Run with extra dependencies

Add additional packages to the tool's environment with `--with`:

```bash
# Run pytest with plugins
uvx --with pytest-cov --with pytest-xdist pytest --cov=src

# Run mkdocs with a theme
uvx --with mkdocs-material mkdocs serve
```

### Run with a specific Python version

```bash
uvx --python 3.12 mypy src/
```

[↑ Back to table of contents](#table-of-contents)

---

## Install tools globally

[↑ Back to table of contents](#table-of-contents)

For tools you use frequently, install them into a persistent isolated environment. The tool's command is added to your PATH.

### Install a tool

```bash
uv tool install ruff
uv tool install pre-commit
uv tool install httpie
```

After installation, you can run the tool directly:

```bash
ruff check .
pre-commit run --all-files
http GET https://httpbin.org/get
```

### List installed tools

```bash
uv tool list                      # List all installed tools
uv tool list --show-paths         # Include installation paths
```

### Upgrade tools

```bash
uv tool upgrade ruff              # Upgrade specific tool
uv tool upgrade --all             # Upgrade all installed tools
```

### Uninstall tools

```bash
uv tool uninstall ruff            # Remove a tool
uv tool uninstall --all           # Remove all tools
```

[↑ Back to table of contents](#table-of-contents)

---

## Common tools

| Tool | Install command | Description |
|:---|:---|:---|
| `ruff` | `uv tool install ruff` | Python linter and formatter |
| `pre-commit` | `uv tool install pre-commit` | Git pre-commit hook manager |
| `mypy` | `uv tool install mypy` | Static type checker |
| `httpie` | `uv tool install httpie` | HTTP client (command: `http`) |
| `cookiecutter` | `uv tool install cookiecutter` | Project scaffolding |
| `tox` | `uv tool install tox` | Test automation |

> [!TIP]
> For tools you use occasionally, prefer `uvx` over `uv tool install`. Ephemeral execution avoids version drift and always uses the latest version.

[↑ Back to table of contents](#table-of-contents)

---

## Troubleshooting

### "Command not found" after install

Ensure `~/.local/bin` is in your PATH:

```bash
echo $PATH | tr ':' '\n' | grep .local/bin
```

If missing, add to your shell profile:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Tool uses wrong Python version

Specify the Python version during install:

```bash
uv tool install --python 3.12 mypy
```

[↑ Back to table of contents](#table-of-contents)

---

## Related guides

- [UV Interactive Python](./uv-interactive-python.md)
- [UV Python Management](./uv-python-management.md)
- [UV Command Reference](../../../reference/python/uv/uv-reference.md)
- [Official UV Tools Documentation](https://docs.astral.sh/uv/guides/tools/)
