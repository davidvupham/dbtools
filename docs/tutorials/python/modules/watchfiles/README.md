# Watchfiles Tutorial

**Level**: Beginner to Advanced
**Category**: Utilities / Automation

Watchfiles provides simple, efficient file watching and code reload for Python, powered by the Rust `notify` crate.

## 📦 Installation

```bash
pip install watchfiles
```

## 🚀 Beginner: The Watch Loop

The simplest usage: loop forever and print when a file changes.

```python
from watchfiles import watch

# Monitor the current directory
for changes in watch('.'):
    for change_type, path in changes:
        print(f"File changed: {change_type.name} at {path}")
```

## 🏃 Intermediate: Triggering a Process

This is excellent for development tools. Run a command every time a file changes.

```python
from watchfiles import run_process

def my_task():
    print("Process started / restarted!")

if __name__ == '__main__':
    # Monitors current dir and restarts 'my_task' if anything changes
    run_process('.', target=my_task)
```

## 🧠 Advanced: Async & Filtering

Use with `asyncio` for non-blocking monitoring, and apply filters to ignore specific files (like `.git` or `__pycache__`).

```python
import asyncio
from watchfiles import awatch, PythonFilter

async def main():
    # Only watch Python files, ignoring hidden directories
    print("Watching for .py file changes...")

    async for changes in awatch('.', watch_filter=PythonFilter()):
        for change in changes:
            print(change)

if __name__ == '__main__':
    asyncio.run(main())
```

## 💡 Use Cases

1.  **Dev Servers**: Automatically reload your web server when code changes (like `uvicorn` or `django` does).
2.  **ETL Pipelines**: Trigger a data processing script as soon as a CSV file drops into a folder.
3.  **Config Updates**: Hot-reload configuration files in long-running services without restarting the application.
