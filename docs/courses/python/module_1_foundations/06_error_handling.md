# Error Handling

## Why Handle Errors?

Programs encounter problems: files don't exist, networks fail, users provide bad input. Error handling lets your program deal with these gracefully instead of crashing.

## Basic Try-Except

```python
# Without error handling - program crashes
result = 10 / 0  # ZeroDivisionError: division by zero

# With error handling - program continues
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
    result = None

print("Program continues...")
```

## Finally Block

```python
# Finally always runs, even if there's an error
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    # This ALWAYS runs, even if there was an error
    if 'file' in locals() and file:
        file.close()
    print("Cleanup complete")
```

## Custom Exceptions

```python
# Define custom exception
class InvalidAgeError(Exception):
    """Raised when age is invalid."""
    pass

# Use custom exception
def set_age(age):
    if age < 0 or age > 150:
        raise InvalidAgeError(f"Invalid age: {age}")
    return age
```

## The Else Clause

The `else` block runs only when no exception occurs. This separates the "happy path" from error handling:

```python
try:
    conn = connect()
    data = conn.read()
except TimeoutError:
    backoff()
else:
    # Only runs if no exception occurred
    process(data)
finally:
    # Always runs for cleanup
    conn.close()
```

Use `else` to keep your try block minimal - only the code that might raise the exception you're catching.

## Exception Chaining

Use `raise ... from e` to preserve the original error context:

```python
try:
    price = float(row["price"])
except KeyError as e:
    raise ValueError("Missing 'price' field") from e
except ValueError as e:
    raise ValueError(f"Invalid price: {row.get('price')!r}") from e
```

This creates a chain showing both the new error and its cause, making debugging easier.

## Anti-Patterns to Avoid

### Silent exception swallowing

```python
# BAD: Hides bugs, returns unexpected None
def get_user(user_id):
    try:
        return database.fetch(user_id)
    except Exception:
        return None  # Silent failure - caller has no idea what went wrong

# GOOD: Catch specific exceptions, let unexpected ones propagate
def get_user(user_id):
    try:
        return database.fetch(user_id)
    except UserNotFoundError:
        return None  # Expected case - caller knows user doesn't exist
    # Other exceptions (connection errors, etc.) propagate up
```

### Catching too broadly

```python
# BAD: Catches KeyboardInterrupt, SystemExit, and real bugs
try:
    result = process_data(data)
except:
    print("Something went wrong")

# BAD: Still too broad - hides TypeError, AttributeError, etc.
try:
    result = int(user_input)
except Exception:
    print("Error")

# GOOD: Catch what you expect
try:
    result = int(user_input)
except ValueError:
    print("Please enter a valid number")
```

### Using exceptions for control flow

```python
# BAD: Using exceptions for expected conditions
def find_item(items, target):
    try:
        return items.index(target)
    except ValueError:
        return -1

# GOOD: Check condition directly
def find_item(items, target):
    if target in items:
        return items.index(target)
    return -1
```

## Best Practices Summary

1. **Catch specific exceptions** - Never use bare `except:` or overly broad `except Exception:`
2. **Catch near the source** - Handle errors where you have context to deal with them
3. **Use exception chaining** - `raise NewError(...) from original_error`
4. **Use `else` for happy path** - Keep try blocks minimal
5. **Use `finally` for cleanup** - Or better, use context managers (`with` statement)
6. **Fail fast** - Let unexpected exceptions propagate; don't silently swallow errors
7. **Log before re-raising** - Capture context with `logger.exception()` or `exc_info=True`
