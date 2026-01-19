# Solutions — 08: OOP Foundations

## Key Concepts Demonstrated

- Class definition with `__init__`
- Instance methods and attributes
- Inheritance and method overriding
- Class methods (`@classmethod`) and static methods (`@staticmethod`)
- Properties for encapsulation
- Magic/dunder methods
- Abstract base classes

## Common Mistakes to Avoid

- Forgetting `self` parameter in instance methods
- Modifying class attributes instead of instance attributes
- Not calling `super().__init__()` in subclasses
- Using mutable default arguments in `__init__`
- Confusing `@classmethod` and `@staticmethod`

---

## Exercise 1 Solution

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def is_square(self) -> bool:
        return self.width == self.height

# Test
r1 = Rectangle(5, 3)
print(r1.area())        # 15
print(r1.perimeter())   # 16
print(r1.is_square())   # False

r2 = Rectangle(4, 4)
print(r2.is_square())   # True
```

---

## Exercise 2 Solution

```python
class BankAccount:
    def __init__(self, account_number: str, owner: str, balance: float = 0):
        self.account_number = account_number
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True

    def __str__(self) -> str:
        return f"Account {self.account_number} ({self.owner}): ${self.balance:.2f}"

# Test
account = BankAccount("123456", "Alice")
print(account)  # Account 123456 (Alice): $0.00

account.deposit(1000)
print(account)  # Account 123456 (Alice): $1000.00

account.withdraw(250)
print(account)  # Account 123456 (Alice): $750.00

result = account.withdraw(1000)  # Returns False
print(f"Withdrawal success: {result}")  # False
print(account)  # Account 123456 (Alice): $750.00
```

---

## Exercise 3 Solution

```python
import math

class Shape:
    def area(self) -> float:
        raise NotImplementedError("Subclasses must implement area()")

    def describe(self) -> str:
        return "I am a shape"

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def describe(self) -> str:
        return f"I am a circle with radius {self.radius}"

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def describe(self) -> str:
        return f"I am a rectangle ({self.width}x{self.height})"

# Test
shapes = [Circle(5), Rectangle(4, 6), Circle(3)]
for shape in shapes:
    print(f"{shape.describe()}, area = {shape.area():.2f}")
```

**Output**:
```
I am a circle with radius 5, area = 78.54
I am a rectangle (4x6), area = 24.00
I am a circle with radius 3, area = 28.27
```

---

## Exercise 4 Solution

```python
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9/5 + 32

    @property
    def kelvin(self) -> float:
        return self.celsius + 273.15

    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        celsius = (f - 32) * 5/9
        return cls(celsius)

    @classmethod
    def from_kelvin(cls, k: float) -> "Temperature":
        celsius = k - 273.15
        return cls(celsius)

    @staticmethod
    def is_freezing(celsius: float) -> bool:
        return celsius <= 0

# Test
t1 = Temperature(25)
print(f"{t1.celsius}°C = {t1.fahrenheit}°F = {t1.kelvin}K")
# 25°C = 77.0°F = 298.15K

t2 = Temperature.from_fahrenheit(98.6)
print(f"{t2.celsius:.1f}°C")  # 37.0°C

t3 = Temperature.from_kelvin(273.15)
print(f"{t3.celsius}°C")  # 0.0°C

print(Temperature.is_freezing(0))   # True
print(Temperature.is_freezing(10))  # False
```

---

## Exercise 5 Solution

```python
from datetime import datetime

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age  # Uses the setter

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not 0 <= value <= 150:
            raise ValueError(f"Age must be between 0 and 150, got {value}")
        self._age = value

    @property
    def birth_year(self) -> int:
        return datetime.now().year - self._age

# Test
person = Person("Alice", 30)
print(person.age)        # 30
print(person.birth_year) # 1996 (assuming current year is 2026)

person.age = 35
print(person.age)        # 35

try:
    person.age = -5
except ValueError as e:
    print(f"Error: {e}")  # Error: Age must be between 0 and 150, got -5

try:
    person.age = 200
except ValueError as e:
    print(f"Error: {e}")  # Error: Age must be between 0 and 150, got 200
```

---

## Exercise 6 Solution

```python
from typing import Optional

class Author:
    def __init__(self, name: str, nationality: str):
        self.name = name
        self.nationality = nationality

    def __repr__(self) -> str:
        return f"Author({self.name})"

class Book:
    """Composition: has an Author."""

    def __init__(self, title: str, author: Author, isbn: str):
        self.title = title
        self.author = author  # Composition
        self.isbn = isbn
        self.is_available = True

    def __repr__(self) -> str:
        return f"Book: {self.title}"

class EBook(Book):
    """Inheritance: is a Book with additional attributes."""

    def __init__(self, title: str, author: Author, isbn: str, file_size_mb: float):
        super().__init__(title, author, isbn)
        self.file_size_mb = file_size_mb

    def __repr__(self) -> str:
        return f"EBook: {self.title} ({self.file_size_mb}MB)"

class Member:
    """Composition: has borrowed books."""

    def __init__(self, name: str, member_id: str):
        self.name = name
        self.member_id = member_id
        self.borrowed_books: list[Book] = []

    def __repr__(self) -> str:
        return f"Member({self.name}, {self.member_id})"

class Library:
    """Composition: has books and members."""

    def __init__(self, name: str):
        self.name = name
        self.books: dict[str, Book] = {}  # isbn -> Book
        self.members: dict[str, Member] = {}  # member_id -> Member

    def add_book(self, book: Book) -> None:
        self.books[book.isbn] = book

    def add_member(self, member: Member) -> None:
        self.members[member.member_id] = member

    def checkout_book(self, isbn: str, member_id: str) -> bool:
        book = self.books.get(isbn)
        member = self.members.get(member_id)

        if not book or not member:
            return False
        if not book.is_available:
            return False

        book.is_available = False
        member.borrowed_books.append(book)
        return True

    def return_book(self, isbn: str, member_id: str) -> bool:
        book = self.books.get(isbn)
        member = self.members.get(member_id)

        if not book or not member:
            return False
        if book not in member.borrowed_books:
            return False

        book.is_available = True
        member.borrowed_books.remove(book)
        return True

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

## Exercise 7 Solution

```python
import math

class Vector:
    """A 2D vector with x and y components."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        return self.__mul__(scalar)

    def __abs__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

# Test
v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(repr(v1))      # Vector(3, 4)
print(str(v1))       # (3, 4)

print(v1 + v2)       # (4, 6)
print(v1 - v2)       # (2, 2)
print(v1 * 2)        # (6, 8)
print(3 * v2)        # (3, 6)

print(abs(v1))       # 5.0
print(v1 == Vector(3, 4))  # True

print(bool(Vector(0, 0)))  # False
print(bool(v1))            # True
```

---

## Exercise 8 Solution

```python
from abc import ABC, abstractmethod
from typing import Any
import json

class Plugin(ABC):
    """Abstract base class for plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def execute(self, data: Any) -> Any:
        pass

    def __repr__(self) -> str:
        return f"{self.name} v{self.version}"

class UppercasePlugin(Plugin):
    @property
    def name(self) -> str:
        return "uppercase"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> str:
        return str(data).upper()

class ReversePlugin(Plugin):
    @property
    def name(self) -> str:
        return "reverse"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> str:
        return str(data)[::-1]

class JsonPlugin(Plugin):
    @property
    def name(self) -> str:
        return "json"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> str:
        return json.dumps(data)

class PluginManager:
    def __init__(self):
        self.plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self.plugins[plugin.name] = plugin

    def run(self, plugin_name: str, data: Any) -> Any:
        if plugin_name not in self.plugins:
            raise KeyError(f"Plugin '{plugin_name}' not found")
        return self.plugins[plugin_name].execute(data)

    def run_all(self, data: Any) -> dict[str, Any]:
        return {name: plugin.execute(data) for name, plugin in self.plugins.items()}

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

## Design Patterns Preview

The exercises touch on several design patterns:

| Pattern | Example | Use Case |
|---------|---------|----------|
| Factory | `Temperature.from_fahrenheit()` | Create objects from different inputs |
| Strategy | Plugin system | Interchangeable algorithms |
| Composite | Library with Books | Tree-like object structures |
| Template Method | `Shape.area()` abstract | Define skeleton, let subclasses fill in |

---

[← Back to Exercises](../exercises/ex_08_oop_foundations.md) | [← Back to Chapter](../08_oop_foundations.md) | [← Back to Module 2](../README.md)
