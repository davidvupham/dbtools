# Solutions — 05a: File Handling

## Key Concepts Demonstrated

- Context managers (`with` statement) for safe file handling
- `pathlib.Path` for cross-platform file paths
- Reading/writing text files with proper encoding
- CSV and JSON file processing
- Directory traversal with `Path.glob()` and `Path.rglob()`
- Error handling for file operations

## Common Mistakes to Avoid

- Forgetting to close files (always use context managers)
- Using string concatenation for paths (use `pathlib` or `os.path.join`)
- Not specifying encoding (always use `encoding='utf-8'`)
- Not handling `FileNotFoundError` and other exceptions
- Using relative paths that depend on current working directory

---

## Exercise 1 Solution

```python
from pathlib import Path

# Create and write to file
filepath = Path("notes.txt")

# Step 1-2: Create and write initial content
with filepath.open("w", encoding="utf-8") as f:
    f.write("Line 1: Hello, World!\n")
    f.write("Line 2: Python is great.\n")
    f.write("Line 3: File handling is useful.\n")

print("File created!")

# Step 3: Read and print with line numbers
print("\nFile contents:")
with filepath.open("r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, start=1):
        print(f"{line_num}: {line.rstrip()}")

# Step 4: Append new line
with filepath.open("a", encoding="utf-8") as f:
    f.write("Line 4: Added later.\n")

print("\nLine appended!")

# Step 5: Read and print final contents
print("\nFinal contents:")
with filepath.open("r", encoding="utf-8") as f:
    print(f.read())

# Cleanup
filepath.unlink()  # Delete the file
```

**Output**:
```
File created!

File contents:
1: Line 1: Hello, World!
2: Line 2: Python is great.
3: Line 3: File handling is useful.

Line appended!

Final contents:
Line 1: Hello, World!
Line 2: Python is great.
Line 3: File handling is useful.
Line 4: Added later.
```

---

## Exercise 2 Solution

```python
from pathlib import Path

def file_stats(filepath: Path) -> dict:
    """
    Calculate statistics for a text file.

    Args:
        filepath: Path to the text file.

    Returns:
        Dictionary with lines, words, chars, unique_words.
    """
    with filepath.open("r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    words = content.split()
    chars = len(content.replace("\n", ""))
    unique_words = set(word.lower() for word in words)

    return {
        "lines": len(lines),
        "words": len(words),
        "chars": chars,
        "unique_words": len(unique_words)
    }


# Create a sample file for testing
sample_path = Path("sample.txt")
sample_content = """Python is a great programming language.
Python is easy to learn and powerful.
Many developers love Python for data science.
"""
sample_path.write_text(sample_content, encoding="utf-8")

# Test the function
stats = file_stats(sample_path)
print(f"Lines: {stats['lines']}")          # 3
print(f"Words: {stats['words']}")          # 20
print(f"Characters: {stats['chars']}")     # 130
print(f"Unique words: {stats['unique_words']}")  # 16

# Cleanup
sample_path.unlink()
```

---

## Exercise 3 Solution

```python
import csv
from pathlib import Path
from datetime import datetime

def read_employees(filepath: Path) -> list[dict]:
    """Read employee data from CSV file."""
    employees = []
    with filepath.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert salary to int
            row["salary"] = int(row["salary"])
            employees.append(row)
    return employees


def avg_salary_by_dept(employees: list[dict]) -> dict[str, float]:
    """Calculate average salary per department."""
    dept_totals = {}
    dept_counts = {}

    for emp in employees:
        dept = emp["department"]
        salary = emp["salary"]
        dept_totals[dept] = dept_totals.get(dept, 0) + salary
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    return {
        dept: dept_totals[dept] / dept_counts[dept]
        for dept in dept_totals
    }


def employees_after_date(employees: list[dict], date: str) -> list[dict]:
    """Filter employees who started after given date (YYYY-MM-DD format)."""
    cutoff = datetime.strptime(date, "%Y-%m-%d")
    return [
        emp for emp in employees
        if datetime.strptime(emp["start_date"], "%Y-%m-%d") > cutoff
    ]


def write_employees(employees: list[dict], filepath: Path) -> None:
    """Write employee data to CSV file."""
    if not employees:
        return

    fieldnames = employees[0].keys()
    with filepath.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(employees)


# Test the functions
csv_path = Path("employees.csv")
csv_content = """name,department,salary,start_date
Alice,Engineering,75000,2020-03-15
Bob,Marketing,65000,2019-07-22
Charlie,Engineering,80000,2018-11-01
Diana,Sales,70000,2021-01-10
Eve,Engineering,85000,2017-06-30"""
csv_path.write_text(csv_content, encoding="utf-8")

# Read and process
employees = read_employees(csv_path)
print("All employees:")
for emp in employees:
    print(f"  {emp['name']}: {emp['department']}, ${emp['salary']:,}")

# Average salary by department
avg_salaries = avg_salary_by_dept(employees)
print("\nAverage salary by department:")
for dept, avg in avg_salaries.items():
    print(f"  {dept}: ${avg:,.2f}")

# Employees after 2020
recent = employees_after_date(employees, "2020-01-01")
print(f"\nEmployees who started after 2020-01-01:")
for emp in recent:
    print(f"  {emp['name']} ({emp['start_date']})")

# Write filtered data
output_path = Path("recent_employees.csv")
write_employees(recent, output_path)
print(f"\nFiltered data written to {output_path}")

# Cleanup
csv_path.unlink()
output_path.unlink()
```

**Output**:
```
All employees:
  Alice: Engineering, $75,000
  Bob: Marketing, $65,000
  Charlie: Engineering, $80,000
  Diana: Sales, $70,000
  Eve: Engineering, $85,000

Average salary by department:
  Engineering: $80,000.00
  Marketing: $65,000.00
  Sales: $70,000.00

Employees who started after 2020-01-01:
  Alice (2020-03-15)
  Diana (2021-01-10)

Filtered data written to recent_employees.csv
```

---

## Exercise 4 Solution

```python
import json
from pathlib import Path
from typing import Any

class ConfigManager:
    """Manage application configuration stored in JSON."""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "debug": False,
        "log_level": "INFO"
    }

    def __init__(self, config_path: Path):
        """Initialize with path to config file."""
        self.config_path = config_path
        self.config = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load existing config or create default."""
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Create default config
            config = self.DEFAULT_CONFIG.copy()
            self._save_config(config)
            return config

    def _save_config(self, config: dict) -> None:
        """Save config dict to file."""
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        self.config[key] = value
        self.save()

    def save(self) -> None:
        """Save configuration to file."""
        self._save_config(self.config)

    def __repr__(self) -> str:
        return f"ConfigManager({self.config_path})"


# Test the implementation
config_path = Path("app_config.json")
config = ConfigManager(config_path)

# Set values
config.set("debug", True)
config.set("database", {"host": "localhost", "port": 5432})
config.set("max_connections", 100)

# Get values
print(f"debug: {config.get('debug')}")  # True
print(f"database: {config.get('database')}")  # {'host': 'localhost', 'port': 5432}
print(f"missing: {config.get('missing', 'default_value')}")  # default_value

# Show saved file contents
print("\nSaved config file:")
print(config_path.read_text())

# Cleanup
config_path.unlink()
```

**Output**:
```
debug: True
database: {'host': 'localhost', 'port': 5432}
missing: default_value

Saved config file:
{
  "version": "1.0.0",
  "debug": true,
  "log_level": "INFO",
  "database": {
    "host": "localhost",
    "port": 5432
  },
  "max_connections": 100
}
```

---

## Exercise 5 Solution

```python
from pathlib import Path

def find_files(
    directory: Path,
    pattern: str = "*",
    recursive: bool = True
) -> list[Path]:
    """
    Find all files matching pattern in directory.

    Args:
        directory: Starting directory.
        pattern: Glob pattern (e.g., "*.py", "*.txt").
        recursive: If True, search subdirectories.

    Returns:
        List of matching file paths.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if recursive:
        # Use ** for recursive search
        files = list(directory.rglob(pattern))
    else:
        files = list(directory.glob(pattern))

    # Filter to only include files (not directories)
    return [f for f in files if f.is_file()]


def summarize_files(files: list[Path]) -> dict:
    """
    Generate summary statistics for files.

    Returns:
        Dictionary with count, total_size, largest, smallest.
    """
    if not files:
        return {
            "count": 0,
            "total_size": 0,
            "largest": None,
            "smallest": None
        }

    sizes = [(f, f.stat().st_size) for f in files]
    total_size = sum(size for _, size in sizes)

    largest = max(sizes, key=lambda x: x[1])
    smallest = min(sizes, key=lambda x: x[1])

    return {
        "count": len(files),
        "total_size": total_size,
        "largest": largest[0],
        "largest_size": largest[1],
        "smallest": smallest[0],
        "smallest_size": smallest[1]
    }


def list_files_by_size(files: list[Path], descending: bool = True) -> list[tuple[Path, int]]:
    """List files sorted by size."""
    sizes = [(f, f.stat().st_size) for f in files]
    return sorted(sizes, key=lambda x: x[1], reverse=descending)


# Test with current directory
try:
    py_files = find_files(Path("."), "*.py", recursive=True)
    summary = summarize_files(py_files)

    print(f"Found {summary['count']} Python files")
    if summary['count'] > 0:
        print(f"Total size: {summary['total_size']:,} bytes")
        print(f"Largest: {summary['largest']} ({summary['largest_size']:,} bytes)")
        print(f"Smallest: {summary['smallest']} ({summary['smallest_size']:,} bytes)")

        print("\nTop 5 largest files:")
        for path, size in list_files_by_size(py_files)[:5]:
            print(f"  {path}: {size:,} bytes")
except FileNotFoundError as e:
    print(f"Error: {e}")
```

---

## Exercise 6 Solution

```python
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str


def parse_log_line(line: str) -> LogEntry | None:
    """Parse a single log line."""
    line = line.strip()
    if not line:
        return None

    try:
        # Expected format: "2024-01-15 10:23:45 LEVEL Message..."
        parts = line.split(" ", 3)
        if len(parts) < 4:
            return None

        date_str = parts[0]
        time_str = parts[1]
        level = parts[2]
        message = parts[3]

        timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

        return LogEntry(timestamp=timestamp, level=level, message=message)
    except (ValueError, IndexError):
        return None


def parse_log_file(filepath: Path) -> list[LogEntry]:
    """Parse log file into list of LogEntry objects."""
    entries = []
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            entry = parse_log_line(line)
            if entry:
                entries.append(entry)
    return entries


def filter_by_level(entries: list[LogEntry], level: str) -> list[LogEntry]:
    """Filter entries by log level."""
    return [e for e in entries if e.level.upper() == level.upper()]


def count_by_level(entries: list[LogEntry]) -> dict[str, int]:
    """Count entries per log level."""
    return dict(Counter(e.level for e in entries))


def get_error_messages(entries: list[LogEntry]) -> list[str]:
    """Extract all error messages."""
    return [e.message for e in entries if e.level == "ERROR"]


# Test with sample log file
log_path = Path("app.log")
log_content = """2024-01-15 10:23:45 INFO User 'alice' logged in
2024-01-15 10:24:12 WARNING High memory usage detected: 85%
2024-01-15 10:25:33 ERROR Database connection failed: timeout
2024-01-15 10:26:01 INFO User 'bob' logged in
2024-01-15 10:27:45 ERROR Authentication failed for user 'charlie'
2024-01-15 10:28:00 INFO User 'alice' logged out"""
log_path.write_text(log_content, encoding="utf-8")

# Parse and analyze
entries = parse_log_file(log_path)
print(f"Parsed {len(entries)} log entries")

# Count by level
counts = count_by_level(entries)
print("\nCounts by level:")
for level, count in counts.items():
    print(f"  {level}: {count}")

# Filter errors
errors = filter_by_level(entries, "ERROR")
print(f"\nError entries ({len(errors)}):")
for entry in errors:
    print(f"  [{entry.timestamp}] {entry.message}")

# Get error messages
error_messages = get_error_messages(entries)
print("\nError messages:")
for msg in error_messages:
    print(f"  - {msg}")

# Cleanup
log_path.unlink()
```

**Output**:
```
Parsed 6 log entries

Counts by level:
  INFO: 3
  WARNING: 1
  ERROR: 2

Error entries (2):
  [2024-01-15 10:25:33] Database connection failed: timeout
  [2024-01-15 10:27:45] Authentication failed for user 'charlie'

Error messages:
  - Database connection failed: timeout
  - Authentication failed for user 'charlie'
```

---

## Exercise 7 Solution

```python
from pathlib import Path
from datetime import datetime
import shutil

class BackupManager:
    """Manage file backups with incremental support."""

    def __init__(self, source: Path, backup_root: Path):
        """Initialize backup manager."""
        self.source = Path(source)
        self.backup_root = Path(backup_root)
        self.log_entries = []

    def create_backup(self, incremental: bool = True) -> Path:
        """Create a backup of the source directory."""
        if not self.source.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source}")

        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_root / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        self._log(f"Starting backup to {backup_dir}")
        self._log(f"Mode: {'incremental' if incremental else 'full'}")

        files_copied = 0
        files_skipped = 0

        # Walk through source directory
        for source_file in self.source.rglob("*"):
            if source_file.is_file():
                # Calculate relative path
                rel_path = source_file.relative_to(self.source)
                dest_file = backup_dir / rel_path

                # Create parent directories
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                if incremental and not self._should_copy(source_file, dest_file):
                    self._log(f"Skipped (unchanged): {rel_path}")
                    files_skipped += 1
                else:
                    shutil.copy2(source_file, dest_file)
                    self._log(f"Copied: {rel_path}")
                    files_copied += 1

        self._log(f"Backup complete: {files_copied} copied, {files_skipped} skipped")
        return backup_dir

    def _should_copy(self, source_file: Path, dest_file: Path) -> bool:
        """Check if file should be copied (for incremental backup)."""
        if not dest_file.exists():
            return True

        # Compare modification times
        source_mtime = source_file.stat().st_mtime
        dest_mtime = dest_file.stat().st_mtime

        return source_mtime > dest_mtime

    def _log(self, message: str) -> None:
        """Add entry to operation log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_entries.append(f"[{timestamp}] {message}")

    def get_log(self) -> list[str]:
        """Return all log entries."""
        return self.log_entries


# Test the implementation
# Create a test source directory
source_dir = Path("test_project")
source_dir.mkdir(exist_ok=True)
(source_dir / "file1.txt").write_text("Hello, World!")
(source_dir / "subdir").mkdir(exist_ok=True)
(source_dir / "subdir" / "file2.txt").write_text("Nested file")

backup_root = Path("backups")

backup = BackupManager(source_dir, backup_root)
backup_path = backup.create_backup(incremental=True)

print(f"Backup created at: {backup_path}")
print("\nOperation log:")
for entry in backup.get_log():
    print(entry)

# Cleanup
shutil.rmtree(source_dir)
shutil.rmtree(backup_root)
```

---

## Exercise 8 Solution

```python
from pathlib import Path

def detect_encoding(filepath: Path) -> str:
    """
    Attempt to detect file encoding by trying common encodings.

    Returns:
        Detected encoding name.
    """
    # Try common encodings in order of likelihood
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]

    for encoding in encodings:
        try:
            with filepath.open("r", encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue

    # Fallback to latin-1 (accepts any byte sequence)
    return "latin-1"


def convert_encoding(
    input_path: Path,
    output_path: Path,
    from_encoding: str,
    to_encoding: str = "utf-8"
) -> None:
    """Convert file from one encoding to another."""
    # Read with source encoding
    with input_path.open("r", encoding=from_encoding) as f:
        content = f.read()

    # Write with target encoding
    with output_path.open("w", encoding=to_encoding) as f:
        f.write(content)


def safe_read(filepath: Path, encodings: list[str] = None) -> str:
    """
    Read file trying multiple encodings until one works.

    Args:
        filepath: Path to file.
        encodings: List of encodings to try.

    Returns:
        File contents as string.

    Raises:
        UnicodeDecodeError: If no encoding works.
    """
    if encodings is None:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with filepath.open("r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue

    # If all fail, raise the error
    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        0,
        f"Could not decode file with any of: {encodings}"
    )


# Test with different encodings
# Create test file with UTF-8
utf8_path = Path("test_utf8.txt")
utf8_path.write_text("Hello, 世界! Ñoño", encoding="utf-8")

# Detect encoding
detected = detect_encoding(utf8_path)
print(f"Detected encoding: {detected}")  # utf-8

# Safe read
content = safe_read(utf8_path)
print(f"Content: {content}")

# Convert to latin-1 (will lose some characters)
latin1_path = Path("test_latin1.txt")
latin1_content = "Hello, World! Niño"
latin1_path.write_text(latin1_content, encoding="latin-1")

# Read with safe_read
content = safe_read(latin1_path)
print(f"Latin-1 content: {content}")

# Cleanup
utf8_path.unlink()
latin1_path.unlink()
```

---

## Alternative Approaches

### Using `chardet` for encoding detection

```python
# pip install chardet
import chardet

def detect_encoding_chardet(filepath: Path) -> str:
    """Detect encoding using chardet library."""
    with filepath.open("rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]
```

### Using `contextlib` for file operations

```python
from contextlib import contextmanager

@contextmanager
def atomic_write(filepath: Path, mode: str = "w", encoding: str = "utf-8"):
    """Write to a temp file, then rename (atomic on most systems)."""
    temp_path = filepath.with_suffix(".tmp")
    try:
        with temp_path.open(mode, encoding=encoding) as f:
            yield f
        temp_path.replace(filepath)  # Atomic rename
    except:
        temp_path.unlink(missing_ok=True)
        raise

# Usage:
# with atomic_write(Path("output.txt")) as f:
#     f.write("Content")
```

---

[← Back to Exercises](../exercises/ex_05a_file_handling.md) | [← Back to Chapter](../05a_file_handling.md) | [← Back to Module 1](../README.md)
