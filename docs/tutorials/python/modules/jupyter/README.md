# Jupyter Tutorial

Interactive computing and notebooks for Python.

## Overview

**Jupyter** provides interactive notebooks combining code, visualizations, and documentation. JupyterLab is the modern interface, while Jupyter Notebook is the classic version.

| | |
|---|---|
| **Package** | `jupyterlab` |
| **Install** | `pip install jupyterlab` |
| **Documentation** | [jupyter.org](https://jupyter.org/) |
| **GitHub** | [jupyter/jupyter](https://github.com/jupyter/jupyter) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Notebook Interface](#notebook-interface)
4. [Cells and Execution](#cells-and-execution)
5. [Magic Commands](#magic-commands)
6. [Visualizations](#visualizations)
7. [Extensions](#extensions)
8. [VS Code Integration](#vs-code-integration)
9. [Best Practices](#best-practices)
10. [Converting Notebooks](#converting-notebooks)

---

## Installation

```bash
# JupyterLab (recommended)
pip install jupyterlab

# Classic Jupyter Notebook
pip install notebook

# With common data science packages
pip install jupyterlab pandas numpy matplotlib seaborn
```

---

## Quick Start

```bash
# Start JupyterLab
jupyter lab

# Start classic Notebook
jupyter notebook

# Specify port
jupyter lab --port 8889

# No browser (for remote)
jupyter lab --no-browser
```

Access at: `http://localhost:8888`

---

## Notebook Interface

### Cell Types

1. **Code Cells** - Execute Python code
2. **Markdown Cells** - Documentation with formatting
3. **Raw Cells** - Unformatted text

### Essential Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Shift + Enter` | Run cell, move to next |
| `Ctrl + Enter` | Run cell, stay in place |
| `Alt + Enter` | Run cell, insert new below |
| `Esc` | Enter command mode |
| `Enter` | Enter edit mode |
| `A` | Insert cell above (command mode) |
| `B` | Insert cell below (command mode) |
| `DD` | Delete cell (command mode) |
| `M` | Change to Markdown (command mode) |
| `Y` | Change to Code (command mode) |
| `Ctrl + S` | Save notebook |

---

## Cells and Execution

### Code Cells

```python
# Variables persist across cells
x = 10
y = 20

# This cell can use x and y
result = x + y
print(f"Result: {result}")
```

### Markdown Cells

```markdown
# Heading 1
## Heading 2

**Bold** and *italic* text

- Bullet point
- Another point

1. Numbered list
2. Second item

`inline code`

```python
# Code block
def example():
    pass
```

[Link](https://example.com)

![Image](path/to/image.png)

LaTeX: $E = mc^2$

```

### Cell Output

```python
# Last expression is displayed
5 + 3  # Shows: 8

# Multiple outputs with display()
from IPython.display import display
display(df1)
display(df2)

# Suppress output with semicolon
plt.plot(x, y);
```

---

## Magic Commands

### Line Magics (single %)

```python
# Time execution
%time result = slow_function()

# Time multiple runs
%timeit [x**2 for x in range(1000)]

# List variables
%whos

# Run external script
%run script.py

# Load code from file
%load utils.py

# Write cell to file
%%writefile output.py
def my_function():
    return "Hello"

# Environment variables
%env MY_VAR=value

# Change directory
%cd /path/to/directory

# List directory
%ls

# Command history
%history
```

### Cell Magics (double %%)

```python
%%time
# Time entire cell
result = []
for i in range(10000):
    result.append(i ** 2)
```

```python
%%bash
# Run bash commands
echo "Hello from bash"
ls -la
```

```python
%%html
<h1 style="color: blue;">Custom HTML</h1>
<p>Rendered in the notebook</p>
```

```python
%%javascript
console.log("Hello from JavaScript");
alert("This runs in browser");
```

### Matplotlib Magic

```python
# Inline plots (default in JupyterLab)
%matplotlib inline

# Interactive plots
%matplotlib widget

# Retina display (higher resolution)
%config InlineBackend.figure_format = 'retina'
```

---

## Visualizations

### Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np

# Basic plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)
plt.show()
```

### Pandas Plotting

```python
import pandas as pd

df = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
    'Sales': [100, 120, 90, 150]
})

# Quick plot
df.plot(x='Month', y='Sales', kind='bar')
```

### Seaborn

```python
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")

# Load example dataset
tips = sns.load_dataset("tips")

# Create visualization
sns.boxplot(x="day", y="total_bill", data=tips)
```

### Interactive Plots with Plotly

```python
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
fig.show()
```

### Display Rich Content

```python
from IPython.display import display, HTML, Image, Video, Audio

# HTML
display(HTML("<h1>Custom HTML</h1>"))

# Images
display(Image("chart.png"))
display(Image(url="https://example.com/image.png"))

# DataFrames are automatically styled
display(df)

# Progress bars
from tqdm.notebook import tqdm
for i in tqdm(range(100)):
    pass
```

---

## Extensions

### JupyterLab Extensions

```bash
# Install extension
pip install jupyterlab-git

# List extensions
jupyter labextension list

# Popular extensions
pip install jupyterlab-code-formatter
pip install jupyterlab-lsp
pip install jupyterlab-git
pip install jupyterlab-execute-time
```

### nbextensions (Classic Notebook)

```bash
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user

# Enable specific extensions
jupyter nbextension enable toc2/main
jupyter nbextension enable execute_time/ExecuteTime
```

---

## VS Code Integration

VS Code provides excellent Jupyter support:

### Setup

1. Install **Jupyter** extension in VS Code
2. Open `.ipynb` file or create new notebook
3. Select Python kernel

### Features

- Cell execution with `Shift + Enter`
- Variable explorer
- Data viewer for DataFrames
- Interactive debugger
- Git integration

### Convert Python to Notebook

```python
# %% - Creates a cell boundary
# This is cell 1
import pandas as pd

# %%
# This is cell 2
df = pd.read_csv("data.csv")

# %% [markdown]
# ## This is a markdown cell
# With documentation
```

---

## Best Practices

### 1. Restart and Run All

Always verify notebook runs from top to bottom:

- `Kernel → Restart & Run All`
- Catches hidden state issues

### 2. Keep Cells Small

```python
# ✅ Good - small, focused cells
def load_data():
    return pd.read_csv("data.csv")

df = load_data()
```

```python
# Separate cell for analysis
summary = df.describe()
summary
```

### 3. Use Markdown Documentation

```markdown
## Data Loading

This section loads the raw data from the CSV file
and performs initial validation.

**Expected columns:**
- `id`: Unique identifier
- `value`: Numeric measurement
```

### 4. Clear Outputs Before Committing

```bash
# Clear outputs
jupyter nbconvert --clear-output notebook.ipynb

# Or use pre-commit hook
pip install nbstripout
nbstripout --install
```

### 5. Parameterize Notebooks

```python
# Parameters cell (tagged with "parameters" for papermill)
input_file = "data.csv"
output_file = "results.csv"
threshold = 0.5
```

Run with different parameters:

```bash
papermill notebook.ipynb output.ipynb -p threshold 0.8
```

---

## Converting Notebooks

### To Python Script

```bash
jupyter nbconvert --to script notebook.ipynb
```

### To HTML

```bash
jupyter nbconvert --to html notebook.ipynb

# Without code
jupyter nbconvert --to html --no-input notebook.ipynb
```

### To PDF

```bash
# Requires LaTeX
jupyter nbconvert --to pdf notebook.ipynb

# Via HTML (easier)
jupyter nbconvert --to webpdf notebook.ipynb
```

### To Markdown

```bash
jupyter nbconvert --to markdown notebook.ipynb
```

### Execute and Convert

```bash
# Execute notebook and save
jupyter nbconvert --execute --to notebook notebook.ipynb

# Execute and convert to HTML
jupyter nbconvert --execute --to html notebook.ipynb
```

---

## Quick Reference

### Keyboard Shortcuts

| Mode | Shortcut | Action |
|------|----------|--------|
| Both | `Shift+Enter` | Run cell |
| Command | `A` | Insert above |
| Command | `B` | Insert below |
| Command | `DD` | Delete cell |
| Command | `M` | To markdown |
| Command | `Y` | To code |
| Command | `Z` | Undo |
| Edit | `Ctrl+/` | Comment |

### Magic Commands

| Command | Purpose |
|---------|---------|
| `%time` | Time single run |
| `%timeit` | Time average |
| `%run` | Run script |
| `%load` | Load file |
| `%%writefile` | Save cell |
| `%whos` | List variables |

---

## See Also

- [Jupyter Documentation](https://docs.jupyter.org/)
- [JupyterLab Documentation](https://jupyterlab.readthedocs.io/)
- [Pandas Tutorial](../pandas/README.md) - Data analysis in notebooks
- [DuckDB Tutorial](../duckdb/README.md) - SQL queries in notebooks

---

[← Back to Modules Index](../README.md)
