# Rich Tutorial

**Level**: Beginner to Advanced
**Category**: Terminal Formatting / UX

Rich is a Python library for writing rich text (with color and style) to the terminal, and for displaying advanced content such as tables, markdown, and syntax highlighted code.

## 📦 Installation

```bash
pip install rich
```

## 🚀 Beginner: Colored Output

Stop using simple `print()`. Use Rich to make your logs readable.

```python
from rich import print

print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:", locals())
print("[italic red]Error[/italic red]: Something went wrong!")
print("[green]Success[/green]: Operation completed.")
```

## 🏃 Intermediate: Console & Tables

For more control, use the `Console` object and creating structured `Table`s.

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Create a table
table = Table(title="Star Wars Movies")

table.add_column("Released", justify="right", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right", style="green")

table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")

console.print(table)
```

## 🧠 Advanced: Progress Bars & Tracebacks

Rich provides beautiful process bars and easy-to-read exception tracebacks.

### Progress Bar

```python
import time
from rich.progress import track

# Wrap any iterable with track()
for step in track(range(10), description="Processing..."):
    time.sleep(0.5)  # Simulate work
```

### Better Tracebacks

Install this once at the start of your app to make all errors readable.

```python
from rich.traceback import install
install(show_locals=True)

# Generate an error to see the magic
def divide_by_zero():
    return 1 / 0

divide_by_zero()
```

## 💡 Use Cases

1.  **CLI Tools**: Build professional-looking command-line interfaces.
2.  **Debugging**: Use `rich.inspect(obj)` to see all methods and attributes of an object clearly.
3.  **Long-running Scripts**: Use progress bars to keep track of batch processing jobs.
