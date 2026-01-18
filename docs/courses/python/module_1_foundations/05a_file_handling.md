# File Handling

## Reading Files

Use the `open()` function with a context manager to safely handle files:

```python
# Read entire file
with open("data.txt", "r") as f:
    content = f.read()

# Read line by line (memory efficient for large files)
with open("data.txt", "r") as f:
    for line in f:
        print(line.strip())

# Read all lines into a list
with open("data.txt", "r") as f:
    lines = f.readlines()
```

## Writing Files

```python
# Write (overwrites existing content)
with open("output.txt", "w") as f:
    f.write("Hello, World!\n")
    f.write("Second line\n")

# Append to existing file
with open("output.txt", "a") as f:
    f.write("Appended line\n")

# Write multiple lines
lines = ["Line 1", "Line 2", "Line 3"]
with open("output.txt", "w") as f:
    f.writelines(line + "\n" for line in lines)
```

## Working with Paths

Use `pathlib` for cross-platform path handling:

```python
from pathlib import Path

# Create path objects
config_dir = Path("config")
config_file = config_dir / "settings.json"

# Check existence
if config_file.exists():
    content = config_file.read_text()

# Create directories
config_dir.mkdir(parents=True, exist_ok=True)

# Write with pathlib
config_file.write_text('{"debug": true}')

# List files in directory
for py_file in Path(".").glob("*.py"):
    print(py_file.name)
```

## JSON Files

```python
import json

# Read JSON
with open("config.json", "r") as f:
    data = json.load(f)

# Write JSON
config = {"database": "postgres", "port": 5432}
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

# Parse JSON string
json_str = '{"name": "Alice"}'
data = json.loads(json_str)
```

## CSV Files

```python
import csv

# Read CSV
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])

# Write CSV
data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]
with open("output.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerows(data)
```

## Best Practices

1. **Always use context managers** (`with` statement) - ensures files are properly closed
2. **Use `pathlib`** for path manipulation instead of string concatenation
3. **Specify encoding** when working with non-ASCII text: `open(f, encoding="utf-8")`
4. **Use binary mode** for non-text files: `open(f, "rb")` or `open(f, "wb")`
