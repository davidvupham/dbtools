# Variables and Data Types

## What is a Variable?

A variable is like a labeled box that stores data. In Python, you don't need to say what type of data it is - Python figures it out!

```python
# Different types of data
name = "Alice"          # String (text)
age = 30                # Integer (whole number)
height = 5.7            # Float (decimal number)
is_student = True       # Boolean (True or False)
nothing = None          # None (represents "no value")
```

## Example from Our Code

From `connection.py`:

```python
class SnowflakeConnection:
    def __init__(self, account: str, user: Optional[str] = None):
        self.account = account      # Store account name
        self.user = user            # Store username (can be None)
        self.connection = None      # No connection yet
        self._initialized = False   # Private variable (starts with _)
```

**Why this design?**

- `self.account` stores the account name for this specific connection
- `self.connection = None` means "no connection yet" - we'll set it later
- `self._initialized` starts with `_` to indicate it's "private" (internal use only)

## Understanding None

`None` is Python's way of saying "no value" or "nothing yet":

```python
# Example: Finding a user
def find_user(user_id):
    if user_id == 1:
        return "Alice"
    else:
        return None  # User not found

user = find_user(5)
if user is None:
    print("User not found!")
```
