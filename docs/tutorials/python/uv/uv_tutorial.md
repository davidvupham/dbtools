# Python `uv` Tutorial

A comprehensive guide to managing Python projects and dependencies with `uv`.

## Table of Contents

* [1. Introduction: Why `uv`?](#1-introduction-why-uv)
* [2. Core Concepts for Beginners](#2-core-concepts-for-beginners)
* [3. Architecture Deep Dive](#3-architecture-deep-dive)
* [4. Installation](#4-installation)
* [5. Quick Start: Your First Project](#5-quick-start-your-first-project)
* [6. Guide: Setting up `uv` for Existing Projects](#6-guide-setting-up-uv-for-existing-projects)
* [7. Workflows: Team & Production](#7-workflows-team--production)
* [8. Comparisons: `uv` vs. The Rest](#8-comparisons-uv-vs-the-rest)
* [9. How-to Guide](#9-how-to-guide)
* [10. Best Practices](#10-best-practices)
* [11. Reference Cheatsheet](#11-reference-cheatsheet)
* [Further Reading](#further-reading)

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

## 2. Core Concepts for Beginners

Before diving in, it's helpful to understand three key concepts that `uv` handles for you.

### 1. Dependencies (Packages)

Dependencies are external libraries (code written by others) that your project needs to function. For example, `requests` is a library for making HTTP calls. Instead of rewriting this code, you "depend" on it.

* **Direct Dependency**: A library you explicitly ask for (e.g., `uv add requests`).
* **Transitive Dependency**: A library that *your* dependency needs (e.g., `requests` might need `urllib3`). `uv` manages these automatically.

### 2. Virtual Environments (The "Box")

A Virtual Environment is an isolated "box" for your project.

* **The Problem**: If Project A needs `requests` version 1.0 and Project B needs `requests` version 2.0, installing them globally causes a conflict.
* **The Solution**: `uv` creates a separate box (`.venv` folder) for every project. Project A gets its own box with v1.0, and Project B gets its own box with v2.0. Neither interferes with the other.

### 3. Resolution (The "Puzzle Solver")

When you add a package, `uv` acts as a solver. It looks at all your requirements and finds the exact set of versions for every package that will work together without crashing. It saves this "solved puzzle" into a `uv.lock` file so that your project works exactly the same way on every computer.

### 4. Isolation (Python vs. Modules)

* **Modules are Local**: Every project has its own `.venv` folder containing its dependencies. If Project A has `pandas` v2.0, it is physically sitting inside Project A's folder.
* **Python is Managed**: `uv` manages Python versions globally on your machine to save disk space. If 10 projects need Python 3.12, `uv` downloads it once to a central cache and "links" it to each project. However, to your project, it *feels* like a completely private installation.

## 3. Architecture Deep Dive

For those interested in *how* `uv` achieves its speed and reliability, here is a look under the hood.

### The "Standard" CPython (No Magic)

When you ask `uv` for Python 3.12, it downloads **CPython**.

**What is CPython?**
It is the "reference implementation" of Python, written in C. It is what 99% of the world means when they say "I use Python". It is maintained by the Python Software Foundation (PSF).

**Pros & Cons**:

* Pros: 100% compatibility with all libraries (including C modules like `numpy`), standard behavior, and huge community support.
* Cons: Slower than some experimental compilers (like PyPy) due to the Global Interpreter Lock (GIL), but it is the industry standard.

**Is it different from python.org?**
**No and Yes**.

* **Code**: It is the **exact same source code**. `uv` does not modify the language logic.
* **Build**: `uv` uses "Portable Builds" (maintained by Astral).
  * *Python.org installers* often depend on your specific OS libraries (like needing a specific version of `glibc` on Linux).
  * *`uv` builds* are statically linked. This means they run on almost *any* Linux machine (or Mac/Windows) without you needing to install system dependencies.
* **Compatibility**: **Zero issues**. It satisfies the same verification tests as python.org builds.

### Building on Rust

`uv` is written in **Rust**, a systems programming language known for memory safety and performance.

* **No Garbage Collection**: Unlike Python, Rust doesn't use a garbage collector, eliminating pauses.
* **True Parallelism**: `uv` can download and unzip packages across many threads simultaneously without the "Global Interpreter Lock" (GIL) that slows down Python tools.

### The PubGrub Resolver

Dependency resolution is an NP-hard problem. `uv` uses **PubGrub**, a state-of-the-art algorithm (originally designed for the Dart language). It effectively searches the vast tree of possible package versions to find a compatible set usually in milliseconds, explaining conflicts clearly when they occur.

### The Global Cache

`uv` uses a **content-addressable global cache**.

* **Deduplication**: If 5 separate projects use `boto3==1.34.0`, `uv` stores the wheel *once* on your disk.
* **Hard Linking**: When creating a virtual environment, `uv` attempts to "hard link" files from the cache rather than copying them. This makes creating an environment almost instantaneous and uses near-zero additional disk space.

### Looking Ahead: Python 3.13+ and Free-Threading (No-GIL)

You might see buzz about Python 3.13/3.14 removing the **Global Interpreter Lock (GIL)** to allow true multi-core threading.

* **Status**: Python 3.13 introduced experimental "free-threaded" builds.
* **UV Support**: `uv` supports installing these variants *today* if you want to test the future of high-performance parallel Python.

```bash
uv python install 3.13t  # 't' stands for free-threading
```

### Where is everything stored?

Even if you have 100 completely unrelated projects (no monorepo), `uv` shares the Python installations managed in a central data directory.

* **Linux**: `~/.local/share/uv/python`
* **macOS**: `~/Library/Application Support/uv/python`
* **Windows**: `%LOCALAPPDATA%\uv\python`

Each project simply links to these central installs, keeping your individual project folders lightweight.

### Visualizing the Storage (The "Symlink" Magic)

Let's say you have **Project A** and **Project B**, and both needed Python 3.12.

1. **The Central Python (Stored Once)**:
    * Location: `~/.local/share/uv/python/cpython-3.12/bin/python`
    * This is the *actual* binary file. It sits here to be shared.

2. **The Project Environment (The Link)**:
    * Location: `~/src/project-a/.venv/bin/python`
    * This is NOT a copy. It is a **symlink** (shortcut) pointing to the central Python above.

3. **The Modules (The Project's library)**:
    * Location: `~/src/project-a/.venv/lib/python3.12/site-packages/`
    * This folder contains your libraries (like `requests`). `uv` fills this folder using hardlinks from its global cache to save space, but logically, they belong to this project.

## 4. Installation

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

## 5. Quick Start: Your First Project

The modern workflow with `uv` revolves around creating a project and letting `uv` manage the environment for you.

### Step 1: Initialize a Project

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

### Step 2: Add Dependencies

Add a library, for example, `requests`:

```bash
uv add requests
```

This automatically:

1. Creates a virtual environment in `.venv` (if it doesn't exist).
2. Installs `requests`.
3. Updates `pyproject.toml`.
4. Updates `uv.lock`.

### Step 3: Run Scripts

Run your script using the managed environment:

```bash
uv run main.py
```

Or run arbitrary commands:

```bash
uv run python -c "import requests; print(requests.__version__)"
```

## 6. Guide: Setting up `uv` for Existing Projects

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

## 7. Workflows: Team & Production

### Developer Workflow (The "Team" Flow)

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

### Version Control (Git)

Knowing what to commit is crucial for team consistency.

| File/Folder | Action | Reason |
| :--- | :--- | :--- |
| `pyproject.toml` | **COMMIT** | Defines your direct dependencies and project metadata. |
| `uv.lock` | **COMMIT** | Locks exact versions of *all* dependencies to ensure everyone has the identical environment. |
| `.python-version` | **COMMIT** | Ensures everyone uses the same Python version. |
| `.venv/` | **IGNORE** | This is the local environment generated by `uv sync`. Never commit it. |

### Docker & Production

For production, you want small images and fast builds. `uv` has an official Docker image (`ghcr.io/astral-sh/uv`) to help.

#### Best Practice: Multi-Stage Build

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

## 8. Comparisons: `uv` vs. The Rest

| Feature | `pip` + `venv` | `Poetry` | `uv` |
| :--- | :--- | :--- | :--- |
| **Speed** | Slow | Slow/Moderate | **Extremely Fast** |
| **Virtual Env** | Manual (`python -m venv`) | Automatic | **Automatic** |
| **Dependency Resolution** | Basic | Advanced | **Advanced** |
| **Python Version Mgmt** | No (need `pyenv`) | No (need `pyenv`) | **Built-in** |
| **Lock File** | No (need `pip-tools`) | `poetry.lock` | **`uv.lock`** |
| **Single Script Run** | Manual setup | `poetry run` | **`uv run`** (zero setup needed) |

## 9. How-to Guide

### How to manage Python versions

Install a specific Python version:

```bash
uv python install 3.12
```

Pin a project to a specific version:

```bash
uv python pin 3.11
```

### How to run tools (replace `pipx`)

Run a CLI tool without installing it globally:

```bash
uv x ruff check .
uv x black .
```

### How to sync dependencies

If you clone a repo with a `uv.lock` file, install everything exactly as specified:

```bash
uv sync
```

### How to use with legacy `requirements.txt`

`uv` respects legacy workflows.
Install from requirements:

```bash
uv pip install -r requirements.txt
```

Compile requirements from `pyproject.toml`:

```bash
uv pip compile pyproject.toml -o requirements.txt
```

## 10. Best Practices

1. **Always use `uv init` for new projects**: It sets up the standard structure (`pyproject.toml`) immediately.
2. **Commit `uv.lock`**: This ensures that everyone working on your project (and your CI system) uses the exact same package versions.
3. **Use `uv run`**: Avoid manually activating virtual environments (`source .venv/bin/activate`). `uv run` handles this context switching for you, ensuring you never run with the "wrong" python.
4. **Use `uv tool run` (alias `uvx`)**: For tools like `ruff`, `black`, `pytest`, or `mypy`. It downloads and runs them in an isolated environment without polluting your project dependencies.
5. **Pin Python Versions**: Use `.python-version` (via `uv python pin`) to ensure your project isn't accidentally upgraded to a newer Python version that breaks your code.

## 11. Reference Cheatsheet

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

## Further Reading

* [Official UV Documentation](https://docs.astral.sh/uv/) — Complete reference from Astral
* [UV GitHub Repository](https://github.com/astral-sh/uv) — Source code and issue tracker
