# How to manage Python versions with `uv`

`uv` simplifies globally installing and managing Python versions.

## Table of contents

- [Install a specific Python version](#install-a-specific-python-version)
- [List available versions](#list-available-versions)
- [Pin a project to a specific version](#pin-a-project-to-a-specific-version)

## Install a specific Python version

Download and install a managed Python version into the central cache:

```bash
uv python install 3.12
```

You can install multiple versions side-by-side (e.g., 3.10, 3.11, 3.12).

## List available versions

See what you have installed and what is available for download:

```bash
uv python list
```

## Pin a project to a specific version

To ensure a project always uses a specific version of Python, "pin" it. This creates a `.python-version` file.

```bash
uv python pin 3.11
```

Next time you run `uv sync` or `uv run`, it will use Python 3.11 for this project.
