# Exercises — 09: Modern Data Structures

## Learning Objectives

After completing these exercises, you will be able to:
- Use dataclasses to create data-holding classes
- Apply NamedTuple for immutable structured data
- Configure dataclass options (frozen, ordering, slots)
- Use field() for default factories and metadata
- Implement post-init processing
- Choose between dataclass, NamedTuple, and regular classes

---

## Exercise 1: Basic Dataclass (Warm-up)

**Bloom Level**: Apply

Convert this regular class to a dataclass:

```python
# Original class
class Product:
    def __init__(self, name: str, price: float, quantity: int = 0):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price}, quantity={self.quantity})"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return (self.name, self.price, self.quantity) == (other.name, other.price, other.quantity)
```

```python
from dataclasses import dataclass

@dataclass
class Product:
    # Your implementation here
    pass

# Test
p1 = Product("Widget", 9.99, 100)
p2 = Product("Widget", 9.99, 100)
p3 = Product("Gadget", 19.99)

print(p1)           # Product(name='Widget', price=9.99, quantity=100)
print(p1 == p2)     # True
print(p3.quantity)  # 0 (default)
```

---

## Exercise 2: NamedTuple (Practice)

**Bloom Level**: Apply

Create NamedTuples for representing:

1. A `Point` with x and y coordinates
2. A `Color` with r, g, b values (each 0-255)
3. A `Person` with name, age, and optional email

```python
from typing import NamedTuple, Optional

class Point(NamedTuple):
    # Your implementation
    pass

class Color(NamedTuple):
    # Your implementation
    pass

class Person(NamedTuple):
    # Your implementation
    pass

# Test
p = Point(3, 4)
print(p.x, p.y)     # 3 4
print(p[0], p[1])   # 3 4 (tuple indexing works)
x, y = p            # Unpacking works
print(f"Distance: {(p.x**2 + p.y**2)**0.5}")  # 5.0

c = Color(255, 128, 0)
print(c)            # Color(r=255, g=128, b=0)

person = Person("Alice", 30)
print(person.email) # None (default)
```

---

## Exercise 3: Dataclass with Defaults and Factory (Practice)

**Bloom Level**: Apply

Create a `Task` dataclass with:
- `title`: string (required)
- `description`: string (default empty)
- `priority`: int (default 1)
- `tags`: list of strings (default empty list - use field!)
- `created_at`: datetime (default to now - use field!)
- `completed`: bool (default False)

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    # Your implementation here
    pass

# Test
t1 = Task("Buy groceries")
t2 = Task("Write report", priority=2, tags=["work", "urgent"])

print(t1)
print(t2)
print(t1.tags is t2.tags)  # False (different lists!)

# Add tag to t1
t1.tags.append("personal")
print(t1.tags)  # ["personal"]
print(t2.tags)  # ["work", "urgent"] (not affected)
```

---

## Exercise 4: Frozen Dataclass (Practice)

**Bloom Level**: Apply

Create an immutable `Coordinate` dataclass:
- `latitude`: float
- `longitude`: float
- Property `is_valid`: True if lat in [-90, 90] and lon in [-180, 180]
- Method `distance_to(other)`: Calculate distance using Haversine formula

```python
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Coordinate:
    # Your implementation here

    @property
    def is_valid(self) -> bool:
        pass

    def distance_to(self, other: "Coordinate") -> float:
        """Calculate distance in kilometers using Haversine formula."""
        pass

# Test
nyc = Coordinate(40.7128, -74.0060)
la = Coordinate(34.0522, -118.2437)

print(nyc.is_valid)  # True
print(nyc.distance_to(la))  # ~3935 km

# Should raise error (frozen)
try:
    nyc.latitude = 0
except Exception as e:
    print(f"Error: {type(e).__name__}")  # FrozenInstanceError
```

---

## Exercise 5: Post-Init Processing (Practice)

**Bloom Level**: Apply

Create an `Email` dataclass that:
- Takes `address` as input
- Automatically extracts `username` and `domain` in `__post_init__`
- Validates the email format

```python
from dataclasses import dataclass, field
import re

@dataclass
class Email:
    address: str
    username: str = field(init=False)
    domain: str = field(init=False)

    def __post_init__(self):
        # Validate and extract parts
        pass

# Test
email = Email("alice@example.com")
print(email.username)  # alice
print(email.domain)    # example.com

try:
    invalid = Email("not-an-email")
except ValueError as e:
    print(f"Error: {e}")  # Error: Invalid email format
```

---

## Exercise 6: Dataclass Ordering (Practice)

**Bloom Level**: Apply

Create a `Version` dataclass that supports comparison:
- `major`: int
- `minor`: int
- `patch`: int
- Should support <, <=, >, >= comparisons

```python
from dataclasses import dataclass

@dataclass(order=True)
class Version:
    # Your implementation here
    pass

# Test
v1 = Version(1, 0, 0)
v2 = Version(1, 2, 0)
v3 = Version(2, 0, 0)
v4 = Version(1, 2, 3)

versions = [v3, v1, v4, v2]
print(sorted(versions))
# [Version(1, 0, 0), Version(1, 2, 0), Version(1, 2, 3), Version(2, 0, 0)]

print(v1 < v2)   # True
print(v3 > v4)   # True
print(v2 <= v4)  # True
```

---

## Exercise 7: Inheritance with Dataclasses (Analyze)

**Bloom Level**: Analyze

Create a class hierarchy for events:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    """Base event class."""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MeetingEvent(Event):
    """Meeting with attendees."""
    attendees: list[str] = field(default_factory=list)
    location: str = "TBD"

@dataclass
class ReminderEvent(Event):
    """Reminder with due date."""
    due_date: datetime = None
    priority: int = 1

# Test
meeting = MeetingEvent(
    name="Team Standup",
    attendees=["Alice", "Bob", "Charlie"],
    location="Room 101"
)
print(meeting)

reminder = ReminderEvent(
    name="Submit report",
    due_date=datetime(2024, 12, 31),
    priority=2
)
print(reminder)
```

**Question**: What happens if you try to add a required field (no default) to a child class when the parent has fields with defaults? How do you solve this?

---

## Exercise 8: Choosing the Right Structure (Evaluate)

**Bloom Level**: Evaluate

For each scenario, choose the best option (regular class, dataclass, NamedTuple, or dict) and explain why:

1. **Configuration settings** that are read from a file and never modified

2. **A user session** with methods for login, logout, and permission checking

3. **An API response** that you need to serialize to JSON

4. **A point in a game** that gets updated every frame

5. **Database query results** returned as rows

6. **A cache entry** with key, value, and expiration time

Implement your chosen structure for scenarios 1, 3, and 5:

```python
# Scenario 1: Configuration settings
# Your implementation

# Scenario 3: API response
# Your implementation

# Scenario 5: Database query results
# Your implementation
```

---

## Exercise 9: Advanced Dataclass (Challenge)

**Bloom Level**: Create

Create a `Configuration` system with validation, serialization, and environment variable support:

```python
from dataclasses import dataclass, field, asdict
from typing import Optional
import os
import json

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "app"
    username: str = "user"
    password: str = field(default="", repr=False)  # Hide in repr

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create from environment variables."""
        pass

@dataclass
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    allowed_hosts: list[str] = field(default_factory=lambda: ["localhost"])

    def __post_init__(self):
        # Validate log_level
        pass

    def to_json(self) -> str:
        """Serialize to JSON."""
        pass

    @classmethod
    def from_json(cls, json_str: str) -> "AppConfig":
        """Deserialize from JSON."""
        pass

# Test
config = AppConfig(
    debug=True,
    log_level="DEBUG",
    database=DatabaseConfig(host="db.example.com", password="secret123")
)

print(config)  # password should be hidden
print(config.to_json())

# Round-trip
json_str = config.to_json()
config2 = AppConfig.from_json(json_str)
print(config2.database.host)  # db.example.com
```

---

## Deliverables

Submit your code for all exercises. Include explanations for Exercise 8.

---

[← Back to Chapter](../09_modern_structs.md) | [View Solutions](../solutions/sol_09_modern_structs.md) | [← Back to Module 2](../README.md)
