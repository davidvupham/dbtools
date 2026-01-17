# Complete Python Tutorial for Beginners - Part 3
## Missing Concepts: Dataclasses, Enums, and More

This is Part 3 of the Python tutorial, covering important concepts that are used in the codebase but not covered in Parts 1 and 2.

**Prerequisites**: Complete [Part 1](01_PYTHON_BASICS_FOR_THIS_PROJECT.md) and [Part 2](01_PYTHON_BASICS_PART2.md) first.

---

## Table of Contents

1. [Dataclasses](#dataclasses)
2. [Enumerations (Enum)](#enumerations-enum)
3. [Class Methods (@classmethod)](#class-methods-classmethod)
4. [Understanding super()](#understanding-super)
5. [List Comprehensions](#list-comprehensions)
6. [enumerate() Function](#enumerate-function)
7. [Sets](#sets)
8. [Advanced f-strings](#advanced-f-strings)

---

## Dataclasses

### What are Dataclasses?

A **dataclass** is a class that's primarily used to store data. Instead of writing repetitive code for `__init__`, `__repr__`, and `__eq__`, Python generates them automatically!

### The Problem Without Dataclasses

```python
# Traditional class - lots of boilerplate!
class Person:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"Person(name={self.name!r}, age={self.age!r}, email={self.email!r})"

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return (self.name == other.name and
                self.age == other.age and
                self.email == other.email)

# Create a person
person = Person("Alice", 30, "alice@example.com")
print(person)  # Person(name='Alice', age=30, email='alice@example.com')

# Compare people
person2 = Person("Alice", 30, "alice@example.com")
print(person == person2)  # True
```

**Problems:**
- Lots of repetitive code
- Easy to make mistakes
- Hard to maintain
- Need to update multiple methods when adding fields

### The Solution: Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str

# That's it! Python generates everything automatically!

# Create a person
person = Person("Alice", 30, "alice@example.com")
print(person)  # Person(name='Alice', age=30, email='alice@example.com')

# Compare people
person2 = Person("Alice", 30, "alice@example.com")
print(person == person2)  # True

# Access attributes
print(person.name)   # "Alice"
print(person.age)    # 30
```

**Benefits:**
- ✅ Less code (no boilerplate)
- ✅ Type hints required (forces good practices)
- ✅ Automatic `__init__`, `__repr__`, `__eq__`
- ✅ Easy to add/remove fields
- ✅ Modern Python best practice

### Default Values

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0        # Default value
    in_stock: bool = True    # Default value

# Can omit default parameters
product1 = Product("Laptop", 999.99)
print(product1)
# Product(name='Laptop', price=999.99, quantity=0, in_stock=True)

# Or provide them
product2 = Product("Mouse", 29.99, quantity=50, in_stock=True)
print(product2)
# Product(name='Mouse', price=29.99, quantity=50, in_stock=True)
```

### Example from Our Code

From `monitor.py`:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class MonitoringResult:
    """Result of a monitoring operation"""
    success: bool
    timestamp: datetime
    account: str
    message: str
    details: Dict[str, Any]
    severity: AlertSeverity = AlertSeverity.INFO  # Default value

# Usage in the monitoring system
result = MonitoringResult(
    success=True,
    timestamp=datetime.now(),
    account="prod",
    message="All checks passed",
    details={"checks": 5, "failures": 0},
    severity=AlertSeverity.INFO
)

# Automatically has nice string representation
print(result)
# MonitoringResult(success=True, timestamp=2025-01-15 10:30:00, ...)

# Can compare results
result2 = MonitoringResult(
    success=True,
    timestamp=datetime.now(),
    account="prod",
    message="All checks passed",
    details={"checks": 5, "failures": 0}
)
print(result == result2)  # Compares all fields
```

**Why use dataclass here?**
- **Clear structure**: Easy to see what data a result contains
- **Type safety**: Can't create result with wrong types
- **Automatic methods**: Don't need to write __init__, __repr__, __eq__
- **Easy to extend**: Adding new fields is simple

### More Examples from Our Code

From `monitor.py`:
```python
@dataclass
class ConnectivityResult:
    """Result of connectivity monitoring"""
    success: bool
    response_time_ms: float
    account_info: Dict[str, str]
    error: Optional[str]

@dataclass
class ReplicationResult:
    """Result of replication monitoring"""
    has_failure: bool
    has_latency: bool
    failure_message: Optional[str]
    latency_message: Optional[str]
    last_refresh: Optional[datetime]
    next_refresh: Optional[datetime]
```

### Immutable Dataclasses

Sometimes you want data that can't be changed after creation:

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # Makes it immutable
class Point:
    x: float
    y: float

point = Point(10.5, 20.3)
print(point.x)  # 10.5

# This will raise an error!
# point.x = 15.0  # FrozenInstanceError: cannot assign to field 'x'
```

**When to use frozen=True:**
- Configuration data that shouldn't change
- Dictionary keys (must be immutable)
- Thread-safe data structures
- Functional programming style

### Dataclass Features

```python
from dataclasses import dataclass, field

@dataclass
class ShoppingCart:
    customer: str
    items: list = field(default_factory=list)  # Mutable default
    total: float = 0.0

    def add_item(self, item, price):
        self.items.append(item)
        self.total += price

# Each cart gets its own list!
cart1 = ShoppingCart("Alice")
cart2 = ShoppingCart("Bob")

cart1.add_item("Book", 15.99)
cart2.add_item("Pen", 2.99)

print(cart1.items)  # ['Book']
print(cart2.items)  # ['Pen']
```

**Important:** Use `field(default_factory=list)` for mutable defaults like lists or dicts!

### When to Use Dataclasses

✅ **Use dataclasses when:**
- Class is primarily for storing data
- Need automatic `__init__`, `__repr__`, `__eq__`
- Want type hints enforced
- Building data transfer objects (DTOs)
- Creating configuration objects
- Returning structured results

❌ **Don't use dataclasses when:**
- Class has complex business logic
- Need custom `__init__` with validation
- Class behavior is more important than data
- Need fine control over comparison

---

## Enumerations (Enum)

### What are Enums?

An **Enum** (enumeration) is a set of named constants. It's a way to give meaningful names to values, making code more readable and type-safe.

### The Problem Without Enums

```python
# Using strings - error-prone and not type-safe!
def send_alert(severity):
    if severity == "INFO":
        print("📘 Info alert")
    elif severity == "WARNING":
        print("⚠️  Warning alert")
    elif severity == "CRITICAL":
        print("🚨 Critical alert")
    else:
        print("Unknown severity!")

# Easy to make typos!
send_alert("INFO")      # Works
send_alert("INFOO")     # Typo! No error, just "Unknown severity!"
send_alert("info")      # Wrong case! No error
send_alert("WARNING")   # Works
send_alert("WARNIGN")   # Typo! No error

# Using numbers - not self-documenting
INFO = 1
WARNING = 2
CRITICAL = 3

def send_alert(severity):
    if severity == INFO:
        print("📘 Info alert")
    elif severity == WARNING:
        print("⚠️  Warning alert")
    elif severity == CRITICAL:
        print("🚨 Critical alert")

send_alert(1)  # What does 1 mean? Not clear!
send_alert(99) # No error, but invalid!
```

**Problems:**
- Easy to typo strings
- No IDE autocomplete
- Not type-safe
- Hard to refactor
- Numbers aren't self-documenting

### The Solution: Enums

```python
from enum import Enum

class AlertSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

def send_alert(severity: AlertSeverity):
    if severity == AlertSeverity.INFO:
        print("📘 Info alert")
    elif severity == AlertSeverity.WARNING:
        print("⚠️  Warning alert")
    elif severity == AlertSeverity.CRITICAL:
        print("🚨 Critical alert")

# Type-safe! IDE autocomplete!
send_alert(AlertSeverity.INFO)      # ✅ Works
send_alert(AlertSeverity.WARNING)   # ✅ Works
send_alert(AlertSeverity.CRITICAL)  # ✅ Works

# These cause errors:
# send_alert("INFO")          # ❌ Type error
# send_alert("INFOO")         # ❌ AttributeError
# send_alert(AlertSeverity.INFOO)  # ❌ AttributeError at write time!
```

**Benefits:**
- ✅ Type-safe (can't use invalid values)
- ✅ IDE autocomplete (suggests valid options)
- ✅ Self-documenting (clear what values are allowed)
- ✅ Easy to refactor (rename in one place)
- ✅ Catch typos at development time

### Example from Our Code

From `monitor.py`:
```python
from enum import Enum
from dataclasses import dataclass

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class MonitoringResult:
    success: bool
    message: str
    severity: AlertSeverity = AlertSeverity.INFO  # Use enum!

# Usage
result = MonitoringResult(
    success=False,
    message="Connection failed",
    severity=AlertSeverity.CRITICAL  # Clear and type-safe!
)

# Check severity
if result.severity == AlertSeverity.CRITICAL:
    send_urgent_alert()
    page_on_call_engineer()
elif result.severity == AlertSeverity.WARNING:
    send_warning_email()
```

**Why use Enum here?**
- **Type safety**: Can't accidentally use "CRITCAL" (typo)
- **Clear intent**: `AlertSeverity.CRITICAL` is more readable than `"CRITICAL"`
- **IDE support**: Autocomplete suggests valid severities
- **Refactoring**: Easy to rename severity levels

### Accessing Enum Values

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# Access by name
color = Color.RED
print(color)        # Color.RED
print(color.name)   # "RED"
print(color.value)  # 1

# Compare enums
print(Color.RED == Color.RED)    # True
print(Color.RED == Color.GREEN)  # False

# Iterate over enums
for color in Color:
    print(f"{color.name} = {color.value}")
# RED = 1
# GREEN = 2
# BLUE = 3

# Get enum by value
color = Color(2)
print(color)  # Color.GREEN

# Get enum by name
color = Color["BLUE"]
print(color)  # Color.BLUE
```

### Enum with String Values

```python
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

# Usage
env = Environment.PRODUCTION
print(env.value)  # "prod"

# Useful for configuration
def get_database_url(env: Environment) -> str:
    urls = {
        Environment.DEVELOPMENT: "localhost:5432",
        Environment.STAGING: "staging-db.company.com",
        Environment.PRODUCTION: "prod-db.company.com"
    }
    return urls[env]

url = get_database_url(Environment.PRODUCTION)
print(url)  # "prod-db.company.com"
```

### Auto-numbering Enums

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()    # Automatically 1
    RUNNING = auto()    # Automatically 2
    COMPLETED = auto()  # Automatically 3
    FAILED = auto()     # Automatically 4

print(Status.PENDING.value)    # 1
print(Status.COMPLETED.value)  # 3
```

### When to Use Enums

✅ **Use enums when:**
- Have a fixed set of related constants
- Want type-safe constants
- Need IDE autocomplete for valid values
- Values have meaning (not just arbitrary numbers)
- Want to prevent typos

❌ **Don't use enums when:**
- Values change frequently
- Need dynamic values
- Simple boolean is enough
- Values come from external source

---

## Class Methods (@classmethod)

### What are Class Methods?

A **class method** is a method that works with the class itself, not instances. It receives the class as the first argument (`cls`) instead of the instance (`self`).

### Instance Methods vs Class Methods

```python
class Person:
    population = 0  # Class variable

    def __init__(self, name, age):
        self.name = name  # Instance variable
        self.age = age
        Person.population += 1

    # Instance method - works with self (the instance)
    def greet(self):
        return f"Hello, I'm {self.name}"

    # Class method - works with cls (the class)
    @classmethod
    def get_population(cls):
        return cls.population

    # Class method as alternative constructor
    @classmethod
    def from_birth_year(cls, name, birth_year):
        age = 2025 - birth_year
        return cls(name, age)  # Create and return instance

# Instance methods need an instance
person = Person("Alice", 30)
print(person.greet())  # "Hello, I'm Alice"

# Class methods work on the class
print(Person.get_population())  # 1

# Alternative constructor
person2 = Person.from_birth_year("Bob", 1995)
print(person2.age)  # 30
print(Person.get_population())  # 2
```

**Key differences:**
- **Instance method**: First parameter is `self` (the instance)
- **Class method**: First parameter is `cls` (the class)
- **Instance method**: Called on instances (`person.greet()`)
- **Class method**: Can be called on class (`Person.get_population()`)

### Example from Our Code

From `base.py`:
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class OperationResult:
    """Standardized result object for operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0

    @classmethod
    def success_result(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'OperationResult':
        """Factory method for successful results."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def failure_result(cls, message: str, error: Optional[str] = None) -> 'OperationResult':
        """Factory method for failed results."""
        return cls(success=False, message=message, error=error)

# Usage - much cleaner and clearer!
result = OperationResult.success_result(
    "Operation completed successfully",
    data={"rows_processed": 1000}
)

# vs the verbose way:
result = OperationResult(
    success=True,
    message="Operation completed successfully",
    data={"rows_processed": 1000},
    error=None,
    duration_ms=0.0
)

# For failures
result = OperationResult.failure_result(
    "Database connection failed",
    error="Connection timeout after 30s"
)
```

**Why use @classmethod here?**
- **Clearer intent**: `success_result()` vs setting `success=True`
- **Less error-prone**: Can't forget to set `success=True`
- **Encapsulation**: Creation logic in one place
- **Convenience**: Don't need to specify all parameters

### More Class Method Examples

```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_string):
        """Create Date from string like '2025-01-15'"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)

    @classmethod
    def today(cls):
        """Create Date for today"""
        import datetime
        today = datetime.date.today()
        return cls(today.year, today.month, today.day)

    def __repr__(self):
        return f"Date({self.year}, {self.month}, {self.day})"

# Different ways to create Date objects
date1 = Date(2025, 1, 15)                    # Regular constructor
date2 = Date.from_string("2025-01-15")       # From string
date3 = Date.today()                         # Today's date

print(date1)  # Date(2025, 1, 15)
print(date2)  # Date(2025, 1, 15)
print(date3)  # Date(2025, 1, 15) (if today is Jan 15)
```

### @classmethod vs @staticmethod

```python
class MathOperations:
    multiplier = 2  # Class variable

    @classmethod
    def multiply_by_class_multiplier(cls, x):
        """Has access to class and its variables"""
        return x * cls.multiplier

    @staticmethod
    def add(x, y):
        """No access to class or instance, just a function"""
        return x + y

# Class method uses class variable
print(MathOperations.multiply_by_class_multiplier(5))  # 10

# Static method is just a regular function
print(MathOperations.add(5, 3))  # 8
```

**When to use each:**
- **@classmethod**: Need access to class or want alternative constructors
- **@staticmethod**: Function logically belongs to class but doesn't need class/instance
- **Instance method**: Need access to instance data

### Factory Pattern with @classmethod

```python
class DatabaseConnection:
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database

    @classmethod
    def for_development(cls):
        """Factory for development environment"""
        return cls("localhost", 5432, "dev_db")

    @classmethod
    def for_production(cls):
        """Factory for production environment"""
        return cls("prod-db.company.com", 5432, "prod_db")

    @classmethod
    def from_config(cls, config_dict):
        """Factory from configuration dictionary"""
        return cls(
            config_dict["host"],
            config_dict["port"],
            config_dict["database"]
        )

# Easy to create different configurations
dev_conn = DatabaseConnection.for_development()
prod_conn = DatabaseConnection.for_production()
config_conn = DatabaseConnection.from_config({
    "host": "staging.company.com",
    "port": 5432,
    "database": "staging_db"
})
```

### When to Use @classmethod

✅ **Use @classmethod when:**
- Creating alternative constructors
- Factory methods for creating instances
- Need access to class variables
- Working with inheritance (cls refers to actual class)
- Implementing factory pattern

❌ **Don't use @classmethod when:**
- Don't need access to class
- Regular instance method works
- Just need a utility function (@staticmethod)

---

## Understanding super()

### What is super()?

`super()` is used to call methods from a parent class. It's essential for proper inheritance, especially with multiple inheritance.

### Basic Usage

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal created: {name}")

    def speak(self):
        return "Some sound"

class Dog(Animal):
    def __init__(self, name, breed):
        # Call parent's __init__
        super().__init__(name)
        self.breed = breed
        print(f"Dog breed: {breed}")

    def speak(self):
        # Can still call parent's method if needed
        parent_sound = super().speak()
        return f"{self.name} says Woof! (parent said: {parent_sound})"

# Create a dog
dog = Dog("Buddy", "Golden Retriever")
# Output:
# Animal created: Buddy
# Dog breed: Golden Retriever

print(dog.speak())
# "Buddy says Woof! (parent said: Some sound)"
```

**Why use super()?**
- Calls parent's method without hardcoding parent name
- Works correctly with multiple inheritance
- Maintains the Method Resolution Order (MRO)
- Makes code more maintainable

### Example from Our Code

From `monitor.py`:
```python
class BaseMonitor(ABC):
    """Abstract base class for all monitoring operations."""

    def __init__(
        self,
        name: str,
        timeout: int = 30,
        log_level: int = logging.INFO
    ):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(log_level)
        self._check_count = 0

class SnowflakeMonitor(BaseMonitor):
    """Snowflake-specific monitor."""

    def __init__(
        self,
        account: str,
        user: Optional[str] = None,
        connectivity_timeout: int = 30,
        **kwargs
    ):
        # Call parent constructor with super()
        super().__init__(
            name=f"SnowflakeMonitor-{account}",
            timeout=connectivity_timeout
        )

        # Then add our own initialization
        self.account = account
        self.user = user
        self.connection = SnowflakeConnection(
            account=account,
            user=user,
            **kwargs
        )

# When we create a SnowflakeMonitor:
monitor = SnowflakeMonitor(account="prod", user="admin")

# This calls:
# 1. SnowflakeMonitor.__init__()
# 2. Which calls super().__init__() -> BaseMonitor.__init__()
# 3. BaseMonitor sets up name, timeout, logger
# 4. Then SnowflakeMonitor sets up account, user, connection
```

**Why use super() here?**
- `BaseMonitor` sets up common monitoring infrastructure
- `SnowflakeMonitor` adds Snowflake-specific setup
- Don't duplicate the base setup code
- If `BaseMonitor` changes, `SnowflakeMonitor` automatically gets updates

### Without super() (Bad Practice)

```python
class Dog(Animal):
    def __init__(self, name, breed):
        # Hardcoding parent class name - BAD!
        Animal.__init__(self, name)
        self.breed = breed

# Problems:
# 1. If you rename Animal, must update here too
# 2. Doesn't work correctly with multiple inheritance
# 3. Breaks Method Resolution Order
# 4. Not maintainable
```

### Multiple Inheritance with super()

```python
class A:
    def __init__(self):
        print("A.__init__")
        super().__init__()

class B:
    def __init__(self):
        print("B.__init__")
        super().__init__()

class C(A, B):
    def __init__(self):
        print("C.__init__")
        super().__init__()

# Create C
c = C()
# Output:
# C.__init__
# A.__init__
# B.__init__

# super() follows the Method Resolution Order (MRO)
print(C.__mro__)
# (<class 'C'>, <class 'A'>, <class 'B'>, <class 'object'>)
```

### Calling Parent's Method

```python
class Shape:
    def area(self):
        return 0

    def describe(self):
        return f"Shape with area {self.area()}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def describe(self):
        # Call parent's describe, then add more info
        parent_desc = super().describe()
        return f"{parent_desc} (Rectangle: {self.width}x{self.height})"

rect = Rectangle(5, 3)
print(rect.describe())
# "Shape with area 15 (Rectangle: 5x3)"
```

### When to Use super()

✅ **Use super() when:**
- Calling parent's `__init__` in child's `__init__`
- Extending parent's method (call parent, then add more)
- Working with multiple inheritance
- Want maintainable inheritance

❌ **Don't use super() when:**
- Completely replacing parent's method (no need to call it)
- Not using inheritance
- Want to call specific parent in multiple inheritance (rare)

---

## List Comprehensions

### What are List Comprehensions?

A **list comprehension** is a concise way to create lists. It's more Pythonic and often faster than traditional loops.

### Basic Syntax

```python
# Traditional way with loop
squares = []
for i in range(10):
    squares.append(i ** 2)

# List comprehension way
squares = [i ** 2 for i in range(10)]

print(squares)
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

**Syntax**: `[expression for item in iterable]`

### More Examples

```python
# Create list of even numbers
evens = [i for i in range(20) if i % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Convert strings to uppercase
words = ["hello", "world", "python"]
upper_words = [word.upper() for word in words]
# ['HELLO', 'WORLD', 'PYTHON']

# Get lengths of strings
lengths = [len(word) for word in words]
# [5, 5, 6]

# Square only positive numbers
numbers = [-2, -1, 0, 1, 2, 3]
positive_squares = [n ** 2 for n in numbers if n > 0]
# [1, 4, 9]
```

### With Filtering

```python
# Syntax: [expression for item in iterable if condition]

# Only even squares
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
# [0, 4, 16, 36, 64]

# Only long words
words = ["cat", "elephant", "dog", "hippopotamus"]
long_words = [word for word in words if len(word) > 5]
# ['elephant', 'hippopotamus']

# Filter and transform
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
doubled_evens = [n * 2 for n in numbers if n % 2 == 0]
# [4, 8, 12, 16, 20]
```

### Example from Our Code

From `database.py`:
```python
# Count non-None databases
metadata = {
    "databases": [
        {"name": "DB1"},
        None,
        {"name": "DB2"},
        {"name": "DB3"},
        None
    ]
}

# Using list comprehension
database_count = len([d for d in metadata["databases"] if d])
# 3 (only counts non-None databases)

# Equivalent verbose version:
databases = []
for d in metadata["databases"]:
    if d:  # If not None
        databases.append(d)
database_count = len(databases)
```

### Nested List Comprehensions

```python
# Create a 3x3 matrix
matrix = [[i + j for j in range(3)] for i in range(3)]
# [[0, 1, 2], [1, 2, 3], [2, 3, 4]]

# Flatten a matrix
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Get all coordinates
coords = [(x, y) for x in range(3) for y in range(3)]
# [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
```

### Dictionary and Set Comprehensions

```python
# Dictionary comprehension
squares_dict = {i: i ** 2 for i in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Set comprehension (unique values only)
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique_squares = {n ** 2 for n in numbers}
# {1, 4, 9, 16}

# Filter dictionary
prices = {"apple": 1.50, "banana": 0.50, "cherry": 3.00}
expensive = {fruit: price for fruit, price in prices.items() if price > 1.00}
# {'apple': 1.5, 'cherry': 3.0}
```

### When to Use List Comprehensions

✅ **Use list comprehensions when:**
- Creating a new list from an existing iterable
- Simple transformation or filtering
- One-liner makes sense and is readable

❌ **Don't use list comprehensions when:**
- Logic is complex (use regular loop)
- Multiple lines needed (use regular loop)
- Reduces readability (use regular loop)
- Need to break/continue (use regular loop)

**Example of too complex:**
```python
# BAD - too complex for list comprehension
result = [process(x) if x > 0 else handle_negative(x) if x < 0 else handle_zero() for x in numbers if x != None and validate(x)]

# GOOD - use regular loop
result = []
for x in numbers:
    if x is None or not validate(x):
        continue
    if x > 0:
        result.append(process(x))
    elif x < 0:
        result.append(handle_negative(x))
    else:
        result.append(handle_zero())
```

---

## enumerate() Function

### What is enumerate()?

`enumerate()` gives you both the index and the item when looping through a sequence. It's more Pythonic than using `range(len(...))`.

### The Problem

```python
# Not Pythonic - using range(len())
fruits = ["apple", "banana", "cherry"]
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Output:
# 0: apple
# 1: banana
# 2: cherry
```

**Problems:**
- Verbose and not Pythonic
- Easy to make off-by-one errors
- Less readable

### The Solution: enumerate()

```python
# Pythonic way with enumerate()
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Output:
# 0: apple
# 1: banana
# 2: cherry
```

**Benefits:**
- ✅ More readable
- ✅ Pythonic idiom
- ✅ Less error-prone
- ✅ Works with any iterable

### Starting from Different Index

```python
fruits = ["apple", "banana", "cherry"]

# Start counting from 1
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")

# Output:
# 1: apple
# 2: banana
# 3: cherry
```

### Example from Our Code

From `monitor.py`:
```python
def _send_email(self, subject: str, body: str):
    """Send email notification."""
    # ... email setup code ...

    # Build email body with numbered items
    parts = body.split('\n')
    formatted_body = []

    for i, part in enumerate(parts):
        if i == 0:
            # First part is the header
            formatted_body.append(f"<h2>{part}</h2>")
        else:
            # Other parts are content
            formatted_body.append(f"<p>{part}</p>")

    html_body = '\n'.join(formatted_body)
```

**Why use enumerate() here?**
- Need both index and content
- First item treated differently
- More readable than `range(len(parts))`

### More Examples

```python
# Find index of first negative number
numbers = [5, 3, -2, 8, -1, 4]
for i, num in enumerate(numbers):
    if num < 0:
        print(f"First negative at index {i}: {num}")
        break
# "First negative at index 2: -2"

# Create dictionary with indices
words = ["hello", "world", "python"]
word_dict = {i: word for i, word in enumerate(words)}
# {0: 'hello', 1: 'world', 2: 'python'}

# Track progress
tasks = ["Task 1", "Task 2", "Task 3", "Task 4"]
for i, task in enumerate(tasks, start=1):
    print(f"Processing {i}/{len(tasks)}: {task}")
# Processing 1/4: Task 1
# Processing 2/4: Task 2
# ...
```

### enumerate() with Unpacking

```python
# List of tuples
pairs = [("a", 1), ("b", 2), ("c", 3)]

for i, (letter, number) in enumerate(pairs):
    print(f"Index {i}: {letter} = {number}")

# Output:
# Index 0: a = 1
# Index 1: b = 2
# Index 2: c = 3
```

### When to Use enumerate()

✅ **Use enumerate() when:**
- Need both index and item
- Looping through a sequence
- Want Pythonic code
- Need to track position

❌ **Don't use enumerate() when:**
- Only need the items (use `for item in items`)
- Only need indices (use `range(len(...))` - rare)
- Working with dictionaries (use `.items()`)

---

## Sets

### What are Sets?

A **set** is an unordered collection of unique items. It's like a list, but automatically removes duplicates and has very fast membership testing.

### Creating Sets

```python
# Create a set with curly braces
fruits = {"apple", "banana", "cherry"}

# Create from a list (duplicates removed)
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique_numbers = set(numbers)
print(unique_numbers)  # {1, 2, 3, 4}

# Empty set (must use set(), not {})
empty_set = set()  # Correct
# empty_dict = {}  # This creates a dict, not a set!
```

### Basic Operations

```python
fruits = {"apple", "banana", "cherry"}

# Add item
fruits.add("date")
print(fruits)  # {'apple', 'banana', 'cherry', 'date'}

# Remove item (raises error if not found)
fruits.remove("banana")

# Discard item (no error if not found)
fruits.discard("grape")  # No error even though grape not in set

# Check membership (very fast - O(1))
if "apple" in fruits:
    print("We have apples!")

# Get size
print(len(fruits))  # 3
```

### Example from Our Code

From `monitor.py`:
```python
class SnowflakeMonitor(BaseMonitor):
    def __init__(self, account: str, **kwargs):
        # ... other initialization ...

        # Track which failures we've already notified about
        # Using set because:
        # 1. Only unique failure names
        # 2. Fast membership testing
        # 3. Easy to add/remove
        self.notified_failures: Set[str] = set()

    def monitor_replication_latency(self):
        """Monitor replication latency."""
        for fg in failover_groups:
            result = self.check_replication_latency(fg)

            if result.has_latency:
                # Check if we've already notified about this
                if fg.name not in self.notified_failures:
                    # First time seeing this failure
                    self.send_alert(fg.name, result.latency_message)
                    self.notified_failures.add(fg.name)  # Track it
            else:
                # Latency resolved, remove from tracking
                self.notified_failures.discard(fg.name)
```

**Why use set here?**
- **Unique items**: Each failure name only once
- **Fast lookup**: O(1) to check if already notified
- **Easy management**: Simple add/discard operations
- **Perfect for tracking**: "Have we seen this before?"

### Set Operations

```python
# Union (all items from both sets)
set1 = {1, 2, 3}
set2 = {3, 4, 5}
print(set1 | set2)  # {1, 2, 3, 4, 5}
print(set1.union(set2))  # Same thing

# Intersection (items in both sets)
print(set1 & set2)  # {3}
print(set1.intersection(set2))  # Same thing

# Difference (items in first but not second)
print(set1 - set2)  # {1, 2}
print(set1.difference(set2))  # Same thing

# Symmetric difference (items in either but not both)
print(set1 ^ set2)  # {1, 2, 4, 5}
print(set1.symmetric_difference(set2))  # Same thing
```

### Removing Duplicates

```python
# Remove duplicates from a list
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique = list(set(numbers))
print(unique)  # [1, 2, 3, 4] (order not guaranteed!)

# Preserve order while removing duplicates
def unique_ordered(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
print(unique_ordered(numbers))  # [1, 2, 3, 4] (order preserved!)
```

### Set Membership Testing

```python
# Very fast membership testing
large_list = list(range(1000000))
large_set = set(large_list)

# Slow with list (O(n))
import time
start = time.time()
999999 in large_list  # Checks every item until found
print(f"List: {time.time() - start:.6f}s")

# Fast with set (O(1))
start = time.time()
999999 in large_set  # Instant lookup
print(f"Set: {time.time() - start:.6f}s")

# Output:
# List: 0.012345s
# Set: 0.000001s
```

### When to Use Sets

✅ **Use sets when:**
- Need unique items only
- Fast membership testing important
- Order doesn't matter
- Need set operations (union, intersection)
- Tracking "seen" items

❌ **Don't use sets when:**
- Need to maintain order
- Need duplicate items
- Need indexing (sets aren't indexed)
- Items aren't hashable (lists, dicts can't be in sets)

---

## Advanced f-strings

### Basic f-strings (Review)

```python
name = "Alice"
age = 30

# Basic f-string
print(f"Hello, {name}!")  # "Hello, Alice!"

# Multiple variables
print(f"{name} is {age} years old")  # "Alice is 30 years old"

# Expressions
print(f"{name} will be {age + 1} next year")  # "Alice will be 31 next year"
```

### Formatting Numbers

```python
# Decimal places
pi = 3.14159265359
print(f"Pi is approximately {pi:.2f}")  # "Pi is approximately 3.14"
print(f"Pi is approximately {pi:.4f}")  # "Pi is approximately 3.1416"

# Percentage
ratio = 0.856
print(f"Success rate: {ratio:.1%}")  # "Success rate: 85.6%"
print(f"Success rate: {ratio:.2%}")  # "Success rate: 85.60%"

# Thousands separator
large_number = 1234567890
print(f"Population: {large_number:,}")  # "Population: 1,234,567,890"

# Scientific notation
small_number = 0.000001234
print(f"Value: {small_number:.2e}")  # "Value: 1.23e-06"
```

### Alignment and Padding

```python
# Right align (default for numbers)
print(f"|{42:10}|")  # "|        42|"

# Left align
print(f"|{42:<10}|")  # "|42        |"

# Center align
print(f"|{42:^10}|")  # "|    42    |"

# With strings
name = "Alice"
print(f"|{name:>10}|")  # "|     Alice|"
print(f"|{name:<10}|")  # "|Alice     |"
print(f"|{name:^10}|")  # "|  Alice   |"

# Padding with specific character
print(f"|{42:0>10}|")  # "|0000000042|"
print(f"|{name:*^10}|")  # "|**Alice***|"
```

### Example from Our Code

From `connection.py` and `monitor.py`:
```python
# Build paths dynamically
vault_namespace = "production"
secret_path = "snowflake/credentials"
full_path = f"{vault_namespace}/{secret_path}"
# "production/snowflake/credentials"

# Monitor naming
account = "prod_account"
monitor_name = f"SnowflakeMonitor-{account}"
# "SnowflakeMonitor-prod_account"

# Error messages with context
account = "prod"
error = "Connection timeout"
message = f"Failed to connect to Snowflake account {account}: {error}"
# "Failed to connect to Snowflake account prod: Connection timeout"

# Formatting monitoring results
response_time = 125.456
print(f"Response time: {response_time:.1f}ms")
# "Response time: 125.5ms"

# Progress messages
current = 5
total = 10
print(f"Processing {current}/{total} ({current/total:.1%})")
# "Processing 5/10 (50.0%)"
```

### Debugging with f-strings

```python
# Python 3.8+ feature: = for debugging
x = 10
y = 20
print(f"{x=}, {y=}, {x+y=}")
# "x=10, y=20, x+y=30"

# Useful for debugging
result = complex_calculation()
print(f"{result=}")  # Shows both name and value
```

### Multiline f-strings

```python
name = "Alice"
age = 30
city = "New York"

# Multiline f-string
message = f"""
Hello {name}!

You are {age} years old and live in {city}.

Have a great day!
"""

print(message)
```

### Calling Functions in f-strings

```python
def get_greeting(name):
    return f"Hello, {name}!"

name = "Alice"
print(f"{get_greeting(name)} How are you?")
# "Hello, Alice! How are you?"

# Method calls
text = "hello world"
print(f"Uppercase: {text.upper()}")
# "Uppercase: HELLO WORLD"

# With formatting
numbers = [1, 2, 3, 4, 5]
print(f"Sum: {sum(numbers)}, Average: {sum(numbers)/len(numbers):.2f}")
# "Sum: 15, Average: 3.00"
```

### Date and Time Formatting

```python
from datetime import datetime

now = datetime.now()

# Different formats
print(f"Date: {now:%Y-%m-%d}")  # "Date: 2025-01-15"
print(f"Time: {now:%H:%M:%S}")  # "Time: 14:30:45"
print(f"Full: {now:%Y-%m-%d %H:%M:%S}")  # "Full: 2025-01-15 14:30:45"
print(f"Readable: {now:%B %d, %Y}")  # "Readable: January 15, 2025"
```

### When to Use f-strings

✅ **Use f-strings when:**
- Building strings with variables
- Need readable string formatting
- Python 3.6+ (modern Python)
- Performance matters (faster than .format())

❌ **Don't use f-strings when:**
- Logging (use lazy logging with %s)
- Template strings reused many times
- Need to store format string separately

**Logging exception:**
```python
# DON'T do this in logging:
logger.info(f"User {user_id} logged in")  # String always created

# DO this instead:
logger.info("User %s logged in", user_id)  # String only if logged
```

---

## Summary

You've now learned all the Python concepts used in the codebase!

### What You Learned

1. **@dataclass** - Automatic class generation for data containers
2. **Enum** - Type-safe constants with meaningful names
3. **@classmethod** - Alternative constructors and factory methods
4. **super()** - Proper parent method calling in inheritance
5. **List comprehensions** - Concise list creation
6. **enumerate()** - Pythonic way to get index and item
7. **Sets** - Unique collections with fast lookup
8. **Advanced f-strings** - Powerful string formatting

### Next Steps

1. **Practice**: Do the exercises in the `exercises/` directory
2. **Read the code**: Find these concepts in the codebase
3. **Experiment**: Try modifying the examples
4. **Build**: Create your own classes using these concepts

### Complete Tutorial Series

- ✅ [Part 1: Python Fundamentals](01_PYTHON_BASICS_FOR_THIS_PROJECT.md)
- ✅ [Part 2: Advanced Concepts](01_PYTHON_BASICS_PART2.md)
- ✅ [Part 3: Missing Concepts](01_PYTHON_BASICS_PART3.md) (You are here!)
- 📚 [Module Tutorials](README.md)

---

**Congratulations!** You now have complete coverage of all Python concepts used in the Snowflake monitoring codebase. Time to practice with the exercises!

---

## Quick Reference

| Concept | Use Case | Example |
|---------|----------|---------|
| @dataclass | Data containers | `@dataclass class Result: success: bool` |
| Enum | Type-safe constants | `class Status(Enum): ACTIVE = "active"` |
| @classmethod | Alternative constructors | `@classmethod def from_string(cls, s):` |
| super() | Call parent method | `super().__init__(name)` |
| List comprehension | Create lists | `[x**2 for x in range(10)]` |
| enumerate() | Index + item | `for i, item in enumerate(items):` |
| Sets | Unique items | `seen = set()` |
| f-strings | String formatting | `f"{name} is {age} years old"` |
