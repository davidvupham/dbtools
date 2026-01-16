# Getting Started with UV: A Beginner's Guide

**🔗 [← Back to UV Documentation Index](../../../explanation/python/uv/README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 13, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Tutorial-blue)

> [!IMPORTANT]
> **Related Docs:** [Architecture](../../../explanation/python/uv/uv-architecture.md) | [Comprehensive Tutorial](./uv_tutorial.md) | [How-to Guides](../../../how-to/python/uv/) | [Reference](../../../reference/python/uv/uv-reference.md)

A step-by-step tutorial to get you up and running with `uv`, the modern Python package manager.

> [!TIP]
> This tutorial is designed for beginners. If you're already familiar with Python development and want a comprehensive reference, see [UV Comprehensive Guide](./uv_tutorial.md).

## Table of Contents

- [What You'll Learn](#what-youll-learn)
- [Prerequisites](#prerequisites)
- [Part 1: Understanding the Basics](#part-1-understanding-the-basics)
- [Part 2: Installing UV](#part-2-installing-uv)
- [Part 3: Your First Project](#part-3-your-first-project)
- [Part 4: Adding Dependencies](#part-4-adding-dependencies)
- [Part 5: Running Your Code](#part-5-running-your-code)
- [Part 6: Sharing Your Project](#part-6-sharing-your-project)
- [Exercises](#exercises)
- [Next Steps](#next-steps)

---

## What You'll Learn

By the end of this tutorial, you will be able to:

1. Install `uv` on your computer
2. Create a new Python project with proper structure
3. Add and manage dependencies (external libraries)
4. Run your Python code using `uv`
5. Share your project so others can run it identically

**Time to complete:** ~30 minutes

---

## Prerequisites

Before starting, you should have:

- Basic familiarity with the command line (terminal)
- Basic Python knowledge (you know what a `.py` file is)
- A text editor or IDE (VS Code recommended)

> [!NOTE]
> You do **not** need Python installed beforehand. UV can install and manage Python for you!

---

## Part 1: Understanding the Basics

Before we dive in, let's understand three key concepts that UV handles for you.

### What is a Dependency?

A **dependency** is code written by someone else that your project needs to work. Instead of writing everything from scratch, you "depend" on libraries.

**Example:** If your code needs to make HTTP requests, you might use the `requests` library:

```python
import requests  # This is a dependency!
response = requests.get("https://api.example.com/data")
```

Without the `requests` library installed, this code fails with `ModuleNotFoundError`.

### What is a Virtual Environment?

Imagine you have two projects:

- **Project A** needs `pandas` version 1.0
- **Project B** needs `pandas` version 2.0

If you install both globally, they conflict! A **virtual environment** is an isolated "box" for each project:

```
Project A's box: pandas 1.0, requests 2.28
Project B's box: pandas 2.0, requests 2.31
```

With UV, each project automatically gets its own box (a `.venv` folder).

### What is a Lock File?

When you add a dependency like `requests`, it might need other libraries to work (called *transitive dependencies*). UV figures out all the exact versions that work together and saves them in a **lock file** (`uv.lock`).

This ensures:

- Your project works the same on every computer
- Your teammate gets the exact same versions
- Your production server runs identically to your laptop

---

## Part 2: Installing UV

### Step 2.1: Install UV

Choose your operating system:

**macOS / Linux / WSL:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2.2: Restart Your Terminal

Close and reopen your terminal (or run `source ~/.bashrc` / `source ~/.zshrc`).

### Step 2.3: Verify Installation

```bash
uv --version
```

You should see output like:

```
uv 0.5.10 (2a3b1234 2024-12-15)
```

### Step 2.4: Enable Shell Completion (Optional but Recommended)

This gives you tab-completion for UV commands:

**Bash:**

```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**

```bash
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc
source ~/.zshrc
```

---

## Part 3: Your First Project

### Step 3.1: Create a Project Directory

```bash
mkdir my-first-uv-project
cd my-first-uv-project
```

### Step 3.2: Initialize the Project

```bash
uv init
```

UV creates several files:

```
my-first-uv-project/
├── .gitignore          # Git ignore patterns
├── .python-version     # Python version for this project
├── main.py             # Sample Python script
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

### Step 3.3: Explore the Files

**`pyproject.toml`** - This is your project's configuration file:

```toml
[project]
name = "my-first-uv-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []
```

**`main.py`** - A simple starter script:

```python
def main():
    print("Hello from my-first-uv-project!")

if __name__ == "__main__":
    main()
```

### Step 3.4: Run the Sample Script

```bash
uv run main.py
```

Output:

```
Hello from my-first-uv-project!
```

> [!NOTE]
> The first time you run `uv run`, UV:
>
> 1. Downloads Python (if not already available)
> 2. Creates a virtual environment (`.venv` folder)
> 3. Runs your script inside that environment
>
> This typically takes a few seconds the first time, then is instant afterward.

---

## Part 4: Adding Dependencies

### Step 4.1: Add Your First Dependency

Let's add the `requests` library to make HTTP calls:

```bash
uv add requests
```

You'll see output like:

```
Resolved 5 packages in 123ms
Prepared 5 packages in 456ms
Installed 5 packages in 78ms
 + certifi==2024.12.14
 + charset-normalizer==3.4.0
 + idna==3.10
 + requests==2.32.3
 + urllib3==2.2.3
```

### Step 4.2: Understand What Happened

UV did several things:

1. **Resolved dependencies**: Found all packages `requests` needs
2. **Updated `pyproject.toml`**: Added `requests` to your dependencies
3. **Created `uv.lock`**: Locked exact versions for reproducibility
4. **Installed packages**: Put them in your `.venv` folder

Check your `pyproject.toml`:

```toml
dependencies = [
    "requests>=2.32.3",
]
```

### Step 4.3: Use the Dependency in Your Code

Edit `main.py`:

```python
import requests

def main():
    response = requests.get("https://httpbin.org/get")
    print(f"Status: {response.status_code}")
    print(f"Your IP: {response.json()['origin']}")

if __name__ == "__main__":
    main()
```

Run it:

```bash
uv run main.py
```

Output:

```
Status: 200
Your IP: 203.0.113.42
```

### Step 4.4: Add Development Dependencies

Development dependencies are tools you need while coding (testing, linting) but not in production:

```bash
uv add --dev pytest ruff
```

These go in a separate section and won't be installed when someone uses your library.

---

## Part 5: Running Your Code

### The `uv run` Command

Always use `uv run` to execute Python code. It ensures the correct environment is used:

```bash
# Run a script
uv run main.py

# Run Python directly
uv run python -c "print('Hello!')"

# Run a module
uv run python -m pytest

# Run an installed tool
uv run pytest
```

### Why Not Just `python main.py`?

If you run `python` directly, you might use:

- The wrong Python version
- A global Python without your project's dependencies
- An outdated virtual environment

`uv run` always uses the correct, synced environment.

---

## Part 6: Sharing Your Project

### What to Commit to Git

| File/Folder | Commit? | Reason |
|-------------|---------|--------|
| `pyproject.toml` | ✅ Yes | Defines your project and dependencies |
| `uv.lock` | ✅ Yes | Locks exact versions for reproducibility |
| `.python-version` | ✅ Yes | Ensures everyone uses the same Python |
| `.venv/` | ❌ No | Generated locally by UV |

Your `.gitignore` already excludes `.venv/`.

### When Someone Clones Your Project

They just need to run:

```bash
git clone https://github.com/you/my-project
cd my-project
uv sync
```

This single command:

1. Reads `uv.lock`
2. Creates a `.venv` if needed
3. Installs the **exact** versions from the lock file

---

## Exercises

### Exercise 1: Create a Weather App

1. Create a new project called `weather-app`
2. Add the `httpx` library (an alternative to requests)
3. Write a script that fetches weather data from `https://wttr.in/London?format=j1`
4. Print the current temperature

<details>
<summary>Solution</summary>

```bash
mkdir weather-app && cd weather-app
uv init
uv add httpx
```

Edit `main.py`:

```python
import httpx

def main():
    response = httpx.get("https://wttr.in/London?format=j1")
    data = response.json()
    temp = data["current_condition"][0]["temp_C"]
    print(f"Current temperature in London: {temp}°C")

if __name__ == "__main__":
    main()
```

Run: `uv run main.py`

</details>

### Exercise 2: Add Testing

1. Add `pytest` as a development dependency
2. Create a `test_main.py` file with a simple test
3. Run the tests

<details>
<summary>Solution</summary>

```bash
uv add --dev pytest
```

Create `test_main.py`:

```python
def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"
```

Run tests:

```bash
uv run pytest
```

</details>

### Exercise 3: Explore the Lock File

1. Open `uv.lock` in your editor
2. Find how many packages are listed
3. Identify which packages are transitive dependencies of `requests`

---

## Next Steps

Congratulations! You now know the basics of UV. Here's where to go next:

| Goal | Resource |
|------|----------|
| Deep dive into UV concepts | [UV Comprehensive Guide](./uv_tutorial.md) |
| Understand "Why UV?" | [UV Adoption Rationale](../../../explanation/python/uv/README.md) |
| Migrate from pip/poetry | [Migration Guide](../../../how-to/python/uv/uv-migrate-from-pip.md) |
| Use UV with Docker | [Docker Integration](../../../how-to/python/uv/uv-docker-integration.md) |
| Set up CI/CD pipelines | [CI/CD Guide](../../../how-to/python/uv/uv-ci-cd-integration.md) |
| Command reference | [UV Reference](../../../reference/python/uv/uv-reference.md) |
| Official documentation | [UV Docs (Astral)](https://docs.astral.sh/uv/) |

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `uv init` | Create a new project |
| `uv add <package>` | Add a dependency |
| `uv add --dev <package>` | Add a development dependency |
| `uv remove <package>` | Remove a dependency |
| `uv run <command>` | Run a command in the project environment |
| `uv sync` | Install dependencies from lock file |
| `uv lock` | Update the lock file |
