# Exercises — 08: OOP Foundations

## Learning Objectives

After completing these exercises, you will be able to:
- Define classes with attributes and methods
- Use `__init__` to initialize objects
- Implement inheritance and method overriding
- Use class methods and static methods
- Apply encapsulation with properties
- Understand the difference between instance and class attributes

---

## Exercise 1: Basic Class (Warm-up)

**Bloom Level**: Apply

Create a `Rectangle` class with:
- Attributes: `width` and `height`
- Method: `area()` returns the area
- Method: `perimeter()` returns the perimeter
- Method: `is_square()` returns True if width equals height

```python
class Rectangle:
    # Your implementation here
    pass

# Test
r1 = Rectangle(5, 3)
print(r1.area())        # 15
print(r1.perimeter())   # 16
print(r1.is_square())   # False

r2 = Rectangle(4, 4)
print(r2.is_square())   # True
```

---

## Exercise 2: Bank Account (Practice)

**Bloom Level**: Apply

Create a `BankAccount` class with:
- Attributes: `account_number`, `owner`, `balance` (default 0)
- Method: `deposit(amount)` adds to balance
- Method: `withdraw(amount)` subtracts from balance (if sufficient funds)
- Method: `__str__()` returns a formatted string representation

```python
class BankAccount:
    # Your implementation here
    pass

# Test
account = BankAccount("123456", "Alice")
print(account)  # Account 123456 (Alice): $0.00

account.deposit(1000)
print(account)  # Account 123456 (Alice): $1000.00

account.withdraw(250)
print(account)  # Account 123456 (Alice): $750.00

result = account.withdraw(1000)  # Should fail or return False
print(account)  # Account 123456 (Alice): $750.00 (unchanged)
```

---

## Exercise 3: Inheritance (Practice)

**Bloom Level**: Apply

Create a class hierarchy for shapes:

1. Base class `Shape` with:
   - Method `area()` that raises `NotImplementedError`
   - Method `describe()` that returns "I am a shape"

2. Class `Circle(Shape)` with:
   - Attribute `radius`
   - Override `area()` to calculate circle area (π × r²)
   - Override `describe()` to return "I am a circle with radius X"

3. Class `Rectangle(Shape)` with:
   - Attributes `width` and `height`
   - Override `area()` to calculate rectangle area
   - Override `describe()` to return "I am a rectangle (WxH)"

```python
import math

class Shape:
    # Your implementation
    pass

class Circle(Shape):
    # Your implementation
    pass

class Rectangle(Shape):
    # Your implementation
    pass

# Test
shapes = [Circle(5), Rectangle(4, 6), Circle(3)]
for shape in shapes:
    print(f"{shape.describe()}, area = {shape.area():.2f}")

# Output:
# I am a circle with radius 5, area = 78.54
# I am a rectangle (4x6), area = 24.00
# I am a circle with radius 3, area = 28.27
```

---

## Exercise 4: Class Methods and Static Methods (Practice)

**Bloom Level**: Apply

Create a `Temperature` class with:
- Instance attribute `celsius`
- Property `fahrenheit` that converts from Celsius
- Property `kelvin` that converts from Celsius
- Class method `from_fahrenheit(f)` that creates instance from Fahrenheit
- Class method `from_kelvin(k)` that creates instance from Kelvin
- Static method `is_freezing(celsius)` that returns True if temp ≤ 0

```python
class Temperature:
    # Your implementation here
    pass

# Test
t1 = Temperature(25)
print(f"{t1.celsius}°C = {t1.fahrenheit}°F = {t1.kelvin}K")
# 25°C = 77.0°F = 298.15K

t2 = Temperature.from_fahrenheit(98.6)
print(f"{t2.celsius:.1f}°C")  # 37.0°C

t3 = Temperature.from_kelvin(273.15)
print(f"{t3.celsius}°C")  # 0°C

print(Temperature.is_freezing(0))   # True
print(Temperature.is_freezing(10))  # False
```

---

## Exercise 5: Properties and Encapsulation (Practice)

**Bloom Level**: Apply

Create a `Person` class with:
- Private attribute `_age`
- Property `age` with getter and setter
- Setter should validate age is between 0 and 150
- Property `birth_year` (read-only) calculated from current year and age

```python
from datetime import datetime

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age  # Use the setter

    # Implement age property with validation
    # Implement birth_year read-only property

# Test
person = Person("Alice", 30)
print(person.age)        # 30
print(person.birth_year) # 1996 (or current year - 30)

person.age = 35
print(person.age)        # 35

try:
    person.age = -5      # Should raise ValueError
except ValueError as e:
    print(f"Error: {e}")

try:
    person.age = 200     # Should raise ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

## Exercise 6: Composition vs Inheritance (Analyze)

**Bloom Level**: Analyze

Design a system for a library. Decide whether to use inheritance or composition for each relationship:

1. `Book` has an `Author`
2. `EBook` is a type of `Book`
3. `Library` has many `Book`s
4. `Member` can borrow `Book`s

Implement the classes:

```python
class Author:
    def __init__(self, name: str, nationality: str):
        self.name = name
        self.nationality = nationality

class Book:
    # Composition: has an Author
    pass

class EBook(Book):
    # Inheritance: is a Book, with additional file_size attribute
    pass

class Member:
    # Composition: has borrowed books (list)
    pass

class Library:
    # Composition: has books and members
    pass

# Test
author = Author("George Orwell", "British")
book1 = Book("1984", author, "978-0451524935")
book2 = Book("Animal Farm", author, "978-0451526342")
ebook = EBook("Digital Fortress", Author("Dan Brown", "American"), "978-0312944926", 2.5)

library = Library("City Library")
library.add_book(book1)
library.add_book(book2)
library.add_book(ebook)

member = Member("Alice", "M001")
library.add_member(member)

library.checkout_book("978-0451524935", "M001")
print(member.borrowed_books)  # [Book: 1984]

library.return_book("978-0451524935", "M001")
print(member.borrowed_books)  # []
```

---

## Exercise 7: Magic Methods (Practice)

**Bloom Level**: Apply

Create a `Vector` class that supports mathematical operations:

```python
class Vector:
    """A 2D vector with x and y components."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    # Implement these magic methods:
    # __repr__: Vector(x, y)
    # __str__: (x, y)
    # __eq__: Compare two vectors
    # __add__: Add two vectors
    # __sub__: Subtract two vectors
    # __mul__: Multiply by scalar (Vector * number)
    # __rmul__: Multiply by scalar (number * Vector)
    # __abs__: Return magnitude (length)
    # __bool__: True if not zero vector

# Test
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(repr(v1))      # Vector(3, 4)
print(str(v1))       # (3, 4)

print(v1 + v2)       # (4, 6)
print(v1 - v2)       # (2, 2)
print(v1 * 2)        # (6, 8)
print(3 * v2)        # (3, 6)

print(abs(v1))       # 5.0 (magnitude)
print(v1 == Vector(3, 4))  # True

print(bool(Vector(0, 0)))  # False
print(bool(v1))            # True
```

---

## Exercise 8: Abstract Base Class (Challenge)

**Bloom Level**: Create

Create an abstract base class for a plugin system:

```python
from abc import ABC, abstractmethod
from typing import Any

class Plugin(ABC):
    """Abstract base class for plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version."""
        pass

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the plugin on input data."""
        pass

    def __repr__(self) -> str:
        return f"{self.name} v{self.version}"

# Implement these concrete plugins:

class UppercasePlugin(Plugin):
    """Converts text to uppercase."""
    pass

class ReversePlugin(Plugin):
    """Reverses text."""
    pass

class JsonPlugin(Plugin):
    """Converts dict to JSON string."""
    pass

class PluginManager:
    """Manages and runs plugins."""

    def __init__(self):
        self.plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        pass

    def run(self, plugin_name: str, data: Any) -> Any:
        """Run a specific plugin."""
        pass

    def run_all(self, data: Any) -> dict[str, Any]:
        """Run all plugins and return results."""
        pass

# Test
manager = PluginManager()
manager.register(UppercasePlugin())
manager.register(ReversePlugin())
manager.register(JsonPlugin())

print(manager.run("uppercase", "hello world"))  # "HELLO WORLD"
print(manager.run("reverse", "hello"))          # "olleh"
print(manager.run("json", {"key": "value"}))    # '{"key": "value"}'

results = manager.run_all("test")
print(results)
# {'uppercase': 'TEST', 'reverse': 'tset', 'json': '"test"'}
```

---

## Deliverables

Submit your code for all exercises. Include docstrings and type hints.

---

[← Back to Chapter](../08_oop_foundations.md) | [View Solutions](../solutions/sol_08_oop_foundations.md) | [← Back to Module 2](../README.md)
