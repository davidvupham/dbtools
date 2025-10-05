# Complete Python Tutorial for Beginners
## Learn Python Through the Snowflake Monitoring Project

Welcome! This tutorial will teach you Python from the ground up, using real examples from our codebase. By the end, you'll understand not just **what** the code does, but **why** it was written this way.

---

## Table of Contents

1. [Introduction to Python](#introduction-to-python)
2. [Variables and Data Types](#variables-and-data-types)
3. [Data Structures](#data-structures)
4. [Functions](#functions)
5. [Object-Oriented Programming (OOP)](#object-oriented-programming)
6. [Inheritance and Polymorphism](#inheritance-and-polymorphism)
7. [Abstract Base Classes](#abstract-base-classes)
8. [Error Handling](#error-handling)
9. [Type Hints](#type-hints)
10. [Decorators](#decorators)
11. [Context Managers](#context-managers)
12. [Logging](#logging)
13. [Modules and Packages](#modules-and-packages)
14. [Design Patterns](#design-patterns)

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

## Object-Oriented Programming

### What is OOP?

**Object-Oriented Programming** organizes code into "objects" that contain both data and functions. Think of it like creating blueprints (classes) and then building things (objects) from those blueprints.

### Real-World Analogy

Imagine a **Car** blueprint:
- **Data (Attributes)**: color, brand, speed, fuel_level
- **Actions (Methods)**: start(), stop(), accelerate(), brake()

From one blueprint, you can create many cars:
```python
my_car = Car(color="red", brand="Toyota")
your_car = Car(color="blue", brand="Honda")
```

### Your First Class

```python
class Dog:
    """A simple class representing a dog."""
    
    # Constructor - runs when creating a new dog
    def __init__(self, name, age):
        """Initialize a dog with name and age."""
        self.name = name  # Each dog has its own name
        self.age = age    # Each dog has its own age
    
    # Method - a function inside a class
    def bark(self):
        """Make the dog bark."""
        print(f"{self.name} says Woof!")
    
    def get_age_in_months(self):
        """Calculate age in months."""
        return self.age * 12
    
    def have_birthday(self):
        """Increase age by 1."""
        self.age += 1
        print(f"Happy birthday {self.name}! Now {self.age} years old.")

# Create dog objects (instances)
my_dog = Dog("Buddy", 5)
your_dog = Dog("Max", 3)

# Each dog is independent
my_dog.bark()  # "Buddy says Woof!"
your_dog.bark()  # "Max says Woof!"

print(my_dog.get_age_in_months())  # 60
print(your_dog.get_age_in_months())  # 36

my_dog.have_birthday()  # Only Buddy ages
print(my_dog.age)   # 6
print(your_dog.age)  # Still 3
```

### Understanding `self`

`self` refers to the specific object (instance) you're working with:

```python
class Counter:
    def __init__(self):
        self.count = 0  # THIS counter's count
    
    def increment(self):
        self.count += 1  # Modify THIS counter's count
    
    def get_count(self):
        return self.count  # Return THIS counter's count

# Create two independent counters
counter1 = Counter()
counter2 = Counter()

counter1.increment()
counter1.increment()
counter2.increment()

print(counter1.get_count())  # 2 (counter1's count)
print(counter2.get_count())  # 1 (counter2's count)
```

**Key Point:** Each object has its own data. `self` lets methods access that object's specific data.

### Example from Our Code

From `connection.py`:
```python
class SnowflakeConnection:
    """Manages connections to Snowflake database."""
    
    def __init__(self, account: str, user: Optional[str] = None):
        """Initialize a new connection."""
        # Store connection parameters for THIS connection
        self.account = account
        self.user = user
        self.connection = None  # No connection yet
        self._initialized = False
    
    def connect(self):
        """Establish connection to Snowflake."""
        # Use THIS connection's account and user
        self.connection = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            private_key=self.private_key
        )
        self._initialized = True
        return self.connection
    
    def is_connected(self) -> bool:
        """Check if THIS connection is active."""
        return self.connection is not None and not self.connection.is_closed()
    
    def close(self):
        """Close THIS connection."""
        if self.connection is not None:
            self.connection.close()
            self._initialized = False

# Create multiple independent connections
prod_conn = SnowflakeConnection(account="prod_account", user="admin")
dev_conn = SnowflakeConnection(account="dev_account", user="developer")

# Each connection is independent
prod_conn.connect()  # Connects to production
dev_conn.connect()   # Connects to development

print(prod_conn.is_connected())  # True
print(dev_conn.is_connected())   # True

prod_conn.close()  # Only closes production
print(prod_conn.is_connected())  # False
print(dev_conn.is_connected())   # Still True!
```

**Why use a class here?**
- Each connection needs its own account, user, and connection object
- Methods like `connect()` and `close()` operate on specific connections
- Encapsulates all connection logic in one place
- Can create multiple connections that don't interfere with each other

### Public vs Private Attributes

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # Public - anyone can access
        self._balance = balance     # Private (by convention) - internal use
        self.__pin = "1234"         # Really private - name mangled
    
    def get_balance(self):
        """Public method to access private balance."""
        return self._balance
    
    def deposit(self, amount):
        """Public method to modify private balance."""
        if amount > 0:
            self._balance += amount
            return True
        return False

account = BankAccount("Alice", 1000)

# Public attribute - OK to access
print(account.owner)  # "Alice"

# Private attribute - shouldn't access directly (but can)
print(account._balance)  # 1000 (works but discouraged)

# Should use public methods instead
print(account.get_balance())  # 1000 (proper way)
account.deposit(500)
print(account.get_balance())  # 1500
```

**Naming Conventions:**
- `name` - Public (anyone can use)
- `_name` - Private by convention (internal use, but not enforced)
- `__name` - Really private (Python mangles the name)

**Example from Our Code** (`connection.py`):
```python
class SnowflakeConnection:
    def __init__(self, account: str):
        self.account = account          # Public - users need this
        self.connection = None          # Public - users might need this
        self._initialized = False       # Private - internal state
    
    def is_initialized(self) -> bool:
        """Public method to check private state."""
        return self._initialized
```

**Why this design?**
- Public attributes (`account`, `connection`) are part of the API
- Private attributes (`_initialized`) are implementation details
- Users don't need to know about `_initialized`, but `is_initialized()` provides access if needed

---

## Inheritance and Polymorphism

### What is Inheritance?

Inheritance lets you create a new class based on an existing class. The new class gets all the features of the original, plus you can add more or change things.

### Simple Inheritance Example

```python
# Base class (parent)
class Animal:
    """Base class for all animals."""
    
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        """Make a sound."""
        return "Some sound"
    
    def move(self):
        """Move around."""
        return f"{self.name} is moving"

# Derived class (child) inherits from Animal
class Dog(Animal):
    """Dog is a type of Animal."""
    
    def speak(self):
        """Override speak method."""
        return f"{self.name} says Woof!"
    
    def fetch(self):
        """New method specific to dogs."""
        return f"{self.name} is fetching the ball"

class Cat(Animal):
    """Cat is a type of Animal."""
    
    def speak(self):
        """Override speak method."""
        return f"{self.name} says Meow!"
    
    def climb(self):
        """New method specific to cats."""
        return f"{self.name} is climbing a tree"

# Create instances
dog = Dog("Buddy")
cat = Cat("Whiskers")

# Inherited method (same for both)
print(dog.move())   # "Buddy is moving"
print(cat.move())   # "Whiskers is moving"

# Overridden method (different for each)
print(dog.speak())  # "Buddy says Woof!"
print(cat.speak())  # "Whiskers says Meow!"

# Specific methods
print(dog.fetch())  # "Buddy is fetching the ball"
print(cat.climb())  # "Whiskers is climbing a tree"
```

**Key Concepts:**
- `Dog(Animal)` means Dog inherits from Animal
- Dog gets all of Animal's methods automatically
- Dog can override methods (like `speak()`)
- Dog can add new methods (like `fetch()`)

### Example from Our Code

From `base.py` and `connection.py`:
```python
# Base class defines the interface
class DatabaseConnection(ABC):
    """Abstract base class for all database connections."""
    
    @abstractmethod
    def connect(self) -> Any:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Execute a query and return results."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass

# Snowflake-specific implementation
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """Snowflake implementation of DatabaseConnection."""
    
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        self.connection = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            private_key=self.private_key
        )
        return self.connection
    
    def disconnect(self) -> None:
        """Close Snowflake connection."""
        self.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Execute a Snowflake query."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def is_connected(self) -> bool:
        """Check if Snowflake connection is active."""
        return self.connection is not None and not self.connection.is_closed()
```

**Why this design?**
- `DatabaseConnection` defines what ALL database connections must do
- `SnowflakeConnection` provides Snowflake-specific implementation
- Could easily add `PostgreSQLConnection`, `MySQLConnection`, etc.
- All would have the same methods, making them interchangeable

### Multiple Inheritance

Python allows inheriting from multiple classes:

```python
class Flyable:
    """Mixin for things that can fly."""
    def fly(self):
        return f"{self.name} is flying"

class Swimmable:
    """Mixin for things that can swim."""
    def swim(self):
        return f"{self.name} is swimming"

class Duck(Animal, Flyable, Swimmable):
    """Duck can do everything!"""
    def speak(self):
        return f"{self.name} says Quack!"

duck = Duck("Donald")
print(duck.speak())  # From Animal (overridden)
print(duck.move())   # From Animal
print(duck.fly())    # From Flyable
print(duck.swim())   # From Swimmable
```

**Example from Our Code** (`connection.py`):
```python
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    Inherits from three base classes:
    - DatabaseConnection: Database-specific methods
    - ConfigurableComponent: Configuration management
    - ResourceManager: Resource lifecycle management
    """
    
    # Gets methods from all three parent classes!
    # - connect(), disconnect(), execute_query() from DatabaseConnection
    # - get_config(), set_config() from ConfigurableComponent
    # - initialize(), cleanup(), __enter__(), __exit__() from ResourceManager
```

**Why multiple inheritance?**
- Each base class provides a specific set of functionality
- Combines features without duplicating code
- Follows "composition over inheritance" principle
- Makes the class more flexible and reusable

### Polymorphism

Polymorphism means "many forms" - different classes can be used interchangeably if they have the same methods:

```python
def make_animal_speak(animal):
    """Works with any animal that has a speak() method."""
    print(animal.speak())

dog = Dog("Buddy")
cat = Cat("Whiskers")
duck = Duck("Donald")

# All work with the same function!
make_animal_speak(dog)   # "Buddy says Woof!"
make_animal_speak(cat)   # "Whiskers says Meow!"
make_animal_speak(duck)  # "Donald says Quack!"

# Can also use in loops
animals = [dog, cat, duck]
for animal in animals:
    print(animal.speak())  # Each speaks differently!
```

**Example from Our Code** (`base.py`):
```python
class BaseMonitor(ABC):
    """Base class for all monitors."""
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """Perform monitoring check."""
        pass

class SnowflakeMonitor(BaseMonitor):
    """Snowflake-specific monitor."""
    def check(self) -> Dict[str, Any]:
        return self.monitor_all()

class PostgreSQLMonitor(BaseMonitor):
    """PostgreSQL-specific monitor."""
    def check(self) -> Dict[str, Any]:
        return self.check_postgres()

# Polymorphism in action
def run_monitoring(monitors: List[BaseMonitor]):
    """Run all monitors, regardless of type."""
    for monitor in monitors:
        result = monitor.check()  # Works for any monitor!
        print(f"Monitor result: {result}")

# All monitors can be used the same way
monitors = [
    SnowflakeMonitor(account="prod"),
    PostgreSQLMonitor(host="localhost")
]
run_monitoring(monitors)  # Works with both!
```

**Why polymorphism?**
- Write code that works with any type of monitor
- Add new monitor types without changing existing code
- Makes code more flexible and maintainable

---

## Abstract Base Classes

### What is an Abstract Base Class?

An **Abstract Base Class (ABC)** is a blueprint that defines what methods a class MUST have, but doesn't implement them. It's like a contract: "If you inherit from me, you MUST implement these methods."

### Why Use ABCs?

```python
from abc import ABC, abstractmethod

# Without ABC - no enforcement
class Animal:
    def speak(self):
        pass  # Forgot to implement!

dog = Animal()
dog.speak()  # Does nothing, no error!

# With ABC - enforced
class Animal(ABC):
    @abstractmethod
    def speak(self):
        """All animals must be able to speak."""
        pass

# This will raise an error!
# dog = Animal()  # TypeError: Can't instantiate abstract class

# Must create a concrete class
class Dog(Animal):
    def speak(self):  # MUST implement this
        return "Woof!"

dog = Dog()  # Now it works!
```

### Example from Our Code

From `base.py`:
```python
from abc import ABC, abstractmethod

class DatabaseConnection(ABC):
    """
    Abstract base class for database connections.
    
    Defines the interface that ALL database connection classes must implement.
    """
    
    @abstractmethod
    def connect(self) -> Any:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Execute a query and return results."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        pass
```

**Why this design?**
- **Enforces consistency**: All database connections must have these methods
- **Self-documenting**: Clear what a database connection should do
- **Prevents errors**: Can't forget to implement required methods
- **Enables polymorphism**: Any DatabaseConnection can be used interchangeably

### Implementing an ABC

```python
class SnowflakeConnection(DatabaseConnection):
    """Concrete implementation of DatabaseConnection for Snowflake."""
    
    # MUST implement all abstract methods
    
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        self.connection = snowflake.connector.connect(...)
        return self.connection
    
    def disconnect(self) -> None:
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Any]:
        """Execute Snowflake query."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def is_connected(self) -> bool:
        """Check if connected to Snowflake."""
        return self.connection is not None and not self.connection.is_closed()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Snowflake connection info."""
        return {
            'account': self.account,
            'user': self.user,
            'connected': self.is_connected()
        }
```

If you forget to implement even ONE method, Python will raise an error when you try to create an instance!

### More Examples from Our Code

**BaseMonitor** (`base.py`):
```python
class BaseMonitor(ABC):
    """
    Abstract base class for all monitoring operations.
    
    Provides common functionality and defines required interface.
    """
    
    def __init__(self, name: str, timeout: int = 30):
        """Initialize base monitor."""
        self.name = name
        self.timeout = timeout
        self._check_count = 0
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """
        Perform the monitoring check.
        
        MUST be implemented by subclasses.
        """
        pass
    
    def _log_result(self, result: Dict[str, Any]) -> None:
        """Log monitoring result (concrete method - already implemented)."""
        status = "SUCCESS" if result.get('success', False) else "FAILED"
        print(f"{self.name} check {status}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics (concrete method)."""
        return {
            'name': self.name,
            'check_count': self._check_count,
            'timeout': self.timeout
        }
```

**SnowflakeMonitor** (`monitor.py`):
```python
class SnowflakeMonitor(BaseMonitor):
    """Concrete implementation of BaseMonitor for Snowflake."""
    
    def __init__(self, account: str, **kwargs):
        # Call parent constructor
        super().__init__(name=f"SnowflakeMonitor-{account}", timeout=30)
        self.account = account
    
    def check(self) -> Dict[str, Any]:
        """
        Implement required check method.
        
        This is what BaseMonitor requires us to implement.
        """
        start_time = time.time()
        
        try:
            # Run Snowflake-specific monitoring
            results = self.monitor_all()
            
            duration_ms = (time.time() - start_time) * 1000
            
            result = {
                'success': results['summary']['connectivity_ok'],
                'message': f"Monitoring completed for {self.account}",
                'duration_ms': duration_ms,
                'data': results
            }
            
            # Use inherited method
            self._log_result(result)
            
            return result
            
        except Exception as e:
            # Handle errors...
            pass
```

**Key Points:**
- `BaseMonitor` defines what ALL monitors must do (`check()`)
- `BaseMonitor` provides common functionality (`_log_result()`, `get_stats()`)
- `SnowflakeMonitor` MUST implement `check()`
- `SnowflakeMonitor` can use inherited methods
- `super().__init__()` calls the parent's constructor

### Benefits of ABCs

1. **Enforces Interface**: Can't forget required methods
2. **Documentation**: Clear what a class should do
3. **Polymorphism**: All implementations can be used interchangeably
4. **Early Error Detection**: Errors at class creation, not runtime
5. **Code Organization**: Separates interface from implementation

---

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