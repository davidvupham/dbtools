# Advanced Object-Oriented Programming Concepts
## Beyond the Basics - Mastering Python OOP

Welcome to the advanced OOP tutorial! This guide covers sophisticated concepts that take your object-oriented programming skills to the next level.

**⚠️ Important Note for Beginners:**
If you're new to OOP, **start with [oop_guide.md](./oop_guide.md) first!** This guide assumes you already understand:
- Classes, objects, and methods
- Inheritance and polymorphism
- Abstract base classes
- SOLID principles
- Basic design patterns

**When should you learn these advanced topics?**
- When you encounter specific problems they solve
- When working on complex, large-scale applications
- When you're comfortable with basic OOP and want to deepen your knowledge
- NOT as your first introduction to OOP!

**Remember:** Just because something is "advanced" doesn't mean you should use it everywhere. Many professional developers rarely use some of these concepts. Use them when they solve real problems, not just because they're interesting!

---

## Table of Contents

1. [Async/Await with Classes](#asyncawait-with-classes)
2. [Multiple Inheritance and the Diamond Problem](#multiple-inheritance-and-the-diamond-problem)
3. [Monkey Patching and Dynamic Class Modification](#monkey-patching-and-dynamic-class-modification)
4. [Advanced Metaclass Usage](#advanced-metaclass-usage)
5. [Protocol Buffers and Serialization](#protocol-buffers-and-serialization)
6. [Performance Optimization Techniques](#performance-optimization-techniques)
7. [Memory Management and Weak References](#memory-management-and-weak-references)
8. [Exercises and Practice](#exercises-and-practice)

---

### Prerequisites and roadmap

This document assumes you’re comfortable with core OOP in Python (classes/objects, encapsulation, inheritance, polymorphism), dataclasses, basic testing, and error handling. If you’re new to these, start with `oop_guide.md` and come back here for deep dives.

## Async/Await with Classes

Asynchronous programming allows your code to handle multiple operations concurrently without blocking. When combined with OOP, it enables building responsive, scalable systems.

### Basic Async Class Methods

```python
import asyncio
import aiohttp
from typing import List, Dict, Any
import time

class AsyncDataFetcher:
    """Asynchronous data fetching service."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def fetch_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch a single user asynchronously."""
        if not self.session:
            raise RuntimeError("Use async context manager")

        url = f"{self.base_url}/users/{user_id}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_multiple_users(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch multiple users concurrently."""
        tasks = [self.fetch_user(user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def fetch_with_timeout(self, user_id: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Fetch user with timeout."""
        try:
            return await asyncio.wait_for(self.fetch_user(user_id), timeout=timeout)
        except asyncio.TimeoutError:
            return {"error": "Request timed out", "user_id": user_id}

# Usage
async def main():
    async with AsyncDataFetcher("https://jsonplaceholder.typicode.com") as fetcher:
        # Fetch single user
        user = await fetcher.fetch_user(1)
        print(f"User: {user}")

        # Fetch multiple users concurrently
        users = await fetcher.fetch_multiple_users([1, 2, 3, 4, 5])
        print(f"Fetched {len(users)} users")

        # With timeout
        user_with_timeout = await fetcher.fetch_with_timeout(1, timeout=1.0)
        print(f"User with timeout: {user_with_timeout}")

# Run the async code
# asyncio.run(main())
```

### Async Class Properties and Descriptors

```python
class AsyncProperty:
    """Descriptor for async properties."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Return a coroutine
        return self.func(obj)

class AsyncDatabaseConnection:
    """Database connection with async properties."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None
        self._connected = False

    async def connect(self):
        """Establish database connection."""
        # Simulate async connection
        await asyncio.sleep(0.1)
        self._connected = True
        self._connection = f"Connected to {self.connection_string}"

    async def disconnect(self):
        """Close database connection."""
        await asyncio.sleep(0.1)
        self._connected = False
        self._connection = None

    @AsyncProperty
    async def connection_status(self):
        """Async property to check connection status."""
        if not self._connected:
            return "Disconnected"

        # Simulate checking connection health
        await asyncio.sleep(0.05)
        return "Connected"

    @AsyncProperty
    async def active_queries(self):
        """Async property to get active query count."""
        if not self._connected:
            return 0

        # Simulate querying active connections
        await asyncio.sleep(0.02)
        return 42  # Mock value

# Usage
async def demo_async_properties():
    db = AsyncDatabaseConnection("postgresql://localhost/mydb")

    print("Before connection:")
    status = await db.connection_status
    print(f"Status: {status}")

    await db.connect()

    print("After connection:")
    status = await db.connection_status
    queries = await db.active_queries
    print(f"Status: {status}")
    print(f"Active queries: {queries}")

    await db.disconnect()

# asyncio.run(demo_async_properties())
```

Note: Awaitable properties (e.g., `await obj.connection_status`) are unconventional in Python and can surprise readers. Prefer explicit async methods (e.g., `await obj.get_connection_status()`) for clarity unless a descriptor-based API is a clear win.

### Async Context Managers and Resource Management

```python
class AsyncResourcePool:
    """Pool of async resources with automatic cleanup."""

    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.available = asyncio.Queue(maxsize=max_size)
        self.in_use = set()
        self._closed = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize the resource pool."""
        for i in range(self.max_size):
            resource = f"Resource-{i}"
            await self.available.put(resource)

    async def acquire(self) -> str:
        """Acquire a resource from the pool."""
        if self._closed:
            raise RuntimeError("Pool is closed")

        resource = await self.available.get()
        self.in_use.add(resource)
        return resource

    async def release(self, resource: str):
        """Release a resource back to the pool."""
        if resource in self.in_use:
            self.in_use.remove(resource)
            await self.available.put(resource)

    async def close(self):
        """Close the pool and cleanup resources."""
        self._closed = True
        # Cleanup logic here
        pass

class AsyncWorker:
    """Worker that uses resources from a pool."""

    def __init__(self, pool: AsyncResourcePool, worker_id: int):
        self.pool = pool
        self.worker_id = worker_id

    async def do_work(self, work_item: str):
        """Perform work using a resource from the pool."""
        resource = await self.pool.acquire()
        try:
            print(f"Worker {self.worker_id} using {resource} for {work_item}")
            await asyncio.sleep(0.1)  # Simulate work
            result = f"Processed {work_item} with {resource}"
            return result
        finally:
            await self.pool.release(resource)

async def demo_resource_pool():
    async with AsyncResourcePool(max_size=3) as pool:
        workers = [AsyncWorker(pool, i) for i in range(5)]

        # Create work tasks
        tasks = []
        for i, worker in enumerate(workers):
            for j in range(2):  # Each worker does 2 tasks
                task = worker.do_work(f"Task-{i}-{j}")
                tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} tasks")

# asyncio.run(demo_resource_pool())
```

### Exercise 1: Async Database Connection Pool

**Task:** Create an async database connection pool that can be used in the dbtools project.

**Requirements:**
1. Implement connection pooling with async context managers
2. Support concurrent queries without blocking
3. Handle connection timeouts and retries
4. Provide both individual connections and pooled usage

**Starter Code:**
```python
import asyncio
from typing import Optional, List
import time

class AsyncDatabasePool:
    """Async database connection pool."""

    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        # TODO: Implement pool initialization

    async def get_connection(self):
        """Get a connection from the pool."""
        # TODO: Implement connection acquisition
        pass

    async def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute query using a pooled connection."""
        # TODO: Implement query execution
        pass

# TODO: Implement the rest of the class
```

---

## Multiple Inheritance and the Diamond Problem

Multiple inheritance allows a class to inherit from multiple parent classes, but it can create the "diamond problem" where method resolution order becomes ambiguous.

### The Diamond Problem

```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):  # Multiple inheritance
    pass

# What does D().method() return?
d = D()
print(d.method())  # "B" - follows MRO
print(D.__mro__)   # Method Resolution Order
```

### Real-World Example from Our Codebase

From `gds_snowflake/connection.py`:
```python
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    Multiple inheritance example from our codebase.

    This class inherits from three abstract base classes:
    - DatabaseConnection: Database interface
    - ConfigurableComponent: Configuration management
    - ResourceManager: Resource lifecycle management
    """
```

Let's examine the inheritance hierarchy:

```python
# From base.py
class DatabaseConnection(ABC):
    @abstractmethod
    def connect(self): pass
    @abstractmethod
    def disconnect(self): pass
    # ... other methods

class ConfigurableComponent(ABC):
    def __init__(self, config=None):
        self.config = config or {}

    @abstractmethod
    def validate_config(self): pass
    # ... other methods

class ResourceManager(ABC):
    @abstractmethod
    def initialize(self): pass
    @abstractmethod
    def cleanup(self): pass
    # ... other methods

# The SnowflakeConnection inherits from all three
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    def __init__(self, **kwargs):
        # Cooperative multiple inheritance: rely on super() so all bases
        # participate according to the MRO
        super().__init__(**kwargs)
        # ... other initialization

    # Implement all abstract methods
    def connect(self): pass
    def disconnect(self): pass
    def validate_config(self): pass
    def initialize(self): pass
    def cleanup(self): pass
    # ... other implementations
```

### Cooperative Multiple Inheritance

```python
class LoggerMixin:
    """Mixin for logging functionality."""

    def __init__(self, logger_name=None, **kwargs):
        super().__init__(**kwargs)
        self.logger_name = logger_name or self.__class__.__name__
        self.logger = logging.getLogger(self.logger_name)

class SerializableMixin:
    """Mixin for serialization functionality."""

    def to_dict(self):
        """Convert object to dictionary."""
        return {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith('_') and not callable(getattr(self, attr))
        }

    def to_json(self):
        """Convert object to JSON string."""
        import json
        return json.dumps(self.to_dict(), default=str)

class ValidatableMixin:
    """Mixin for validation functionality."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._errors = []

    def validate(self):
        """Validate the object."""
        self._errors = []
        self._run_validations()
        return len(self._errors) == 0

    def _run_validations(self):
        """Override in subclasses to add validations."""
        pass

    def add_error(self, field, message):
        """Add validation error."""
        self._errors.append({'field': field, 'message': message})

    def get_errors(self):
        """Get validation errors."""
        return self._errors.copy()

class User(LoggerMixin, SerializableMixin, ValidatableMixin):
    """User class with multiple mixins."""

    def __init__(self, name, email, age=None, **kwargs):
        super().__init__(**kwargs)  # Initialize mixins
        self.name = name
        self.email = email
        self.age = age

    def _run_validations(self):
        """Custom validations for User."""
        if not self.name or len(self.name.strip()) == 0:
            self.add_error('name', 'Name is required')

        if not self.email or '@' not in self.email:
            self.add_error('email', 'Valid email is required')

        if self.age is not None and (self.age < 0 or self.age > 150):
            self.add_error('age', 'Age must be between 0 and 150')

# Usage
user = User("Alice", "alice@example.com", age=30)

# Validation
if user.validate():
    print("User is valid")
    # Logging (from LoggerMixin)
    user.logger.info("User validated successfully")
    # Serialization (from SerializableMixin)
    print("User JSON:", user.to_json())
else:
    print("Validation errors:", user.get_errors())
```

### Method Resolution Order (MRO) in Detail

```python
class A:
    def __init__(self):
        print("A.__init__")
        super().__init__()

class B(A):
    def __init__(self):
        print("B.__init__")
        super().__init__()

class C(A):
    def __init__(self):
        print("C.__init__")
        super().__init__()

class D(B, C):
    def __init__(self):
        print("D.__init__")
        super().__init__()

# Check MRO
print("MRO:", D.__mro__)

# Create instance
d = D()
# Output:
# D.__init__
# B.__init__
# C.__init__
# A.__init__
```

### Exercise 2: Multiple Inheritance Design

**Task:** Design a class hierarchy for a content management system using multiple inheritance.

**Requirements:**
1. Create mixins for different capabilities (Searchable, Versionable, Publishable)
2. Implement a Content class that inherits from multiple mixins
3. Ensure proper MRO and cooperative inheritance
4. Add validation and error handling

**Starter Code:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time

class SearchableMixin:
    """Mixin for searchable content."""
    # TODO: Implement search functionality

class VersionableMixin:
    """Mixin for version control."""
    # TODO: Implement versioning

class PublishableMixin:
    """Mixin for publishable content."""
    # TODO: Implement publishing

class Content(SearchableMixin, VersionableMixin, PublishableMixin):
    """Content class with multiple mixins."""
    # TODO: Implement Content class

# TODO: Test the implementation
```

---

## Monkey Patching and Dynamic Class Modification

Monkey patching allows runtime modification of classes and objects. While powerful, it should be used carefully as it can make code unpredictable.

### Basic Monkey Patching

```python
class Calculator:
    def add(self, a, b):
        return a + b

# Original usage
calc = Calculator()
print(calc.add(2, 3))  # 5

# Monkey patch the method
def patched_add(self, a, b):
    print(f"Adding {a} + {b}")
    result = a + b
    print(f"Result: {result}")
    return result

# Apply the patch
Calculator.add = patched_add

# Now all instances use the patched method
calc2 = Calculator()
print(calc2.add(4, 5))  # Shows debug output

# Even existing instances are affected
print(calc.add(1, 2))   # Shows debug output
```

### Instance-Level Monkey Patching

```python
class DatabaseConnection:
    def __init__(self, host):
        self.host = host

    def connect(self):
        return f"Connected to {self.host}"

# Create instance
db = DatabaseConnection("localhost")

# Add method to specific instance only
def debug_connect(self):
    print(f"DEBUG: Connecting to {self.host}")
    # Call the original class method to avoid recursion
    result = DatabaseConnection.connect(self)
    print(f"DEBUG: {result}")
    return result

original_connect = DatabaseConnection.connect  # keep original for reference
db.connect = debug_connect.__get__(db, DatabaseConnection)

# Only this instance has the debug behavior
db2 = DatabaseConnection("remote")
print(db.connect())   # Debug output
print(db2.connect())  # Normal output
```

### Class Attribute Modification

```python
class APIClient:
    BASE_URL = "https://api.example.com"
    TIMEOUT = 30

    def __init__(self, api_key):
        self.api_key = api_key

# Monkey patch class attributes
APIClient.BASE_URL = "https://staging.api.example.com"
APIClient.TIMEOUT = 60

# Add new class method
@classmethod
def get_config(cls):
    return {
        'base_url': cls.BASE_URL,
        'timeout': cls.TIMEOUT
    }

APIClient.get_config = get_config

# All instances and the class itself are affected
client = APIClient("key123")
print(client.BASE_URL)      # staging URL
print(APIClient.get_config())  # New method available
```

### Safe Monkey Patching with Context Managers

```python
import contextlib
from typing import Any, Callable

class MonkeyPatch:
    """Context manager for safe monkey patching."""

    def __init__(self):
        self.patches = []

    def patch(self, obj: Any, attr: str, new_value: Any):
        """Add a patch to be applied."""
        existed = hasattr(obj, attr)
        original = getattr(obj, attr) if existed else None
        self.patches.append((obj, attr, existed, original, new_value))

    def __enter__(self):
        # Apply all patches
        for obj, attr, _, _, new_value in self.patches:
            setattr(obj, attr, new_value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original values
        for obj, attr, existed, original_value, _ in reversed(self.patches):
            if existed:
                setattr(obj, attr, original_value)
            else:
                try:
                    delattr(obj, attr)
                except AttributeError:
                    pass

# Usage
def patched_method(self):
    return "Patched result!"

original_method = DatabaseConnection.connect

with MonkeyPatch() as mp:
    mp.patch(DatabaseConnection, 'connect', patched_method)

    db = DatabaseConnection("test")
    print(db.connect())  # "Patched result!"

# Outside context, original method is restored
db2 = DatabaseConnection("test")
print(db2.connect())  # "Connected to test"
```

### Practical Example: Testing with Monkey Patching

```python
import unittest.mock as mock

class PaymentService:
    def __init__(self):
        self.api_key = "secret"

    def process_payment(self, amount, card_number):
        # Simulate API call
        return {"status": "success", "transaction_id": "123"}

class OrderProcessor:
    def __init__(self):
        self.payment_service = PaymentService()

    def process_order(self, order):
        payment_result = self.payment_service.process_payment(
            order['amount'],
            order['card_number']
        )

        if payment_result['status'] == 'success':
            return {
                'order_id': order['id'],
                'status': 'processed',
                'transaction_id': payment_result['transaction_id']
            }
        else:
            raise ValueError("Payment failed")

# Testing with monkey patching
def test_order_processing():
    processor = OrderProcessor()

    # Mock the payment service method
    original_process = processor.payment_service.process_payment

    def mock_payment(amount, card_number):
        if amount > 1000:
            return {"status": "declined"}
        return {"status": "success", "transaction_id": "mock_123"}

    # Apply patch for testing
    processor.payment_service.process_payment = mock_payment

    try:
        # Test successful payment
        order = {'id': 'order_1', 'amount': 100, 'card_number': '4111...'}
        result = processor.process_order(order)
        assert result['status'] == 'processed'

        # Test failed payment
        order2 = {'id': 'order_2', 'amount': 1500, 'card_number': '4111...'}
        try:
            processor.process_order(order2)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

    finally:
        # Restore original method
        processor.payment_service.process_payment = original_process

# Run test
test_order_processing()
print("All tests passed!")
```

### Exercise 3: Safe Monkey Patching Utility

**Task:** Create a utility for safe monkey patching that can be used in testing.

**Requirements:**
1. Support patching methods, attributes, and class attributes
2. Automatic restoration after use
3. Context manager support
4. Support for multiple patches
5. Error handling for invalid patches

**Starter Code:**
```python
from contextlib import contextmanager
from typing import Any, Dict, List

class SafeMonkeyPatch:
    """Safe monkey patching utility."""

    def __init__(self):
        self._patches = []

    def patch(self, target: Any, attribute: str, new_value: Any):
        """Add a patch to be applied."""
        # TODO: Implement patch registration

    def apply(self):
        """Apply all patches."""
        # TODO: Implement patch application

    def restore(self):
        """Restore all original values."""
        # TODO: Implement restoration

    @contextmanager
    def patch_context(self):
        """Context manager for patches."""
        # TODO: Implement context manager

# TODO: Test the implementation
```

---

## The Descriptor Protocol

Descriptors are one of Python's most powerful and unique features. They are the mechanism behind properties, static methods, class methods, and `super()`. A descriptor is any object that defines at least one of the `__get__`, `__set__`, or `__delete__` methods.

By implementing the descriptor protocol, you can customize what happens when an attribute is accessed, assigned, or deleted.

### How Descriptors Work

-   `__get__(self, instance, owner)`: Called to get the attribute from the owner class (`owner`) or from an instance of that class (`instance`).
-   `__set__(self, instance, value)`: Called to set the attribute on an instance of the owner class to a new `value`.
-   `__delete__(self, instance)`: Called to delete the attribute from an instance of the owner class.

### Example: A Validation Descriptor

Let's create a descriptor that enforces type and value constraints on an attribute.

```python
class Validated:
    """A descriptor for validating attribute values."""

    def __init__(self, validator, doc="A validated attribute."):
        self.validator = validator
        self.__doc__ = doc
        self._name = '' # Will be set by __set_name__

    def __set_name__(self, owner, name):
        # In Python 3.6+, this is called to set the descriptor's name
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self # Accessing from the class, return the descriptor itself
        # Use a private name to store the value in the instance's __dict__
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        self.validator(value)
        instance.__dict__[self._name] = value

# --- Validator Functions ---
def is_positive_number(value):
    if not isinstance(value, (int, float)):
        raise TypeError("Must be a number.")
    if value <= 0:
        raise ValueError("Must be a positive number.")

def is_non_empty_string(value):
    if not isinstance(value, str):
        raise TypeError("Must be a string.")
    if not value.strip():
        raise ValueError("Must not be an empty string.")

# --- Class using the descriptor ---
class Product:
    """A product with validated attributes."""
    name = Validated(is_non_empty_string, "The name of the product.")
    price = Validated(is_positive_number, "The price of the product.")
    quantity = Validated(is_positive_number, "The available quantity.")

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

# --- Usage ---
try:
    # Valid usage
    product = Product("Laptop", 1200.50, 10)
    print(f"Created: {product.name}, Price: ${product.price}")

    # The descriptor intercepts the assignment and validates the value
    product.price = 1150.00
    print(f"New price: ${product.price}")

    # Invalid usage
    print("\nAttempting invalid assignments...")
    product.quantity = -5
except ValueError as e:
    print(f"Caught expected error: {e}")

try:
    product.name = ""
except ValueError as e:
    print(f"Caught expected error: {e}")

try:
    product.price = "free"
except TypeError as e:
    print(f"Caught expected error: {e}")
```

**Why use descriptors?**
-   **Reusable Logic:** The validation logic is encapsulated in the `Validated` class and can be reused for any attribute in any class.
-   **Clean Code:** The `Product` class remains clean and declarative. The validation rules are attached directly to the attribute definitions.
-   **Single Source of Truth:** The validation logic is defined in one place, making it easy to maintain and update.

---

## Advanced Metaclass Usage

Metaclasses are "classes of classes" - they control class creation and behavior. They're powerful but complex tools.

### Basic Metaclass

```python
class SingletonMeta(type):
    """Metaclass for singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connected = False

# Usage
db1 = DatabaseConnection("sqlite:///test.db")
db2 = DatabaseConnection("postgres://localhost/test")

print(db1 is db2)  # True - same instance!
print(db1.connection_string)  # "sqlite:///test.db" - first one wins
```

### Metaclass for Automatic Registration

```python
class PluginRegistry(type):
    """Metaclass that automatically registers plugin classes."""

    registry = {}

    def __new__(cls, name, bases, attrs):
        # Create the class
        new_class = super().__new__(cls, name, bases, attrs)

        # Register if it's a plugin (not the base class)
        if name != 'PluginBase':
            plugin_name = attrs.get('PLUGIN_NAME', name.lower())
            cls.registry[plugin_name] = new_class

        return new_class

class PluginBase(metaclass=PluginRegistry):
    """Base class for plugins."""

    @classmethod
    def get_plugin(cls, name):
        """Get a plugin by name."""
        return cls.registry.get(name)

class EmailPlugin(PluginBase):
    PLUGIN_NAME = 'email'

    def send(self, message):
        return f"Email: {message}"

class SMSPlugin(PluginBase):
    PLUGIN_NAME = 'sms'

    def send(self, message):
        return f"SMS: {message}"

# Usage
email_plugin = PluginBase.get_plugin('email')()
sms_plugin = PluginBase.get_plugin('sms')()

print(email_plugin.send("Hello"))  # "Email: Hello"
print(sms_plugin.send("Hello"))    # "SMS: Hello"

print("Available plugins:", list(PluginBase.registry.keys()))
```

### Metaclass for Validation

```python
class ValidatedMeta(type):
    """Metaclass that adds validation to class attributes."""

    def __new__(cls, name, bases, attrs):
        # Add validation to attributes
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_') and not callable(attr_value):
                # Create a validated property
                attrs[attr_name] = cls._create_validated_property(attr_name, attr_value)

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def _create_validated_property(name, default_value):
        """Create a property with validation."""
        def getter(self):
            return getattr(self, f'_{name}', default_value)

        def setter(self, value):
            # Basic validation
            if name == 'age' and (value < 0 or value > 150):
                raise ValueError(f"Invalid age: {value}")
            elif name == 'email' and '@' not in str(value):
                raise ValueError(f"Invalid email: {value}")
            setattr(self, f'_{name}', value)

        return property(getter, setter)

class Person(metaclass=ValidatedMeta):
    name = "Unknown"
    age = 0
    email = "unknown@example.com"

# Usage
person = Person()
person.name = "Alice"
person.age = 30
person.email = "alice@example.com"

print(f"Name: {person.name}")
print(f"Age: {person.age}")
print(f"Email: {person.email}")

# This will raise an error
try:
    person.age = 200
except ValueError as e:
    print(f"Validation error: {e}")
```

### Metaclass for API Generation

```python
class APIMeta(type):
    """Metaclass that generates API methods automatically."""

    def __new__(cls, name, bases, attrs):
        # Generate CRUD methods
        if 'MODEL' in attrs:
            model = attrs['MODEL']
            cls._generate_api_methods(attrs, model)

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def _generate_api_methods(attrs, model):
        """Generate API methods for the model."""

        def create_method(self, data):
            return f"Created {model}: {data}"

        def read_method(self, id):
            return f"Read {model} {id}"

        def update_method(self, id, data):
            return f"Updated {model} {id}: {data}"

        def delete_method(self, id):
            return f"Deleted {model} {id}"

        attrs['create'] = create_method
        attrs['read'] = read_method
        attrs['update'] = update_method
        attrs['delete'] = delete_method

class UserAPI(metaclass=APIMeta):
    MODEL = 'User'

class ProductAPI(metaclass=APIMeta):
    MODEL = 'Product'

# Usage
user_api = UserAPI()
product_api = ProductAPI()

print(user_api.create({'name': 'Alice'}))
print(user_api.read(123))
print(product_api.update(456, {'price': 29.99}))
```

### Exercise 4: Custom Metaclass

**Task:** Create a metaclass that automatically adds logging to all methods.

**Requirements:**
1. Log method entry and exit
2. Include method arguments and return values
3. Handle exceptions
4. Allow configuration of log levels

**Starter Code:**
```python
import logging
import functools
from typing import Any

class LoggingMeta(type):
    """Metaclass that adds logging to all methods."""

    def __new__(cls, name, bases, attrs):
        # TODO: Add logging to methods
        return super().__new__(cls, name, bases, attrs)

class LoggedClass(metaclass=LoggingMeta):
    """Example class with automatic logging."""

    def method1(self, arg1, arg2=None):
        return f"Result: {arg1} {arg2}"

    def method2(self):
        raise ValueError("Test error")

# TODO: Test the logging metaclass
```

---

## Protocol Buffers and Serialization

Protocol Buffers provide efficient serialization for structured data, often used in APIs and data storage.

### Basic Protocol Buffer Usage

```python
# user.proto (Protocol Buffer definition)
"""
syntax = "proto3";

message User {
    string name = 1;
    string email = 2;
    int32 age = 3;
    repeated string hobbies = 4;
}

message UserList {
    repeated User users = 1;
}
"""

# Python implementation
from typing import List, Dict, Any
import json

class ProtoUser:
    """Simulated Protocol Buffer User message."""

    def __init__(self, name: str = "", email: str = "", age: int = 0, hobbies: List[str] = None):
        self.name = name
        self.email = email
        self.age = age
        self.hobbies = hobbies or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (simulates proto serialization)."""
        return {
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'hobbies': self.hobbies
        }

    def to_bytes(self) -> bytes:
        """Serialize to bytes (simulates proto binary format)."""
        # In real protobuf, this would be much more efficient
        data = json.dumps(self.to_dict()).encode('utf-8')
        return data

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ProtoUser':
        """Deserialize from bytes."""
        dict_data = json.loads(data.decode('utf-8'))
        return cls(**dict_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtoUser':
        """Create from dictionary."""
        return cls(**data)

# Usage
user = ProtoUser(
    name="Alice",
    email="alice@example.com",
    age=30,
    hobbies=["reading", "coding"]
)

# Serialize
serialized = user.to_bytes()
print(f"Serialized size: {len(serialized)} bytes")

# Deserialize
user_copy = ProtoUser.from_bytes(serialized)
print(f"Deserialized: {user_copy.to_dict()}")
```

### Advanced Serialization with Custom Types

```python
from datetime import datetime
from typing import Any, Dict, Optional
import pickle  # For complex Python objects

class SerializableMixin:
    """Mixin for serializable objects."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        result = {}
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            value = getattr(self, attr)
            if callable(value):
                continue
            result[attr] = self._serialize_value(value)
        return result

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        else:
            return value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerializableMixin':
        """Create object from dictionary."""
        # Deserialize special types
        deserialized_data = {}
        for key, value in data.items():
            deserialized_data[key] = cls._deserialize_value(value)

        instance = cls.__new__(cls)
        for key, value in deserialized_data.items():
            setattr(instance, key, value)
        return instance

    @classmethod
    def _deserialize_value(cls, value: Any) -> Any:
        """Deserialize a single value."""
        if isinstance(value, str):
            # Try to parse as datetime
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass
        elif isinstance(value, list):
            return [cls._deserialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: cls._deserialize_value(v) for k, v in value.items()}
        return value

class User(SerializableMixin):
    def __init__(self, name: str, email: str, created_at: Optional[datetime] = None):
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now()

class Post(SerializableMixin):
    def __init__(self, title: str, content: str, author: User, tags: List[str] = None):
        self.title = title
        self.content = content
        self.author = author
        self.tags = tags or []
        self.created_at = datetime.now()

# Usage
user = User("Alice", "alice@example.com")
post = Post(
    title="Advanced OOP Tutorial",
    content="This is a comprehensive guide...",
    author=user,
    tags=["python", "oop", "tutorial"]
)

# Serialize the entire object graph
serialized = post.to_dict()
print("Serialized post:")
print(json.dumps(serialized, indent=2, default=str))

# Deserialize
post_copy = Post.from_dict(serialized)
print(f"Deserialized title: {post_copy.title}")
print(f"Author name: {post_copy.author.name}")
```

### Binary Serialization for Performance

```python
import struct
from typing import List

class BinarySerializer:
    """Efficient binary serialization."""

    @staticmethod
    def pack_user(user: ProtoUser) -> bytes:
        """Pack user data into binary format."""
        # Format: name_len(4) + name + email_len(4) + email + age(4) + hobbies_count(4) + hobbies
        name_bytes = user.name.encode('utf-8')
        email_bytes = user.email.encode('utf-8')

        # Pack header
        header = struct.pack('>III', len(name_bytes), len(email_bytes), user.age)

        # Pack hobbies
        hobbies_data = b''
        for hobby in user.hobbies:
            hobby_bytes = hobby.encode('utf-8')
            hobbies_data += struct.pack('>I', len(hobby_bytes)) + hobby_bytes

        return header + name_bytes + email_bytes + struct.pack('>I', len(user.hobbies)) + hobbies_data

    @staticmethod
    def unpack_user(data: bytes) -> ProtoUser:
        """Unpack user data from binary format."""
        # Unpack header
        header_size = 12  # 3 ints * 4 bytes
        name_len, email_len, age = struct.unpack('>III', data[:header_size])

        pos = header_size

        # Unpack name
        name = data[pos:pos + name_len].decode('utf-8')
        pos += name_len

        # Unpack email
        email = data[pos:pos + email_len].decode('utf-8')
        pos += email_len

        # Unpack hobbies count
        hobbies_count = struct.unpack('>I', data[pos:pos + 4])[0]
        pos += 4

        # Unpack hobbies
        hobbies = []
        for _ in range(hobbies_count):
            hobby_len = struct.unpack('>I', data[pos:pos + 4])[0]
            pos += 4
            hobby = data[pos:pos + hobby_len].decode('utf-8')
            pos += hobby_len
            hobbies.append(hobby)

        return ProtoUser(name=name, email=email, age=age, hobbies=hobbies)

# Performance comparison
user = ProtoUser("Alice", "alice@example.com", 30, ["reading", "coding", "hiking"])

# JSON serialization
json_data = json.dumps(user.to_dict())
json_size = len(json_data.encode('utf-8'))

# Binary serialization
binary_data = BinarySerializer.pack_user(user)
binary_size = len(binary_data)

print(f"JSON size: {json_size} bytes")
print(f"Binary size: {binary_size} bytes")
print(f"Space savings: {((json_size - binary_size) / json_size * 100):.1f}%")

# Verify round-trip
user_restored = BinarySerializer.unpack_user(binary_data)
print(f"Round-trip successful: {user_restored.to_dict() == user.to_dict()}")
```

### Exercise 5: Custom Serialization Framework

**Task:** Create a serialization framework that can handle complex object graphs.

**Requirements:**
1. Support for nested objects and circular references
2. Type preservation during serialization/deserialization
3. Efficient binary format
4. Error handling for unsupported types

**Starter Code:**
```python
from typing import Any, Dict, Set
import pickle

class AdvancedSerializer:
    """Advanced serialization framework."""

    def __init__(self):
        self._seen_objects = {}
        self._object_ids = {}

    def serialize(self, obj: Any) -> bytes:
        """Serialize an object to bytes."""
        # TODO: Implement serialization

    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to object."""
        # TODO: Implement deserialization

# TODO: Test with complex object graphs
```

---

## Performance Optimization

For a deep dive into performance optimization, including profiling, memory management, and advanced techniques, please refer to our dedicated guide:

**[Python Performance Optimization Guide](../python/performance_guide.md)**

This guide provides a comprehensive overview of the tools and strategies for making your Python code faster and more memory-efficient.

---

## Memory Management and Weak References

Weak references allow objects to be garbage collected even when referenced, preventing memory leaks.

### Basic Weak References

```python
import weakref
from typing import Optional

class CacheWithWeakRefs:
    """Cache that doesn't prevent garbage collection."""

    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get(self, key):
        """Get item from cache."""
        return self._cache.get(key)

    def put(self, key, value):
        """Put item in cache."""
        self._cache[key] = value

class ExpensiveObject:
    """Object that uses lots of memory."""

    def __init__(self, id: int):
        self.id = id
        self.data = list(range(10000))  # Simulate large data

    def __str__(self):
        return f"ExpensiveObject(id={self.id})"

# Usage
cache = CacheWithWeakRefs()

# Create objects
obj1 = ExpensiveObject(1)
obj2 = ExpensiveObject(2)

# Cache them
cache.put('obj1', obj1)
cache.put('obj2', obj2)

print("Objects cached")
print(f"obj1 in cache: {cache.get('obj1')}")
print(f"obj2 in cache: {cache.get('obj2')}")

# Delete references
del obj1

print("obj1 deleted")
print(f"obj1 in cache: {cache.get('obj1')}")  # May be None (garbage collected)
print(f"obj2 in cache: {cache.get('obj2')}")  # Still available
```

### Weak Reference Callbacks

```python
class ConnectionPool:
    """Connection pool with weak reference cleanup."""

    def __init__(self):
        self._connections = set()
        self._refs = []

    def add_connection(self, conn):
        """Add connection with weak reference."""
        self._connections.add(conn)

        # Create weak reference with callback
        ref = weakref.ref(conn, self._cleanup_connection)
        self._refs.append(ref)

    def _cleanup_connection(self, ref):
        """Called when connection is garbage collected."""
        print("Connection garbage collected, cleaning up")
        # Remove from our tracking
        self._refs.remove(ref)

    def get_stats(self):
        """Get pool statistics."""
        return {
            'active_connections': len(self._connections),
            'tracked_refs': len(self._refs)
        }

class DatabaseConnection:
    """Database connection that can be pooled."""

    def __init__(self, conn_string):
        self.conn_string = conn_string
        self.connected = True

    def close(self):
        """Close connection."""
        self.connected = False
        print(f"Connection {self.conn_string} closed")

# Usage
pool = ConnectionPool()

# Create connections
conn1 = DatabaseConnection("db1")
conn2 = DatabaseConnection("db2")

pool.add_connection(conn1)
pool.add_connection(conn2)

print("Pool stats:", pool.get_stats())

# Delete one connection
del conn1
print("After deleting conn1:", pool.get_stats())

# Force garbage collection
import gc
gc.collect()
print("After GC:", pool.get_stats())
```

### Preventing Memory Leaks with Weak References

```python
class EventSystem:
    """Event system that doesn't cause memory leaks."""

    def __init__(self):
        self._listeners = weakref.WeakSet()

    def add_listener(self, listener):
        """Add event listener with weak reference."""
        self._listeners.add(listener)

    def remove_listener(self, listener):
        """Remove event listener."""
        self._listeners.discard(listener)

    def notify(self, event):
        """Notify all listeners."""
        # Create a strong reference to prevent GC during iteration
        listeners = list(self._listeners)
        for listener in listeners:
            if hasattr(listener, 'on_event'):
                listener.on_event(event)

class UIComponent:
    """UI component that listens to events."""

    def __init__(self, name):
        self.name = name

    def on_event(self, event):
        """Handle event."""
        print(f"{self.name} received event: {event}")

# Usage
event_system = EventSystem()

# Create components
button = UIComponent("Button")
label = UIComponent("Label")

# Add as listeners
event_system.add_listener(button)
event_system.add_listener(label)

# Send event
event_system.notify("click")

# Components can be garbage collected without memory leaks
del button
event_system.notify("another_click")  # Only label receives it
```

### Weak Reference Proxies

```python
class DataItem:
    def __init__(self, value: str):
        self.value = value
    def __repr__(self):
        return f"DataItem({self.value!r})"

class DataProcessor:
    """Processor that holds weak references to data."""

    def __init__(self):
        self._data_refs = []

    def add_data(self, data: DataItem):
        """Add data with weak reference (must be weakref-able)."""
        ref = weakref.ref(data, self._cleanup_data)
        self._data_refs.append(ref)

    def _cleanup_data(self, ref):
        """Clean up when data is garbage collected."""
        self._data_refs.remove(ref)

    def process_all(self):
        """Process all available data."""
        results = []
        # Clean up dead references
        self._data_refs = [ref for ref in self._data_refs if ref() is not None]

        for ref in self._data_refs:
            data = ref()
            if data is not None:
                results.append(self._process_data(data))

        return results

    def _process_data(self, data: DataItem):
        """Process individual data item."""
        return f"Processed: {data.value}"

# Usage
processor = DataProcessor()

# Add some data (strings are not weakref-able; use a custom class)
data1 = DataItem("Important data 1")
data2 = DataItem("Important data 2")
processor.add_data(data1)
processor.add_data(data2)

print("Processing:", processor.process_all())

# Data can be garbage collected
del data1
print("After deleting data1:", processor.process_all())
```

### Exercise 7: Memory Management

**Task:** Implement a memory-efficient object cache using weak references.

**Requirements:**
1. Cache objects without preventing garbage collection
2. Automatic cleanup of dead references
3. Thread-safe operations
4. Performance monitoring

**Starter Code:**
```python
import weakref
from typing import Any, Dict
import threading

class WeakReferenceCache:
    """Memory-efficient cache using weak references."""

    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any:
        """Get item from cache."""
        # TODO: Implement thread-safe get

    def put(self, key: str, value: Any):
        """Put item in cache."""
        # TODO: Implement thread-safe put

    def clear(self):
        """Clear cache."""
        # TODO: Implement clear

    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        # TODO: Implement stats

# TODO: Test the weak reference cache
```

---

## Exercises and Practice

### Exercise Solutions

Here are solutions to the exercises above:

#### Exercise 1: Async Database Connection Pool

```python
import asyncio
from typing import Optional, List
import time

class AsyncDatabasePool:
    """Async database connection pool."""

    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.available_connections = asyncio.Queue()
        self.used_connections = set()
        self._closed = False

    async def initialize(self):
        """Initialize the connection pool."""
        for i in range(self.pool_size):
            conn = f"Connection-{i}"
            await self.available_connections.put(conn)

    async def get_connection(self) -> Optional[str]:
        """Get a connection from the pool."""
        if self._closed:
            return None

        try:
            conn = await asyncio.wait_for(
                self.available_connections.get(),
                timeout=5.0
            )
            self.used_connections.add(conn)
            return conn
        except asyncio.TimeoutError:
            return None

    async def release_connection(self, conn: str):
        """Release a connection back to the pool."""
        if conn in self.used_connections:
            self.used_connections.remove(conn)
            await self.available_connections.put(conn)

    async def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute query using a pooled connection."""
        conn = await self.get_connection()
        if not conn:
            raise RuntimeError("No available connections")

        try:
            # Simulate query execution
            await asyncio.sleep(0.01)
            result = f"Query result from {conn}: {query}"
            return result
        finally:
            await self.release_connection(conn)

    async def close(self):
        """Close the pool."""
        self._closed = True

async def demo_pool():
    pool = AsyncDatabasePool(3)
    await pool.initialize()

    # Execute multiple queries concurrently
    tasks = [
        pool.execute_query(f"SELECT * FROM table_{i}")
        for i in range(10)
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)

# asyncio.run(demo_pool())
```

#### Exercise 2: Multiple Inheritance Design

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time

class SearchableMixin:
    """Mixin for searchable content."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_index = {}

    def add_to_search_index(self, field: str, value: str):
        """Add field to search index."""
        if field not in self._search_index:
            self._search_index[field] = []
        self._search_index[field].append(value.lower())

    def search(self, query: str) -> bool:
        """Search content."""
        query = query.lower()
        for field_values in self._search_index.values():
            if any(query in value for value in field_values):
                return True
        return False

class VersionableMixin:
    """Mixin for version control."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._versions = []
        self._current_version = 0

    def save_version(self):
        """Save current state as new version."""
        version_data = self._get_version_data()
        self._versions.append(version_data)
        self._current_version = len(self._versions) - 1

    def _get_version_data(self) -> Dict[str, Any]:
        """Get current state for versioning."""
        # This would be overridden in subclasses
        return {}

    def restore_version(self, version: int):
        """Restore to specific version."""
        if 0 <= version < len(self._versions):
            version_data = self._versions[version]
            self._restore_from_version_data(version_data)
            self._current_version = version

    def _restore_from_version_data(self, data: Dict[str, Any]):
        """Restore state from version data."""
        # This would be overridden in subclasses
        pass

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get version history."""
        return self._versions.copy()

class PublishableMixin:
    """Mixin for publishable content."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._published = False
        self._publish_date = None

    def publish(self):
        """Publish the content."""
        self._published = True
        self._publish_date = time.time()

    def unpublish(self):
        """Unpublish the content."""
        self._published = False
        self._publish_date = None

    def is_published(self) -> bool:
        """Check if content is published."""
        return self._published

    def get_publish_date(self) -> float:
        """Get publish timestamp."""
        return self._publish_date

class Content(SearchableMixin, VersionableMixin, PublishableMixin):
    """Content class with multiple mixins."""

    def __init__(self, title: str, body: str, author: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.body = body
        self.author = author

        # Initialize search index
        self.add_to_search_index('title', title)
        self.add_to_search_index('body', body)
        self.add_to_search_index('author', author)

    def _get_version_data(self) -> Dict[str, Any]:
        """Get current state for versioning."""
        return {
            'title': self.title,
            'body': self.body,
            'author': self.author
        }

    def _restore_from_version_data(self, data: Dict[str, Any]):
        """Restore state from version data."""
        self.title = data['title']
        self.body = data['body']
        self.author = data['author']

# Test the implementation
content = Content(
    title="Advanced OOP Tutorial",
    body="This tutorial covers advanced concepts...",
    author="Tutorial Author"
)

# Test search
print("Search 'tutorial':", content.search("tutorial"))
print("Search 'python':", content.search("python"))

# Test versioning
content.save_version()
content.title = "Updated Tutorial"
content.save_version()

print("Version history length:", len(content.get_version_history()))

# Restore to first version
content.restore_version(0)
print("Restored title:", content.title)

# Test publishing
content.publish()
print("Is published:", content.is_published())
print("Publish date:", content.get_publish_date())
```

### Practice Projects

1. **Async Web Crawler**: Build a concurrent web crawler using async/await
2. **Plugin System**: Create a plugin architecture using metaclasses
3. **Memory-Efficient Cache**: Implement a cache with weak references
4. **ORM-like System**: Build a simple ORM using multiple inheritance
5. **Serialization Framework**: Create a custom serialization system

### Further Reading

- "Fluent Python" by Luciano Ramalho
- "Effective Python" by Brett Slatkin
- Python documentation on advanced features
- Design Patterns literature

Remember: These advanced concepts are powerful tools. Use them when they solve real problems, not just because they're advanced!
