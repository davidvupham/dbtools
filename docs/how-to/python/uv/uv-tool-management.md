# How to run tools with `uv`

`uv` can replace tools like `pipx` for running command-line utilities in isolated environments.

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
