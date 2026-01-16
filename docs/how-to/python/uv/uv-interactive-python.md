# How to Use Python Interactively (Ad-hoc)

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Productivity-orange)

> [!IMPORTANT]
> **Related Docs:** [Tool Management](./uv-tool-management.md) | [Python Management](./uv-python-management.md)

You can use `uv` to launch specific Python versions or run scripts without creating a project or virtual environment. All downloads are managed centrally, keeping your workspace clean.

## Table of contents

- [Launch a Python REPL (Shell)](#launch-a-python-repl-shell)
	- [Launch a specific version](#launch-a-specific-version)
	- [Launch the latest available version](#launch-the-latest-available-version)
- [Run a single-file script with dependencies](#run-a-single-file-script-with-dependencies)
	- [Example: Quick One-Liner](#example-quick-one-liner)
- ["Pinning" for Ad-hoc Scripts (PEP 723)](#pinning-for-ad-hoc-scripts-pep-723)

## Launch a Python REPL (Shell)

You can drop into a Python shell instantly, even for versions you haven't explicitly installed yet.

### Launch a specific version

`uv` will download the requested version (if needed) and start the shell.

```bash
uv run --python 3.12 python
```

### Launch the latest available version

```bash
uv run python
```

## Run a single-file script with dependencies

You don't need a `pyproject.toml` or a virtual environment to run a standalone script that requires third-party libraries. `uv` creates an ephemeral environment for the execution.

Use the `--with` flag to **temporarily** add dependencies for just this run:

```bash
# Run script.py using Python 3.11 and the 'requests' library
uv run --python 3.11 --with requests script.py
```

### Example: Quick One-Liner

You can also combine this with `python -c` for quick experiments:

```bash
uv run --with pandas python -c "import pandas as pd; print(pd.DataFrame({'a': [1, 2], 'b': [3, 4]}))"
```

## "Pinning" for Ad-hoc Scripts (PEP 723)

If you have a standalone script that you run frequently, you don't want to type `--with` every time. `uv` supports **PEP 723 (Inline Script Metadata)**.

You can declare the dependencies directly at the top of your python script:

**`my_script.py`**:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests<3",
#     "rich",
# ]
# ///

import requests
from rich import print

resp = requests.get("https://peps.python.org/api/peps.json")
print(resp.json())
```

Now you can run it simply with:

```bash
uv run my_script.py
```

`uv` will automatically detect the header, create the necessary environment, and run the script.
