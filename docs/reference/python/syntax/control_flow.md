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

The `match` statement is similar to `switch` in other languages but more powerful (structural pattern matching).

```python
def http_error(status):
    match status:
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"
        case _:
            return "Something's wrong with the internet"

# Deconstruct patterns
point = (0, 10)
match point:
    case (0, 0):
        print("Origin")
    case (0, y):
        print(f"Y-axis at {y}")
    case (x, 0):
        print(f"X-axis at {x}")
    case (x, y):
        print(f"Point at {x}, {y}")
```

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
