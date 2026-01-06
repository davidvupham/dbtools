# How to manage dependencies with `uv`

## Sync dependencies

If you clone a repo with a `uv.lock` file, you can install everything exactly as specified in the lockfile:

```bash
uv sync
```

This creates/updates the `.venv` and installs all packages.

## Manage legacy `requirements.txt`

`uv` respects legacy workflows and can interact with standard requirements files.

### Install from requirements.txt

To install dependencies from a `requirements.txt` into specific virtual environment:

```bash
uv pip install -r requirements.txt
```

### Compile requirements.txt from `pyproject.toml`

If you need to generate a `requirements.txt` for a legacy system that doesn't support `uv` (or for simple sharing):

```bash
uv pip compile pyproject.toml -o requirements.txt
```
