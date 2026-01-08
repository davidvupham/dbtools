# How to run tools with `uv`

`uv` can replace tools like `pipx` for running command-line utilities in isolated environments.

## Table of contents

- [Run a tool ephemerally (`uvx`)](#run-a-tool-ephemerally-uvx)
- [Install a tool globally](#install-a-tool-globally)

## Run a tool ephemerally (`uvx`)

Use `uvx` (an alias for `uv tool run`) to download and run a tool in a temporary environment without installing it globally.

**Format code with Ruff:**

```bash
uvx ruff check .
```

**Format code with Black:**

```bash
uvx black .
```

## Install a tool globally

If you use a tool constantly, you can install it into an isolated environment that is added to your PATH.

```bash
uv tool install ruff
```

Now you can just run `ruff check` directly from your shell.
