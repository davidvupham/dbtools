# Complete Python Tutorial for Beginners
## Learn Python Through the Snowflake Monitoring Project

Welcome! This tutorial will teach you Python from the ground up, using real examples from our codebase. By the end, you'll understand not just **what** the code does, but **why** it was written this way.

---

## Table of Contents

1. [Introduction to Python](#introduction-to-python)
2. [Variables and Data Types](#variables-and-data-types)
3. [Data Structures](#data-structures)
4. [Functions](#functions)
5. [Error Handling](#error-handling)
6. [Type Hints](#type-hints)
7. [Decorators](#decorators)
8. [Context Managers](#context-managers)
9. [Logging](#logging)
10. [Modules and Packages](#modules-and-packages)
11. [Design Patterns](#design-patterns)

---

## Introduction to Python

### What is Python?

Python is a **high-level programming language** that emphasizes code readability. Unlike languages like C++ or Java, Python code looks almost like English, making it perfect for beginners.

### Why Python?

```python
# This is valid Python code!
if user_is_authenticated:
    print("Welcome back!")
```

Compare this to Java:
```java
// Same thing in Java
if (userIsAuthenticated) {
    System.out.println("Welcome back!");
}
```

Python is cleaner and easier to read!

### Your First Python Program

```python
# This is a comment - Python ignores it
# Comments help explain what code does

# Print text to the screen
print("Hello, World!")

# Store data in a variable
name = "Alice"
print(f"Hello, {name}!")  # Output: Hello, Alice!
```

**Key Concepts:**
- `#` starts a comment
- `print()` displays output
- Variables store data (no need to declare types!)
- `f"..."` creates formatted strings

---

## Variables and Data Types

### What is a Variable?

A variable is like a labeled box that stores data. In Python, you don't need to say what type of data it is - Python figures it out!

```python
# Different types of data
name = "Alice"          # String (text)
age = 30                # Integer (whole number)
height = 5.7            # Float (decimal number)
is_student = True       # Boolean (True or False)
nothing = None          # None (represents "no value")
```

### Example from Our Code

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

### Understanding None

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

From our code in `connection.py`:
```python
self.connection = None  # No connection established yet

def close(self):
    if self.connection is not None:  # Check if we have a connection
        self.connection.close()      # Only close if it exists
```

---

## Data Structures

### Lists - Ordered Collections

Lists store multiple items in order:

```python
# Create a list
fruits = ["apple", "banana", "cherry"]

# Access items (counting starts at 0!)
first_fruit = fruits[0]   # "apple"
last_fruit = fruits[-1]   # "cherry" (negative counts from end)

# Add items
fruits.append("date")     # Add to end
fruits.insert(1, "blueberry")  # Insert at position 1

# Loop through items
for fruit in fruits:
    print(f"I like {fruit}")

# Check if item exists
if "apple" in fruits:
    print("We have apples!")
```

**Example from Our Code** (`monitor.py`):
```python
def monitor_all(self) -> MonitoringResult:
    """Monitor everything and return results."""

    # Create empty lists to store results
    failure_results = []
    latency_results = []

    # Add results as we find them
    for fg in failover_groups:
        result = self.check_replication_failure(fg)
        if result.has_failure:
            failure_results.append(result)  # Add to list

    # Return all results
    return MonitoringResult(
        failures=failure_results,
        latencies=latency_results
    )
```

**Why use lists?**
- We don't know how many failures we'll find
- Lists can grow dynamically
- Easy to loop through and process each item

### Dictionaries - Key-Value Pairs

Dictionaries store data with labels (keys):

```python
# Create a dictionary
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Access values by key
print(person["name"])  # "Alice"

# Add or update values
person["email"] = "alice@example.com"
person["age"] = 31  # Update existing value

# Check if key exists
if "email" in person:
    print(f"Email: {person['email']}")

# Loop through dictionary
for key, value in person.items():
    print(f"{key}: {value}")
```

**Example from Our Code** (`connection.py`):
```python
def get_connection_info(self) -> Dict[str, Any]:
    """Get information about this connection."""
    return {
        'account': self.account,
        'user': self.user,
        'warehouse': self.warehouse,
        'role': self.role,
        'database': self.database,
        'connected': self.is_connected()
    }
```

**Why use dictionaries?**
- Descriptive labels make code self-documenting
- Easy to add new fields
- Perfect for returning structured data
- JSON-like format (common in APIs)

### Tuples - Immutable Collections

Tuples are like lists but can't be changed after creation:

```python
# Create a tuple
coordinates = (10.5, 20.3)
x, y = coordinates  # Unpack values

# Multiple return values use tuples
def get_status():
    return True, "Connected", 100  # Returns a tuple

success, message, code = get_status()  # Unpack
```

**Example from Our Code** (`connection.py`):
```python
def execute_query(self, query: str, params: Optional[tuple] = None):
    """Execute a query with optional parameters."""
    if params:
        cursor.execute(query, params)  # params is a tuple
```

**Why tuples?**
- Immutable (can't accidentally change)
- Slightly faster than lists
- Used for multiple return values
- Database parameters are traditionally tuples

---

## Functions

### What is a Function?

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

### Parameters and Arguments

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

**Example from Our Code** (`connection.py`):
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

### Return Values

```python
# Return a single value
def add(a, b):
    return a + b

result = add(5, 3)  # 8

# Return multiple values (tuple)
def divide_with_remainder(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide_with_remainder(17, 5)  # q=3, r=2

# Return None (implicit)
def log_message(message):
    print(message)
    # No return statement = returns None
```

**Example from Our Code** (`connection.py`):
```python
def test_connectivity(self, timeout_seconds: int = 30) -> Dict[str, Any]:
    """Test if we can connect to Snowflake."""
    try:
        # ... test connection ...
        return {
            'success': True,
            'response_time_ms': response_time,
            'account_info': account_info,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'response_time_ms': 0,
            'account_info': None,
            'error': str(e)
        }
```

**Why return a dictionary?**
- Returns multiple pieces of information
- Self-documenting (keys explain values)
- Easy to add more fields later
- Caller can check `result['success']` to see if it worked

---

<!-- OOP content intentionally removed to keep Python Part 1 focused on core language fundamentals. For OOP, see docs/tutorials/oop/. -->

## Error Handling

### Why Handle Errors?

Programs encounter problems: files don't exist, networks fail, users provide bad input. Error handling lets your program deal with these gracefully instead of crashing.

### Basic Try-Except

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

### Multiple Exception Types

```python
def safe_divide(a, b):
    """Divide two numbers safely."""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Error: Cannot divide by zero")
        return None
    except TypeError:
        print("Error: Both inputs must be numbers")
        return None

print(safe_divide(10, 2))      # 5.0
print(safe_divide(10, 0))      # Error message, returns None
print(safe_divide(10, "2"))    # Error message, returns None
```

### Example from Our Code

From `connection.py`:
```python
def connect(self) -> snowflake.connector.SnowflakeConnection:
    """Establish connection to Snowflake."""
    try:
        # Try to connect
        connection_params = {
            "account": self.account,
            "user": self.user,
            "private_key": self.private_key,
        }

        self.connection = snowflake.connector.connect(**connection_params)
        logger.info("Successfully connected to Snowflake account: %s", self.account)
        return self.connection

    except Exception as e:
        # If anything goes wrong, log it and raise a custom error
        logger.error("Failed to connect to Snowflake account %s: %s", self.account, str(e))
        raise SnowflakeConnectionError(
            f"Failed to connect to Snowflake account {self.account}: {str(e)}"
        ) from e
```

**Why this design?**
- Try to connect (might fail for many reasons)
- Log the error (helps debugging)
- Raise a custom error with context (tells user what went wrong)
- `from e` preserves the original error (for detailed debugging)

### Finally Block

```python
# Finally always runs, even if there's an error
file = None
try:
    file = open("data.txt", "r")
    data = file.read()
    process_data(data)
except FileNotFoundError:
    print("File not found!")
except Exception as e:
    print(f"Error: {e}")
finally:
    # This ALWAYS runs, even if there was an error
    if file:
        file.close()
    print("Cleanup complete")
```

### Custom Exceptions

```python
# Define custom exception
class InvalidAgeError(Exception):
    """Raised when age is invalid."""
    def __init__(self, age, message="Age must be between 0 and 150"):
        self.age = age
        self.message = message
        super().__init__(self.message)

# Use custom exception
def set_age(age):
    if age < 0 or age > 150:
        raise InvalidAgeError(age)
    return age

try:
    set_age(-5)
except InvalidAgeError as e:
    print(f"Invalid age {e.age}: {e.message}")
```

**Example from Our Code** (`exceptions.py`):
```python
class SnowflakeConnectionError(Exception):
    """Exception raised for Snowflake connection errors."""

    def __init__(self, message: str, account: Optional[str] = None):
        """
        Initialize the exception.

        Args:
            message: Error message
            account: Snowflake account name (optional)
        """
        self.message = message
        self.account = account
        super().__init__(self.message)

    def __str__(self):
        """String representation of the error."""
        if self.account:
            return f"SnowflakeConnectionError for account '{self.account}': {self.message}"
        return f"SnowflakeConnectionError: {self.message}"

# Usage
try:
    conn = SnowflakeConnection(account="prod")
    conn.connect()
except SnowflakeConnectionError as e:
    print(f"Connection failed: {e}")
    print(f"Account: {e.account}")
```

**Why custom exceptions?**
- More descriptive than generic `Exception`
- Can include additional context (like `account`)
- Easier to catch specific errors
- Self-documenting code

### Exception Chaining

```python
# Exception chaining preserves the original error
try:
    result = fetch_data_from_api()
except requests.RequestException as e:
    # Raise new exception but keep original
    raise DataFetchError("Failed to fetch data") from e
    # Now you can see BOTH errors in the traceback!
```

**Example from Our Code** (`connection.py`):
```python
try:
    secret = get_secret_from_vault(secret_path, **vault_kwargs)
except VaultError as e:
    logger.error("Vault error: %s", e)
    # Raise new error but preserve original
    raise RuntimeError(
        "Snowflake private key could not be retrieved from Vault."
    ) from e
    # Traceback will show both the RuntimeError and the original VaultError
```

**Why chain exceptions?**
- Preserves full error context
- Shows the complete chain of what went wrong
- Helps debugging by showing root cause
- Best practice in Python

---

## Type Hints

### What are Type Hints?

Type hints tell Python (and developers) what type of data a variable or function expects. They don't change how Python runs, but they help catch errors and make code clearer.

### Basic Type Hints

```python
# Without type hints
def greet(name):
    return f"Hello, {name}!"

# With type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"
    # name: str means "name should be a string"
    # -> str means "this function returns a string"
```

### Common Type Hints

```python
from typing import Optional, List, Dict, Tuple, Any

# Basic types
def add(a: int, b: int) -> int:
    return a + b

def get_name() -> str:
    return "Alice"

def is_valid() -> bool:
    return True

# Optional (can be None)
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None  # Can return None

# Lists
def get_names() -> List[str]:
    return ["Alice", "Bob", "Charlie"]

def process_numbers(numbers: List[int]) -> int:
    return sum(numbers)

# Dictionaries
def get_user_info() -> Dict[str, Any]:
    return {"name": "Alice", "age": 30, "active": True}

def count_words(text: str) -> Dict[str, int]:
    # Returns dict with string keys and int values
    return {"hello": 2, "world": 1}

# Tuples
def get_coordinates() -> Tuple[float, float]:
    return (10.5, 20.3)

# Multiple types with Union
from typing import Union

def process_id(id: Union[int, str]) -> str:
    return str(id)  # Can accept int or str
```

### Example from Our Code

From `connection.py`:
```python
class SnowflakeConnection:
    def __init__(
        self,
        account: str,                      # Must be a string
        user: Optional[str] = None,        # String or None
        warehouse: Optional[str] = None,   # String or None
        role: Optional[str] = None,        # String or None
        database: Optional[str] = None,    # String or None
        config: Optional[Dict[str, Any]] = None,  # Dict or None
    ):
        """Initialize connection."""
        self.account = account
        self.user = user

    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Returns a Snowflake connection object."""
        # ...

    def execute_query(
        self,
        query: str,                    # Query must be a string
        params: Optional[tuple] = None  # Params can be tuple or None
    ) -> List[Any]:                    # Returns list of any type
        """Execute a query."""
        # ...

    def get_connection_info(self) -> Dict[str, Any]:
        """Returns dictionary with string keys and any values."""
        return {
            'account': self.account,
            'user': self.user,
            'connected': self.is_connected()
        }

    def is_connected(self) -> bool:
        """Returns True or False."""
        return self.connection is not None
```

**Why type hints?**
- **Documentation**: Clear what types are expected
- **Error Prevention**: IDEs can warn about type mismatches
- **Autocomplete**: IDEs know what methods are available
- **Refactoring**: Easier to change code safely
- **Self-Documenting**: Code explains itself

### Type Hints for Classes

```python
from typing import Optional

class User:
    def __init__(self, name: str, age: int):
        self.name: str = name
        self.age: int = age
        self.email: Optional[str] = None  # Can be set later

def get_user() -> User:
    """Returns a User object."""
    return User("Alice", 30)

def process_users(users: List[User]) -> None:
    """Takes a list of User objects."""
    for user in users:
        print(user.name)  # IDE knows user has .name
```

### Any vs Specific Types

```python
from typing import Any

# Any - accepts anything (least specific)
def process_data(data: Any) -> Any:
    return data  # Can be anything

# Specific types (better!)
def process_user(user: Dict[str, str]) -> str:
    return user['name']  # IDE knows it's a dict

# Even more specific (best!)
class User:
    name: str
    email: str

def process_user(user: User) -> str:
    return user.name  # IDE knows exactly what user is
```

**Example from Our Code** (`base.py`):
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

class BaseMonitor(ABC):
    def __init__(
        self,
        name: str,              # Name must be string
        timeout: int = 30,      # Timeout must be int, defaults to 30
        log_level: int = logging.INFO  # Log level must be int
    ):
        self.name: str = name
        self.timeout: int = timeout
        self._start_time: Optional[datetime] = None  # datetime or None
        self._check_count: int = 0

    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """Must return a dictionary."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Returns dictionary with statistics."""
        return {
            'name': self.name,
            'check_count': self._check_count,
            'timeout': self.timeout
        }
```

### Benefits of Type Hints

1. **Catch Errors Early**: IDE warns before running code
2. **Better Documentation**: Clear what functions expect
3. **Improved Autocomplete**: IDE knows available methods
4. **Easier Refactoring**: Change types safely
5. **Team Communication**: Clear interfaces between code

---

**(Continued in next part due to length...)**

Would you like me to continue with the remaining sections (Decorators, Context Managers, Logging, Modules, and Design Patterns)?
