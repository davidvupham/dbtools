# Functions

## What is a Function?

A function is a reusable block of code with a name:

```python
# Define a function
def greet(name):
    """Say hello to someone."""  # Docstring explains what it does
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # "Hello, Alice!"
```

## Parameters and Arguments

```python
# Positional parameters (order matters)
def describe_pet(animal_type, pet_name):
    print(f"I have a {animal_type} named {pet_name}")

describe_pet("dog", "Buddy")  # Must be in order

# Default parameters (optional)
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))              # "Hello, Alice!"
print(greet("Bob", "Hi"))          # "Hi, Bob!"
```

## Example from Our Code

From `connection.py`:

```python
def __init__(
    self,
    account: str,                    # Required parameter
    user: Optional[str] = None,      # Optional (has default)
    warehouse: Optional[str] = None, # Optional
    role: Optional[str] = None,      # Optional
    database: Optional[str] = None   # Optional
):
    """Initialize connection with required and optional parameters."""
    self.account = account  # Must be provided
    self.user = user or os.getenv("SNOWFLAKE_USER")  # Use env var if not provided
```

**Why this design?**

- `account` is required - you must provide it
- Other parameters are optional - use defaults if not provided
- Flexible: minimal required parameters, but can customize everything

## Return Values

```python
# Return multiple values (tuple)
def divide_with_remainder(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide_with_remainder(17, 5)  # q=3, r=2
```
