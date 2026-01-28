# How to Use UV with Jupyter Notebooks

**🔗 [← Back to UV How-to Index](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** Application Infrastructure Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Topic](https://img.shields.io/badge/Topic-Jupyter-orange)

> [!IMPORTANT]
> **Related Docs:** [Getting Started](../../../tutorials/languages/python/uv/uv-getting-started.md) | [Interactive Python](./uv-interactive-python.md)

This guide covers using UV with Jupyter notebooks for data science and interactive development workflows.

## Table of contents

- [Quick Start](#quick-start)
- [Project-Based Jupyter](#project-based-jupyter)
  - [Set Up a Jupyter Project](#set-up-a-jupyter-project)
  - [Run Jupyter Lab](#run-jupyter-lab)
  - [Run Jupyter Notebook](#run-jupyter-notebook)
- [Kernel Management](#kernel-management)
  - [Install Kernel for Your Project](#install-kernel-for-your-project)
  - [Use Project Kernel in System Jupyter](#use-project-kernel-in-system-jupyter)
  - [List Available Kernels](#list-available-kernels)
  - [Remove a Kernel](#remove-a-kernel)
- [One-Off Jupyter Sessions](#one-off-jupyter-sessions)
  - [Quick Jupyter with uvx](#quick-jupyter-with-uvx)
  - [Jupyter with Specific Packages](#jupyter-with-specific-packages)
- [VS Code Integration](#vs-code-integration)
  - [Configure VS Code to Use UV Environment](#configure-vs-code-to-use-uv-environment)
  - [Selecting the Kernel](#selecting-the-kernel)
- [Data Science Project Template](#data-science-project-template)
  - [Project Structure](#project-structure)
  - [pyproject.toml](#pyprojecttoml)
- [Docker with Jupyter](#docker-with-jupyter)
  - [Development Dockerfile](#development-dockerfile)
  - [Docker Compose](#docker-compose)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Related Guides](#related-guides)

---

## Quick Start

```bash
# Create a project and add Jupyter
uv init my-notebook-project
cd my-notebook-project
uv add jupyterlab pandas matplotlib

# Run Jupyter Lab
uv run jupyter lab
```

---

## Project-Based Jupyter

### Set Up a Jupyter Project

```bash
# Create a new project
uv init data-analysis
cd data-analysis

# Add Jupyter and common data science packages
uv add jupyterlab ipykernel

# Add your data science dependencies
uv add pandas numpy matplotlib seaborn scikit-learn
```

### Run Jupyter Lab

```bash
# Start Jupyter Lab (recommended)
uv run jupyter lab

# With specific options
uv run jupyter lab --port 8888 --no-browser
```

### Run Jupyter Notebook

```bash
# Start classic notebook interface
uv run jupyter notebook

# With specific options
uv run jupyter notebook --port 8888 --notebook-dir ./notebooks
```

---

## Kernel Management

### Install Kernel for Your Project

To make your project's environment available as a kernel in Jupyter:

```bash
# Install ipykernel
uv add ipykernel

# Register the kernel
uv run python -m ipykernel install --user --name my-project --display-name "My Project (Python 3.12)"
```

This creates a kernel specification that points to your project's Python interpreter.

### Use Project Kernel in System Jupyter

If you have a system-wide Jupyter installation and want to use your UV project's environment:

```bash
# In your UV project directory
uv add ipykernel

# Install kernel with full path to project
uv run python -m ipykernel install \
    --user \
    --name "data-analysis" \
    --display-name "Data Analysis Project"
```

Now when you run `jupyter lab` from anywhere, you'll see "Data Analysis Project" as a kernel option.

### List Available Kernels

```bash
# List all installed kernels
uv run jupyter kernelspec list

# Or with system Jupyter
jupyter kernelspec list
```

### Remove a Kernel

```bash
# Remove a kernel by name
uv run jupyter kernelspec remove my-project

# Or with system Jupyter
jupyter kernelspec remove my-project
```

---

## One-Off Jupyter Sessions

### Quick Jupyter with uvx

Run Jupyter without a project for quick exploration:

```bash
# Run Jupyter Lab in a temporary environment
uvx --with jupyterlab jupyter lab

# With specific Python version
uvx --python 3.12 --with jupyterlab jupyter lab
```

### Jupyter with Specific Packages

```bash
# Jupyter with pandas and matplotlib
uvx --with jupyterlab --with pandas --with matplotlib jupyter lab

# Jupyter with a complete data science stack
uvx --with jupyterlab \
    --with pandas \
    --with numpy \
    --with matplotlib \
    --with seaborn \
    jupyter lab
```

> [!TIP]
> For repeated use, create a project instead. One-off sessions are best for quick experiments.

---

## VS Code Integration

### Configure VS Code to Use UV Environment

VS Code automatically detects `.venv` folders. Ensure your project has one:

```bash
# Create project and sync (creates .venv)
uv init my-project
cd my-project
uv add ipykernel pandas
uv sync
```

### Selecting the Kernel

1. Open a `.ipynb` file in VS Code
2. Click "Select Kernel" in the top right
3. Choose "Python Environments..."
4. Select the `.venv` from your project directory

Alternatively, add to `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "jupyter.notebookFileRoot": "${workspaceFolder}"
}
```

---

## Data Science Project Template

### Project Structure

```
data-science-project/
├── .venv/                  # Created by uv sync
├── data/
│   ├── raw/               # Original data
│   ├── processed/         # Cleaned data
│   └── external/          # External datasets
├── notebooks/
│   ├── 01-exploration.ipynb
│   ├── 02-analysis.ipynb
│   └── 03-visualization.ipynb
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── data.py        # Data loading functions
│       └── viz.py         # Visualization helpers
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

### pyproject.toml

```toml
[project]
name = "data-science-project"
version = "0.1.0"
description = "Data analysis project"
requires-python = ">=3.11"
dependencies = [
    # Jupyter
    "jupyterlab>=4.0",
    "ipykernel>=6.0",
    "ipywidgets>=8.0",

    # Data manipulation
    "pandas>=2.0",
    "numpy>=1.24",
    "polars>=0.20",

    # Visualization
    "matplotlib>=3.8",
    "seaborn>=0.13",
    "plotly>=5.18",

    # Machine learning
    "scikit-learn>=1.4",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "nbqa>=1.8",  # Run linters on notebooks
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
extend-include = ["*.ipynb"]
```

---

## Docker with Jupyter

### Development Dockerfile

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy project files
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Run Jupyter Lab
CMD ["uv", "run", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  jupyter:
    build: .
    ports:
      - "8888:8888"
    volumes:
      # Mount notebooks for persistence
      - ./notebooks:/app/notebooks
      # Mount data directory
      - ./data:/app/data
      # Mount source code for hot reload
      - ./src:/app/src
    environment:
      - JUPYTER_TOKEN=my-secret-token
    command: >
      uv run jupyter lab
      --ip=0.0.0.0
      --port=8888
      --no-browser
      --allow-root
      --NotebookApp.token=${JUPYTER_TOKEN:-}
```

Run with:

```bash
docker compose up
# Access at http://localhost:8888?token=my-secret-token
```

---

## Best Practices

### 1. Keep Notebooks Clean

Use `nbqa` to lint notebooks:

```bash
uv add --dev nbqa ruff

# Lint notebooks
uv run nbqa ruff notebooks/

# Format notebooks
uv run nbqa ruff --fix notebooks/
```

### 2. Version Control Notebooks

Strip output before committing:

```bash
# Install nbstripout
uv add --dev nbstripout

# Configure git to strip output automatically
uv run nbstripout --install

# Or manually strip a notebook
uv run nbstripout notebook.ipynb
```

### 3. Convert Notebooks to Scripts

```bash
# Convert notebook to Python script
uv run jupyter nbconvert --to script notebooks/analysis.ipynb

# Convert to HTML for sharing
uv run jupyter nbconvert --to html notebooks/analysis.ipynb
```

### 4. Use Project Imports

Import from your project's `src/` in notebooks:

```python
# In notebook
import sys
sys.path.insert(0, '../src')

from my_project.data import load_dataset
from my_project.viz import plot_results
```

Or install your project in editable mode (default with `uv sync`):

```python
# Directly import if project is installed
from my_project.data import load_dataset
```

---

## Troubleshooting

### "Kernel not found"

Reinstall the kernel:

```bash
uv run python -m ipykernel install --user --name my-project
```

### "Module not found" in notebook

Ensure the notebook is using the correct kernel:

1. Check kernel name in notebook (top right)
2. Restart kernel after adding dependencies:
   ```bash
   uv add new-package
   # Then restart kernel in Jupyter
   ```

### Jupyter won't start

Check for port conflicts:

```bash
# Use a different port
uv run jupyter lab --port 8889

# Or find what's using port 8888
lsof -i :8888
```

### Extensions not working

Install JupyterLab extensions:

```bash
# Most extensions are pip-installable now
uv add jupyterlab-git
uv add jupyterlab-lsp

# Rebuild if needed
uv run jupyter lab build
```

### Widgets not displaying

```bash
# Ensure ipywidgets is installed
uv add ipywidgets

# May need to enable extension
uv run jupyter labextension list
```

---

## Related Guides

- [UV Getting Started](../../../tutorials/languages/python/uv/uv-getting-started.md)
- [UV Interactive Python](./uv-interactive-python.md)
- [UV Docker Integration](./uv-docker-integration.md)
- [Official UV Jupyter Guide](https://docs.astral.sh/uv/guides/integration/jupyter/)
