# Context Managers

## The `with` Statement

Context managers are used to manage resources like files, network connections, and locks. They ensure that cleanup code matches setup code.

### The Problem

```python
f = open('file.txt', 'w')
try:
    f.write('hello')
finally:
    f.close()
```

### The Solution

```python
with open('file.txt', 'w') as f:
    f.write('hello')
# f is automatically closed here
```

## Creating Context Managers

### Class-Based (`__enter__`, `__exit__`)

```python
class FileManager:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename, 'w')
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

with FileManager('test.txt') as f:
    f.write('testing')
```

### Generator-Based (`@contextmanager`)

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename):
    f = open(filename, 'w')
    try:
        yield f
    finally:
        f.close()

with file_manager('test.txt') as f:
    f.write('testing')
```
