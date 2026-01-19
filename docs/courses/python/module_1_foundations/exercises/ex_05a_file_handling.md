# Exercises — 05a: File Handling

## Learning Objectives

After completing these exercises, you will be able to:
- Read and write text files using context managers
- Work with file paths safely using pathlib
- Handle common file operations (copy, move, delete)
- Process CSV and JSON files
- Handle file encoding properly
- Implement error handling for file operations

---

## Exercise 1: Basic File Operations (Warm-up)

**Bloom Level**: Apply

Create a program that:

1. Creates a new text file called `notes.txt`
2. Writes these lines to it:
   ```
   Line 1: Hello, World!
   Line 2: Python is great.
   Line 3: File handling is useful.
   ```
3. Reads the file back and prints each line with its line number
4. Appends a new line: "Line 4: Added later."
5. Reads and prints the final contents

**Requirements**:
- Use context managers (`with` statement)
- Use `pathlib.Path` for file paths

---

## Exercise 2: Word Counter (Practice)

**Bloom Level**: Apply

Write a function that reads a text file and returns statistics:

```python
from pathlib import Path

def file_stats(filepath: Path) -> dict:
    """
    Calculate statistics for a text file.

    Args:
        filepath: Path to the text file.

    Returns:
        Dictionary with keys:
        - lines: number of lines
        - words: number of words
        - chars: number of characters (excluding newlines)
        - unique_words: number of unique words (case-insensitive)
    """
    pass

# Test with a sample file
stats = file_stats(Path("sample.txt"))
print(f"Lines: {stats['lines']}")
print(f"Words: {stats['words']}")
print(f"Characters: {stats['chars']}")
print(f"Unique words: {stats['unique_words']}")
```

Create a sample text file to test your function.

---

## Exercise 3: CSV Processing (Practice)

**Bloom Level**: Apply

Given a CSV file `employees.csv`:

```csv
name,department,salary,start_date
Alice,Engineering,75000,2020-03-15
Bob,Marketing,65000,2019-07-22
Charlie,Engineering,80000,2018-11-01
Diana,Sales,70000,2021-01-10
Eve,Engineering,85000,2017-06-30
```

Write functions to:

1. **Read the CSV** and return a list of dictionaries
2. **Calculate average salary by department**
3. **Find employees who started after 2020**
4. **Write filtered data to a new CSV file**

```python
import csv
from pathlib import Path
from datetime import datetime

def read_employees(filepath: Path) -> list[dict]:
    """Read employee data from CSV file."""
    pass

def avg_salary_by_dept(employees: list[dict]) -> dict[str, float]:
    """Calculate average salary per department."""
    pass

def employees_after_date(employees: list[dict], date: str) -> list[dict]:
    """Filter employees who started after given date (YYYY-MM-DD format)."""
    pass

def write_employees(employees: list[dict], filepath: Path) -> None:
    """Write employee data to CSV file."""
    pass
```

---

## Exercise 4: JSON Configuration (Practice)

**Bloom Level**: Apply

Create a configuration manager that works with JSON files:

```python
import json
from pathlib import Path
from typing import Any

class ConfigManager:
    """Manage application configuration stored in JSON."""

    def __init__(self, config_path: Path):
        """Initialize with path to config file."""
        self.config_path = config_path
        self.config = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load existing config or create default."""
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        pass

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        pass

    def save(self) -> None:
        """Save configuration to file."""
        pass

# Test your implementation
config = ConfigManager(Path("app_config.json"))
config.set("debug", True)
config.set("database", {"host": "localhost", "port": 5432})
print(config.get("debug"))  # True
print(config.get("database"))  # {'host': 'localhost', 'port': 5432}
print(config.get("missing", "default_value"))  # default_value
```

---

## Exercise 5: Directory Walker (Practice)

**Bloom Level**: Analyze

Write a program that:

1. Walks through a directory tree
2. Finds all files matching a pattern (e.g., `*.py`, `*.txt`)
3. Reports the total size and count
4. Optionally lists files sorted by size

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
    pass

def summarize_files(files: list[Path]) -> dict:
    """
    Generate summary statistics for files.

    Returns:
        Dictionary with:
        - count: number of files
        - total_size: total size in bytes
        - largest: path to largest file
        - smallest: path to smallest file
    """
    pass

# Test: find all Python files in current directory
py_files = find_files(Path("."), "*.py", recursive=True)
summary = summarize_files(py_files)
print(f"Found {summary['count']} Python files")
print(f"Total size: {summary['total_size']:,} bytes")
```

---

## Exercise 6: Log File Parser (Analyze)

**Bloom Level**: Analyze

Parse a log file and extract meaningful information:

```
2024-01-15 10:23:45 INFO User 'alice' logged in
2024-01-15 10:24:12 WARNING High memory usage detected: 85%
2024-01-15 10:25:33 ERROR Database connection failed: timeout
2024-01-15 10:26:01 INFO User 'bob' logged in
2024-01-15 10:27:45 ERROR Authentication failed for user 'charlie'
2024-01-15 10:28:00 INFO User 'alice' logged out
```

Write a log parser that:

1. Reads the log file line by line
2. Parses each line into components (timestamp, level, message)
3. Filters entries by log level
4. Counts occurrences of each log level
5. Extracts all error messages

```python
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    message: str

def parse_log_file(filepath: Path) -> list[LogEntry]:
    """Parse log file into list of LogEntry objects."""
    pass

def filter_by_level(entries: list[LogEntry], level: str) -> list[LogEntry]:
    """Filter entries by log level."""
    pass

def count_by_level(entries: list[LogEntry]) -> dict[str, int]:
    """Count entries per log level."""
    pass

def get_error_messages(entries: list[LogEntry]) -> list[str]:
    """Extract all error messages."""
    pass
```

---

## Exercise 7: File Backup Utility (Challenge)

**Bloom Level**: Create

Create a backup utility that:

1. Copies files from a source directory to a backup directory
2. Preserves the directory structure
3. Adds timestamps to backup folder names
4. Skips files that haven't changed (based on modification time)
5. Logs all operations

```python
from pathlib import Path
from datetime import datetime
import shutil

class BackupManager:
    """Manage file backups with incremental support."""

    def __init__(self, source: Path, backup_root: Path):
        """
        Initialize backup manager.

        Args:
            source: Directory to back up.
            backup_root: Root directory for backups.
        """
        self.source = source
        self.backup_root = backup_root
        self.log_entries = []

    def create_backup(self, incremental: bool = True) -> Path:
        """
        Create a backup of the source directory.

        Args:
            incremental: If True, only copy changed files.

        Returns:
            Path to the backup directory.
        """
        pass

    def _should_copy(self, source_file: Path, dest_file: Path) -> bool:
        """Check if file should be copied (for incremental backup)."""
        pass

    def _log(self, message: str) -> None:
        """Add entry to operation log."""
        pass

    def get_log(self) -> list[str]:
        """Return all log entries."""
        return self.log_entries

# Test your implementation
backup = BackupManager(Path("./my_project"), Path("./backups"))
backup_path = backup.create_backup(incremental=True)
print(f"Backup created at: {backup_path}")
for entry in backup.get_log():
    print(entry)
```

---

## Exercise 8: File Encoding Detective (Challenge)

**Bloom Level**: Analyze

Write a utility that:

1. Detects the encoding of a text file
2. Converts files between encodings
3. Handles common encoding errors gracefully

```python
from pathlib import Path

def detect_encoding(filepath: Path) -> str:
    """
    Attempt to detect file encoding.

    Returns:
        Detected encoding name (e.g., 'utf-8', 'latin-1').
    """
    pass

def convert_encoding(
    input_path: Path,
    output_path: Path,
    from_encoding: str,
    to_encoding: str = "utf-8"
) -> None:
    """
    Convert file from one encoding to another.

    Args:
        input_path: Path to source file.
        output_path: Path to destination file.
        from_encoding: Source encoding.
        to_encoding: Target encoding (default: utf-8).
    """
    pass

def safe_read(filepath: Path, encodings: list[str] = None) -> str:
    """
    Read file trying multiple encodings until one works.

    Args:
        filepath: Path to file.
        encodings: List of encodings to try (default: common ones).

    Returns:
        File contents as string.

    Raises:
        UnicodeDecodeError: If no encoding works.
    """
    pass
```

**Hint**: Try encodings in order: `['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']`

---

## Deliverables

Submit your code for all exercises. Ensure proper error handling in all file operations.

---

[← Back to Chapter](../05a_file_handling.md) | [View Solutions](../solutions/sol_05a_file_handling.md) | [← Back to Module 1](../README.md)
