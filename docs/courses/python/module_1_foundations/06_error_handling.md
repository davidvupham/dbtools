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
