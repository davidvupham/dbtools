# Python Control Flow Reference

## Conditional Statements (`if`)

```python
x = 10
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")
```

## Loops

### `for` Loop

Iterates over a sequence (list, tuple, string, range).

```python
for i in range(5):
    if i == 3:
        continue  # Skip iteration
    print(i)
else:
    print("Loop finished normally (no break)")
```

### `while` Loop

Repeats as long as a condition is true.

```python
count = 0
while count < 5:
    print(count)
    count += 1
    if count == 2:
        break  # Exit loop
```

## Pattern Matching (`match`)

*Added in Python 3.10*

The `match` statement provides structural pattern matching - more powerful than a simple `switch`.

```python
def http_error(status):
    match status:
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case _:
            return "Unknown error"
```

See **[Pattern Matching Reference](./pattern-matching.md)** for guards, destructuring, mapping patterns, and best practices.

## Exception Handling (`try` / `except`)

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except (TypeError, ValueError):
    print("Invalid input")
else:
    print("No errors occurred")
finally:
    print("Always runs (cleanup)")
```

## Context Managers (`with`)

Used for resource management (files, locks, connections).

```python
with open("file.txt", "r") as f:
    data = f.read()
# File is automatically closed here
```
