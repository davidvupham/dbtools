# Python pattern matching reference

*Added in Python 3.10 (PEP 634)*

Python's `match`/`case` syntax provides structural pattern matching - it matches **structure**, not just values. Think of it as if-statements that explain themselves.

## Basic syntax

```python
match subject:
    case pattern1:
        # handle pattern1
    case pattern2:
        # handle pattern2
    case _:
        # wildcard/default case
```

## Pattern types

### Literal patterns

Match exact values:

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

### Capture patterns

Bind values to names:

```python
match point:
    case (x, y):
        print(f"Point at {x}, {y}")
```

### Wildcard pattern

`_` matches anything without binding:

```python
match value:
    case (_, y):  # Ignore first element
        print(f"Second element: {y}")
```

### Sequence patterns

Match lists and tuples with destructuring:

```python
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

### Mapping patterns

Match dictionaries by structure:

```python
event = {"type": "user_action", "action": "login", "user_id": "uid123"}

match event:
    case {"type": "user_action", "action": "login", "user_id": uid}:
        handle_login(uid)
    case {"type": "user_action", "action": "logout"}:
        handle_logout()
    case {"type": "system_event", "level": level}:
        log_system_event(level)
```

This eliminates nested `.get()` calls and makes the expected structure explicit.

### Class patterns

Match object attributes:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

match point:
    case Point(x=0, y=0):
        print("Origin")
    case Point(x=0, y=y):
        print(f"On Y-axis at {y}")
    case Point(x=x, y=0):
        print(f"On X-axis at {x}")
```

### OR patterns

Match multiple alternatives:

```python
match status:
    case 400 | 401 | 403:
        return "Client error"
    case 500 | 502 | 503:
        return "Server error"
```

## Guards

Add conditions with `if`:

```python
match status, retries, result:
    case "pending", r, _ if r < 3:
        handle_retry()
    case "pending", r, _:
        fail_job()  # retries >= 3
    case "success", _, res if res is not None:
        save_result(res)
    case "error", _, _:
        log_error()
    case _:
        raise ValueError("Unknown state")
```

## Refactoring example

### Before (if-elif chains)

```python
if status == "pending" and retries < 3:
    handle_retry()
elif status == "pending" and retries >= 3:
    fail_job()
elif status == "success" and result is not None:
    save_result()
elif status == "error":
    log_error()
else:
    raise ValueError("Unknown state")
```

### After (pattern matching)

```python
match status, retries, result:
    case "pending", r, _ if r < 3:
        handle_retry()
    case "pending", r, _:
        fail_job()
    case "success", _, res if res is not None:
        save_result(res)
    case "error", _, _:
        log_error()
    case _:
        raise ValueError("Unknown state")
```

Benefits:
- Each case reads like a rule
- Control flow is obvious
- No mental backtracking required
- Missing cases stand out immediately

## When to use pattern matching

**Use `match` for states** - answering "What kind of thing is this?"

```python
match event:
    case {"type": "click", "target": target}:
        handle_click(target)
    case {"type": "keypress", "key": key}:
        handle_key(key)
```

**Use `if` for decisions** - answering "Should I do this?"

```python
if user.is_active:
    send_email()
```

### Good use cases

- Multiple related conditions on the same data
- Destructuring complex data structures (JSON, tuples, dataclasses)
- State machines and event handling
- Parsing structured input

### Avoid pattern matching for

- Simple boolean checks
- One-line guards
- Performance-critical hot paths (profile first)
- Codebases requiring Python < 3.10

## Benefits

1. **Explicit edge cases**: Each case is isolated and visible
2. **No overlapping conditions**: Order feels intentional
3. **Missing cases stand out**: Encourages total logic
4. **Self-documenting**: The match block reads like documentation
5. **Better API design**: Encourages predictable, shape-driven data structures

## Performance considerations

Pattern matching is typically not slower than equivalent if-elif chains. In most applications:

- I/O dominates performance
- Readability beats micro-optimizations
- Correctness saves more time than speed

If performance matters, measure. Otherwise, optimize for clarity.

## Related resources

- [PEP 634 - Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [PEP 635 - Motivation and Rationale](https://peps.python.org/pep-0635/)
- [PEP 636 - Tutorial](https://peps.python.org/pep-0636/)
