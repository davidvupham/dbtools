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
   - [SOLID at a Glance](#solid-at-a-glance)
   - [Single Responsibility Principle](#1-single-responsibility-principle-srp)
   - [Open/Closed Principle](#2-openclosed-principle-ocp)
   - [Liskov Substitution Principle](#3-liskov-substitution-principle-lsp)
   - [Interface Segregation Principle](#4-interface-segregation-principle-isp)
   - [Dependency Inversion Principle](#5-dependency-inversion-principle-dip)
9. [Composition vs Inheritance](#composition-vs-inheritance)
   - [Visual Decision Tree](#visual-decision-tree)
   - [Strategy Pattern with Composition](#strategy-pattern-with-composition)
10. [Design Patterns](#design-patterns)
    - [Factory Pattern](#1-factory-pattern)
    - [Singleton Pattern](#2-singleton-pattern)
    - [Observer Pattern](#3-observer-pattern)
    - [Decorator Pattern](#4-decorator-pattern)
    - [Composite Pattern](#5-composite-pattern)
11. [Advanced OOP Concepts](#advanced-oop-concepts)
    - [Context Managers](#context-managers)
    - [Descriptors](#descriptors)
    - [Metaclasses](#metaclasses)
    - [Class Decorators](#class-decorators)
    - [Thread-safety Basics](#thread-safety-basics)
12. [Modern Python OOP Features](#modern-python-oop-features)
    - [Dataclasses](#dataclasses)
    - [Enum Classes](#enum-classes)
    - [The Python Data Model (Dunder Methods)](#the-python-data-model-dunder-methods)
      - [`__call__`, `__getattr__`, `__setattr__`](#making-objects-callable-__call__)
    - [Type Hints and Protocols](#type-hints-and-protocols)
      - [Generics and Type Parameters](#generic-classes-type-parameters)
      - [The `Self` Type](#the-self-type-python-311)
    - [JSON Serialization](#json-serialization-tips)
13. [Best Practices Summary](#best-practices-summary)
14. [Performance Considerations](#performance-considerations)
    - [OOP-Specific Performance Tips](#oop-specific-performance-tips)
    - [Performance Comparison Table](#performance-comparison-table)
    - [When to Optimize](#when-to-optimize)
15. [Error Handling in OOP](#error-handling-in-oop)
16. [Testing OOP Code](#testing-oop-code)
17. [Real-World Examples from Our Codebase](#real-world-examples-from-our-codebase)
18. [Practice Exercises](#practice-exercises)
19. [Appendices](#appendices)
20. [What's Missing?](#whats-missing)
21. [Quick Reference for Beginners](#quick-reference-for-beginners)

---

## Introduction to OOP

### What is Object-Oriented Programming?

**Object-Oriented Programming (OOP)** is a programming paradigm that organizes code into "objects" that contain both data (attributes) and functions (methods). Think of it like creating blueprints (classes) and then building things (objects) from those blueprints.

### Real-World Analogy

Think of OOP like building with LEGO blocks. Each type of block is a **class** (the design), and each actual block you place is an **object** (an instance of that design).

Another example - imagine a **Car** blueprint:

- **Data (Attributes)**: Things the car HAS - color, brand, speed, fuel_level
- **Actions (Methods)**: Things the car DOES - start(), stop(), accelerate(), brake()

From one blueprint (class), you can create many cars (objects):

```python
class Car:
    def __init__(self, color: str, brand: str):
        self.color = color
        self.brand = brand


my_car = Car(color="red", brand="Toyota")
your_car = Car(color="blue", brand="Honda")
```

Each car is independent - when you paint `my_car` red, `your_car` stays blue!

### Why Use OOP?

1. **Modularity**: Code is organized into self-contained objects
2. **Reusability**: Classes can be reused and extended
3. **Maintainability**: Changes to one class don't affect others
4. **Abstraction**: Hide complex implementation details
5. **Real-world modeling**: Naturally represents real-world entities

---

### Quickstart: How to run the examples

Most examples in this guide can be run immediately! Here's how:

**To run an example:**

1. Copy the code block
2. Save it to a file like `example.py`
3. Run it: `python3 example.py` (Linux/macOS) or `python example.py` (Windows)
4. Or paste it into a Python REPL: run `python3`, then paste the code

**Important notes:**

- Recommended Python: 3.10+ (examples use type hints and modern features)
- **Some examples are illustrative only**: Examples labeled "from our codebase" (like Snowflake connections) show real-world patterns but may reference libraries you don't have installed. These are for learning the concepts, not for running.
- **Most examples are self-contained**: If there's no note saying "from our codebase", you can run the example as-is!

**What if an example doesn't run?**

- Check if it's marked "from our codebase" - those are illustrative
- Make sure you're using Python 3.10 or later
- Check if you need to install any libraries (we'll mention if you do)

### Glossary (beginner-friendly)

- Class: A blueprint for creating objects.
- Object (instance): A thing created from a class.
- Attribute: A piece of data stored on an object (e.g., `user.name`).
- Method: A function defined in a class that operates on objects (e.g., `user.save()`).
- Constructor: The `__init__` method that runs when creating an object.
- Encapsulation: Keeping implementation details private behind a clean interface.
- Inheritance: A class reusing/extending another class’s behavior.
- Polymorphism: Different classes exposing the same interface so you can use them interchangeably.
- Interface/ABC: A contract specifying required methods; ABC enforces this in Python.
- Composition: Building classes by combining other objects ("has-a"), rather than inheriting ("is-a").

---

## Classes and Objects

### Your First Class

Let's start with something simple - a class to represent a dog:

```python
class Dog:
    """A simple class representing a dog."""

    # Constructor - runs when creating a new dog
    # Think of this as the "birth" of a dog object
    def __init__(self, name, age):
        """Initialize a dog with name and age."""
        self.name = name  # Each dog has its own name
        self.age = age    # Each dog has its own age

    # Method - a function inside a class
    # Think of this as an action the dog can perform
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

# Create dog objects (instances) - like adopting actual dogs
my_dog = Dog("Buddy", 5)
your_dog = Dog("Max", 3)

# Each dog is independent
my_dog.bark()  # Output: "Buddy says Woof!"
your_dog.bark()  # Output: "Max says Woof!"

# Each dog has its own data
print(my_dog.get_age_in_months())  # Output: 60
print(your_dog.get_age_in_months())  # Output: 36

# Changes to one dog don't affect the other
my_dog.have_birthday()  # Only Buddy ages
print(my_dog.age)   # Output: 6
print(your_dog.age)  # Output: 3 (Still 3!)
```

**Key Points for Beginners:**

- `class Dog:` creates the blueprint (like a cookie cutter)
- `Dog("Buddy", 5)` creates an actual dog object (like an actual cookie)
- `self` refers to the specific dog you're working with
- Methods (like `bark()`) are actions that objects can perform
- Attributes (like `name` and `age`) are data that objects store

**Try it yourself!** Create a `Cat` class with:

- Attributes: `name` and `color`
- Methods: `meow()` that prints "{name} says Meow!", and `change_color(new_color)` that changes the cat's color
- Create two cat objects and test all the methods

<details>
<summary>Click to see solution</summary>

```python
class Cat:
    """A simple cat class."""

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def meow(self):
        print(f"{self.name} says Meow!")

    def change_color(self, new_color):
        print(f"{self.name} changed from {self.color} to {new_color}")
        self.color = new_color

# Test it
fluffy = Cat("Fluffy", "white")
shadow = Cat("Shadow", "black")

fluffy.meow()  # "Fluffy says Meow!"
shadow.meow()  # "Shadow says Meow!"

fluffy.change_color("gray")  # "Fluffy changed from white to gray"
print(fluffy.color)  # "gray"
print(shadow.color)  # "black" (unchanged!)
```

</details>

### Class vs Instance Variables

Variables in a class can belong to the class itself (shared by all instances) or to each instance (unique per object).

```python
class Dog:
    # Class variable - shared by ALL dogs
    species = "Canis lupus"
    total_dogs = 0

    def __init__(self, name, age):
        # Instance variables - unique to each dog
        self.name = name
        self.age = age

        # Update class variable when a new instance is created
        Dog.total_dogs += 1

    @classmethod
    def get_total_dogs(cls):
        """
        A class method receives the class itself as the first argument,
        conventionally named `cls`. It can access and modify class state.
        Use case: Factory methods or operations on the class itself.
        """
        return f"Total dogs: {cls.total_dogs}"

    @classmethod
    def from_birth_year(cls, name, birth_year):
        """Alternative constructor using a class method."""
        from datetime import date
        age = date.today().year - birth_year
        return cls(name, age)

    @staticmethod
    def is_good_boy():
        """
        A static method doesn't receive any implicit first argument.
        It's essentially a regular function namespaced within the class.
        It cannot modify class or instance state.
        Use case: Utility functions that are logically related to the class.
        """
        return True

# Usage
dog1 = Dog("Buddy", 5)
dog2 = Dog.from_birth_year("Max", 2020)

# Accessing class variables
print(f"Species: {Dog.species}")        # "Species: Canis lupus"
print(f"Dog 1 species: {dog1.species}") # Also accessible via instance

# Using the class method
print(Dog.get_total_dogs())  # "Total dogs: 2"

# Using the static method
print(f"Is Max a good boy? {Dog.is_good_boy()}")  # "Is Max a good boy? True"

print(f"{dog2.name} is {dog2.age} years old.")
```

**When to use which?**

- **Instance Method (`def method(self, ...)`):** The most common type. Needs access to the object's instance data (`self`).
- **Class Method (`@classmethod def method(cls, ...)`):** Needs access to the class, but not a specific instance. Perfect for factory methods that create instances in alternative ways (e.g., from a file, a dictionary, or a different representation).
- **Static Method (`@staticmethod def method(...)`):** Doesn't need access to the instance or the class. It's a helper function that lives inside the class's namespace for organizational purposes.

### Example from Our Codebase

From `connection.py`:

```python
from typing import Optional
# Note: This example uses snowflake.connector from our actual codebase
# You don't need to run this - it's just showing real-world usage

class SnowflakeConnection:
    """Manages connections to Snowflake database."""

    def __init__(self, account: str, user: Optional[str] = None, private_key: Optional[str] = None):
        """Initialize a new connection."""
        # Store connection parameters for THIS connection
        self.account = account
        self.user = user
        self.private_key = private_key
        self.connection = None  # No connection yet
        self._initialized = False

    def connect(self):
        """Establish connection to Snowflake."""
        # Use THIS connection's account and user
        self.connection = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            private_key=self.private_key,
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

The word `self` might seem confusing at first, but think of it this way: **`self` means "THIS specific object"**.

When you have multiple dogs, and you call `my_dog.bark()`, how does Python know WHICH dog should bark? That's what `self` does - it tells Python "use THIS dog's name".

Here's a simple example with counters:

```python
class Counter:
    """A simple counter that can count up."""

    def __init__(self):
        self.count = 0  # THIS counter's count starts at 0

    def increment(self):
        """Add 1 to THIS counter's count."""
        self.count += 1  # Modify THIS counter's count

    def get_count(self):
        """Get THIS counter's current count."""
        return self.count  # Return THIS counter's count

# Create two independent counters
counter1 = Counter()
counter2 = Counter()

# Each counter keeps its own count
counter1.increment()  # counter1 is now at 1
counter1.increment()  # counter1 is now at 2
counter2.increment()  # counter2 is now at 1

print(counter1.get_count())  # Output: 2 (counter1's count)
print(counter2.get_count())  # Output: 1 (counter2's count)
```

**Key Points:**

- `self` is automatically passed to methods - you don't type it when calling methods
- When you call `counter1.increment()`, Python automatically passes `counter1` as `self`
- This is why each object has its own separate data
- You could name it something else (like `this` or `me`), but `self` is the Python convention

**Think of it like this:** When you say "I brush my teeth", the word "my" refers to YOUR teeth. Similarly, when a method uses `self.count`, it's referring to THAT object's count.

---

## Encapsulation and Data Hiding

**Encapsulation** is a fancy word for a simple idea: **hiding the complex parts and showing only what's needed**.

Think of a car: You don't need to know how the engine works internally. You just need to know how to use the steering wheel, pedals, and gear shift. The complex engine details are "hidden" or "encapsulated".

In programming, encapsulation means:

1. **Hiding internal data** (like a car hiding its engine complexity)
2. **Providing simple methods to use** (like a car providing a steering wheel)
3. **Protecting data from being changed incorrectly** (like a car not letting you put water in the gas tank)

### Public vs Private Attributes

In Python, we use naming conventions to indicate whether something should be used from outside:

```python
class Person:
    """A person with a publicly visible name and private age."""

    def __init__(self, name, age):
        self.name = name      # Public - anyone can see and change
        self._age = age       # Private (by convention) - internal use only

    def get_age(self):
        """Public method to get the age."""
        return self._age

    def have_birthday(self):
        """Public method to increase age."""
        self._age += 1

# Using the class
person = Person("Alice", 30)

# Public attribute - OK to use
print(person.name)  # Output: "Alice"
person.name = "Alice Smith"  # OK to change

# Private attribute - we CAN access it, but we SHOULDN'T
print(person._age)  # Works, but discouraged

# Better: Use the public methods
print(person.get_age())  # Output: 30 (proper way)
person.have_birthday()
print(person.get_age())  # Output: 31
```

Now let's see a more realistic example with a bank account:

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
from typing import Optional, Dict, Any

class SnowflakeConnection:
    def __init__(self, account: str, user: Optional[str] = None):
        self.account = account          # Public - users need this
        self.user = user                # Public - often part of info
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
            'connected': (self.connection is not None)
        }

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Run a query and return mock results."""
        user_id = params[0] if params else 0
        return [{"id": user_id, "name": "Example", "email": "example@example.com"}]
```

**Why this design?**

- Public attributes (`account`, `connection`) are part of the API
- Private attributes (`_initialized`) are implementation details
- Properties provide controlled access to internal state
- Can add validation or computation without changing the interface

---

## Inheritance

### What is Inheritance?

**Inheritance** is like family traits. Just as you inherit your parents' traits (like eye color), classes can inherit features from other classes.

Think of it this way:

- You have a general **"Animal"** class with basic features (eating, sleeping, moving)
- Then you create a **"Dog"** class that inherits from Animal
- Dog automatically gets all Animal features, PLUS you can add dog-specific things (barking, fetching)

**Why use inheritance?**

- **Avoid repetition**: Don't rewrite the same code for similar things
- **Organize code**: Group related classes together
- **Easy to extend**: Add new types without changing existing code

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

**Try it yourself!** Create a `Bird` class that inherits from `Animal`:

- Override `speak()` to return "{name} says Tweet!"
- Add a `fly()` method
- Create a bird and test all its methods (including inherited ones like `move()`)

<details>
<summary>Click to see solution</summary>

```python
class Bird(Animal):
    """Bird is a type of Animal."""

    def __init__(self, name):
        super().__init__(name, "Aves")

    def speak(self):
        """Override speak method."""
        return f"{self.name} says Tweet!"

    def fly(self):
        """New method specific to birds."""
        self.energy -= 10
        return f"{self.name} is flying"

# Test it
tweety = Bird("Tweety")
print(tweety.speak())  # "Tweety says Tweet!"
print(tweety.fly())    # "Tweety is flying"
print(tweety.move())   # "Tweety is moving" (inherited from Animal!)
print(tweety.energy)   # Energy decreased from both fly() and move()
```

</details>

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

Note: For diamond-problem details and cooperative multiple inheritance with `super()`, see the advanced guide `advanced_oop_concepts.md`.

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
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent):
    """Snowflake implementation of DatabaseConnection."""

    def connect(self) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake."""
        self.connection = snowflake.connector.connect(
            account=self.account,
            user=self.user,
            # ... other parameters
        )
        return self.connection

    def disconnect(self) -> None:
        """Close Snowflake connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

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

**Polymorphism** is another fancy word for a simple idea: **different things responding to the same command in their own way**.

Think about a "speak" command:

- Tell a dog to speak → "Woof!"
- Tell a cat to speak → "Meow!"
- Tell a duck to speak → "Quack!"

They all respond to "speak", but each in their own way. That's polymorphism!

In programming terms: **different classes can be used interchangeably if they have the same methods**.

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
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseMonitor(ABC):
    """Base class for all monitors."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def check(self) -> Dict[str, Any]:
        """Perform monitoring check."""
        raise NotImplementedError


class SnowflakeMonitor(BaseMonitor):
    """Snowflake-specific monitor."""

    def __init__(self, name: str, account: str, timeout: Optional[int] = None):
        super().__init__(name)
        self.account = account
        self.timeout = timeout

    def check(self) -> Dict[str, Any]:
        return {
            "monitor": self.name,
            "type": "snowflake",
            "account": self.account,
            "timeout": self.timeout,
            "status": "ok",
        }


class PostgreSQLMonitor(BaseMonitor):
    """PostgreSQL-specific monitor."""

    def __init__(self, name: str, host: str):
        super().__init__(name)
        self.host = host

    def check(self) -> Dict[str, Any]:
        return {
            "monitor": self.name,
            "type": "postgres",
            "host": self.host,
            "status": "ok",
        }


# Polymorphism in action
def run_monitoring(monitors: List[BaseMonitor]):
    """Run all monitors, regardless of type."""
    for monitor in monitors:
        result = monitor.check()  # Works for any monitor!
        print(f"Monitor result: {result}")


# All monitors can be used the same way
monitors = [
    SnowflakeMonitor(name="sf_prod", account="prod_account"),
    PostgreSQLMonitor(name="pg_local", host="localhost"),
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

An **Abstract Base Class (ABC)** is like a promise or contract. It says: "Any class that inherits from me MUST implement these specific methods."

Think of it like a job description:

- Job Description (ABC): "All employees must be able to: work(), take_breaks(), report_progress()"
- Actual Employee (Concrete Class): Implements those methods in their specific way

**Why is this useful?**

- **Enforces rules**: Makes sure all similar classes have the same methods
- **Prevents mistakes**: You get an error immediately if you forget to implement a required method
- **Clear documentation**: Makes it obvious what methods a class should have

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

SOLID is an acronym for five important principles that help you write better object-oriented code. Don't worry if they seem complex at first - we'll explain each one with simple examples!

**Why learn SOLID?**

- Your code will be easier to understand
- Changes will be easier to make
- You'll have fewer bugs
- Your code will be more professional

The SOLID principles are five fundamental design principles that make software designs more understandable, flexible, and maintainable.

### SOLID at a Glance

```
┌────────────────────────────────────────────────────────────────────┐
│                      SOLID PRINCIPLES                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  S - Single Responsibility Principle                                │
│      │                                                              │
│      └──▶ One class = One job = One reason to change               │
│           "Do one thing and do it well"                             │
│                                                                     │
│  O - Open/Closed Principle                                          │
│      │                                                              │
│      └──▶ Open for extension, Closed for modification              │
│           "Add new features without changing existing code"         │
│                                                                     │
│  L - Liskov Substitution Principle                                  │
│      │                                                              │
│      └──▶ Subclass should work wherever parent works               │
│           "Don't break parent's promises"                           │
│                                                                     │
│  I - Interface Segregation Principle                                │
│      │                                                              │
│      └──▶ Many specific interfaces > One general interface         │
│           "Don't force classes to implement unused methods"         │
│                                                                     │
│  D - Dependency Inversion Principle                                 │
│      │                                                              │
│      └──▶ Depend on abstractions, not concretions                  │
│           "Use interfaces/protocols, not concrete classes"          │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘

Quick Decision Guide:

  Your class does multiple things? ──────────▶ Violates SRP
       │
       └─ Split into multiple classes


  Adding feature requires editing existing code? ─▶ Violates OCP
       │
       └─ Use inheritance, polymorphism, or composition


  Subclass changes parent behavior? ─────────▶ Violates LSP
       │
       └─ Redesign hierarchy or use composition


  Interface forces unused methods? ──────────▶ Violates ISP
       │
       └─ Split into smaller, focused interfaces


  High-level depends on low-level details? ──▶ Violates DIP
       │
       └─ Introduce abstraction layer (Protocol/ABC)
```

### 1. Single Responsibility Principle (SRP)

**Simple version:** Each class should do ONE thing and do it well.

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

**Simple version:** You should be able to add new features without changing existing code.

Think of it like a USB port: You can plug in new devices (extension) without modifying the computer (modification).

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

**Simple version:** If you have a class that works with a parent type, it should also work with any child type.

Think: If your code works with "Animals", it should work with any specific animal (Dog, Cat, etc.) without breaking.

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

**Simple version:** Don't force classes to implement methods they don't need.

Think: A robot worker shouldn't be forced to have an `eat()` method - only human workers need that!

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

**Simple version:** Depend on abstractions (interfaces/ABCs), not specific implementations.

Think: Your TV remote (high-level) works with any TV that has infrared (abstraction), not just one specific TV brand.

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

This is a common question: "Should I use inheritance or composition?" Here's a simple way to decide:

**Inheritance (IS-A relationship):**

- A Dog **IS AN** Animal → Use inheritance
- A Cat **IS AN** Animal → Use inheritance
- Think: "Can I say X IS A Y?"

**Composition (HAS-A relationship):**

- A Car **HAS AN** Engine → Use composition
- A Person **HAS A** Name → Use composition
- Think: "Can I say X HAS A Y?"

**Rule of thumb:** If you're unsure, prefer composition! It's more flexible.

### Visual Decision Tree

```
                    Need to reuse code/behavior?
                              |
                              v
                    ┌─────────┴─────────┐
                    |                   |
                    v                   v
            Does X IS-A Y?       Does X HAS-A Y?
                    |                   |
                    v                   v
                 ┌──┴──┐            ┌───┴───┐
                 |     |            |       |
               YES    NO           YES     NO
                 |     |            |       |
                 v     v            v       v
            Inheritance  \    Composition   \
               ✓          \        ✓         \
                           \                  \
                            └──────┬───────────┘
                                   |
                                   v
                          Consider Interfaces/
                           Protocols instead


┌─────────────────────────────────────────────────────────┐
│  COMPOSITION                   vs.      INHERITANCE      │
├─────────────────────────────────────────────────────────┤
│  Flexible                               Rigid            │
│  Runtime behavior changes               Compile-time     │
│  Multiple "has-a" relationships         Single parent    │
│  Loose coupling                         Tight coupling   │
│  Easy to test (inject deps)             Harder to test   │
│  Prefer by default                      Use sparingly    │
└─────────────────────────────────────────────────────────┘

          COMPOSITION                    INHERITANCE
               │                             │
               │                             │
    ┌──────────┴──────────┐       ┌─────────┴────────┐
    │                     │       │                  │
    v                     v       v                  v
  Car                   Person   Dog                Cat
 ┌───┐                 ┌────┐   └────┬────┘     └────┬────┘
 │   │──HAS-A──▶Engine │    │           │                │
 │   │                  │    │           └────IS-A───────┘
 │   │──HAS-A──▶GPS     │    │──HAS-A──▶Name            │
 └───┘                  └────┘                         Animal
```

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

### 5. Composite Pattern

Treat individual objects (leaves) and compositions (groups) uniformly.

```python
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def size(self) -> int: ...
    @abstractmethod
    def show(self, indent: int = 0) -> None: ...

class File(Node):  # Leaf
    def __init__(self, name: str, size: int):
        self.name, self._size = name, size
    def size(self) -> int:
        return self._size
    def show(self, indent: int = 0) -> None:
        print(" " * indent + f"- {self.name} ({self._size} bytes)")

class Directory(Node):  # Composite
    def __init__(self, name: str):
        self.name = name
        self.children: list[Node] = []
    def add(self, node: Node) -> None:
        self.children.append(node)
    def size(self) -> int:
        return sum(child.size() for child in self.children)
    def show(self, indent: int = 0) -> None:
        print(" " * indent + f"+ {self.name}/ ({self.size()} bytes)")
        for child in self.children:
            child.show(indent + 2)

# Usage
root = Directory("root")
docs = Directory("docs")
root.add(File("readme.txt", 1200))
docs.add(File("guide.md", 5000))
root.add(docs)

root.show()
# Both File and Directory share the same interface (size, show)
```

When to use:

- Tree structures (files/dirs, UI widgets, organization charts) where you want a uniform API.

Pitfalls:

- Mutability: be careful with shared children; consider making leaves immutable.

### 6. State Pattern

Let an object change its behavior when its internal state changes—object appears to change class.

```python
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def send(self, ctx, data: str) -> str: ...

class Disconnected(State):
    def send(self, ctx, data: str) -> str:
        ctx.state = Connected()  # auto-connect for demo
        return "connecting... then sending: " + data

class Connected(State):
    def send(self, ctx, data: str) -> str:
        return "sent: " + data

class Client:
    def __init__(self):
        self.state: State = Disconnected()
    def send(self, data: str) -> str:
        return self.state.send(self, data)

# Usage
c = Client()
print(c.send("hello"))  # connects, then sends
print(c.send("world"))  # already connected, sends directly
```

When to use:

- Objects with clear modes (disconnected/connected, draft/published) where behavior varies by mode.

Pitfalls:

- Too many tiny state classes can add overhead; keep transitions clear and documented.

### 7. Proxy Pattern

Provide a placeholder to control access to another object (lazy load, caching, access control, remote proxy).

```python
class ImageRepository:
    def get(self, image_id: str) -> bytes:
        print("fetching from origin...")
        return b"<image-bytes>"  # pretend expensive IO

class CachingRepoProxy:
    def __init__(self, repo: ImageRepository):
        self._repo = repo
        self._cache: dict[str, bytes] = {}
    def get(self, image_id: str) -> bytes:
        if image_id not in self._cache:
            self._cache[image_id] = self._repo.get(image_id)
        return self._cache[image_id]

# Usage
repo = CachingRepoProxy(ImageRepository())
repo.get("logo")  # hits origin
repo.get("logo")  # served from cache
```

When to use:

- Remote calls, expensive loads, access control, logging, rate limiting.

Pitfalls:

- Keep proxy responsibilities focused; otherwise it drifts into a God object.

### 8. Visitor Pattern

Separate algorithms from the objects they operate on. Add new operations without modifying the classes.

```python
from abc import ABC, abstractmethod

class Visitable(ABC):
    @abstractmethod
    def accept(self, v): ...

class File(Visitable):
    def __init__(self, name: str):
        self.name = name
    def accept(self, v):
        return v.visit_file(self)

class Directory(Visitable):
    def __init__(self, name: str, children: list[Visitable] | None = None):
        self.name = name
        self.children = children or []
    def accept(self, v):
        return v.visit_directory(self)

class CountVisitor:
    def visit_file(self, f: File) -> int:
        return 1
    def visit_directory(self, d: Directory) -> int:
        return sum(child.accept(self) for child in d.children)

# Usage
tree = Directory("root", [File("a"), Directory("docs", [File("g1"), File("g2")])])
total = tree.accept(CountVisitor())
print(total)  # 3
```

When to use:

- Stable hierarchies where you frequently add new operations over the structure.

Pitfalls:

- Adding new element types requires updating all visitors (trade-off vs adding new operations).

### Other patterns to explore

- Adapter: Make incompatible interfaces work together (wrap/translate).
- Facade: Provide a simple API over a complex subsystem.
- Command: Encapsulate an action as an object (undo/redo, queues).
- Chain of Responsibility: Pass requests along a chain until handled.
- Mediator: Centralize complex communication among many objects.
- Memento: Capture/restore object state (snapshots, undo).
- Builder: Step-by-step object construction with fluent APIs.
- Prototype: Clone existing objects to create new ones.

---

## Advanced OOP Concepts

### Context Managers

**Context managers** ensure resources are properly managed (opened, closed, cleaned up) even when errors occur. They're Python's way of handling setup and teardown automatically.

#### Basic Context Manager Protocol

Implement `__enter__` and `__exit__` to create a context manager:

```python
class FileManager:
    """Basic file manager context manager."""

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        """Called when entering 'with' block."""
        print(f"Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file  # This is what 'as f' receives

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block (always!)."""
        print(f"Closing {self.filename}")
        if self.file:
            self.file.close()
        # Return False to propagate exceptions
        return False

# Usage
with FileManager("test.txt", "w") as f:
    f.write("Hello, World!")
# File is automatically closed, even if an exception occurs!
```

#### Understanding `__exit__` Parameters

The `__exit__` method receives information about any exception that occurred:

```python
class ExceptionHandler:
    """Demonstrates __exit__ parameters."""

    def __enter__(self):
        print("Entering context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        exc_type: Exception class (e.g., ValueError) or None
        exc_val: Exception instance or None
        exc_tb: Traceback object or None
        """
        if exc_type is None:
            print("Exited normally (no exception)")
        else:
            print(f"Exception occurred: {exc_type.__name__}: {exc_val}")

        # Return True to suppress the exception
        # Return False (or None) to propagate it
        return False

# Normal exit
with ExceptionHandler():
    print("No error")

# Exception exit
try:
    with ExceptionHandler():
        raise ValueError("Something went wrong!")
except ValueError:
    print("Exception propagated")
```

#### Suppressing Exceptions

```python
class ErrorSuppressor:
    """Context manager that suppresses specific exceptions."""

    def __init__(self, *exception_types):
        self.exception_types = exception_types
        self.exception_caught = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and issubclass(exc_type, self.exception_types):
            self.exception_caught = exc_val
            print(f"Suppressed {exc_type.__name__}: {exc_val}")
            return True  # Suppress the exception
        return False  # Don't suppress other exceptions

# Usage
with ErrorSuppressor(ValueError, TypeError) as suppressor:
    int("not a number")  # ValueError - suppressed
    print("This line executes!")

print(f"Caught: {suppressor.exception_caught}")
```

#### Resource Management with Cleanup

```python
import tempfile
import os

class TemporaryDirectory:
    """Create and cleanup a temporary directory."""

    def __init__(self):
        self.path = None

    def __enter__(self):
        """Create temporary directory."""
        self.path = tempfile.mkdtemp()
        print(f"Created temp directory: {self.path}")
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Delete temporary directory and all contents."""
        if self.path and os.path.exists(self.path):
            # Clean up all files
            for root, dirs, files in os.walk(self.path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.path)
            print(f"Cleaned up temp directory: {self.path}")
        return False

# Usage
with TemporaryDirectory() as temp_dir:
    # Create temporary files
    temp_file = os.path.join(temp_dir, "data.txt")
    with open(temp_file, "w") as f:
        f.write("temporary data")
    print(f"Using {temp_file}")
# temp_dir is automatically deleted here!
```

#### Nested Context Managers

```python
class Timer:
    """Context manager to time code execution."""

    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        print(f"Starting {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.time() - self.start_time
        print(f"{self.name} took {self.elapsed:.4f} seconds")
        return False

class ResourceLock:
    """Simulated resource lock."""

    def __init__(self, resource_name):
        self.resource_name = resource_name

    def __enter__(self):
        print(f"Acquired lock on {self.resource_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Released lock on {self.resource_name}")
        return False

# Multiple context managers in one 'with' statement
with Timer("Database operation"), ResourceLock("users_table"):
    print("Doing work...")
    import time
    time.sleep(0.1)
```

#### Using `contextlib` for Simple Context Managers

The `contextlib` module provides utilities for creating context managers:

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    """Generator-based context manager (simpler!)."""
    print(f"Opening {filename}")
    file = open(filename, mode)
    try:
        yield file  # Provide file to 'with' block
    finally:
        print(f"Closing {filename}")
        file.close()

# Usage
with file_manager("test.txt", "w") as f:
    f.write("Hello from contextlib!")
```

#### Advanced Example: Database Connection Pool

```python
import threading
from contextlib import contextmanager

class ConnectionPool:
    """Thread-safe database connection pool."""

    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.available = []
        self.in_use = set()
        self.lock = threading.Lock()

    def __enter__(self):
        """Initialize pool when entering context."""
        for i in range(self.max_connections):
            self.available.append(f"Connection-{i}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all connections."""
        with self.lock:
            # Close all connections
            all_conns = self.available + list(self.in_use)
            for conn in all_conns:
                print(f"Closing {conn}")
            self.available.clear()
            self.in_use.clear()
        return False

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)."""
        conn = None
        with self.lock:
            if not self.available:
                raise RuntimeError("No available connections")
            conn = self.available.pop()
            self.in_use.add(conn)

        try:
            print(f"Using {conn}")
            yield conn
        finally:
            with self.lock:
                self.in_use.remove(conn)
                self.available.append(conn)
            print(f"Returned {conn}")

# Usage
with ConnectionPool(max_connections=2) as pool:
    # Use connection 1
    with pool.get_connection() as conn1:
        print(f"Working with {conn1}")

    # Use connection 2
    with pool.get_connection() as conn2:
        print(f"Working with {conn2}")
# All connections closed automatically
```

#### Practical Example: Atomic File Operations

```python
import os
import tempfile
import shutil

class AtomicWrite:
    """Write to a file atomically (all-or-nothing)."""

    def __init__(self, filename):
        self.filename = filename
        self.temp_file = None
        self.temp_name = None

    def __enter__(self):
        """Create temporary file for writing."""
        # Create temp file in same directory for atomic rename
        directory = os.path.dirname(self.filename) or '.'
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            dir=directory,
            delete=False
        )
        self.temp_name = self.temp_file.name
        return self.temp_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close and rename temp file, or delete on error."""
        self.temp_file.close()

        if exc_type is None:
            # Success - atomically replace original file
            shutil.move(self.temp_name, self.filename)
            print(f"Atomically wrote to {self.filename}")
        else:
            # Error - remove temp file
            os.unlink(self.temp_name)
            print(f"Error occurred, temp file removed")

        return False  # Propagate any exceptions

# Usage
try:
    with AtomicWrite("important_data.txt") as f:
        f.write("Line 1\n")
        f.write("Line 2\n")
        # If error occurs here, original file is unchanged!
        # raise RuntimeError("Oops!")
        f.write("Line 3\n")
    print("File written successfully")
except Exception as e:
    print(f"Failed to write file: {e}")
```

#### Common Pitfalls

```python
# ❌ WRONG: Not returning anything from __exit__
class BadContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Cleanup")
        # Implicitly returns None (False), which is correct
        # But explicit is better than implicit!

# ✅ CORRECT: Explicitly return False or True
class GoodContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Cleanup")
        return False  # Explicit!

# ❌ WRONG: Forgetting to handle cleanup in __exit__
class ForgetsCleanup:
    def __enter__(self):
        self.resource = open("file.txt", "w")
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Oops! File never closed!

# ✅ CORRECT: Always cleanup
class RemembersCleanup:
    def __enter__(self):
        self.resource = open("file.txt", "w")
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.resource:
            self.resource.close()  # Always cleanup!
        return False
```

**When to use context managers:**

- File I/O operations
- Database connections and transactions
- Network connections (sockets, HTTP sessions)
- Locks and synchronization primitives
- Temporary resources (files, directories)
- Any resource that needs guaranteed cleanup

### Descriptors

**Descriptors** are a powerful Python feature that lets you customize attribute access. They're the mechanism behind properties, methods, and many advanced Python features.

#### The Descriptor Protocol

A descriptor is any object that implements at least one of these methods:

- `__get__(self, instance, owner)` - Get attribute value
- `__set__(self, instance, value)` - Set attribute value
- `__delete__(self, instance)` - Delete attribute

```python
class Descriptor:
    """Basic descriptor demonstrating all three methods."""

    def __init__(self, name=None):
        self.name = name

    def __set_name__(self, owner, name):
        """Called automatically when descriptor is assigned to a class attribute."""
        self.name = name

    def __get__(self, instance, owner):
        """
        instance: The instance accessing the attribute (None if accessed via class)
        owner: The class that owns this descriptor
        """
        if instance is None:
            return self  # Accessed via class, return descriptor itself
        print(f"Getting {self.name} from {instance}")
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        """Set the attribute value."""
        print(f"Setting {self.name} to {value}")
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        """Delete the attribute."""
        print(f"Deleting {self.name}")
        del instance.__dict__[self.name]

class MyClass:
    attr = Descriptor()  # __set_name__ is called automatically

    def __init__(self, attr):
        self.attr = attr  # Calls __set__

# Usage
obj = MyClass(42)  # "Setting attr to 42"
print(obj.attr)    # "Getting attr from ...", then prints 42
del obj.attr       # "Deleting attr"
```

#### Validation Descriptor

```python
class ValidatedAttribute:
    """Descriptor for validating attribute values."""

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Store value in instance.__dict__ with a private name
        return instance.__dict__.get(f'_{self.name}')

    def __set__(self, instance, value):
        # Validate before setting
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")
        instance.__dict__[f'_{self.name}'] = value

class Person:
    age = ValidatedAttribute(min_value=0, max_value=150)
    height = ValidatedAttribute(min_value=0, max_value=300)  # cm

    def __init__(self, name, age, height):
        self.name = name
        self.age = age      # Calls ValidatedAttribute.__set__
        self.height = height

# Usage
person = Person("Alice", 30, 165)
print(person.age)     # 30
person.age = 31       # OK
# person.age = -5     # ValueError: age must be >= 0
# person.age = 200    # ValueError: age must be <= 150
```

#### Type-Checking Descriptor

```python
class TypedAttribute:
    """Descriptor that enforces type checking."""

    def __init__(self, expected_type):
        self.expected_type = expected_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(f'_{self.name}')

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"not {type(value).__name__}"
            )
        instance.__dict__[f'_{self.name}'] = value

class User:
    name = TypedAttribute(str)
    age = TypedAttribute(int)
    email = TypedAttribute(str)

    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

# Usage
user = User("Alice", 30, "alice@example.com")
user.age = 31  # OK
# user.age = "thirty"  # TypeError: age must be int, not str
```

#### Lazy-Loading Descriptor

```python
class LazyProperty:
    """Descriptor that computes value only once (lazy loading)."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # Check if value already computed
        if self.name not in instance.__dict__:
            # Compute and cache the value
            print(f"Computing {self.name}...")
            value = self.func(instance)
            instance.__dict__[self.name] = value

        return instance.__dict__[self.name]

class DataAnalyzer:
    def __init__(self, data):
        self.data = data

    @LazyProperty
    def mean(self):
        """Compute mean (expensive operation)."""
        return sum(self.data) / len(self.data)

    @LazyProperty
    def sorted_data(self):
        """Sort data (expensive operation)."""
        return sorted(self.data)

# Usage
analyzer = DataAnalyzer([5, 2, 8, 1, 9])
print("Analyzer created")
print(analyzer.mean)         # "Computing mean...", then 5.0
print(analyzer.mean)         # 5.0 (no recomputation!)
print(analyzer.sorted_data)  # "Computing sorted_data...", then [1, 2, 5, 8, 9]
print(analyzer.sorted_data)  # [1, 2, 5, 8, 9] (cached!)
```

#### Read-Only Descriptor

```python
class ReadOnly:
    """Descriptor for read-only attributes."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func(instance)

    def __set__(self, instance, value):
        raise AttributeError(f"'{self.name}' is read-only")

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @ReadOnly
    def diameter(self):
        """Computed property (read-only)."""
        return self._radius * 2

    @ReadOnly
    def area(self):
        """Computed property (read-only)."""
        import math
        return math.pi * self._radius ** 2

# Usage
circle = Circle(5)
print(circle.diameter)  # 10
print(circle.area)      # 78.53981633974483
# circle.diameter = 20  # AttributeError: 'diameter' is read-only
```

#### Descriptor for Caching with Expiration

```python
import time

class CachedProperty:
    """Descriptor with time-based cache expiration."""

    def __init__(self, ttl=60):
        """
        ttl: Time to live in seconds
        """
        self.ttl = ttl
        self.func = None
        self.name = None

    def __call__(self, func):
        """Allow using as decorator."""
        self.func = func
        self.name = func.__name__
        return self

    def __get__(self, instance, owner):
        if instance is None:
            return self

        cache_key = f'_{self.name}_cache'
        timestamp_key = f'_{self.name}_timestamp'

        current_time = time.time()
        cached_time = instance.__dict__.get(timestamp_key, 0)

        # Check if cache is expired
        if current_time - cached_time > self.ttl:
            print(f"Cache expired for {self.name}, recomputing...")
            value = self.func(instance)
            instance.__dict__[cache_key] = value
            instance.__dict__[timestamp_key] = current_time

        return instance.__dict__[cache_key]

class APIClient:
    def __init__(self):
        self.call_count = 0

    @CachedProperty(ttl=2)  # Cache for 2 seconds
    def user_count(self):
        """Expensive API call (simulated)."""
        self.call_count += 1
        print(f"Making API call #{self.call_count}...")
        time.sleep(0.1)  # Simulate network delay
        return 42

# Usage
client = APIClient()
print(client.user_count)  # "Making API call #1...", then 42
print(client.user_count)  # 42 (cached)
time.sleep(2.5)
print(client.user_count)  # "Cache expired...", "Making API call #2...", then 42
```

#### Descriptors vs Properties

**When to use each:**

```python
# Use @property for simple, instance-specific logic
class SimpleClass:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        """Simple computed property."""
        return self._value * 2

# Use descriptors for reusable, class-level attribute behavior
class ReusableValidation:
    """Can be used across many classes."""
    positive = ValidatedAttribute(min_value=0)
    percentage = ValidatedAttribute(min_value=0, max_value=100)
```

**Key differences:**

- **Property**: Defined per-class, not reusable
- **Descriptor**: Defined once, reusable across classes
- **Property**: Simpler for one-off cases
- **Descriptor**: Better for repeated patterns

#### Common Use Cases for Descriptors

1. **Validation**: Type checking, range validation, format validation
2. **Lazy Loading**: Compute expensive values only when needed
3. **Caching**: Store computed values to avoid recomputation
4. **Logging**: Track attribute access and modifications
5. **Type Conversion**: Automatically convert types on assignment
6. **ORM Fields**: Database column definitions (like Django models)
7. **API Client**: Lazy connection initialization

#### Real-World Example: ORM-Style Field

```python
class Field:
    """Base descriptor for database fields."""

    def __init__(self, field_type, default=None):
        self.field_type = field_type
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"{self.name} must be {self.field_type.__name__}")
        instance.__dict__[self.name] = value

class IntegerField(Field):
    def __init__(self, default=0, min_value=None, max_value=None):
        super().__init__(int, default)
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, instance, value):
        super().__set__(instance, value)
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"{self.name} must be >= {self.min_value}")
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"{self.name} must be <= {self.max_value}")

class StringField(Field):
    def __init__(self, default="", max_length=None):
        super().__init__(str, default)
        self.max_length = max_length

    def __set__(self, instance, value):
        super().__set__(instance, value)
        if value is not None and self.max_length and len(value) > self.max_length:
            raise ValueError(f"{self.name} must be <= {self.max_length} characters")

class Product:
    """ORM-style model class."""
    id = IntegerField(min_value=1)
    name = StringField(max_length=100)
    price = IntegerField(min_value=0)
    quantity = IntegerField(default=0, min_value=0)

    def __init__(self, id, name, price, quantity=0):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

# Usage
product = Product(1, "Laptop", 1200, 5)
print(f"{product.name}: ${product.price}")
# product.price = -100  # ValueError: price must be >= 0
# product.name = "A" * 200  # ValueError: name must be <= 100 characters
```

**Key Takeaway:** Descriptors are Python's most powerful attribute access mechanism. Use them when you need reusable attribute behavior across multiple classes.

### Metaclasses

Metaclasses are "classes of classes" that can control how classes are created or modified (e.g., automatic registration, API generation, singletons, attribute validation). They are powerful but easy to overuse. Prefer decorators, descriptors, or simple registries unless a metaclass is clearly the right tool. For worked examples and best practices, see `advanced_oop_concepts.md` (Advanced Metaclass Usage).

---

### Class Decorators

**Class decorators** are functions that take a class and return a modified class. They're simpler than metaclasses and should be your first choice for class transformation.

#### Basic Class Decorator

```python
def add_repr(cls):
    """Decorator that adds a __repr__ method to a class."""
    def __repr__(self):
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"

    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(p)  # Point(x=3, y=4)
```

#### Auto-Registration Pattern

A common use case is automatically registering classes:

```python
class Registry:
    """Global registry for plugins."""
    _plugins = {}

    @classmethod
    def register(cls, name):
        """Decorator to register a plugin class."""
        def decorator(plugin_class):
            cls._plugins[name] = plugin_class
            plugin_class.plugin_name = name  # Add attribute
            return plugin_class
        return decorator

    @classmethod
    def get_plugin(cls, name):
        """Get a registered plugin by name."""
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls):
        """List all registered plugins."""
        return list(cls._plugins.keys())

# Using the decorator
@Registry.register('email')
class EmailNotifier:
    def send(self, message):
        print(f"Sending email: {message}")

@Registry.register('sms')
class SMSNotifier:
    def send(self, message):
        print(f"Sending SMS: {message}")

# Usage
print(Registry.list_plugins())  # ['email', 'sms']
notifier = Registry.get_plugin('email')()
notifier.send("Hello!")  # "Sending email: Hello!"
```

#### Validation and Enforcement

```python
def require_methods(*method_names):
    """Decorator that ensures a class implements required methods."""
    def decorator(cls):
        for method_name in method_names:
            if not hasattr(cls, method_name):
                raise TypeError(
                    f"{cls.__name__} must implement {method_name}() method"
                )
            method = getattr(cls, method_name)
            if not callable(method):
                raise TypeError(
                    f"{cls.__name__}.{method_name} must be callable"
                )
        return cls
    return decorator

@require_methods('process', 'validate')
class DataProcessor:
    def process(self, data):
        return data.upper()

    def validate(self, data):
        return isinstance(data, str)

# This would raise TypeError: MissingMethod must implement process() method
# @require_methods('process', 'validate')
# class MissingMethod:
#     pass
```

#### Adding Functionality

```python
def singleton(cls):
    """Decorator that makes a class a singleton."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, host):
        self.host = host
        print(f"Creating connection to {host}")

# Both are the same instance!
db1 = DatabaseConnection("localhost")  # "Creating connection to localhost"
db2 = DatabaseConnection("localhost")  # No output - reuses existing
print(db1 is db2)  # True
```

#### Parametrized Class Decorators

```python
def add_method(method_name, method_impl):
    """Decorator that adds a method to a class."""
    def decorator(cls):
        setattr(cls, method_name, method_impl)
        return cls
    return decorator

def greet(self):
    return f"Hello, I'm {self.name}"

@add_method('greet', greet)
class Person:
    def __init__(self, name):
        self.name = name

p = Person("Alice")
print(p.greet())  # "Hello, I'm Alice"
```

#### Timing and Performance Tracking

```python
import time
import functools

def track_calls(cls):
    """Decorator that tracks method calls and timing."""
    original_methods = {}

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            original_methods[attr_name] = attr

    for method_name, method in original_methods.items():
        @functools.wraps(method)
        def wrapper(*args, _method=method, _name=method_name, **kwargs):
            start = time.time()
            result = _method(*args, **kwargs)
            elapsed = time.time() - start
            print(f"{_name} took {elapsed:.4f}s")
            return result

        setattr(cls, method_name, wrapper)

    return cls

@track_calls
class DataAnalyzer:
    def process(self, data):
        time.sleep(0.1)  # Simulate work
        return len(data)

    def validate(self, data):
        time.sleep(0.05)  # Simulate work
        return isinstance(data, list)

analyzer = DataAnalyzer()
analyzer.process([1, 2, 3])  # "process took 0.1001s"
analyzer.validate([1, 2])    # "validate took 0.0501s"
```

#### When to Use Class Decorators vs Metaclasses

**Use Class Decorators when:**

- You need to modify or add attributes/methods after class creation
- You want simple, readable transformations
- You're registering classes
- You're adding validation or type checking
- You want to wrap methods

**Use Metaclasses when:**

- You need to control class creation itself (before the class exists)
- You need to modify the class namespace during creation
- You're building a framework with complex class hierarchies
- You need to enforce rules across an entire class hierarchy

**Example: Equivalent functionality**

```python
# With class decorator (simpler!)
def add_id(cls):
    cls.class_id = id(cls)
    return cls

@add_id
class MyClass:
    pass

# With metaclass (more complex)
class AddIdMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        new_class.class_id = id(new_class)
        return new_class

class MyClass(metaclass=AddIdMeta):
    pass
```

**Rule of thumb:** Start with class decorators. Only use metaclasses if decorators can't solve your problem.

---

### Thread-safety basics

When classes mutate shared state across threads, protect critical sections:

```python
import threading

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    def increment(self):
        with self._lock:
            self._value += 1
    @property
    def value(self):
        with self._lock:
            return self._value
```

Guidelines:

- Avoid exposing partially updated state; use locks or immutable snapshots.
- Prefer message-passing (queues) for complex coordination.
- Consider async (`asyncio`) for IO-bound concurrency.

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

#### Dataclass options and caveats

- `slots=True`: Generates slotted classes to reduce memory and speed up attribute access.
- `eq`, `order`, `frozen`, `unsafe_hash`: Control equality, ordering, immutability, and hashing.
- Mutable defaults: Always use `field(default_factory=list)` (or dict, set) to avoid shared mutable defaults.
- Interop: Dataclasses can be easily converted to dicts with `dataclasses.asdict` (but be mindful of nested objects).

Example with slots and ordering:

```python
from dataclasses import dataclass, field

@dataclass(slots=True, order=True)
class User:
    id: int
    name: str
    tags: list[str] = field(default_factory=list)
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

### The Python Data Model (Dunder Methods)

"Dunder" methods (short for "double underscore") are special methods that allow your custom objects to integrate with Python's built-in syntax and behaviors. Implementing them is key to creating idiomatic, "Pythonic" classes.

#### String Representation: `__str__` vs. `__repr__`

- **`__repr__(self)`**: Should return an **unambiguous**, developer-focused string representation of the object. Ideally, `eval(repr(obj)) == obj`. This is what you see in a debugger or when you type the object's name in a shell.
- **`__str__(self)`**: Should return a **readable**, user-focused string representation. This is what `print(obj)` and `str(obj)` use. If `__str__` is not defined, Python falls back to `__repr__`.

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        # Unambiguous, good for developers
        return f"Vector(x={self.x}, y={self.y})"

    def __str__(self):
        # Readable, good for users
        return f"({self.x}, {self.y})"

v = Vector(3, 4)
print(repr(v))  # Output: Vector(x=3, y=4)
print(str(v))   # Output: (3, 4)
print(v)        # print() uses __str__: (3, 4)
# In a Python shell, just typing 'v' would show the __repr__
```

#### Equality and Hashing: `__eq__` and `__hash__`

- **`__eq__(self, other)`**: Defines behavior for the equality operator (`==`). Without it, Python defaults to identity comparison (`is`), which is rarely what you want.
- **`__hash__(self)`**: Computes an integer hash for the object, allowing it to be used as a key in dictionaries and as an element in sets.

**Rule:** If you implement `__eq__`, you should also implement `__hash__` if your object is immutable. If the object is mutable, you should set `__hash__ = None` to make it unhashable.

```python
@dataclass(frozen=True) # frozen=True makes it immutable and auto-generates __hash__
class Point:
    x: int
    y: int

p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(3, 4)

print(p1 == p2)  # True, because __eq__ is implemented by dataclass

# Because Point is hashable, we can use it in a set or as a dict key
point_set = {p1, p2, p3}
print(len(point_set))  # 2, because p1 and p2 are considered equal

# For mutable classes:
class MutablePoint:
    __hash__ = None # Explicitly make it unhashable

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return isinstance(other, MutablePoint) and self.x == other.x and self.y == other.y

# {MutablePoint(1, 2)} would raise a TypeError
```

#### Making Your Class a Container: `__len__`, `__getitem__`, `__iter__`

Implement these methods to make your object behave like a sequence or collection.

```python
class Team:
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __len__(self):
        """Returns the number of members in the team."""
        return len(self.members)

    def __getitem__(self, position):
        """Allows accessing members by index, e.g., team[0]."""
        return self.members[position]

    def __iter__(self):
        """Allows iterating over the team, e.g., for member in team: ..."""
        return iter(self.members)

    def __contains__(self, member):
        """Allows using the 'in' operator, e.g., 'Alice' in team."""
        return member in self.members

# Usage
justice_league = Team("Justice League", ["Batman", "Superman", "Wonder Woman"])

print(f"The team has {len(justice_league)} members.") # Uses __len__
print(f"The first member is {justice_league[0]}.")   # Uses __getitem__

print("Is Batman on the team?", "Batman" in justice_league) # Uses __contains__

print("Team members:")
for member in justice_league: # Uses __iter__
    print(f"- {member}")
```

#### Numeric Operators: Making Objects Work with Math

You can make your objects work with `+`, `-`, `*`, etc:

```python
class Money:
    """Represent money amounts."""

    def __init__(self, dollars):
        self.dollars = dollars

    def __add__(self, other):
        """Enable: money1 + money2"""
        if isinstance(other, Money):
            return Money(self.dollars + other.dollars)
        return Money(self.dollars + other)

    def __sub__(self, other):
        """Enable: money1 - money2"""
        if isinstance(other, Money):
            return Money(self.dollars - other.dollars)
        return Money(self.dollars - other)

    def __repr__(self):
        return f"Money(${self.dollars})"

# Usage
wallet = Money(50)
bonus = Money(20)
total = wallet + bonus  # Uses __add__
print(total)  # Money($70)

remaining = total - Money(15)  # Uses __sub__
print(remaining)  # Money($55)
```

#### Comparison Operators: Making Objects Comparable

```python
class Student:
    """Student with comparable grades."""

    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __lt__(self, other):
        """Less than: student1 < student2"""
        return self.grade < other.grade

    def __le__(self, other):
        """Less than or equal: student1 <= student2"""
        return self.grade <= other.grade

    def __gt__(self, other):
        """Greater than: student1 > student2"""
        return self.grade > other.grade

    def __ge__(self, other):
        """Greater than or equal: student1 >= student2"""
        return self.grade >= other.grade

    def __eq__(self, other):
        """Equal: student1 == student2"""
        return self.grade == other.grade

    def __repr__(self):
        return f"{self.name}({self.grade})"

# Usage
alice = Student("Alice", 95)
bob = Student("Bob", 87)

print(alice > bob)  # True (95 > 87)
print(bob < alice)  # True (87 < 95)

# Can even sort students!
students = [Student("Charlie", 78), alice, bob]
students.sort()  # Uses __lt__ for sorting
print(students)  # Sorted by grade
```

#### Making Objects Callable: `__call__`

Make your objects behave like functions by implementing `__call__`:

```python
class Multiplier:
    """A callable object that multiplies by a factor."""

    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        """Called when instance is used like a function."""
        return value * self.factor

# Usage
times_five = Multiplier(5)
print(times_five(10))  # 50 - calling the object like a function!
print(times_five(3))   # 15

# Useful for stateful functions
class Counter:
    """Count how many times it's been called."""

    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return self.count

counter = Counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

**Real-world use cases:**

- Decorators that need to maintain state
- Function factories
- Callback objects with state
- Machine learning models (in frameworks like PyTorch, models are callable)

#### Attribute Access Control: `__getattr__`, `__setattr__`, `__delattr__`

Control what happens when attributes are accessed, set, or deleted:

```python
class DynamicAttributes:
    """Object that tracks all attribute access."""

    def __init__(self):
        # Use object.__setattr__ to avoid recursion
        object.__setattr__(self, '_data', {})
        object.__setattr__(self, '_access_log', [])

    def __getattr__(self, name):
        """Called when attribute is NOT found in normal places."""
        self._access_log.append(f"Getting {name}")
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"{name} not found")

    def __setattr__(self, name, value):
        """Called for ALL attribute assignments."""
        if name.startswith('_'):
            # Use object.__setattr__ for internal attributes
            object.__setattr__(self, name, value)
        else:
            self._access_log.append(f"Setting {name} = {value}")
            self._data[name] = value

    def __delattr__(self, name):
        """Called when del obj.attr is used."""
        self._access_log.append(f"Deleting {name}")
        if name in self._data:
            del self._data[name]

# Usage
obj = DynamicAttributes()
obj.name = "Alice"        # Calls __setattr__
print(obj.name)           # Calls __getattr__ -> "Alice"
del obj.name              # Calls __delattr__

print(obj._access_log)
# ['Setting name = Alice', 'Getting name', 'Deleting name']
```

**`__getattribute__` vs `__getattr__`:**

```python
class StrictAccess:
    """Demonstrates the difference between __getattr__ and __getattribute__."""

    def __init__(self):
        self.public = "visible"

    def __getattribute__(self, name):
        """Called for EVERY attribute access."""
        print(f"__getattribute__: Accessing {name}")
        # Must use object.__getattribute__ to avoid infinite recursion
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        """Only called if attribute NOT found by __getattribute__."""
        print(f"__getattr__: {name} not found, returning default")
        return "default_value"

obj = StrictAccess()
print(obj.public)     # Calls __getattribute__ only
print(obj.missing)    # Calls __getattribute__, then __getattr__
```

**⚠️ Warning:** Be very careful with `__setattr__` and `__getattribute__` - they can easily cause infinite recursion if not implemented correctly!

**Common use cases:**

- Lazy loading of attributes
- Proxies and wrappers
- ORMs (Object-Relational Mappers)
- Logging and debugging
- Access control and validation

#### Context Manager Protocol: `__enter__` and `__exit__`

Briefly covered here; see [Context Managers](#context-managers-for-resource-management) for full details.

```python
class Transaction:
    """Database transaction context manager."""

    def __enter__(self):
        print("Beginning transaction")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("Committing transaction")
        else:
            print(f"Rolling back transaction due to {exc_type.__name__}")
        return False  # Don't suppress exceptions

# Usage
with Transaction() as tx:
    print("Doing work...")
    # Transaction commits automatically
```

**Other common dunder methods:**

- **Numeric operators**: `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__floordiv__`, `__mod__`, `__pow__`
- **Comparison**: `__lt__`, `__le__`, `__gt__`, `__ge__`, `__eq__`, `__ne__`
- **Context Managers**: `__enter__`, `__exit__` (see dedicated section below)
- **Callable**: `__call__` (makes an object callable like a function)

### Type Hints and Protocols

#### Basic Protocols: Structural Typing

Protocols enable "duck typing" with type checking - if it walks like a duck and quacks like a duck, it's a duck:

```python
from typing import Protocol

class Drawable(Protocol):
    """Anything that can be drawn."""
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "Drawing a circle"

class Square:
    def draw(self) -> str:
        return "Drawing a square"

def draw_shape(shape: Drawable) -> None:
    """Works with any object that has a draw() method."""
    print(shape.draw())

# Both work without explicit inheritance!
draw_shape(Circle())  # "Drawing a circle"
draw_shape(Square())  # "Drawing a square"
```

**Protocols vs ABCs:**

- **Protocol**: Structural typing - "has these methods" (duck typing with types)
- **ABC**: Nominal typing - "declared as this type" (explicit inheritance)

#### Generic Classes: Type Parameters

Make your classes work with different types while maintaining type safety:

```python
from typing import Generic, TypeVar

T = TypeVar('T')  # Type variable

class Box(Generic[T]):
    """A box that can hold any type of item."""

    def __init__(self, item: T):
        self.item = item

    def get_item(self) -> T:
        return self.item

    def set_item(self, item: T) -> None:
        self.item = item

# Type checker knows box_int contains int
box_int: Box[int] = Box(42)
print(box_int.get_item())  # Type: int

# Type checker knows box_str contains str
box_str: Box[str] = Box("hello")
print(box_str.get_item())  # Type: str

# Type error! Can't put str in Box[int]
# box_int.set_item("wrong")  # Type checker catches this!
```

#### Multiple Type Variables

```python
from typing import Generic, TypeVar

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type

class Pair(Generic[K, V]):
    """A pair of values with different types."""

    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value

    def get_key(self) -> K:
        return self.key

    def get_value(self) -> V:
        return self.value

# String key, int value
pair1: Pair[str, int] = Pair("age", 30)
print(pair1.get_key())    # Type: str
print(pair1.get_value())  # Type: int

# Int key, list value
pair2: Pair[int, list[str]] = Pair(1, ["a", "b"])
print(pair2.get_value())  # Type: list[str]
```

#### Bounded Type Variables

Restrict what types can be used:

```python
from typing import TypeVar, Protocol, Generic

class Comparable(Protocol):
    """Protocol for objects that can be compared."""
    def __lt__(self, other) -> bool: ...

# T must be a subtype of Comparable
T = TypeVar('T', bound=Comparable)

class SortedList(Generic[T]):
    """A list that keeps items sorted."""

    def __init__(self):
        self._items: list[T] = []

    def add(self, item: T) -> None:
        """Add item in sorted position."""
        self._items.append(item)
        self._items.sort()  # Works because T is Comparable

    def get_items(self) -> list[T]:
        return self._items.copy()

# Works with int (comparable)
sorted_nums: SortedList[int] = SortedList()
sorted_nums.add(5)
sorted_nums.add(2)
sorted_nums.add(8)
print(sorted_nums.get_items())  # [2, 5, 8]
```

#### The `Self` Type (Python 3.11+)

Use `Self` to refer to the current class type in methods:

```python
from typing import Self  # Python 3.11+

class Builder:
    """Fluent builder pattern with proper typing."""

    def __init__(self):
        self.value = 0

    def add(self, n: int) -> Self:
        """Returns Self, not Builder."""
        self.value += n
        return self

    def multiply(self, n: int) -> Self:
        """Returns Self for method chaining."""
        self.value *= n
        return self

    def build(self) -> int:
        return self.value

class ExtendedBuilder(Builder):
    """Subclass with additional methods."""

    def subtract(self, n: int) -> Self:
        """Returns ExtendedBuilder, not Builder!"""
        self.value -= n
        return self

# Type checker knows result is ExtendedBuilder, not Builder
result = ExtendedBuilder().add(10).subtract(3).multiply(2).build()
print(result)  # 14
```

**Before Python 3.11:** Use `TypeVar` bound to the class:

```python
from typing import TypeVar

T = TypeVar('T', bound='Builder')

class Builder:
    def add(self: T, n: int) -> T:
        self.value += n
        return self
```

#### Generic Protocols

Combine Protocols with Generics:

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Container(Protocol[T]):
    """Protocol for containers holding type T."""

    def get(self) -> T: ...
    def put(self, item: T) -> None: ...

class StringBox:
    """Implements Container[str] implicitly."""

    def __init__(self):
        self._item: str = ""

    def get(self) -> str:
        return self._item

    def put(self, item: str) -> None:
        self._item = item

def process_container(container: Container[str]) -> str:
    """Works with any container of strings."""
    item = container.get()
    return item.upper()

box = StringBox()
box.put("hello")
print(process_container(box))  # "HELLO"
```

#### Type Narrowing with isinstance

```python
from typing import Union

class Dog:
    def bark(self) -> str:
        return "Woof!"

class Cat:
    def meow(self) -> str:
        return "Meow!"

def make_sound(animal: Union[Dog, Cat]) -> str:
    """Type checker understands isinstance."""
    if isinstance(animal, Dog):
        # Type narrowed to Dog here
        return animal.bark()
    else:
        # Type narrowed to Cat here
        return animal.meow()

print(make_sound(Dog()))  # "Woof!"
print(make_sound(Cat()))  # "Meow!"
```

#### Practical Example: Generic Repository

```python
from typing import Generic, TypeVar, Protocol, Optional
from abc import ABC, abstractmethod

T = TypeVar('T')

class Entity(Protocol):
    """Protocol for database entities."""
    id: int

class Repository(ABC, Generic[T]):
    """Generic repository for any entity type."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity to database."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass

class User:
    """User entity."""
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class UserRepository(Repository[User]):
    """Concrete repository for User entities."""

    def __init__(self):
        self._users: dict[int, User] = {}

    def get_by_id(self, id: int) -> Optional[User]:
        return self._users.get(id)

    def save(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def delete(self, id: int) -> bool:
        if id in self._users:
            del self._users[id]
            return True
        return False

# Type checker knows this returns Optional[User]
repo: Repository[User] = UserRepository()
user = repo.get_by_id(1)
```

### JSON serialization tips

Convert objects to/from JSON safely:

```python
from dataclasses import dataclass, asdict
import json

@dataclass
class User:
    id: int
    name: str

u = User(1, "Alice")
payload = json.dumps(asdict(u))       # Serialize
loaded = User(**json.loads(payload))  # Deserialize
```

Notes:

- Non-serializable types (datetime, Decimal) need custom encoding/decoding.
- For big models with versions, include a `schema_version` field and migration logic.

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

### 7. Project structure and imports

- Group related classes into modules and packages (folders with `__init__.py`).
- Keep module size modest; split when files get long or responsibilities diverge.
- Prefer absolute imports in applications; consider relative imports inside packages when refactoring.
- Example layout:
  - `package_name/`
    - `__init__.py`
    - `models/` (domain classes)
    - `services/` (classes orchestrating models)
    - `adapters/` (DB/API integrations)
    - `tests/` (mirrors package structure)

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
            self._connection = object()
            self._logger.info(f"Connected to {self._config.host}:{self._config.port}")
            return True
        except Exception as e:
            self._logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._connection:
            if hasattr(self._connection, "close"):
                self._connection.close()
            self._connection = None
            self._logger.info("Disconnected from database")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
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

---

## Performance Considerations

Writing performant code is crucial, but it's important to balance performance with clarity and maintainability. **Premature optimization is the root of all evil** - always profile first, then optimize!

### OOP-Specific Performance Tips

#### 1. Use `__slots__` for Memory Efficiency

Normal classes store attributes in a `__dict__`, which uses more memory. `__slots__` uses a fixed list instead:

```python
import sys

# Without slots
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# With slots
class PointSlots:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

# Memory comparison
p1 = Point(1, 2)
p2 = PointSlots(1, 2)

print(f"Without slots: {sys.getsizeof(p1)} + {sys.getsizeof(p1.__dict__)} = {sys.getsizeof(p1) + sys.getsizeof(p1.__dict__)} bytes")
print(f"With slots: {sys.getsizeof(p2)} bytes")
# Output: Without slots: 48 + 112 = 160 bytes
#         With slots: 48 bytes
```

**Benefits of `__slots__`:**

- ~50% memory reduction
- Slightly faster attribute access
- Prevents accidental attribute creation

**Drawbacks:**

- Can't add new attributes dynamically
- No `__dict__` (breaks some metaprogramming)
- Inheritance requires care

#### 2. Property vs Direct Attribute Access

```python
import timeit

class WithProperty:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

class DirectAccess:
    def __init__(self, value):
        self.value = value

# Benchmark
prop = WithProperty(42)
direct = DirectAccess(42)

print("Property access:", timeit.timeit(lambda: prop.value, number=1000000))
print("Direct access:", timeit.timeit(lambda: direct.value, number=1000000))
# Output: Property access: ~0.05s
#         Direct access: ~0.03s
```

**Takeaway:** Properties are ~60% slower. Use them for validation/computation, not for simple attribute access.

#### 3. Method Call Overhead

```python
import timeit

class Calculator:
    def add(self, a, b):
        return a + b

    @staticmethod
    def add_static(a, b):
        return a + b

def add_function(a, b):
    return a + b

calc = Calculator()

# Benchmark
print("Instance method:", timeit.timeit(lambda: calc.add(1, 2), number=1000000))
print("Static method:", timeit.timeit(lambda: Calculator.add_static(1, 2), number=1000000))
print("Function:", timeit.timeit(lambda: add_function(1, 2), number=1000000))
# Output: Instance method: ~0.12s
#         Static method: ~0.08s
#         Function: ~0.06s
```

**Takeaway:** Method calls have overhead. For performance-critical code, consider functions.

#### 4. Descriptor vs Property Performance

```python
import timeit

class DescriptorValidator:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(f'_{self.name}')

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("Must be positive")
        instance.__dict__[f'_{self.name}'] = value

class WithDescriptor:
    value = DescriptorValidator('value')

    def __init__(self, value):
        self.value = value

class WithProperty:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val < 0:
            raise ValueError("Must be positive")
        self._value = val

# Benchmark reads
desc = WithDescriptor(42)
prop = WithProperty(42)

print("Descriptor read:", timeit.timeit(lambda: desc.value, number=1000000))
print("Property read:", timeit.timeit(lambda: prop.value, number=1000000))
# Output: Descriptor read: ~0.15s
#         Property read: ~0.05s
```

**Takeaway:** Properties are faster than descriptors for single-class use. Use descriptors only when you need reusability.

#### 5. Lazy Initialization

```python
import timeit

class EagerInit:
    """Compute everything upfront."""
    def __init__(self, data):
        self.data = data
        self.result = self._expensive_computation()

    def _expensive_computation(self):
        return sum(x**2 for x in self.data)

class LazyInit:
    """Compute only when needed."""
    def __init__(self, data):
        self.data = data
        self._result = None

    @property
    def result(self):
        if self._result is None:
            self._result = sum(x**2 for x in self.data)
        return self._result

data = list(range(10000))

# Benchmark creation
print("Eager init:", timeit.timeit(lambda: EagerInit(data), number=1000))
print("Lazy init:", timeit.timeit(lambda: LazyInit(data), number=1000))
# Output: Eager init: ~0.4s (always pays cost)
#         Lazy init: ~0.001s (defers cost)
```

**Takeaway:** Use lazy initialization for expensive operations that might not be needed.

#### 6. Inheritance Depth

```python
import timeit

# Shallow hierarchy
class A:
    def method(self):
        return 1

class B(A):
    pass

# Deep hierarchy
class C:
    def method(self):
        return 1

class D(C): pass
class E(D): pass
class F(E): pass
class G(F): pass

b = B()
g = G()

print("Shallow:", timeit.timeit(lambda: b.method(), number=1000000))
print("Deep:", timeit.timeit(lambda: g.method(), number=1000000))
# Output: Shallow: ~0.11s
#         Deep: ~0.13s
```

**Takeaway:** Deep inheritance hierarchies are slightly slower. Keep hierarchies shallow (max 3-4 levels).

### Performance Comparison Table

```
┌──────────────────────────────────────────────────────────────┐
│ Operation                    Relative Speed   Memory Use      │
├──────────────────────────────────────────────────────────────┤
│ Direct attribute access      1.0x (fastest)   High (no slots) │
│ Property access              0.6x             High            │
│ Descriptor access            0.4x             High            │
│ Method call                  0.5x             -               │
│ Deep inheritance            0.9x              -               │
│                                                                │
│ With __slots__              1.0x              50% less memory │
│ Lazy initialization         10x+ faster       Same            │
│ Caching (memoization)       100x+ faster      More memory     │
└──────────────────────────────────────────────────────────────┘
```

### Best Practices for Performance

1. **Profile First**: Use `cProfile` to find bottlenecks

  ```python
  import cProfile


  def your_function():
      """Example workload to profile."""
      return sum(range(1_000))


  if __name__ == "__main__":
      cProfile.runctx("your_function()", globals(), locals())
  ```

2. **Use `__slots__` for:**
   - Classes with many instances
   - Data-heavy objects
   - Performance-critical code

3. **Avoid `__slots__` for:**
   - Classes that need `__dict__`
   - Complex inheritance hierarchies
   - Code that needs flexibility

4. **Cache Expensive Operations:**

   ```python
   from functools import lru_cache

   class DataProcessor:
       @lru_cache(maxsize=128)
       def expensive_operation(self, data):
           return compute_result(data)
   ```

5. **Use Generators for Large Datasets:**

   ```python
   class DataStream:
       def get_items(self):
           # Bad: Returns everything at once
           return [process(x) for x in huge_dataset]

       def get_items_generator(self):
           # Good: Yields one at a time
           for x in huge_dataset:
               yield process(x)
   ```

### When to Optimize

```
                Performance Issue?
                       |
                       v
                   Profile it!
                       |
                       v
              Is it a real bottleneck?
                   /        \
                 NO          YES
                 /              \
                v                v
          Don't optimize    Is it OOP overhead?
          (Focus on          /            \
           readability)    NO              YES
                          /                  \
                         v                    v
                  Optimize           Use __slots__
                  algorithm          Cache results
                  or data            Lazy init
                  structure          Reduce method calls
```

### Additional Resources

For a deep dive into performance optimization, including profiling, memory management, and advanced techniques, see:

**[Python Performance Optimization Guide](../python/performance_guide.md)**

**Remember:** "Premature optimization is the root of all evil" - Donald Knuth. Write clear code first, optimize later if needed!

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

## Practice Exercises

Try these short exercises to reinforce each concept. **Expected outputs are shown for each exercise.**

### Exercise 1: Encapsulation - SafeCounter

Create a `SafeCounter` with a private value and `increment()`, `decrement()` methods that never let it drop below zero. Add a read-only property `value`.

**Expected behavior:**
```python
counter = SafeCounter()
counter.increment()
counter.increment()
print(counter.value)  # Expected Output: 2

counter.decrement()
print(counter.value)  # Expected Output: 1

# Should not go below zero
counter.decrement()
counter.decrement()  # Stays at 0
print(counter.value)  # Expected Output: 0

# Trying to set value directly should fail
# counter.value = 10  # Expected: AttributeError
```

---

### Exercise 2: Inheritance & Polymorphism - Shapes

Implement `Shape` with `area()`; add `Rectangle` and `Circle`, then write a function that takes a list of shapes and prints their areas.

**Expected behavior:**
```python
shapes = [
    Rectangle(5, 3),
    Circle(2),
    Rectangle(10, 4)
]

print_areas(shapes)
# Expected Output:
# Rectangle area: 15.00
# Circle area: 12.57
# Rectangle area: 40.00

# Polymorphism in action
for shape in shapes:
    print(shape.area())  # Each shape calculates differently
```

---

### Exercise 3: Composition - Car with Components

Build a `Car` that uses `Engine` and `GPS` components. Add `start()`, `accelerate()`, and `navigate_to()` methods.

**Expected behavior:**
```python
car = Car("Toyota", "Camry", engine_hp=200)

car.start()            # Expected Output: "Engine started"
car.accelerate()       # Expected Output: "Accelerating to 10 mph"
car.accelerate()       # Expected Output: "Accelerating to 20 mph"
car.navigate_to("Home")  # Expected Output: "Navigating to Home"

# Before starting engine
car2 = Car("Honda", "Civic", engine_hp=180)
car2.accelerate()      # Expected Output: "Can't accelerate - engine not running"
```

---

### Exercise 4: ABCs - Notifier System

Define an abstract `Notifier` and implement `EmailNotifier` and `SMSNotifier`. Write a function that accepts any notifier and sends messages.

**Expected behavior:**
```python
from abc import ABC, abstractmethod

email = EmailNotifier()
sms = SMSNotifier()

send_notification(email, "Hello!", "user@example.com")
# Expected Output: "[EMAIL] Sent to user@example.com: Hello!"

send_notification(sms, "Alert!", "+1234567890")
# Expected Output: "[SMS] Sent to +1234567890: Alert!"

# Trying to instantiate abstract class should fail
# notifier = Notifier()  # Expected: TypeError: Can't instantiate abstract class
```

---

### Exercise 5: Dataclasses - User Serialization

Create a `@dataclass(slots=True)` `User` with `id`, `name`; serialize to JSON and back.

**Expected behavior:**
```python
import json
from dataclasses import dataclass, asdict

user = User(id=1, name="Alice")
print(user)  # Expected Output: User(id=1, name='Alice')

# Serialize to JSON
json_str = json.dumps(asdict(user))
print(json_str)  # Expected Output: {"id": 1, "name": "Alice"}

# Deserialize from JSON
data = json.loads(json_str)
user2 = User(**data)
print(user2)  # Expected Output: User(id=1, name='Alice')
print(user == user2)  # Expected Output: True
```

---

### Exercise 6: Dunder Methods - Vector

Create a `Vector` supporting `+`, printable with `repr`, and equality checks.

**Expected behavior:**
```python
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(repr(v1))    # Expected Output: Vector(x=3, y=4)
print(str(v1))     # Expected Output: <3, 4>

v3 = v1 + v2
print(v3)          # Expected Output: <4, 6>

print(v1 == Vector(3, 4))  # Expected Output: True
print(v1 == v2)            # Expected Output: False

# Magnitude
print(abs(v1))     # Expected Output: 5.0 (sqrt(3^2 + 4^2))
```

---

### Exercise 7: Thread-Safety - Bank Account

Implement a thread-safe `BankAccount` supporting `deposit`/`withdraw` with a lock.

**Expected behavior:**
```python
import threading

account = BankAccount(initial_balance=1000)

def deposit_money():
    for _ in range(100):
        account.deposit(10)

def withdraw_money():
    for _ in range(100):
        account.withdraw(5)

# Create threads
threads = [
    threading.Thread(target=deposit_money),
    threading.Thread(target=deposit_money),
    threading.Thread(target=withdraw_money)
]

# Run all threads
for t in threads:
    t.start()
for t in threads:
    t.join()

print(account.balance)  # Expected Output: 2500
# (1000 + 2*100*10 - 100*5 = 1000 + 2000 - 500 = 2500)
# Without lock: result would be unpredictable!
```

---

### Optional: Testing with pytest

Add tests for the above exercises:

```python
# test_exercises.py
import pytest

def test_safe_counter_never_negative():
    counter = SafeCounter()
    counter.decrement()  # Should stay at 0
    assert counter.value == 0

def test_shapes_polymorphism():
    shapes = [Rectangle(5, 3), Circle(2)]
    areas = [shape.area() for shape in shapes]
    assert areas[0] == 15
    assert abs(areas[1] - 12.566) < 0.01  # π * 2^2

def test_car_needs_engine_started():
    car = Car("Toyota", "Camry", 200)
    result = car.accelerate()
    assert "Can't accelerate" in result

def test_notifier_abstract():
    with pytest.raises(TypeError):
        Notifier()  # Can't instantiate abstract class

def test_user_serialization():
    user = User(id=1, name="Alice")
    data = asdict(user)
    user2 = User(**data)
    assert user == user2

def test_vector_addition():
    v1 = Vector(3, 4)
    v2 = Vector(1, 2)
    v3 = v1 + v2
    assert v3.x == 4 and v3.y == 6

def test_bank_account_thread_safety():
    # See example above - verifies thread-safe operations
    pass
```

Let's look at how OOP concepts are applied in our actual project code, with references to the real implementations.

---

## Appendices

For deeper guidance beyond this guide:

- Appendix A: [OOP Anti‑Patterns and Refactoring](./appendix_oop_antipatterns.md)
- Appendix B: [Pattern Picker (Problem → Approaches)](./appendix_oop_pattern_picker.md)
- Appendix C: [Packaging & Public API Design](./appendix_oop_packaging_public_api.md)

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
class SnowflakeConnection(DatabaseConnection, ConfigurableComponent):
    """
    Snowflake database connection implementation.

    Demonstrates multiple inheritance and composition:
    - DatabaseConnection: Core database interface
    - ConfigurableComponent: Configuration management
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
from typing import Any, Dict, List


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


class HealthMonitor(BaseMonitor):
    """Simple uptime monitor."""

    def __init__(self, name: str):
        super().__init__(name)

    def check(self) -> Dict[str, Any]:
        return {"monitor": self.name, "type": "health", "status": "ok"}


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
import logging
from typing import Any, Dict, Optional


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
            ConnectionConfig(host='localhost', port=5432, database='myapp')
        )
    else:
        raise ValueError(f"Unsupported connection type: {connection_type}")

    # Inject the connection into the service
    return DatabaseService(connection)

# Usage
service = create_user_service('snowflake')
user = service.get_user_by_id(123)
print(user)
```

---

## What's Missing?

This guide covers the core OOP concepts and best practices. For advanced topics that go beyond the fundamentals, see our companion tutorial:

**[Advanced OOP Concepts](advanced_oop_concepts.md)** - Covers advanced OOP concepts including:

- **Async/await with classes** - Building responsive, concurrent systems
- **Multiple inheritance diamond problem** - Advanced inheritance patterns
- **Monkey patching and dynamic class modification** - Runtime code modification
- **Advanced metaclass usage** - Controlling class creation and behavior
- **Protocol buffers and serialization** - Efficient data serialization
- **Performance optimization techniques** - Advanced performance tuning
- **Memory management and weak references** - Preventing memory leaks

The key is to master the fundamentals first, then gradually explore more advanced concepts as your projects require them.

Remember: Good OOP design is about creating code that is easy to understand, maintain, and extend. Start with these principles and patterns, and you'll be well on your way to writing excellent object-oriented Python code!

---

## Quick Reference for Beginners

### Creating a Class

```python
class ClassName:
    def __init__(self, param1, param2):
        self.attribute1 = param1
        self.attribute2 = param2

    def method_name(self):
        # Do something with self.attribute1
        pass
```

### Inheritance

```python
class ParentClass:
    def __init__(self, param1):
        self.attribute1 = param1


class ChildClass(ParentClass):
    def __init__(self, param1, param2):
        super().__init__(param1)  # Call parent constructor
        self.attribute2 = param2
```

### Common Patterns

```python
# Property (getter/setter)
@property
def attribute(self):
    return self._attribute

@attribute.setter
def attribute(self, value):
    self._attribute = value

# Class method
@classmethod
def from_string(cls, string):
    # Create and return instance
    return cls(data)

# Static method
@staticmethod
def utility_function(arg):
    # No self or cls needed
    return result

# String representation
def __repr__(self):
    return f"ClassName(attr={self.attr})"

def __str__(self):
    return "Readable description"
```

### When to Use What

| Situation | Use |
|-----------|-----|
| Objects have different data but same behaviors | **Class with methods** |
| "Is-A" relationship (Dog is an Animal) | **Inheritance** |
| "Has-A" relationship (Car has an Engine) | **Composition** |
| Multiple classes need same methods | **Abstract Base Class** |
| Need to enforce method existence | **ABC with @abstractmethod** |
| Need to validate data on assignment | **@property with setter** |
| Need alternative constructors | **@classmethod** |
| Need utility functions in class | **@staticmethod** |

### Common Mistakes to Avoid

1. ❌ Forgetting `self` in methods

   ```python
   def method():  # WRONG - no self
       self.value = 5
   ```

   ✅ Always include `self` as first parameter

   ```python
   def method(self):  # CORRECT
       self.value = 5
   ```

2. ❌ Not calling parent's `__init__`

   ```python
   class Parent:
       def __init__(self):
           self.value = 0

   class Child(Parent):
       def __init__(self):
           self.child_attr = 1  # WRONG - parent not initialized
   ```

   ✅ Call `super().__init__()`

   ```python
   class Parent:
       def __init__(self):
           self.value = 0

   class Child(Parent):
       def __init__(self):
           super().__init__()  # CORRECT
           self.child_attr = 1
   ```

3. ❌ Mutable default arguments

   ```python
   def __init__(self, items=[]):  # WRONG - shared list!
       self.items = items
   ```

   ✅ Use None and create new list

   ```python
   def __init__(self, items=None):  # CORRECT
       self.items = items if items is not None else []
   ```

4. ❌ Modifying class variables thinking they're instance variables

   ```python
   class Counter:
       count = 0  # Class variable
       def increment(self):
           Counter.count += 1  # Modifies for ALL instances
   ```

   ✅ Use instance variables for per-object data

   ```python
   class Counter:
       def __init__(self):
           self.count = 0  # Instance variable
       def increment(self):
           self.count += 1  # Modifies only THIS instance
   ```

### Next Steps

1. ✅ **Practice**: Do the exercises throughout this guide
2. ✅ **Build something**: Create a small project using classes
3. ✅ **Read code**: Look at well-written Python projects on GitHub
4. ✅ **Advanced topics**: When comfortable, explore [advanced_oop_concepts.md](./advanced_oop_concepts.md)
5. ✅ **Design patterns**: Study common patterns for specific problems
