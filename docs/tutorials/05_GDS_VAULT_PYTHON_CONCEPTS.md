# Python Concepts in gds_vault
## Complete Guide for Beginners

This tutorial covers ALL Python concepts used in the `gds_vault` package, explained from scratch with real examples from the code.

---

## Table of Contents

1. [Abstract Base Classes (ABC)](#abstract-base-classes)
2. [Multiple Inheritance](#multiple-inheritance)
3. [Properties and Descriptors](#properties-and-descriptors)
4. [Magic Methods](#magic-methods)
5. [Context Managers](#context-managers)
6. [Decorators](#decorators)
7. [Type Hints and Protocols](#type-hints-and-protocols)
8. [Composition Over Inheritance](#composition-over-inheritance)
9. [Strategy Pattern](#strategy-pattern)
10. [Exception Hierarchy](#exception-hierarchy)
11. [Class Methods and Static Methods](#class-methods-and-static-methods)
12. [Dataclasses](#dataclasses)
13. [Logging](#logging)
14. [Module Structure and Imports](#module-structure-and-imports)

---

## Abstract Base Classes (ABC)

### What Are They?

Abstract Base Classes (ABCs) are "contracts" that define what methods a class MUST implement. Think of them as blueprints.

### Real-World Analogy

Imagine a job posting that says: "To be a delivery driver, you MUST be able to:
- Load packages
- Navigate to addresses
- Deliver packages"

This is like an ABC - it doesn't say HOW to do these things, just that you MUST be able to do them.

### Basic Example

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    """Abstract base class for animals."""
    
    @abstractmethod
    def make_sound(self):
        """All animals must make a sound."""
        pass
    
    @abstractmethod
    def move(self):
        """All animals must be able to move."""
        pass

# This works
class Dog(Animal):
    def make_sound(self):
        return "Woof!"
    
    def move(self):
        return "Running on four legs"

# This FAILS - missing methods!
class Cat(Animal):
    def make_sound(self):
        return "Meow!"
    # ERROR: Forgot to implement move()!

# Usage
dog = Dog()
print(dog.make_sound())  # "Woof!"
print(dog.move())        # "Running on four legs"

cat = Cat()  # TypeError: Can't instantiate abstract class Cat
```

### In gds_vault: SecretProvider

```python
# From base.py
class SecretProvider(ABC):
    """
    Blueprint for ALL secret providers.
    
    Any class that provides secrets MUST implement these methods.
    """
    
    @abstractmethod
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """Every secret provider MUST be able to get a secret."""
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Every secret provider MUST be able to authenticate."""
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Every secret provider MUST know if it's authenticated."""
        pass
```

```python
# From client.py
class VaultClient(SecretProvider):
    """
    Concrete implementation of SecretProvider.
    MUST implement all abstract methods!
    """
    
    def get_secret(self, path: str, **kwargs) -> dict[str, Any]:
        """Implementation for Vault."""
        # Actually fetch from Vault
        ...
    
    def authenticate(self) -> bool:
        """Implementation for Vault."""
        # Actually authenticate with Vault
        ...
    
    def is_authenticated(self) -> bool:
        """Implementation for Vault."""
        # Check if we have a valid token
        return self._token is not None
```

### Why Use ABCs?

1. **Contract Enforcement**: Python ensures all methods are implemented
2. **Clear Documentation**: Shows exactly what's required
3. **IDE Support**: Autocomplete knows what methods exist
4. **Polymorphism**: Different implementations work the same way

```python
def fetch_secret(provider: SecretProvider, path: str):
    """
    Works with ANY SecretProvider!
    
    Could be VaultClient, ConsulClient, AWSSecretsClient, etc.
    As long as they implement SecretProvider, this works!
    """
    if not provider.is_authenticated():
        provider.authenticate()
    return provider.get_secret(path)

# Works with any implementation
vault_client = VaultClient()
consul_client = ConsulClient()
aws_client = AWSSecretsClient()

fetch_secret(vault_client, "secret/data/app1")    # Works!
fetch_secret(consul_client, "config/app1")        # Works!
fetch_secret(aws_client, "prod/app1/secrets")     # Works!
```

### Exercise

Create an abstract `Database` class with methods `connect()`, `query()`, and `close()`. Then create a concrete `PostgresDatabase` class that implements these methods.

<details>
<summary>Solution</summary>

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def query(self, sql: str):
        pass
    
    @abstractmethod
    def close(self):
        pass

class PostgresDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL...")
        self.connection = "postgres_connection"
    
    def query(self, sql: str):
        print(f"Executing: {sql}")
        return "result"
    
    def close(self):
        print("Closing PostgreSQL connection")
        self.connection = None

# Usage
db = PostgresDatabase()
db.connect()
result = db.query("SELECT * FROM users")
db.close()
```
</details>

---

## Multiple Inheritance

### What Is It?

A class can inherit from multiple parent classes, gaining features from all of them.

### Real-World Analogy

You inherit traits from both parents:
- From Mom: Eye color, height
- From Dad: Hair color, athletic ability

### Basic Example

```python
class Flyable:
    def fly(self):
        return "Flying through the air"

class Swimmable:
    def swim(self):
        return "Swimming in water"

class Duck(Flyable, Swimmable):
    """Duck can both fly and swim!"""
    pass

duck = Duck()
print(duck.fly())   # "Flying through the air"
print(duck.swim())  # "Swimming in water"
```

### In gds_vault: VaultClient

```python
# From client.py
class VaultClient(SecretProvider, ResourceManager, Configurable):
    """
    VaultClient inherits from THREE classes!
    
    Gets these methods from SecretProvider:
    - get_secret()
    - authenticate()
    - is_authenticated()
    
    Gets these methods from ResourceManager:
    - initialize()
    - cleanup()
    - __enter__()
    - __exit__()
    
    Gets these methods from Configurable:
    - get_config()
    - set_config()
    - get_all_config()
    """
    
    def __init__(self, ...):
        # Initialize all parent classes
        Configurable.__init__(self)
        ResourceManager.__init__(self)
        # SecretProvider has no __init__
```

### Why Use Multiple Inheritance?

1. **Mix Features**: Combine capabilities from different sources
2. **Code Reuse**: Don't rewrite common functionality
3. **Flexibility**: Pick and choose what you need

### Method Resolution Order (MRO)

When a method is called, Python searches for it in this order:

```python
class VaultClient(SecretProvider, ResourceManager, Configurable):
    pass

# Python searches in this order:
# 1. VaultClient itself
# 2. SecretProvider
# 3. ResourceManager
# 4. Configurable
# 5. Object (base of all classes)

print(VaultClient.__mro__)
# Output shows the order Python will search
```

### Exercise

Create a `SmartPhone` class that inherits from `Phone`, `Camera`, and `Computer` classes.

<details>
<summary>Solution</summary>

```python
class Phone:
    def make_call(self, number):
        return f"Calling {number}"

class Camera:
    def take_photo(self):
        return "📸 Photo taken"

class Computer:
    def browse_web(self, url):
        return f"Opening {url}"

class SmartPhone(Phone, Camera, Computer):
    def __init__(self, model):
        self.model = model

# Usage
iphone = SmartPhone("iPhone 15")
print(iphone.make_call("555-1234"))      # From Phone
print(iphone.take_photo())                # From Camera
print(iphone.browse_web("google.com"))   # From Computer
```
</details>

---

## Properties and Descriptors

### What Are Properties?

Properties make methods look like attributes. They provide controlled access to data.

### Real-World Analogy

Think of a thermostat:
- You see a simple number display (property)
- Behind the scenes, it's reading sensors and calculating (method)
- When you change it, it validates the value and adjusts the system (setter)

### Basic Example

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius  # Private attribute
    
    @property
    def celsius(self):
        """Get temperature in Celsius."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set temperature with validation."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get temperature in Fahrenheit (computed property)."""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set temperature using Fahrenheit."""
        self.celsius = (value - 32) * 5/9

# Usage
temp = Temperature(25)
print(temp.celsius)      # 25 (looks like attribute!)
print(temp.fahrenheit)   # 77.0 (computed on the fly!)

temp.celsius = 30        # Calls setter
temp.fahrenheit = 100    # Calls setter, converts to Celsius
temp.celsius = -300      # ValueError: Temperature below absolute zero!
```

### In gds_vault: VaultClient

```python
# From client.py
class VaultClient:
    def __init__(self, vault_addr, timeout=10):
        self._vault_addr = vault_addr  # Private
        self._timeout = timeout        # Private
        self._token = None            # Private
        self._token_expiry = None     # Private
    
    @property
    def vault_addr(self) -> str:
        """Get Vault address (read-only)."""
        return self._vault_addr
    
    @property
    def timeout(self) -> int:
        """Get timeout."""
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        """Set timeout with validation."""
        if value <= 0:
            raise ValueError("Timeout must be positive")
        self._timeout = value
        logger.debug("Timeout updated to %ds", value)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated (computed property)."""
        if not self._token:
            return False
        
        # Check if token expired
        if self._token_expiry and time.time() >= self._token_expiry:
            return False
        
        return True
    
    @property
    def cached_secret_count(self) -> int:
        """Number of cached secrets (computed property)."""
        return len(self._cache)

# Usage
client = VaultClient("https://vault.example.com")

# Read-only property
print(client.vault_addr)     # Works
client.vault_addr = "new"    # AttributeError: can't set attribute

# Property with setter
print(client.timeout)        # 10
client.timeout = 30          # Works, validates
client.timeout = -5          # ValueError: Timeout must be positive

# Computed property
print(client.is_authenticated)     # False (no token yet)
client.authenticate()
print(client.is_authenticated)     # True (has valid token)

# Another computed property
print(client.cached_secret_count)  # 0
client.get_secret("secret/data/app1")
print(client.cached_secret_count)  # 1
```

### Types of Properties

1. **Read-Only Property**: Only `@property`, no setter
   ```python
   @property
   def vault_addr(self):
       return self._vault_addr
   # Can read, can't write
   ```

2. **Read-Write Property**: Both `@property` and `@setter`
   ```python
   @property
   def timeout(self):
       return self._timeout
   
   @timeout.setter
   def timeout(self, value):
       if value <= 0:
           raise ValueError("Must be positive")
       self._timeout = value
   # Can read and write with validation
   ```

3. **Computed Property**: Calculated on demand
   ```python
   @property
   def is_authenticated(self):
       return self._token is not None and not self._is_expired()
   # No backing variable, computed each time
   ```

### Why Use Properties?

1. **Encapsulation**: Hide internal implementation
2. **Validation**: Check values before setting
3. **Computed Values**: Calculate on demand
4. **Backward Compatibility**: Can add logic without changing API
5. **Pythonic**: Looks like attribute access, acts like method call

### Exercise

Create a `BankAccount` class with a `balance` property that:
- Can be read anytime
- Can only be set to non-negative values
- Has a computed `formatted_balance` property that shows "$X.XX"

<details>
<summary>Solution</summary>

```python
class BankAccount:
    def __init__(self, initial_balance=0):
        self._balance = initial_balance
    
    @property
    def balance(self):
        """Get current balance."""
        return self._balance
    
    @balance.setter
    def balance(self, value):
        """Set balance with validation."""
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value
    
    @property
    def formatted_balance(self):
        """Get formatted balance string."""
        return f"${self._balance:.2f}"

# Usage
account = BankAccount(100)
print(account.balance)            # 100
print(account.formatted_balance)  # "$100.00"

account.balance = 250.50
print(account.formatted_balance)  # "$250.50"

account.balance = -50  # ValueError: Balance cannot be negative
```
</details>

---

## Magic Methods

### What Are They?

Magic methods (also called dunder methods) are special methods with double underscores that Python calls automatically in certain situations.

### Common Magic Methods

```python
class MyClass:
    def __init__(self):        # Constructor
    def __str__(self):         # str(obj) and print(obj)
    def __repr__(self):        # repr(obj) and debugger display
    def __len__(self):         # len(obj)
    def __getitem__(self, key): # obj[key]
    def __setitem__(self, key, value): # obj[key] = value
    def __contains__(self, item): # item in obj
    def __enter__(self):       # with obj:
    def __exit__(self):        # End of with block
    def __eq__(self, other):   # obj == other
    def __lt__(self, other):   # obj < other
    def __add__(self, other):  # obj + other
    def __call__(self):        # obj()
```

### Example: Making a Custom List

```python
class ShoppingCart:
    def __init__(self):
        self._items = []
    
    def __len__(self):
        """len(cart) returns number of items."""
        return len(self._items)
    
    def __getitem__(self, index):
        """cart[0] returns first item."""
        return self._items[index]
    
    def __setitem__(self, index, value):
        """cart[0] = 'apple' sets first item."""
        self._items[index] = value
    
    def __contains__(self, item):
        """'apple' in cart checks if item exists."""
        return item in self._items
    
    def __str__(self):
        """print(cart) shows user-friendly representation."""
        return f"Shopping cart with {len(self)} items"
    
    def __repr__(self):
        """repr(cart) shows developer-friendly representation."""
        return f"ShoppingCart({self._items!r})"
    
    def add(self, item):
        """Add item to cart."""
        self._items.append(item)

# Usage
cart = ShoppingCart()
cart.add("apple")
cart.add("banana")
cart.add("orange")

print(len(cart))           # 3 (calls __len__)
print(cart[0])             # "apple" (calls __getitem__)
cart[0] = "grape"          # Changes first item (calls __setitem__)
print("grape" in cart)     # True (calls __contains__)
print(cart)                # "Shopping cart with 3 items" (calls __str__)
print(repr(cart))          # "ShoppingCart(['grape', 'banana', 'orange'])"
```

### In gds_vault: VaultClient

```python
# From client.py
class VaultClient:
    def __init__(self, vault_addr=None, auth=None, ...):
        """
        Constructor - called when creating instance.
        VaultClient() calls this automatically.
        """
        self._vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self._auth = auth or AppRoleAuth()
        ...
    
    def __enter__(self):
        """
        Context manager entry - called by 'with' statement.
        
        with VaultClient() as client:  # __enter__ called here
            ...
        """
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - called at end of 'with' block.
        
        with VaultClient() as client:
            ...
        # __exit__ called here (even if exception!)
        """
        self.cleanup()
        return False
    
    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        Used in debugger and logging.
        """
        return (
            f"VaultClient(vault_addr='{self._vault_addr}', "
            f"authenticated={self.is_authenticated})"
        )
    
    def __str__(self) -> str:
        """
        User-friendly representation.
        Used in print() and str().
        """
        status = "authenticated" if self.is_authenticated else "not authenticated"
        return f"Vault client at {self._vault_addr} ({status})"
    
    def __len__(self) -> int:
        """
        Return number of cached secrets.
        len(client) returns this.
        """
        return len(self._cache)
    
    def __bool__(self) -> bool:
        """
        Truth value - is client ready to use?
        if client: ... checks this.
        """
        return self.is_authenticated

# Usage
client = VaultClient("https://vault.example.com")

# __str__ in action
print(client)
# "Vault client at https://vault.example.com (not authenticated)"

# __repr__ in action
print(repr(client))
# "VaultClient(vault_addr='https://vault.example.com', authenticated=False)"

# __bool__ in action
if client:
    print("Client ready")  # Doesn't print (not authenticated)
else:
    print("Client not ready")  # Prints this

# __len__ in action
client.authenticate()
client.get_secret("secret/data/app1")
print(len(client))  # 1 (one cached secret)

# __enter__ and __exit__ in action
with VaultClient() as client:
    secret = client.get_secret("secret/data/app1")
    # __enter__ called automatically
    # Client initialized
    # Use the client
# __exit__ called automatically
# Client cleaned up
```

### In gds_vault: Cache Classes

```python
# From cache.py
class SecretCache:
    def __init__(self, max_size=100):
        self._cache = {}
        self.max_size = max_size
    
    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Check if key is in cache."""
        return key in self._cache
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"SecretCache(size={len(self)}, max_size={self.max_size})"
    
    def __str__(self) -> str:
        """User representation."""
        return f"Cache with {len(self)} secrets (max: {self.max_size})"

# Usage
cache = SecretCache(max_size=50)
cache.set("key1", {"password": "secret"})
cache.set("key2", {"api_key": "abc123"})

print(len(cache))           # 2
print("key1" in cache)      # True
print("key3" in cache)      # False
print(cache)                # "Cache with 2 secrets (max: 50)"
print(repr(cache))          # "SecretCache(size=2, max_size=50)"
```

### In gds_vault: Auth Classes

```python
# From auth.py
class AppRoleAuth:
    def __init__(self, role_id, secret_id):
        self.role_id = role_id
        self.secret_id = secret_id
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        role_id_masked = f"{self.role_id[:8]}..." if self.role_id else "None"
        return f"AppRoleAuth(role_id='{role_id_masked}')"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        return "AppRole Authentication"

# Usage
auth = AppRoleAuth("my-role-id-12345", "my-secret-id-67890")
print(auth)          # "AppRole Authentication"
print(repr(auth))    # "AppRoleAuth(role_id='my-role-...')"
```

### Exercise

Create a `Library` class that:
- Uses `__len__` to return number of books
- Uses `__getitem__` to access books by index
- Uses `__contains__` to check if a book is in the library
- Uses `__str__` for user-friendly display

<details>
<summary>Solution</summary>

```python
class Library:
    def __init__(self):
        self._books = []
    
    def add_book(self, title):
        self._books.append(title)
    
    def __len__(self):
        return len(self._books)
    
    def __getitem__(self, index):
        return self._books[index]
    
    def __contains__(self, title):
        return title in self._books
    
    def __str__(self):
        return f"Library with {len(self)} books"
    
    def __repr__(self):
        return f"Library({self._books!r})"

# Usage
library = Library()
library.add_book("Python Basics")
library.add_book("Advanced Python")

print(len(library))                    # 2
print(library[0])                      # "Python Basics"
print("Python Basics" in library)      # True
print("Java Basics" in library)        # False
print(library)                         # "Library with 2 books"
```
</details>

---

## Context Managers

### What Are They?

Context managers ensure resources are properly cleaned up, even if errors occur. They use the `with` statement.

### Real-World Analogy

Borrowing a car:
1. **Enter**: Get the keys, adjust seat, check fuel
2. **Use**: Drive where you need to go
3. **Exit**: Return keys, log mileage, lock doors

Even if you have an accident (exception), you MUST return the car!

### Basic Example: File Handling

```python
# Without context manager (manual cleanup)
file = open("data.txt")
try:
    data = file.read()
    process(data)
finally:
    file.close()  # Must remember!

# With context manager (automatic cleanup)
with open("data.txt") as file:
    data = file.read()
    process(data)
# File automatically closed!
```

### Creating Your Own Context Manager

Method 1: Using `__enter__` and `__exit__` magic methods

```python
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """Setup - open connection."""
        print(f"Opening connection to {self.db_name}")
        self.connection = f"connected_to_{self.db_name}"
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup - close connection."""
        print(f"Closing connection to {self.db_name}")
        self.connection = None
        
        if exc_type:
            print(f"An error occurred: {exc_val}")
        
        return False  # Don't suppress exceptions
    
    def query(self, sql):
        if not self.connection:
            raise RuntimeError("Not connected")
        return f"Results from: {sql}"

# Usage
with DatabaseConnection("mydb") as db:
    result = db.query("SELECT * FROM users")
    print(result)
# Connection automatically closed!

# Output:
# Opening connection to mydb
# Results from: SELECT * FROM users
# Closing connection to mydb
```

Method 2: Using `@contextmanager` decorator

```python
from contextlib import contextmanager

@contextmanager
def database_connection(db_name):
    """Context manager using decorator."""
    # Setup (before yield)
    print(f"Opening connection to {db_name}")
    connection = f"connected_to_{db_name}"
    
    try:
        yield connection  # Give control back to caller
    finally:
        # Cleanup (after yield)
        print(f"Closing connection to {db_name}")

# Usage
with database_connection("mydb") as conn:
    print(f"Using {conn}")
# Automatically cleaned up!
```

### In gds_vault: VaultClient

```python
# From client.py
class VaultClient(ResourceManager):
    def __init__(self, ...):
        self._initialized = False
        ...
    
    def initialize(self) -> None:
        """Initialize resources."""
        if self._initialized:
            return
        
        logger.debug("Initializing VaultClient")
        
        # Authenticate if needed
        if not self.is_authenticated:
            self.authenticate()
        
        self._initialized = True
        logger.debug("VaultClient initialized")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        logger.debug("Cleaning up VaultClient")
        
        # Clear cached secrets
        self._cache.clear()
        
        # Clear sensitive data
        self._token = None
        self._token_expiry = None
        
        self._initialized = False
        logger.debug("VaultClient cleanup complete")
    
    def __enter__(self):
        """Context manager entry."""
        logger.debug("Entering VaultClient context manager")
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        logger.debug("Exiting VaultClient context manager")
        
        if exc_type:
            logger.error("Exception in VaultClient context: %s", exc_val)
        
        self.cleanup()
        return False  # Don't suppress exceptions

# Usage 1: Manual management
client = VaultClient()
try:
    client.initialize()
    secret = client.get_secret("secret/data/app1")
finally:
    client.cleanup()

# Usage 2: Context manager (better!)
with VaultClient() as client:
    secret = client.get_secret("secret/data/app1")
    # Use the secret
# Automatically cleaned up!

# Usage 3: Multiple operations
with VaultClient() as client:
    db_secret = client.get_secret("secret/data/database")
    api_secret = client.get_secret("secret/data/api")
    email_secret = client.get_secret("secret/data/email")
    # All secrets fetched
# Cleanup happens once at the end
```

### Why Use Context Managers?

1. **Automatic Cleanup**: Resources cleaned up even if exception occurs
2. **Clear Boundaries**: Setup and teardown are explicit
3. **No Resource Leaks**: Can't forget to cleanup
4. **Cleaner Code**: No nested try/finally blocks
5. **Pythonic**: Standard Python pattern

### Real Example: Temporary Configuration

```python
class TemporaryConfig:
    """Temporarily change configuration."""
    
    def __init__(self, client, **temp_config):
        self.client = client
        self.temp_config = temp_config
        self.old_config = {}
    
    def __enter__(self):
        # Save current config
        for key in self.temp_config:
            self.old_config[key] = self.client.get_config(key)
        
        # Apply temporary config
        for key, value in self.temp_config.items():
            self.client.set_config(key, value)
        
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old config
        for key, value in self.old_config.items():
            self.client.set_config(key, value)
        
        return False

# Usage
client = VaultClient()
client.set_config("timeout", 10)

print(client.get_config("timeout"))  # 10

with TemporaryConfig(client, timeout=30):
    print(client.get_config("timeout"))  # 30 (temporary)
    # Do something with increased timeout
# Config automatically restored

print(client.get_config("timeout"))  # 10 (restored!)
```

### Exercise

Create a `Timer` context manager that:
- Records start time on entry
- Records end time on exit
- Prints elapsed time

<details>
<summary>Solution</summary>

```python
import time

class Timer:
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        print(f"{self.name} starting...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        print(f"{self.name} took {elapsed:.2f} seconds")
        return False

# Usage
with Timer("Data processing"):
    # Simulate work
    time.sleep(2)

# Output:
# Data processing starting...
# Data processing took 2.00 seconds
```
</details>

---

(Continued in next section...)

## Decorators

### What Are They?

Decorators are functions that modify or enhance other functions. They "wrap" a function to add behavior before/after it runs.

### Real-World Analogy

Think of gift wrapping:
- You have a gift (function)
- You wrap it in paper (decorator)
- The gift is still inside, but now it's prettier and has extra features

### Basic Example

```python
def uppercase_decorator(func):
    """Decorator that makes function return uppercase."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)  # Call original function
        return result.upper()            # Modify result
    return wrapper

# Apply decorator manually
def greet(name):
    return f"Hello, {name}"

greet = uppercase_decorator(greet)
print(greet("Alice"))  # "HELLO, ALICE"

# Apply decorator with @ syntax (same thing!)
@uppercase_decorator
def greet(name):
    return f"Hello, {name}"

print(greet("Bob"))  # "HELLO, BOB"
```

### In gds_vault: @property

The `@property` decorator we saw earlier is Python's built-in decorator!

```python
class VaultClient:
    @property
    def vault_addr(self):
        return self._vault_addr
    
    # This is equivalent to:
    # vault_addr = property(vault_addr)
```

### In gds_vault: @abstractmethod

```python
from abc import ABC, abstractmethod

class SecretProvider(ABC):
    @abstractmethod
    def get_secret(self, path: str):
        pass
    
    # Marks this method as "must be implemented by subclasses"
```

### In gds_vault: @dataclass

```python
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """Automatically generates __init__, __repr__, __eq__, etc."""
    key: str
    value: dict
    timestamp: float
    ttl: int = 3600
```

### Custom Decorator Example: Logging

```python
import logging
from functools import wraps

def log_calls(func):
    """Decorator that logs function calls."""
    @wraps(func)  # Preserves original function's metadata
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"{func.__name__} succeeded")
            return result
        except Exception as e:
            logging.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper

@log_calls
def get_secret(path):
    print(f"Fetching secret from {path}")
    return {"password": "secret123"}

# Usage
secret = get_secret("secret/data/app1")
# Logs: "Calling get_secret"
# Prints: "Fetching secret from secret/data/app1"
# Logs: "get_secret succeeded"
```

(Due to length constraints, I'll create a separate file for the remaining concepts and exercises)

