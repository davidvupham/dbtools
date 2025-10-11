# Complete Object-Oriented Programming Guide for Python
## From Basics to Best Practices

Welcome to the comprehensive guide to Object-Oriented Programming (OOP) in Python! This guide will take you from the fundamentals to advanced concepts and best practices used in professional software development.

---

## Table of Contents

1. [Introduction to OOP](#introduction-to-oop)
2. [Classes and Objects](#classes-and-objects)
3. [Understanding `self`](#understanding-self)
4. [Encapsulation and Data Hiding](#encapsulation-and-data-hiding)
5. [Inheritance](#inheritance)
6. [Polymorphism](#polymorphism)
7. [Abstract Base Classes](#abstract-base-classes)
8. [SOLID Principles](#solid-principles)
9. [Composition vs Inheritance](#composition-vs-inheritance)
10. [Design Patterns](#design-patterns)
11. [Advanced OOP Concepts](#advanced-oop-concepts)
12. [Modern Python OOP Features](#modern-python-oop-features)
13. [Best Practices Summary](#best-practices-summary)
14. [Performance Considerations](#performance-considerations)
15. [Error Handling in OOP](#error-handling-in-oop)
16. [Testing OOP Code](#testing-oop-code)
17. [Real-World Examples from Our Codebase](#real-world-examples-from-our-codebase)
18. [What's Missing?](#whats-missing)

---

## Introduction to OOP

### What is Object-Oriented Programming?

**Object-Oriented Programming (OOP)** is a programming paradigm that organizes code into "objects" that contain both data (attributes) and functions (methods). Think of it like creating blueprints (classes) and then building things (objects) from those blueprints.

### Real-World Analogy

Imagine a **Car** blueprint:
- **Data (Attributes)**: color, brand, speed, fuel_level
- **Actions (Methods)**: start(), stop(), accelerate(), brake()

From one blueprint, you can create many cars:
```python
my_car = Car(color="red", brand="Toyota")
your_car = Car(color="blue", brand="Honda")
```

### Why Use OOP?

1. **Modularity**: Code is organized into self-contained objects
2. **Reusability**: Classes can be reused and extended
3. **Maintainability**: Changes to one class don't affect others
4. **Abstraction**: Hide complex implementation details
5. **Real-world modeling**: Naturally represents real-world entities

---

## Classes and Objects

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

### Class vs Instance Variables

```python
class Dog:
    # Class variable - shared by ALL dogs
    species = "Canis lupus"
    total_dogs = 0
    
    def __init__(self, name, age):
        # Instance variables - unique to each dog
        self.name = name
        self.age = age
        
        # Update class variable
        Dog.total_dogs += 1
    
    @classmethod
    def get_total_dogs(cls):
        """Class method to access class variables."""
        return cls.total_dogs
    
    @staticmethod
    def is_good_boy():
        """Static method - doesn't need class or instance."""
        return True

# Usage
dog1 = Dog("Buddy", 5)
dog2 = Dog("Max", 3)

print(Dog.species)        # "Canis lupus" (class variable)
print(dog1.species)       # "Canis lupus" (accessed through instance)
print(Dog.get_total_dogs())  # 2
print(Dog.is_good_boy())  # True
```

### Example from Our Codebase

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

---

## Understanding `self`

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

---

## Encapsulation and Data Hiding

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
    
    def _internal_audit(self):
        """Private method for internal use."""
        print("Performing internal audit...")

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

### Property Decorators - Pythonic Getters and Setters

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Get temperature in Celsius."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set temperature in Celsius with validation."""
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get temperature in Fahrenheit."""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set temperature using Fahrenheit."""
        self.celsius = (value - 32) * 5/9

# Usage - looks like simple attribute access!
temp = Temperature()
temp.celsius = 25      # Uses setter with validation
print(temp.celsius)    # 25 (uses getter)
print(temp.fahrenheit) # 77.0 (calculated property)

temp.fahrenheit = 100  # Uses Fahrenheit setter
print(temp.celsius)    # 37.77... (converted)
```

**Example from Our Code** (`connection.py`):
```python
class SnowflakeConnection:
    def __init__(self, account: str):
        self.account = account          # Public - users need this
        self.connection = None          # Public - users might need this
        self._initialized = False       # Private - internal state
    
    @property
    def is_initialized(self) -> bool:
        """Public property to check private state."""
        return self._initialized
    
    @property
    def connection_info(self) -> Dict[str, Any]:
        """Get connection information as a property."""
        return {
            'account': self.account,
            'user': self.user,
            'connected': self.is_connected()
        }
```

**Why this design?**
- Public attributes (`account`, `connection`) are part of the API
- Private attributes (`_initialized`) are implementation details
- Properties provide controlled access to internal state
- Can add validation or computation without changing the interface

---

## Inheritance

### What is Inheritance?

Inheritance lets you create a new class based on an existing class. The new class gets all the features of the original, plus you can add more or change things.

### Simple Inheritance Example

```python
# Base class (parent)
class Animal:
    """Base class for all animals."""
    
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.energy = 100
    
    def speak(self):
        """Make a sound."""
        return "Some sound"
    
    def move(self):
        """Move around."""
        self.energy -= 10
        return f"{self.name} is moving"
    
    def rest(self):
        """Rest to regain energy."""
        self.energy = min(100, self.energy + 20)
        return f"{self.name} is resting"

# Derived class (child) inherits from Animal
class Dog(Animal):
    """Dog is a type of Animal."""
    
    def __init__(self, name, breed):
        # Call parent constructor
        super().__init__(name, "Canis lupus")
        self.breed = breed
    
    def speak(self):
        """Override speak method."""
        return f"{self.name} says Woof!"
    
    def fetch(self):
        """New method specific to dogs."""
        self.energy -= 15
        return f"{self.name} is fetching the ball"

class Cat(Animal):
    """Cat is a type of Animal."""
    
    def __init__(self, name):
        super().__init__(name, "Felis catus")
        self.lives = 9
    
    def speak(self):
        """Override speak method."""
        return f"{self.name} says Meow!"
    
    def climb(self):
        """New method specific to cats."""
        self.energy -= 5
        return f"{self.name} is climbing a tree"

# Create instances
dog = Dog("Buddy", "Golden Retriever")
cat = Cat("Whiskers")

# Inherited methods (same for both)
print(dog.move())   # "Buddy is moving"
print(cat.move())   # "Whiskers is moving"

# Overridden methods (different for each)
print(dog.speak())  # "Buddy says Woof!"
print(cat.speak())  # "Whiskers says Meow!"

# Specific methods
print(dog.fetch())  # "Buddy is fetching the ball"
print(cat.climb())  # "Whiskers is climbing a tree"

# Check energy levels
print(f"Dog energy: {dog.energy}")  # Energy reduced from activities
print(f"Cat energy: {cat.energy}")
```

**Key Concepts:**
- `Dog(Animal)` means Dog inherits from Animal
- `super().__init__()` calls the parent's constructor
- Dog gets all of Animal's methods automatically
- Dog can override methods (like `speak()`)
- Dog can add new methods (like `fetch()`)

### Multiple Inheritance and Mixins

Python supports multiple inheritance, but use it carefully:

```python
class Flyable:
    """Mixin for things that can fly."""
    def fly(self):
        self.energy -= 20
        return f"{self.name} is flying"

class Swimmable:
    """Mixin for things that can swim."""
    def swim(self):
        self.energy -= 15
        return f"{self.name} is swimming"

class Duck(Animal, Flyable, Swimmable):
    """Duck can do everything!"""
    
    def __init__(self, name):
        super().__init__(name, "Anas platyrhynchos")
    
    def speak(self):
        return f"{self.name} says Quack!"

duck = Duck("Donald")
print(duck.speak())  # From Animal (overridden)
print(duck.move())   # From Animal
print(duck.fly())    # From Flyable
print(duck.swim())   # From Swimmable
```

### Method Resolution Order (MRO)

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")
        super().method()

class C(A):
    def method(self):
        print("C")
        super().method()

class D(B, C):
    def method(self):
        print("D")
        super().method()

# Check the method resolution order
print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)

d = D()
d.method()
# Output:
# D
# B
# C
# A
```

**Key Points:**
- MRO determines which method gets called in multiple inheritance
- Use `super()` to follow the MRO chain
- You can check MRO with `ClassName.__mro__`

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

---

## Polymorphism

Polymorphism means "many forms" - different classes can be used interchangeably if they have the same interface:

```python
def make_animal_speak(animal):
    """Works with any animal that has a speak() method."""
    print(animal.speak())

def exercise_animals(animals):
    """Exercise a list of animals."""
    for animal in animals:
        print(animal.move())
        print(animal.speak())
        if hasattr(animal, 'fetch'):  # Duck typing
            print(animal.fetch())

# Create different animals
dog = Dog("Buddy", "Labrador")
cat = Cat("Whiskers")
duck = Duck("Donald")

# All work with the same functions!
make_animal_speak(dog)   # "Buddy says Woof!"
make_animal_speak(cat)   # "Whiskers says Meow!"
make_animal_speak(duck)  # "Donald says Quack!"

# Can also use in loops
animals = [dog, cat, duck]
exercise_animals(animals)  # Each behaves differently!
```

### Duck Typing

Python uses "duck typing" - if it walks like a duck and quacks like a duck, it's a duck:

```python
class RobotDog:
    """Doesn't inherit from Animal, but has same interface."""
    
    def __init__(self, model):
        self.name = f"RobotDog-{model}"
        self.battery = 100
    
    def speak(self):
        return f"{self.name} says *BEEP*"
    
    def move(self):
        self.battery -= 5
        return f"{self.name} is rolling"

robot = RobotDog("X1")

# Works with our polymorphic functions!
make_animal_speak(robot)  # "RobotDog-X1 says *BEEP*"

# Can include in animal list
all_creatures = [dog, cat, duck, robot]
for creature in all_creatures:
    print(creature.speak())  # All have speak() method!
```

### Example from Our Code

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

### Advanced ABC Example

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class Shape(ABC):
    """Abstract base class for all shapes."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape."""
        pass
    
    # Concrete method that uses abstract methods
    def describe(self) -> str:
        """Describe the shape."""
        return f"{self.name}: Area = {self.area():.2f}, Perimeter = {self.perimeter():.2f}"
    
    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> 'Shape':
        """Create shape from string representation."""
        pass

class Rectangle(Shape):
    """Concrete implementation of Shape."""
    
    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)
    
    @classmethod
    def from_string(cls, data: str) -> 'Rectangle':
        # Parse "5x3" format
        width, height = map(float, data.split('x'))
        return cls(width, height)

class Circle(Shape):
    """Another concrete implementation."""
    
    def __init__(self, radius: float):
        super().__init__("Circle")
        self.radius = radius
    
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
    
    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius
    
    @classmethod
    def from_string(cls, data: str) -> 'Circle':
        # Parse "r5" format
        radius = float(data[1:])
        return cls(radius)

# Usage
shapes = [
    Rectangle(5, 3),
    Circle(2),
    Rectangle.from_string("4x6"),
    Circle.from_string("r3")
]

for shape in shapes:
    print(shape.describe())
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

### Benefits of ABCs

1. **Enforces Interface**: Can't forget required methods
2. **Documentation**: Clear what a class should do
3. **Polymorphism**: All implementations can be used interchangeably
4. **Early Error Detection**: Errors at class creation, not runtime
5. **Code Organization**: Separates interface from implementation

---

## SOLID Principles

The SOLID principles are five fundamental design principles that make software designs more understandable, flexible, and maintainable.

### 1. Single Responsibility Principle (SRP)

**A class should have only one reason to change.**

```python
# BAD: Multiple responsibilities
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        # Database logic
        pass
    
    def send_email(self):
        # Email logic
        pass
    
    def generate_report(self):
        # Report logic
        pass

# GOOD: Single responsibility per class
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user: User):
        # Database logic
        pass

class EmailService:
    def send_email(self, user: User, message: str):
        # Email logic
        pass

class ReportGenerator:
    def generate_user_report(self, user: User):
        # Report logic
        pass
```

### 2. Open/Closed Principle (OCP)

**Classes should be open for extension but closed for modification.**

```python
# BAD: Need to modify existing code for new payment types
class PaymentProcessor:
    def process_payment(self, payment_type, amount):
        if payment_type == "credit_card":
            # Process credit card
            pass
        elif payment_type == "paypal":
            # Process PayPal
            pass
        # Adding new payment type requires modifying this method!

# GOOD: Use inheritance/polymorphism
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Credit card logic
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # PayPal logic
        return True

# Easy to add new payment methods without changing existing code
class BitcoinProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Bitcoin logic
        return True
```

### 3. Liskov Substitution Principle (LSP)

**Objects of a superclass should be replaceable with objects of its subclasses without breaking functionality.**

```python
# BAD: Violates LSP
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Breaks the contract!

# GOOD: Proper hierarchy
class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return "Flying"
    
    def fly(self):
        return "Flying high"

class FlightlessBird(Bird):
    def move(self):
        return "Walking"

class Eagle(FlyingBird):
    pass

class Penguin(FlightlessBird):
    def swim(self):
        return "Swimming"
```

### 4. Interface Segregation Principle (ISP)

**Clients should not be forced to depend on interfaces they don't use.**

```python
# BAD: Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass
    
    @abstractmethod
    def eat(self):
        pass
    
    @abstractmethod
    def sleep(self):
        pass

class Robot(Worker):
    def work(self):
        return "Working"
    
    def eat(self):
        raise NotImplementedError("Robots don't eat!")  # Forced to implement!
    
    def sleep(self):
        raise NotImplementedError("Robots don't sleep!")  # Forced to implement!

# GOOD: Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self):
        return "Working"
    
    def eat(self):
        return "Eating"
    
    def sleep(self):
        return "Sleeping"

class Robot(Workable):  # Only implements what it needs
    def work(self):
        return "Working"
```

### 5. Dependency Inversion Principle (DIP)

**High-level modules should not depend on low-level modules. Both should depend on abstractions.**

```python
# BAD: High-level depends on low-level
class MySQLDatabase:
    def save(self, data):
        # MySQL specific code
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Directly depends on MySQL!
    
    def create_user(self, user_data):
        self.db.save(user_data)

# GOOD: Both depend on abstraction
class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        # MySQL specific code
        pass

class PostgreSQLDatabase(Database):
    def save(self, data):
        # PostgreSQL specific code
        pass

class UserService:
    def __init__(self, database: Database):  # Depends on abstraction
        self.db = database
    
    def create_user(self, user_data):
        self.db.save(user_data)

# Usage - can switch databases easily
mysql_db = MySQLDatabase()
postgres_db = PostgreSQLDatabase()

user_service1 = UserService(mysql_db)
user_service2 = UserService(postgres_db)
```

---

## Composition vs Inheritance

### When to Use Inheritance vs Composition

**Use Inheritance when:**
- There's a clear "is-a" relationship
- You want to extend existing functionality
- The relationship is stable and won't change

**Use Composition when:**
- There's a "has-a" relationship
- You need more flexibility
- You want to combine multiple behaviors

### Composition Example

```python
# Composition: Car "has-a" engine, not "is-a" engine
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False
    
    def start(self):
        self.running = True
        return "Engine started"
    
    def stop(self):
        self.running = False
        return "Engine stopped"

class GPS:
    def __init__(self):
        self.current_location = "Unknown"
    
    def navigate_to(self, destination):
        return f"Navigating to {destination}"

class Car:
    def __init__(self, make, model, engine_hp):
        self.make = make
        self.model = model
        self.engine = Engine(engine_hp)  # Composition
        self.gps = GPS()                 # Composition
        self.speed = 0
    
    def start(self):
        return self.engine.start()
    
    def accelerate(self):
        if self.engine.running:
            self.speed += 10
            return f"Accelerating to {self.speed} mph"
        return "Can't accelerate - engine not running"
    
    def navigate_to(self, destination):
        return self.gps.navigate_to(destination)

car = Car("Toyota", "Camry", 200)
print(car.start())           # "Engine started"
print(car.accelerate())      # "Accelerating to 10 mph"
print(car.navigate_to("Home"))  # "Navigating to Home"
```

### Strategy Pattern with Composition

```python
# Different strategies for sorting
class BubbleSort:
    def sort(self, data):
        # Bubble sort implementation
        return sorted(data)  # Simplified

class QuickSort:
    def sort(self, data):
        # Quick sort implementation
        return sorted(data)  # Simplified

class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy  # Composition
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def sort_data(self, data):
        return self.strategy.sort(data)

# Usage
data = [3, 1, 4, 1, 5, 9, 2, 6]

sorter = Sorter(BubbleSort())
result1 = sorter.sort_data(data)

sorter.set_strategy(QuickSort())  # Change strategy at runtime
result2 = sorter.sort_data(data)
```

---

## Design Patterns

### 1. Factory Pattern

Creates objects without specifying their exact classes:

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type: str) -> Animal:
        if animal_type.lower() == "dog":
            return Dog()
        elif animal_type.lower() == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Usage
factory = AnimalFactory()
dog = factory.create_animal("dog")
cat = factory.create_animal("cat")

print(dog.speak())  # "Woof!"
print(cat.speak())  # "Meow!"
```

### 2. Singleton Pattern

Ensures only one instance of a class exists:

```python
class DatabaseConnection:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.connection = None
            self._initialized = True
    
    def connect(self):
        if not self.connection:
            self.connection = "Connected to database"
        return self.connection

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()

print(db1 is db2)  # True - same instance
```

### 3. Observer Pattern

Notifies multiple objects about state changes:

```python
from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state = None
    
    def attach(self, observer: Observer):
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.notify()

class EmailNotifier(Observer):
    def update(self, subject):
        print(f"Email: State changed to {subject.state}")

class SMSNotifier(Observer):
    def update(self, subject):
        print(f"SMS: State changed to {subject.state}")

# Usage
subject = Subject()
email_notifier = EmailNotifier()
sms_notifier = SMSNotifier()

subject.attach(email_notifier)
subject.attach(sms_notifier)

subject.state = "New Order"  # Both observers get notified
```

### 4. Decorator Pattern

Adds behavior to objects dynamically:

```python
class Coffee:
    def cost(self):
        return 5
    
    def description(self):
        return "Simple coffee"

class CoffeeDecorator:
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost()
    
    def description(self):
        return self._coffee.description()

class MilkDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 2
    
    def description(self):
        return self._coffee.description() + ", milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 1
    
    def description(self):
        return self._coffee.description() + ", sugar"

# Usage
coffee = Coffee()
coffee_with_milk = MilkDecorator(coffee)
coffee_with_milk_and_sugar = SugarDecorator(coffee_with_milk)

print(coffee_with_milk_and_sugar.description())  # "Simple coffee, milk, sugar"
print(coffee_with_milk_and_sugar.cost())         # 8
```

---

## Advanced OOP Concepts

### Context Managers

Use classes as context managers for resource management:

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()

# Usage
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")
# File is automatically closed
```

### Descriptors

Control attribute access at the class level:

```python
class ValidatedAttribute:
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.value = None
    
    def __get__(self, obj, objtype=None):
        return self.value
    
    def __set__(self, obj, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value must be <= {self.max_value}")
        self.value = value

class Person:
    age = ValidatedAttribute(min_value=0, max_value=150)
    
    def __init__(self, name, age):
        self.name = name
        self.age = age  # Uses the descriptor

# Usage
person = Person("Alice", 30)
print(person.age)  # 30

# person.age = -5   # Would raise ValueError
# person.age = 200  # Would raise ValueError
```

### Metaclasses

Classes that create classes:

```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Database connection"

# Usage
db1 = Database()
db2 = Database()
print(db1 is db2)  # True - same instance
```

---

## Modern Python OOP Features

### Dataclasses

Simplified class creation for data containers:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Person:
    name: str
    age: int
    email: str = ""  # Default value
    hobbies: List[str] = field(default_factory=list)  # Mutable default
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")

# Usage
person = Person("Alice", 30, "alice@example.com")
print(person)  # Person(name='Alice', age=30, email='alice@example.com', hobbies=[])

person.hobbies.append("reading")
print(person.hobbies)  # ['reading']
```

### Frozen Dataclasses (Immutable)

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

point = Point(3, 4)
print(point.distance_from_origin())  # 5.0

# point.x = 5  # Would raise FrozenInstanceError
```

### Enum Classes

Type-safe enumerations:

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()

class Order:
    def __init__(self, id: str):
        self.id = id
        self.status = Status.PENDING
    
    def process(self):
        if self.status == Status.PENDING:
            self.status = Status.PROCESSING
            print(f"Order {self.id} is now processing")
        else:
            print(f"Order {self.id} cannot be processed from {self.status}")

# Usage
order = Order("12345")
print(order.status)  # Status.PENDING
order.process()      # "Order 12345 is now processing"
```

### Type Hints and Protocols

Define structural typing:

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "Drawing a circle"

class Square:
    def draw(self) -> str:
        return "Drawing a square"

def draw_shape(shape: Drawable) -> None:
    print(shape.draw())

# Both Circle and Square satisfy the Drawable protocol
draw_shape(Circle())  # "Drawing a circle"
draw_shape(Square())  # "Drawing a square"
```

---

## Best Practices Summary

### 1. Class Design

- **Single Responsibility**: Each class should have one clear purpose
- **Meaningful Names**: Use descriptive class and method names
- **Small Classes**: Keep classes focused and manageable
- **Composition over Inheritance**: Prefer composition when possible

### 2. Method Design

- **Short Methods**: Methods should do one thing well
- **Clear Parameters**: Use type hints and meaningful parameter names
- **Return Values**: Be consistent with return types
- **Error Handling**: Use exceptions appropriately

### 3. Encapsulation

- Use private attributes (`_attribute`) for internal state
- Provide public methods for necessary access
- Use properties for computed values or validation
- Hide implementation details

### 4. Inheritance

- Use inheritance for "is-a" relationships
- Keep inheritance hierarchies shallow
- Use abstract base classes for interfaces
- Don't inherit just for code reuse

### 5. Documentation

- Write clear docstrings for classes and methods
- Document the public interface
- Explain complex algorithms
- Provide usage examples

### 6. Testing

- Design for testability
- Use dependency injection
- Create focused unit tests
- Test edge cases and error conditions

### Example: Well-Designed Class

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class ConnectionConfig:
    """Configuration for database connections."""
    host: str
    port: int
    database: str
    timeout: int = 30

class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to database."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> list:
        """Execute query and return results."""
        pass

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation."""
    
    def __init__(self, config: ConnectionConfig):
        self._config = config
        self._connection = None
        self._logger = logging.getLogger(__name__)
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._connection is not None
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database."""
        try:
            # Connection logic here
            self._logger.info(f"Connected to {self._config.host}:{self._config.port}")
            return True
        except Exception as e:
            self._logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._logger.info("Disconnected from database")
    
    def execute_query(self, query: str) -> list:
        """Execute SQL query and return results."""
        if not self.is_connected:
            raise RuntimeError("Not connected to database")
        
        # Query execution logic here
        return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

# Usage
config = ConnectionConfig(
    host="localhost",
    port=5432,
    database="mydb"
)

with PostgreSQLConnection(config) as db:
    results = db.execute_query("SELECT * FROM users")
    print(results)
# Connection automatically closed
```

### Key Takeaways

1. **Start Simple**: Begin with basic classes and evolve them
2. **Follow SOLID**: Apply SOLID principles consistently
3. **Use Type Hints**: They improve code quality and maintainability
4. **Test Your Code**: Well-designed classes are easy to test
5. **Document Everything**: Good documentation is part of good design
6. **Refactor Regularly**: Improve your design as you learn
7. **Learn Patterns**: Study common design patterns
8. **Practice**: The more you use OOP, the better you'll get

# Connection automatically closed
```

---

## Performance Considerations

While OOP provides excellent maintainability and organization, it's important to understand its performance implications and optimization techniques.

### Object Creation Overhead

**Understanding the Cost:**
```python
import time

# Function-based approach
def create_user_dict(name, email, age):
    return {'name': name, 'email': email, 'age': age}

# Class-based approach
class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

# Performance comparison
def benchmark_creation(n=100000):
    # Dictionary approach
    start = time.time()
    users_dict = [create_user_dict(f"User{i}", f"user{i}@example.com", i%100) for i in range(n)]
    dict_time = time.time() - start
    
    # Class approach
    start = time.time()
    users_class = [User(f"User{i}", f"user{i}@example.com", i%100) for i in range(n)]
    class_time = time.time() - start
    
    print(f"Dictionary creation: {dict_time:.4f}s")
    print(f"Class creation: {class_time:.4f}s")
    print(f"Class overhead: {((class_time/dict_time - 1) * 100):.1f}%")

benchmark_creation()
```

**Key Insights:**
- Objects have ~20-50% overhead compared to dictionaries
- Use classes when behavior matters more than raw performance
- Consider `__slots__` for memory optimization

### Memory Optimization with `__slots__`

```python
class RegularClass:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class SlottedClass:
    __slots__ = ('x', 'y', 'z')  # Restricts attributes
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

import sys

regular = RegularClass(1, 2, 3)
slotted = SlottedClass(1, 2, 3)

print(f"Regular class memory: {sys.getsizeof(regular)} bytes")
print(f"Slotted class memory: {sys.getsizeof(slotted)} bytes")
print(f"Memory savings: {((sys.getsizeof(regular) - sys.getsizeof(slotted)) / sys.getsizeof(regular) * 100):.1f}%")
```

**Benefits of `__slots__`:**
- Reduces memory usage by ~40-50%
- Faster attribute access
- Prevents accidental attribute creation
- Trade-off: Less flexible, no `__dict__`

### Method Dispatch Costs

```python
class Animal:
    def speak(self):
        return "Some sound"

class Dog(Animal):
    def speak(self):
        return "Woof!"

def call_speak_polymorphic(animal):
    return animal.speak()

def call_speak_direct(dog):
    return dog.speak()

# Performance comparison
dog = Dog()
iterations = 1000000

import time

# Polymorphic calls (virtual method dispatch)
start = time.time()
for _ in range(iterations):
    result = call_speak_polymorphic(dog)
poly_time = time.time() - start

# Direct calls
start = time.time()
for _ in range(iterations):
    result = call_speak_direct(dog)
direct_time = time.time() - start

print(f"Polymorphic calls: {poly_time:.4f}s")
print(f"Direct calls: {direct_time:.4f}s")
print(f"Overhead: {((poly_time/direct_time - 1) * 100):.1f}%")
```

**Optimization Strategies:**
- Use direct calls when polymorphism isn't needed
- Cache method references for repeated calls
- Consider protocols/structual typing over inheritance for performance-critical code

### Inheritance Depth and Method Resolution

```python
# Shallow inheritance
class A:
    def method(self): return "A"

class B(A):
    def method(self): return "B"

# Deep inheritance
class Deep1: pass
class Deep2(Deep1): pass
class Deep3(Deep2): pass
class Deep4(Deep3): pass
class Deep5(Deep4): pass
class Deep6(Deep5): pass
class Deep7(Deep6): pass
class Deep8(Deep7): pass
class Deep9(Deep8): pass
class Deep10(Deep9):
    def method(self): return "Deep10"

# Performance comparison
shallow = B()
deep = Deep10()

iterations = 1000000
import time

start = time.time()
for _ in range(iterations):
    result = shallow.method()
shallow_time = time.time() - start

start = time.time()
for _ in range(iterations):
    result = deep.method()
deep_time = time.time() - start

print(f"Shallow inheritance: {shallow_time:.4f}s")
print(f"Deep inheritance: {deep_time:.4f}s")
print(f"Overhead: {((deep_time/shallow_time - 1) * 100):.1f}%")
```

**Best Practices:**
- Keep inheritance hierarchies shallow (3-4 levels max)
- Use composition over deep inheritance
- Profile before optimizing - inheritance overhead is usually minimal

### When OOP Performance Matters

**Use Classes When:**
- Code maintainability is priority
- Objects have complex behavior
- Polymorphism is needed
- Memory usage isn't critical

**Consider Alternatives When:**
- Processing millions of simple data objects
- Memory is constrained
- Raw speed is critical
- Data is mostly static

**Hybrid Approach:**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class UserData:
    """Fast data container."""
    id: int
    name: str
    email: str

class UserService:
    """Behavioral class."""
    
    def __init__(self, users: List[UserData]):
        self.users = users
    
    def find_by_email(self, email: str) -> UserData:
        return next((u for u in self.users if u.email == email), None)
    
    def validate_user(self, user: UserData) -> bool:
        return len(user.name) > 0 and '@' in user.email

# Usage: Fast data with behavioral methods
users = [UserData(i, f"User{i}", f"user{i}@example.com") for i in range(1000)]
service = UserService(users)
```

---

## Error Handling in OOP

Proper error handling is crucial for robust object-oriented code. OOP provides excellent patterns for managing errors consistently across your application.

### Custom Exception Hierarchies

```python
class DatabaseError(Exception):
    """Base class for all database-related errors."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a query execution fails."""
    pass

class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass

class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self._connected = False
    
    def connect(self):
        try:
            # Connection logic here
            if not self._validate_config():
                raise ValidationError("Invalid database configuration")
            self._connected = True
        except ConnectionError:
            raise  # Re-raise connection errors
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
    
    def execute_query(self, query):
        if not self._connected:
            raise ConnectionError("Not connected to database")
        
        try:
            # Query execution logic
            return self._run_query(query)
        except Exception as e:
            raise QueryError(f"Query failed: {e}") from e
    
    def _validate_config(self):
        return bool(self.config.get('host') and self.config.get('database'))
    
    def _run_query(self, query):
        # Simulate query execution
        if "SELECT" in query:
            return [{"id": 1, "name": "Test"}]
        else:
            raise QueryError("Unsupported query type")

# Usage with proper error handling
db = DatabaseConnection({"host": "localhost", "database": "test"})

try:
    db.connect()
    results = db.execute_query("SELECT * FROM users")
    print(f"Query results: {results}")
except ValidationError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except QueryError as e:
    print(f"Query error: {e}")
except DatabaseError as e:
    print(f"General database error: {e}")
```

### Context Managers for Resource Management

```python
class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection
        self._committed = False
        self._rolled_back = False
    
    def __enter__(self):
        self.connection.execute_query("BEGIN TRANSACTION")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exception - commit
            self.connection.execute_query("COMMIT")
            self._committed = True
        else:
            # Exception occurred - rollback
            self.connection.execute_query("ROLLBACK")
            self._rolled_back = True
            return False  # Re-raise the exception
    
    def execute(self, query):
        if self._committed or self._rolled_back:
            raise RuntimeError("Transaction already finished")
        return self.connection.execute_query(query)

# Usage
db = DatabaseConnection({"host": "localhost", "database": "test"})
db.connect()

try:
    with DatabaseTransaction(db) as transaction:
        transaction.execute("INSERT INTO users (name) VALUES ('Alice')")
        transaction.execute("INSERT INTO users (name) VALUES ('Bob')")
        # If this fails, everything rolls back automatically
        transaction.execute("INVALID QUERY")
except QueryError as e:
    print(f"Transaction failed and was rolled back: {e}")
```

### Defensive Programming with Validation

```python
from typing import Optional, Union

class User:
    def __init__(self, user_id: int, name: str, email: str):
        self._user_id = None
        self._name = None
        self._email = None
        
        # Validate and set attributes
        self.user_id = user_id
        self.name = name
        self.email = email
    
    @property
    def user_id(self) -> int:
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("User ID must be a positive integer")
        self._user_id = value
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string")
        if len(value.strip()) > 100:
            raise ValueError("Name must be 100 characters or less")
        self._name = value.strip()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        value = value.strip().lower()
        if '@' not in value or '.' not in value.split('@')[1]:
            raise ValueError("Invalid email format")
        self._email = value
    
    def update_profile(self, name: Optional[str] = None, email: Optional[str] = None):
        """Update user profile with validation."""
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
    
    def to_dict(self) -> dict:
        """Safe export of user data."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email
        }

# Usage with comprehensive error handling
def create_user_from_input(user_data: dict) -> Union[User, None]:
    try:
        user = User(
            user_id=user_data.get('user_id'),
            name=user_data.get('name'),
            email=user_data.get('email')
        )
        return user
    except (ValueError, TypeError) as e:
        print(f"Invalid user data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error creating user: {e}")
        return None

# Example usage
valid_data = {'user_id': 1, 'name': 'Alice', 'email': 'alice@example.com'}
invalid_data = {'user_id': 'not_a_number', 'name': '', 'email': 'invalid-email'}

user1 = create_user_from_input(valid_data)  # Success
user2 = create_user_from_input(invalid_data)  # None with error message
```

### Error Recovery Patterns

```python
class ResilientDatabaseConnection:
    def __init__(self, config, max_retries=3, retry_delay=1.0):
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._connection = None
        self._retry_count = 0
    
    def connect_with_retry(self):
        """Connect with automatic retry on failure."""
        for attempt in range(self.max_retries + 1):
            try:
                self._connect()
                self._retry_count = 0  # Reset on success
                return True
            except ConnectionError as e:
                if attempt < self.max_retries:
                    print(f"Connection attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    print(f"All {self.max_retries + 1} connection attempts failed")
                    raise
    
    def execute_query_with_retry(self, query):
        """Execute query with retry on transient failures."""
        for attempt in range(self.max_retries + 1):
            try:
                return self._execute_query(query)
            except QueryError as e:
                if self._is_transient_error(e) and attempt < self.max_retries:
                    print(f"Query attempt {attempt + 1} failed: {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise
    
    def _is_transient_error(self, error):
        """Check if error is transient and worth retrying."""
        transient_messages = [
            "connection timeout",
            "temporary server error",
            "lock wait timeout"
        ]
        error_msg = str(error).lower()
        return any(msg in error_msg for msg in transient_messages)
    
    def _connect(self):
        # Actual connection logic
        pass
    
    def _execute_query(self, query):
        # Actual query execution
        pass
```

---

## Testing OOP Code

Well-designed OOP code is inherently testable. Here's how to write effective tests for your classes and objects.

### Unit Testing Classes

```python
import pytest
from unittest.mock import Mock, patch

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        return self.history.copy()

# Test file: test_calculator.py
class TestCalculator:
    
    def test_add_basic(self):
        """Test basic addition functionality."""
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5
    
    def test_add_history(self):
        """Test that addition is recorded in history."""
        calc = Calculator()
        calc.add(1, 2)
        calc.add(3, 4)
        
        history = calc.get_history()
        assert len(history) == 2
        assert "1 + 2 = 3" in history
        assert "3 + 4 = 7" in history
    
    def test_get_history_returns_copy(self):
        """Test that get_history returns a copy, not the original list."""
        calc = Calculator()
        calc.add(1, 1)
        
        history = calc.get_history()
        history.append("modified")  # This shouldn't affect the original
        
        assert len(calc.get_history()) == 1  # Original unchanged
    
    def test_add_with_floats(self):
        """Test addition with floating point numbers."""
        calc = Calculator()
        result = calc.add(1.5, 2.5)
        assert result == 4.0
    
    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300)
    ])
    def test_add_parametrized(self, a, b, expected):
        """Test addition with multiple input combinations."""
        calc = Calculator()
        assert calc.add(a, b) == expected

# Running the tests
if __name__ == "__main__":
    pytest.main([__file__])
```

### Testing Inheritance and Polymorphism

```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message, recipient):
        pass

class EmailNotifier(Notifier):
    def send(self, message, recipient):
        # Send email logic
        return f"Email sent to {recipient}: {message}"

class SMSNotifier(Notifier):
    def send(self, message, recipient):
        # Send SMS logic
        return f"SMS sent to {recipient}: {message}"

class NotificationService:
    def __init__(self, notifiers):
        self.notifiers = notifiers
    
    def notify_all(self, message, recipients):
        results = []
        for notifier in self.notifiers:
            for recipient in recipients:
                results.append(notifier.send(message, recipient))
        return results

# Test file: test_notifications.py
import pytest
from unittest.mock import Mock

class TestEmailNotifier:
    
    def test_send_email(self):
        notifier = EmailNotifier()
        result = notifier.send("Hello", "user@example.com")
        assert "Email sent to user@example.com: Hello" == result

class TestSMSNotifier:
    
    def test_send_sms(self):
        notifier = SMSNotifier()
        result = notifier.send("Alert!", "+1234567890")
        assert "SMS sent to +1234567890: Alert!" == result

class TestNotificationService:
    
    def test_notify_all_with_multiple_notifiers(self):
        # Create mock notifiers
        email_mock = Mock()
        email_mock.send.return_value = "Email sent"
        
        sms_mock = Mock()
        sms_mock.send.return_value = "SMS sent"
        
        service = NotificationService([email_mock, sms_mock])
        recipients = ["user1@example.com", "user2@example.com"]
        
        results = service.notify_all("Test message", recipients)
        
        # Verify both notifiers were called for each recipient
        assert email_mock.send.call_count == 2
        assert sms_mock.send.call_count == 2
        assert len(results) == 4
    
    def test_polymorphic_behavior(self):
        """Test that any Notifier implementation works."""
        # Create a custom notifier for testing
        class TestNotifier(Notifier):
            def send(self, message, recipient):
                return f"Test: {message} to {recipient}"
        
        service = NotificationService([TestNotifier()])
        results = service.notify_all("Hello", ["test@example.com"])
        
        assert results == ["Test: Hello to test@example.com"]

# Testing abstract base classes
def test_notifier_is_abstract():
    """Test that Notifier cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Notifier()
```

### Mocking Dependencies

```python
from unittest.mock import Mock, patch, MagicMock
import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_user(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data):
        url = f"{self.base_url}/users"
        response = self.session.post(url, json=user_data)
        response.raise_for_status()
        return response.json()

# Test file: test_api_client.py
import pytest
from requests.exceptions import HTTPError

class TestAPIClient:
    
    def test_get_user_success(self):
        # Create mock response
        mock_response = Mock()
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status.return_value = None
        
        # Create mock session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        
        # Create client with mocked session
        client = APIClient("https://api.example.com")
        client.session = mock_session
        
        result = client.get_user(1)
        
        # Verify the call was made correctly
        mock_session.get.assert_called_once_with("https://api.example.com/users/1")
        assert result == {"id": 1, "name": "Alice"}
    
    def test_get_user_http_error(self):
        # Create mock response that raises HTTPError
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        client.session = mock_session
        
        with pytest.raises(HTTPError):
            client.get_user(999)
    
    @patch('requests.Session')  # Patch at import level
    def test_create_user_with_patch(self, mock_session_class):
        # Setup mock session instance
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {"id": 2, "name": "Bob"}
        mock_session.post.return_value = mock_response
        
        client = APIClient("https://api.example.com")
        result = client.create_user({"name": "Bob"})
        
        mock_session.post.assert_called_once_with(
            "https://api.example.com/users", 
            json={"name": "Bob"}
        )
        assert result == {"id": 2, "name": "Bob"}

# Integration test example
class TestAPIClientIntegration:
    
    @pytest.mark.integration
    def test_real_api_call(self):
        # This would run against a real test server
        client = APIClient("https://jsonplaceholder.typicode.com")
        user = client.get_user(1)
        
        assert user["id"] == 1
        assert "name" in user
```

### Testing Context Managers

```python
class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self.connected = False
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def connect(self):
        self.connected = True
    
    def disconnect(self):
        self.connected = False
    
    def execute(self, query):
        if not self.connected:
            raise RuntimeError("Not connected")
        return f"Executed: {query}"

# Test file: test_database_connection.py
import pytest

class TestDatabaseConnection:
    
    def test_context_manager(self):
        """Test that context manager properly connects and disconnects."""
        config = {"host": "localhost", "database": "test"}
        db = DatabaseConnection(config)
        
        assert not db.connected
        
        with db as conn:
            assert conn.connected
            result = conn.execute("SELECT 1")
            assert result == "Executed: SELECT 1"
        
        # Should be disconnected after context
        assert not db.connected
    
    def test_context_manager_exception_handling(self):
        """Test that connection is closed even when exception occurs."""
        db = DatabaseConnection({})
        
        with pytest.raises(RuntimeError):
            with db as conn:
                assert conn.connected
                # This will raise an exception
                conn.execute("INVALID QUERY")
        
        # Should still be disconnected
        assert not db.connected
    
    def test_manual_connection(self):
        """Test manual connect/disconnect without context manager."""
        db = DatabaseConnection({})
        
        db.connect()
        assert db.connected
        
        db.disconnect()
        assert not db.connected
```

### Test Organization Best Practices

```python
# tests/conftest.py - Shared fixtures
import pytest

@pytest.fixture
def sample_user_data():
    return {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com"
    }

@pytest.fixture
def mock_database():
    """Fixture providing a mocked database connection."""
    db = Mock()
    db.execute_query.return_value = [{"id": 1, "name": "Test"}]
    return db

# tests/test_user_service.py
class TestUserService:
    
    def test_create_user(self, sample_user_data, mock_database):
        service = UserService(mock_database)
        user = service.create_user(sample_user_data)
        
        assert user.id == 1
        assert user.name == "Alice"
        mock_database.execute_query.assert_called_once()
    
    def test_get_user_by_id(self, mock_database):
        service = UserService(mock_database)
        user = service.get_user_by_id(1)
        
        assert user is not None
        mock_database.execute_query.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )

# tests/integration/test_user_workflow.py
class TestUserWorkflow:
    
    @pytest.mark.integration
    def test_complete_user_workflow(self, test_database):
        """Test creating, updating, and deleting a user."""
        # This would use a real test database
        service = UserService(test_database)
        
        # Create user
        user_data = {"name": "Alice", "email": "alice@example.com"}
        user = service.create_user(user_data)
        assert user.id is not None
        
        # Update user
        user.name = "Alice Smith"
        service.update_user(user)
        
        # Verify update
        updated_user = service.get_user_by_id(user.id)
        assert updated_user.name == "Alice Smith"
        
        # Delete user
        service.delete_user(user.id)
        assert service.get_user_by_id(user.id) is None
```

---

## Real-World Examples from Our Codebase

Let's look at how OOP concepts are applied in our actual project code, with references to the real implementations.

### Database Connection Hierarchy

From `gds_snowflake/gds_snowflake/base.py`:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class DatabaseConnection(ABC):
    """
    Abstract base class defining the interface for all database connections.
    
    This ensures all database implementations have the same core methods,
    enabling polymorphism across different database types.
    """
    
    @abstractmethod
    def connect(self) -> Any:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection."""
        pass

class ConfigurableComponent(ABC):
    """
    Abstract base class for components that can be configured.
    
    Demonstrates the Interface Segregation Principle - components only
    implement configuration if they need it.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration and validate."""
        self._config.update(new_config)
        if not self.validate_config():
            raise ValueError("Invalid configuration")
```

From `gds_snowflake/gds_snowflake/connection.py`:
```python
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent, ResourceManager):
    """
    Snowflake database connection implementation.
    
    Demonstrates multiple inheritance and composition:
    - DatabaseConnection: Core database interface
    - ConfigurableComponent: Configuration management
    - ResourceManager: Resource lifecycle management
    """
    
    def __init__(self, account: str, user: Optional[str] = None, **kwargs):
        # Initialize parent classes
        ConfigurableComponent.__init__(self, kwargs.get('config'))
        
        self.account = account
        self.user = user
        self.connection = None
        self._initialized = False
        
        # Composition: Use other objects for specific functionality
        self._logger = logging.getLogger(__name__)
    
    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Connect to Snowflake with proper error handling."""
        try:
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                # ... other parameters
            )
            self._initialized = True
            self._logger.info(f"Connected to Snowflake account: {self.account}")
            return self.connection
        except Exception as e:
            self._logger.error(f"Failed to connect to Snowflake: {e}")
            raise ConnectionError(f"Snowflake connection failed: {e}") from e
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query with error handling and logging."""
        if not self.is_connected():
            raise ConnectionError("Not connected to Snowflake")
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                
                # Convert to list of dictionaries for consistency
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in results]
                return results
        except Exception as e:
            self._logger.error(f"Query execution failed: {e}")
            raise QueryError(f"Failed to execute query: {e}") from e
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return (self.connection is not None and 
                not self.connection.is_closed())
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection details."""
        return {
            'type': 'Snowflake',
            'account': self.account,
            'user': self.user,
            'connected': self.is_connected(),
            'warehouse': getattr(self, 'warehouse', None),
            'database': getattr(self, 'database', None)
        }
    
    # Context manager implementation
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
```

### Monitor Pattern Implementation

From `gds_snowflake/gds_snowflake/base.py`:
```python
class BaseMonitor(ABC):
    """
    Abstract base class for monitoring components.
    
    Demonstrates the Template Method pattern and Strategy pattern:
    - Template Method: Common monitoring workflow in check()
    - Strategy: Different monitors implement different checking strategies
    """
    
    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # State tracking
        self._check_count = 0
        self._last_check_time = None
        self._errors = []
    
    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """
        Perform the actual monitoring check.
        
        Returns:
            Dictionary with check results
        """
        pass
    
    def run_check(self) -> Dict[str, Any]:
        """
        Template method: Standard monitoring workflow.
        
        This method defines the algorithm skeleton, while subclasses
        implement the specific check logic.
        """
        start_time = datetime.now()
        
        try:
            # Pre-check setup
            self._check_count += 1
            
            # Perform the actual check (implemented by subclasses)
            result = self.check()
            
            # Post-check processing
            result['check_number'] = self._check_count
            result['duration_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            result['timestamp'] = start_time.isoformat()
            
            # Log success
            self._log_success(result)
            
            return result
            
        except Exception as e:
            # Handle errors consistently
            error_result = {
                'success': False,
                'error': str(e),
                'check_number': self._check_count,
                'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'timestamp': start_time.isoformat()
            }
            
            self._errors.append(error_result)
            self._log_error(error_result)
            
            return error_result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            'name': self.name,
            'total_checks': self._check_count,
            'error_count': len(self._errors),
            'last_check': self._last_check_time,
            'recent_errors': self._errors[-5:]  # Last 5 errors
        }
    
    def _log_success(self, result: Dict[str, Any]) -> None:
        """Log successful check."""
        duration = result.get('duration_ms', 0)
        self._logger.info(
            f"{self.name} check PASSED in {duration:.1f}ms"
        )
    
    def _log_error(self, result: Dict[str, Any]) -> None:
        """Log failed check."""
        duration = result.get('duration_ms', 0)
        error = result.get('error', 'Unknown error')
        self._logger.error(
            f"{self.name} check FAILED in {duration:.1f}ms: {error}"
        )
```

### Factory Pattern in Action

From monitoring modules:
```python
class MonitorFactory:
    """
    Factory pattern for creating monitor instances.
    
    Demonstrates the Factory pattern: Centralizes monitor creation logic
    and allows easy addition of new monitor types.
    """
    
    @staticmethod
    def create_monitor(monitor_type: str, name: str, **kwargs) -> BaseMonitor:
        """
        Create a monitor instance based on type.
        
        Args:
            monitor_type: Type of monitor ('snowflake', 'postgres', etc.)
            name: Name for the monitor instance
            **kwargs: Monitor-specific configuration
        
        Returns:
            Configured monitor instance
        """
        if monitor_type.lower() == 'snowflake':
            return SnowflakeMonitor(name=name, **kwargs)
        elif monitor_type.lower() == 'postgres':
            return PostgreSQLMonitor(name=name, **kwargs)
        elif monitor_type.lower() == 'health':
            return HealthMonitor(name=name, **kwargs)
        else:
            raise ValueError(f"Unknown monitor type: {monitor_type}")
    
    @staticmethod
    def create_monitors_from_config(config: Dict[str, Any]) -> List[BaseMonitor]:
        """
        Create multiple monitors from configuration.
        
        Demonstrates bulk object creation and configuration-driven design.
        """
        monitors = []
        
        for monitor_config in config.get('monitors', []):
            monitor_type = monitor_config.pop('type')
            monitor_name = monitor_config.pop('name', f"{monitor_type}_monitor")
            
            monitor = MonitorFactory.create_monitor(
                monitor_type, monitor_name, **monitor_config
            )
            monitors.append(monitor)
        
        return monitors

# Usage example
factory = MonitorFactory()

# Create single monitor
snowflake_monitor = factory.create_monitor(
    'snowflake',
    'prod_snowflake_monitor',
    account='prod_account',
    timeout=60
)

# Create multiple monitors from config
config = {
    'monitors': [
        {'type': 'snowflake', 'name': 'prod_monitor', 'account': 'prod'},
        {'type': 'postgres', 'name': 'db_monitor', 'host': 'localhost'},
        {'type': 'health', 'name': 'health_monitor'}
    ]
}

monitors = factory.create_monitors_from_config(config)
```

### Dependency Injection Example

From service classes:
```python
class DatabaseService:
    """
    Service class demonstrating dependency injection.
    
    The service depends on abstractions (DatabaseConnection) rather than
    concrete implementations, following the Dependency Inversion Principle.
    """
    
    def __init__(self, connection: DatabaseConnection):
        """
        Inject the database connection dependency.
        
        Args:
            connection: Any database connection implementing DatabaseConnection
        """
        self._connection = connection
        self._logger = logging.getLogger(__name__)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with proper error handling."""
        try:
            query = "SELECT id, name, email FROM users WHERE id = ?"
            results = self._connection.execute_query(query, (user_id,))
            return results[0] if results else None
        except Exception as e:
            self._logger.error(f"Failed to get user {user_id}: {e}")
            raise
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user."""
        try:
            query = """
                INSERT INTO users (name, email, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """
            self._connection.execute_query(query, 
                (user_data['name'], user_data['email'])
            )
            
            # Get the created user
            return self.get_user_by_id(self._get_last_insert_id())
        except Exception as e:
            self._logger.error(f"Failed to create user: {e}")
            raise
    
    def _get_last_insert_id(self) -> int:
        """Get the last inserted ID (database-specific implementation)."""
        # This would be implemented differently for each database
        pass

# Usage with dependency injection
def create_user_service(connection_type: str = 'snowflake') -> DatabaseService:
    """
    Factory function demonstrating dependency injection setup.
    
    This function creates the appropriate connection and injects it
    into the service, following the Dependency Inversion Principle.
    """
    if connection_type == 'snowflake':
        connection = SnowflakeConnection(
            account='my_account',
            user='my_user'
        )
    elif connection_type == 'postgres':
        connection = PostgreSQLConnection(
            host='localhost',
            database='myapp'
        )
    else:
        raise ValueError(f"Unsupported connection type: {connection_type}")
    
    # Inject the connection into the service
    return DatabaseService(connection)

# Usage
service = create_user_service('snowflake')
user = service.get_user_by_id(123)
```

---

## What's Missing?

This guide covers the core OOP concepts and best practices. For advanced topics that go beyond the fundamentals, see our companion tutorial:

**[04_ADVANCED_OOP_CONCEPTS.md](../04_ADVANCED_OOP_CONCEPTS.md)** - Covers advanced OOP concepts including:

- **Async/await with classes** - Building responsive, concurrent systems
- **Multiple inheritance diamond problem** - Advanced inheritance patterns
- **Monkey patching and dynamic class modification** - Runtime code modification
- **Advanced metaclass usage** - Controlling class creation and behavior
- **Protocol buffers and serialization** - Efficient data serialization
- **Performance optimization techniques** - Advanced performance tuning
- **Memory management and weak references** - Preventing memory leaks

The key is to master the fundamentals first, then gradually explore more advanced concepts as your projects require them.

Remember: Good OOP design is about creating code that is easy to understand, maintain, and extend. Start with these principles and patterns, and you'll be well on your way to writing excellent object-oriented Python code!