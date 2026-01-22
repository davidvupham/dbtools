# Python `uv` Tutorial

**🔗 [← Back to UV Documentation Index](../../../explanation/python/uv/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Deep_Dive-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../../explanation/python/uv/uv-architecture.md) | [Getting Started](./uv-getting-started.md) | [How-to Guides](../../../how-to/python/uv/) | [Reference](../../../reference/python/uv/uv-reference.md)

A comprehensive guide to managing Python projects and dependencies with `uv`.

## Table of contents

* [1. Introduction: Why `uv`?](#1-introduction-why-uv)
* [2. Core concepts for beginners](#2-core-concepts-for-beginners)
* [3. Architecture & speed](#3-architecture--speed)
* [4. Installation](#4-installation)
* [5. Quick start: Your first project](#5-quick-start-your-first-project)
* [6. Guide: Setting up `uv` for existing projects](#6-guide-setting-up-uv-for-existing-projects)
* [7. Workflows: Team & production](#7-workflows-team--production)
* [8. Comparisons](#8-comparisons)
* [9. Common tasks (how-to)](#9-common-tasks-how-to)
* [10. Best practices](#10-best-practices)
* [11. Reference cheatsheet](#11-reference-cheatsheet)
* [Further reading](#further-reading)

## 1. Introduction: Why `uv`?

[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package installer and project manager, written in Rust. It serves as a modern, high-performance replacement for `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, and `virtualenv`.

### Why is it the modern way?

* **Speed**: It is 10-100x faster than `pip` and `poetry`.
* **Unified Tooling**: It handles Python version management, virtual environments, dependency resolution, execution, and tool management in one single binary.
* **Drop-in Replacement**: It offers a `pip`-compatible interface (`uv pip install ...`) for easy migration.
* **Reliability**: Provides a universal lock file (`uv.lock`) that works across platforms.

### Who is Astral?

**Astral** is the company behind `uv`.

* **Creators of Ruff**: They built `Ruff`, the Python linter/formatter that revolutionized the ecosystem with 100x speedups.
* **Backing**: They are a venture-backed company (investors include Accel) dedicated to high-performance open-source developer tools.
* **Philosophy**: They believe Python tooling should be instant, reliable, and unified. `uv` is the next step in that vision, following `Ruff`.

## 2. Core concepts for beginners

Before diving in, it's helpful to understand three key concepts that `uv` handles for you.

### 1. Dependencies (packages)

Dependencies are external libraries (code written by others) that your project needs to function. For example, `requests` is a library for making HTTP calls. Instead of rewriting this code, you "depend" on it.

* **Direct Dependency**: A library you explicitly ask for (e.g., `uv add requests`).
* **Transitive Dependency**: A library that *your* dependency needs (e.g., `requests` might need `urllib3`). `uv` manages these automatically.

### 2. Virtual environments (the "box")

A Virtual Environment is an isolated "box" for your project.

* **The Problem**: If Project A needs `requests` version 1.0 and Project B needs `requests` version 2.0, installing them globally causes a conflict.
* **The Solution**: `uv` creates a separate box (`.venv` folder) for every project. Project A gets its own box with v1.0, and Project B gets its own box with v2.0. Neither interferes with the other.

### 3. Resolution (the "puzzle solver")

When you add a package, `uv` acts as a solver. It looks at all your requirements and finds the exact set of versions for every package that will work together without crashing. It saves this "solved puzzle" into a `uv.lock` file so that your project works exactly the same way on every computer.

### 4. Isolation (Python vs. modules)

* **Modules are Local**: Every project has its own `.venv` folder containing its dependencies. If Project A has `pandas` v2.0, it is physically sitting inside Project A's folder.
* **Python is Managed**: `uv` manages Python versions globally on your machine to save disk space. If 10 projects need Python 3.12, `uv` downloads it once to a central cache and "links" it to each project. However, to your project, it *feels* like a completely private installation.

## 3. Architecture & speed

[↑ Back to table of contents](#table-of-contents)

`uv` achieves 10-100x speedups by using Rust and a global cache. For a deep dive into how it works (PubGrub, lockfiles, etc.), see the **[UV Architecture](../../../../explanation/python/uv/uv-architecture.md)** guide.

## 4. Installation

[↑ Back to table of contents](#table-of-contents)

You can install `uv` on macOS, Linux, and Windows.

**MacOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**RedHat Enterprise Linux (RHEL) & CentOS:**
Since `uv` is a single static binary, the standard installer works perfectly.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows Subsystem for Linux (WSL) / Ubuntu:**
Treat WSL exactly like a standard Linux installation.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Using pip:**

```bash
pip install uv
```

Verify installation:

```bash
uv --version
```

## 5. Quick start: Your first project

[↑ Back to table of contents](#table-of-contents)

The modern workflow with `uv` revolves around creating a project and letting `uv` manage the environment for you.

### Step 1: Initialize a project

Create a new directory and initialize it:

```bash
mkdir my-app
cd my-app
uv init
```

This creates:

* `pyproject.toml` (standard configuration file)
* `README.md`
* `.python-version` (files specifying the python version)
* `main.py` (sample script)

### Step 2: Add dependencies

Add a library, for example, `requests`:

```bash
uv add requests
```

This automatically:

1. Creates a virtual environment in `.venv` (if it doesn't exist).
2. Installs `requests`.
3. Updates `pyproject.toml`.
4. Updates `uv.lock`.

### Step 3: Run scripts

Run your script using the managed environment:

```bash
uv run main.py
```

Or run arbitrary commands:

```bash
uv run python -c "import requests; print(requests.__version__)"
```

## 6. Guide: Setting up `uv` for existing projects

[↑ Back to table of contents](#table-of-contents)

If you have existing projects (e.g., inside `~/src`), here is how to switch them to `uv`.

1. **Navigate to your project**:

    ```bash
    cd ~/src/my-existing-repo
    ```

2. **Initialize `uv`**:

    ```bash
    uv init
    ```

    * `uv` will detect your existing code.
    * It creates a `pyproject.toml` if you don't have one.

3. **Add your dependencies**:
    * If you have a `requirements.txt`:

        ```bash
        uv pip install -r requirements.txt
        ```

    * Or add them manually to move to the modern `pyproject.toml` workflow:

        ```bash
        uv add requests pandas
        ```

4. **Run your code**:

    ```bash
    uv run python main.py
    ```

## 7. Workflows: Team & production

[↑ Back to table of contents](#table-of-contents)

### Developer workflow (the "team" flow)

When a new developer joins your team or clones the repo, they don't need to manually create virtual environments or guess pip commands.

1. **Clone the repo**:

    ```bash
    git clone https://github.com/my-org/my-repo
    cd my-repo
    ```

2. **Sync**:

    ```bash
    uv sync
    ```

    This single command:
    * Reads `uv.lock`.
    * Creates the `.venv` if missing.
    * Installs the exact versions specified in the lockfile.
    * Installs your project in "editable" mode so changes happen instantly.

### Version control (Git)

Knowing what to commit is crucial for team consistency.

| File/Folder | Action | Reason |
| :--- | :--- | :--- |
| `pyproject.toml` | **COMMIT** | Defines your direct dependencies and project metadata. |
| `uv.lock` | **COMMIT** | Locks exact versions of *all* dependencies to ensure everyone has the identical environment. |
| `.python-version` | **COMMIT** | Ensures everyone uses the same Python version. |
| `.venv/` | **IGNORE** | This is the local environment generated by `uv sync`. Never commit it. |

### Docker & production

For production, you want small images and fast builds. `uv` has an official Docker image (`ghcr.io/astral-sh/uv`) to help.

#### Best practice: Multi-stage build

```dockerfile
# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
# Install the project
COPY . .
RUN uv sync --frozen --no-dev

# Stage 2: Runtime (Small & Secure)
FROM python:3.12-slim-bookworm
# Copy the completely built environment from builder
COPY --from=builder /app/.venv /app/.venv
# Put the environment on the PATH
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY . .
CMD ["fastapi", "run", "app/main.py"]
```

## 8. Comparisons

[↑ Back to table of contents](#table-of-contents)

For a detailed breakdown of how `uv` compares to `pip`, `poetry`, and `pipenv`, including a "Migration ROI" matrix, see **[UV Adoption Rationale](../../../../explanation/python/uv/README.md#2-migration-roi-what-do-you-gain)**.

## 9. Common tasks (how-to)

[↑ Back to table of contents](#table-of-contents)

`uv` is capable of much more than just project management. Check out our dedicated **How-To Guides** for specific tasks:

* **[Manage Python Versions](../../../../how-to/python/uv/uv-python-management.md)**: Install specific versions (e.g., 3.12), pin projects, and list available versions.
* **[Interactive Python (Ad-hoc)](../../../../how-to/python/uv/uv-interactive-python.md)**: Run scripts and REPLs without a project.
* **[Run Tools (uvx)](../../../../how-to/python/uv/uv-tool-management.md)**: Run CLIs like `ruff`, `black`, or `pytest` in isolated environments (replaces `pipx`).
* **[Dependency Management](../../../../how-to/python/uv/uv-dependency-management.md)**: Sync dependencies and work with legacy `requirements.txt`.

## 10. Best practices

[↑ Back to table of contents](#table-of-contents)

1. **Always use `uv init` for new projects**: It sets up the standard structure (`pyproject.toml`) immediately.
2. **Commit `uv.lock`**: This ensures that everyone working on your project (and your CI system) uses the exact same package versions.
3. **Use `uv run`**: Avoid manually activating virtual environments (`source .venv/bin/activate`). `uv run` handles this context switching for you, ensuring you never run with the "wrong" python.
4. **Use `uv tool run` (alias `uvx`)**: For tools like `ruff`, `black`, `pytest`, or `mypy`. It downloads and runs them in an isolated environment without polluting your project dependencies.
5. **Pin Python Versions**: Use `.python-version` (via `uv python pin`) to ensure your project isn't accidentally upgraded to a newer Python version that breaks your code.

## 11. Reference cheatsheet

[↑ Back to table of contents](#table-of-contents)

| Command | Description |
| :--- | :--- |
| `uv init` | Initialize a new project |
| `uv add <pkg>` | Add a dependency |
| `uv remove <pkg>` | Remove a dependency |
| `uv run <script>` | Run a script in the project environment |
| `uv sync` | Sync environment with lock file |
| `uv lock` | Update lock file without installing |
| `uv python list` | List available Python versions |
| `uv python install <ver>` | Install a Python version |
| `uv pip install ...` | Legacy pip-style install |

---

## Further reading

[↑ Back to table of contents](#table-of-contents)

* [Official UV Documentation](https://docs.astral.sh/uv/) — Complete reference from Astral
* [UV GitHub Repository](https://github.com/astral-sh/uv) — Source code and issue tracker
