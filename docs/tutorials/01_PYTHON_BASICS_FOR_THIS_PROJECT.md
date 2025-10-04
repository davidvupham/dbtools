# Python Basics for Snowflake Monitoring Project

## Tutorial for Beginners

This document introduces the Python concepts you need to understand to work with the Snowflake Monitoring project.

---

## Table of Contents

1. [Python Basics](#python-basics)
2. [Object-Oriented Programming](#object-oriented-programming)
3. [Functions and Methods](#functions-and-methods)
4. [Error Handling](#error-handling)
5. [Logging](#logging)
6. [Decorators](#decorators)
7. [Type Hints](#type-hints)
8. [Working with Modules](#working-with-modules)

---

## Python Basics

### What is Python?

Python is a high-level programming language that's easy to read and write. Code looks almost like English!

### Variables

Variables store data:

```python
# String (text)
name = "Snowflake"

# Integer (whole number)
count = 10

# Float (decimal number)
timeout = 30.5

# Boolean (True/False)
is_connected = True

# None (represents "no value")
error = None
```

### Data Structures

#### Lists (ordered collection)

```python
# List of strings
accounts = ["account1", "account2", "account3"]

# Access items by position (starts at 0)
first_account = accounts[0]  # "account1"

# Add items
accounts.append("account4")

# Loop through items
for account in accounts:
    print(account)
```

#### Dictionaries (key-value pairs)

```python
# Dictionary stores data with keys
user_info = {
    "username": "john",
    "email": "john@example.com",
    "role": "admin"
}

# Access values by key
username = user_info["username"]  # "john"

# Add or update values
user_info["phone"] = "555-1234"

# Loop through dictionary
for key, value in user_info.items():
    print(f"{key}: {value}")
```

#### Tuples (immutable ordered collection)

```python
# Tuple - cannot be changed after creation
coordinates = (10, 20)
x, y = coordinates  # Unpacking

# Multiple return values use tuples
def get_status():
    return True, "Connected"

success, message = get_status()
```

### String Formatting

```python
# f-strings (modern Python)
name = "Alice"
age = 30
message = f"Hello {name}, you are {age} years old"

# % formatting (used in logging)
message = "Hello %s, you are %d years old" % (name, age)

# .format() method
message = "Hello {}, you are {} years old".format(name, age)
```

---

## Object-Oriented Programming

### Classes and Objects

A **class** is a blueprint for creating objects. An **object** is an instance of a class.

```python
# Define a class
class Dog:
    """A simple Dog class."""
    
    # Constructor - runs when creating a new object
    def __init__(self, name, age):
        """Initialize a dog with name and age."""
        self.name = name  # Instance variable
        self.age = age
    
    # Method (function inside a class)
    def bark(self):
        """Make the dog bark."""
        print(f"{self.name} says Woof!")
    
    def get_age_in_months(self):
        """Calculate age in months."""
        return self.age * 12

# Create objects (instances)
my_dog = Dog("Buddy", 5)
your_dog = Dog("Max", 3)

# Use methods
my_dog.bark()  # "Buddy says Woof!"
print(my_dog.get_age_in_months())  # 60

# Access attributes
print(my_dog.name)  # "Buddy"
```

### Understanding `self`

`self` refers to the current instance of the class:

```python
class Counter:
    def __init__(self):
        self.count = 0  # Each instance has its own count
    
    def increment(self):
        self.count += 1  # Access this instance's count
    
    def get_count(self):
        return self.count

# Create two separate counters
counter1 = Counter()
counter2 = Counter()

counter1.increment()
counter1.increment()
counter2.increment()

print(counter1.get_count())  # 2
print(counter2.get_count())  # 1
```

### Inheritance

One class can inherit from another:

```python
# Base class (parent)
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "Some sound"

# Derived class (child)
class Cat(Animal):
    def speak(self):  # Override parent method
        return f"{self.name} says Meow!"

# Usage
cat = Cat("Whiskers")
print(cat.speak())  # "Whiskers says Meow!"
```

---

## Functions and Methods

### Functions

Functions are reusable blocks of code:

```python
# Basic function
def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # "Hello, Alice!"

# Function with multiple parameters
def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

result = add_numbers(5, 3)  # 8

# Function with default parameters
def greet_with_title(name, title="Mr."):
    """Greet with an optional title."""
    return f"Hello, {title} {name}!"

print(greet_with_title("Smith"))  # "Hello, Mr. Smith!"
print(greet_with_title("Jones", "Dr."))  # "Hello, Dr. Jones!"
```

### Methods

Methods are functions inside a class:

```python
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, number):
        """Add a number to the result."""
        self.result += number
        return self.result
    
    def reset(self):
        """Reset the result to zero."""
        self.result = 0

# Usage
calc = Calculator()
calc.add(5)
calc.add(3)
print(calc.result)  # 8
calc.reset()
print(calc.result)  # 0
```

### Arguments

```python
# Positional arguments (order matters)
def describe_pet(animal_type, pet_name):
    print(f"I have a {animal_type} named {pet_name}")

describe_pet("dog", "Buddy")  # Must be in order

# Keyword arguments (order doesn't matter)
describe_pet(pet_name="Buddy", animal_type="dog")

# *args - variable number of positional arguments
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3, 4, 5))  # 15

# **kwargs - variable number of keyword arguments
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="NYC")
```

---

## Error Handling

### Try-Except Blocks

Handle errors gracefully:

```python
# Basic error handling
try:
    result = 10 / 0  # This will cause an error
except ZeroDivisionError:
    print("Cannot divide by zero!")
    result = None

# Multiple exception types
try:
    number = int("not a number")
except ValueError:
    print("Invalid number format")
except TypeError:
    print("Wrong type")

# Catch all exceptions (use carefully!)
try:
    risky_operation()
except Exception as e:
    print(f"An error occurred: {e}")

# Finally block (always runs)
try:
    file = open("data.txt", "r")
    data = file.read()
except FileNotFoundError:
    print("File not found")
finally:
    file.close()  # Always close the file
```

### Raising Exceptions

```python
# Define custom exception
class InvalidAgeError(Exception):
    """Raised when age is invalid."""
    pass

# Raise an exception
def set_age(age):
    if age < 0:
        raise InvalidAgeError("Age cannot be negative")
    return age

# Exception chaining (from e)
try:
    data = fetch_data()
except ConnectionError as e:
    raise DataError("Failed to fetch data") from e
    # Preserves original error for debugging
```

---

## Logging

### Why Use Logging?

Logging helps you track what your program is doing, which is essential for:
- Debugging issues
- Monitoring in production
- Understanding program flow

### Logging Levels

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Different severity levels (from lowest to highest)
logger.debug("Detailed information for debugging")
logger.info("General information about program execution")
logger.warning("Warning - something unexpected happened")
logger.error("Error - something failed")
logger.critical("Critical - serious error")
```

### Practical Example

```python
import logging

logger = logging.getLogger(__name__)

def connect_to_database(server):
    """Connect to a database server."""
    logger.info("Attempting to connect to %s", server)
    
    try:
        # Simulate connection
        if server == "":
            raise ValueError("Server name is empty")
        
        logger.debug("Connection parameters validated")
        # ... actual connection code ...
        logger.info("Successfully connected to %s", server)
        return True
        
    except Exception as e:
        logger.error("Failed to connect to %s: %s", server, e)
        return False
```

### Lazy Logging (Best Practice)

```python
# GOOD - Lazy evaluation (string only created if logged)
logger.info("User %s logged in at %s", username, timestamp)

# BAD - String always created (even if not logged)
logger.info(f"User {username} logged in at {timestamp}")
```

---

## Decorators

### What is a Decorator?

A decorator is a function that modifies another function's behavior.

### Basic Decorator

```python
# Define a decorator
def make_bold(func):
    """Decorator that adds bold tags."""
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper

# Use the decorator
@make_bold
def say_hello():
    return "Hello!"

print(say_hello())  # "<b>Hello!</b>"
```

### Decorator with Arguments

```python
def repeat(times):
    """Decorator that repeats a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    return f"Hello {name}!"

print(greet("Alice"))
# ["Hello Alice!", "Hello Alice!", "Hello Alice!"]
```

### Practical Example: Retry Decorator

```python
import time

def retry(max_attempts=3):
    """Retry a function if it fails."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise  # Re-raise on last attempt
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(1)
        return wrapper
    return decorator

@retry(max_attempts=3)
def unstable_function():
    """Function that might fail."""
    import random
    if random.random() < 0.5:
        raise Exception("Random failure")
    return "Success!"
```

---

## Type Hints

### Why Type Hints?

Type hints make code easier to understand and catch errors early:

```python
# Without type hints
def add(a, b):
    return a + b

# With type hints
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b
```

### Common Type Hints

```python
from typing import Optional, List, Dict, Tuple, Any

# Basic types
def greet(name: str) -> str:
    return f"Hello {name}"

# Optional (can be None)
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None  # Can return None

# Lists
def get_names() -> List[str]:
    return ["Alice", "Bob", "Charlie"]

# Dictionaries
def get_user_info() -> Dict[str, Any]:
    return {"name": "Alice", "age": 30}

# Tuples
def get_coordinates() -> Tuple[float, float]:
    return (10.5, 20.3)

# Multiple return values
def check_connection() -> Tuple[bool, str]:
    return True, "Connected"
```

---

## Working with Modules

### Importing Modules

```python
# Import entire module
import math
print(math.sqrt(16))  # 4.0

# Import specific items
from math import sqrt, pi
print(sqrt(16))  # 4.0

# Import with alias
import pandas as pd
df = pd.DataFrame()

# Import from local file
from my_module import my_function

# Import from package
from gds_vault.vault import VaultClient
```

### Module Structure

```
my_project/
├── my_module/
│   ├── __init__.py      # Makes it a package
│   ├── core.py          # Core functionality
│   └── utils.py         # Utility functions
└── main.py              # Main script
```

### Creating a Module

```python
# File: my_module/core.py
"""Core functionality for my module."""

def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

# File: main.py
from my_module.core import hello

print(hello("World"))  # "Hello, World!"
```

---

## Context Managers

### What is a Context Manager?

Context managers handle setup and cleanup automatically:

```python
# Without context manager
file = open("data.txt", "r")
try:
    data = file.read()
finally:
    file.close()  # Must remember to close

# With context manager
with open("data.txt", "r") as file:
    data = file.read()
    # File automatically closed when done!
```

### Creating a Context Manager

```python
class Timer:
    """Context manager to time code execution."""
    
    def __enter__(self):
        """Called when entering 'with' block."""
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block."""
        self.end = time.time()
        print(f"Elapsed: {self.end - self.start:.2f} seconds")
        return False  # Don't suppress exceptions

# Usage
with Timer():
    # Code to time
    time.sleep(1)
    # Automatically prints elapsed time
```

---

## Environment Variables

### What are Environment Variables?

Environment variables store configuration outside your code:

```python
import os

# Get environment variable
api_key = os.getenv("API_KEY")

# With default value
timeout = os.getenv("TIMEOUT", "30")

# Convert to integer
max_retries = int(os.getenv("MAX_RETRIES", "3"))

# Set environment variable (in code)
os.environ["DEBUG"] = "true"

# Check if variable exists
if "DATABASE_URL" in os.environ:
    db_url = os.environ["DATABASE_URL"]
```

### Using .env Files

```bash
# .env file
API_KEY=abc123
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
```

```python
# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Now variables are available
api_key = os.getenv("API_KEY")
```

---

## Next Steps

Now that you understand these Python basics, you're ready to dive into the specific modules:

1. **[Vault Module Tutorial](02_VAULT_MODULE_TUTORIAL.md)** - Learn about HashiCorp Vault integration
2. **[Connection Module Tutorial](03_CONNECTION_MODULE_TUTORIAL.md)** - Understand Snowflake connections
3. **[Replication Module Tutorial](04_REPLICATION_MODULE_TUTORIAL.md)** - Learn about replication monitoring
4. **[Monitor Module Tutorial](05_MONITOR_MODULE_TUTORIAL.md)** - Comprehensive monitoring
5. **[Monitoring App Tutorial](06_MONITORING_APP_TUTORIAL.md)** - The complete application

---

## Practice Exercises

### Exercise 1: Create a Simple Class

```python
# Create a Person class with name and age
# Add a method to calculate birth year
# Create instances and test

class Person:
    def __init__(self, name, age):
        # Your code here
        pass
    
    def birth_year(self, current_year=2025):
        # Your code here
        pass

# Test it
person = Person("Alice", 30)
print(person.birth_year())
```

### Exercise 2: Error Handling

```python
# Write a function that divides two numbers
# Handle division by zero
# Handle non-numeric inputs

def safe_divide(a, b):
    # Your code here
    pass

# Test it
print(safe_divide(10, 2))   # Should return 5.0
print(safe_divide(10, 0))   # Should handle error
print(safe_divide("10", 2)) # Should handle error
```

### Exercise 3: Using Decorators

```python
# Create a decorator that logs function calls

def log_calls(func):
    # Your code here
    pass

@log_calls
def add(a, b):
    return a + b

# Test it
result = add(5, 3)  # Should log "Calling add(5, 3)"
```

---

## Additional Resources

- [Official Python Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/) - Excellent tutorials
- [Python Type Checking Guide](https://realpython.com/python-type-checking/)
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)

---

Ready to continue? Head to the [Vault Module Tutorial](02_VAULT_MODULE_TUTORIAL.md)!
