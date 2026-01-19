# Solutions — 09: Modern Data Structures

## Key Concepts Demonstrated

- Dataclass basic usage and automatic methods
- NamedTuple for immutable structured data
- field() for default factories and metadata
- Post-init processing with `__post_init__`
- Frozen dataclasses for immutability
- Ordering support with `order=True`
- Dataclass inheritance

## Common Mistakes to Avoid

- Using mutable defaults directly (use `field(default_factory=list)`)
- Adding required fields in child when parent has defaults
- Forgetting `repr=False` for sensitive data
- Using `@dataclass` when you need custom `__init__` logic

---

## Exercise 1 Solution

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0

# Test
p1 = Product("Widget", 9.99, 100)
p2 = Product("Widget", 9.99, 100)
p3 = Product("Gadget", 19.99)

print(p1)           # Product(name='Widget', price=9.99, quantity=100)
print(p1 == p2)     # True
print(p3.quantity)  # 0
```

---

## Exercise 2 Solution

```python
from typing import NamedTuple, Optional

class Point(NamedTuple):
    x: float
    y: float

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Person(NamedTuple):
    name: str
    age: int
    email: Optional[str] = None

# Test
p = Point(3, 4)
print(p.x, p.y)     # 3 4
print(p[0], p[1])   # 3 4
x, y = p
print(f"Distance: {(p.x**2 + p.y**2)**0.5}")  # 5.0

c = Color(255, 128, 0)
print(c)            # Color(r=255, g=128, b=0)

person = Person("Alice", 30)
print(person.email) # None
```

---

## Exercise 3 Solution

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    title: str
    description: str = ""
    priority: int = 1
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False

# Test
t1 = Task("Buy groceries")
t2 = Task("Write report", priority=2, tags=["work", "urgent"])

print(t1)
print(t2)
print(t1.tags is t2.tags)  # False

t1.tags.append("personal")
print(t1.tags)  # ["personal"]
print(t2.tags)  # ["work", "urgent"]
```

---

## Exercise 4 Solution

```python
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float

    @property
    def is_valid(self) -> bool:
        return -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180

    def distance_to(self, other: "Coordinate") -> float:
        """Calculate distance in kilometers using Haversine formula."""
        R = 6371  # Earth's radius in km

        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c

# Test
nyc = Coordinate(40.7128, -74.0060)
la = Coordinate(34.0522, -118.2437)

print(nyc.is_valid)  # True
print(f"{nyc.distance_to(la):.0f} km")  # 3936 km

try:
    nyc.latitude = 0
except Exception as e:
    print(f"Error: {type(e).__name__}")  # FrozenInstanceError
```

---

## Exercise 5 Solution

```python
from dataclasses import dataclass, field
import re

@dataclass
class Email:
    address: str
    username: str = field(init=False)
    domain: str = field(init=False)

    def __post_init__(self):
        # Validate format
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, self.address):
            raise ValueError(f"Invalid email format: {self.address}")

        # Extract parts
        self.username, self.domain = self.address.split("@")

# Test
email = Email("alice@example.com")
print(email.username)  # alice
print(email.domain)    # example.com

try:
    invalid = Email("not-an-email")
except ValueError as e:
    print(f"Error: {e}")
```

---

## Exercise 6 Solution

```python
from dataclasses import dataclass

@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

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

## Exercise 7 Solution

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:
    name: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MeetingEvent(Event):
    attendees: list[str] = field(default_factory=list)
    location: str = "TBD"

@dataclass
class ReminderEvent(Event):
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

**Answer to the question**: If a parent class has fields with defaults, all fields in child classes must also have defaults. To add a required field in a child:

```python
# Problem: This fails!
@dataclass
class BaseWithDefault:
    name: str = "default"

# @dataclass
# class ChildWithRequired(BaseWithDefault):
#     required_field: str  # Error! Non-default after default

# Solution 1: Use field with default_factory that raises
@dataclass
class ChildWithRequired(BaseWithDefault):
    required_field: str = field(default_factory=lambda: (_ for _ in ()).throw(
        TypeError("required_field is required")
    ))

# Solution 2: Use __post_init__ for validation
@dataclass
class Child(BaseWithDefault):
    required_field: str = None

    def __post_init__(self):
        if self.required_field is None:
            raise TypeError("required_field is required")
```

---

## Exercise 8 Solution

| Scenario | Choice | Reasoning |
|----------|--------|-----------|
| 1. Config settings (read-only) | **Frozen dataclass** or **NamedTuple** | Immutable, typed, clear structure |
| 2. User session with methods | **Regular class** | Needs methods and mutable state |
| 3. API response (JSON) | **Dataclass** | Easy serialization with `asdict()` |
| 4. Game point (frequent updates) | **Dataclass** or **regular class** | Mutable, frequent modifications |
| 5. Database results | **NamedTuple** | Immutable rows, memory efficient |
| 6. Cache entry | **Dataclass** | Needs mutability for expiration check |

```python
from dataclasses import dataclass, field, asdict
from typing import NamedTuple, Any
import json

# Scenario 1: Configuration settings (frozen)
@dataclass(frozen=True)
class AppSettings:
    app_name: str
    debug: bool = False
    max_connections: int = 100
    log_level: str = "INFO"

settings = AppSettings("MyApp", debug=True)
print(settings)
# settings.debug = False  # Would raise FrozenInstanceError

# Scenario 3: API response
@dataclass
class ApiResponse:
    success: bool
    data: dict = field(default_factory=dict)
    error: str = None
    status_code: int = 200

    def to_json(self) -> str:
        return json.dumps(asdict(self))

response = ApiResponse(
    success=True,
    data={"user_id": 123, "name": "Alice"},
    status_code=200
)
print(response.to_json())

# Scenario 5: Database results
class UserRow(NamedTuple):
    id: int
    username: str
    email: str
    created_at: str

# Simulate query results
results = [
    UserRow(1, "alice", "alice@example.com", "2024-01-15"),
    UserRow(2, "bob", "bob@example.com", "2024-01-16"),
]
for row in results:
    print(f"{row.username}: {row.email}")
```

---

## Exercise 9 Solution

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
    password: str = field(default="", repr=False)

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "app"),
            username=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", ""),
        )

@dataclass
class AppConfig:
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    allowed_hosts: list[str] = field(default_factory=lambda: ["localhost"])

    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def __post_init__(self):
        if self.log_level not in self.VALID_LOG_LEVELS:
            raise ValueError(f"Invalid log_level: {self.log_level}")

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "AppConfig":
        data = json.loads(json_str)
        # Handle nested DatabaseConfig
        if "database" in data and isinstance(data["database"], dict):
            data["database"] = DatabaseConfig(**data["database"])
        return cls(**data)

# Test
config = AppConfig(
    debug=True,
    log_level="DEBUG",
    database=DatabaseConfig(host="db.example.com", password="secret123")
)

print(config)  # password hidden
print(config.to_json())

# Round-trip
json_str = config.to_json()
config2 = AppConfig.from_json(json_str)
print(config2.database.host)  # db.example.com
```

---

## Quick Reference

| Feature | dataclass | NamedTuple | Regular class |
|---------|-----------|------------|---------------|
| Mutable | Yes (default) | No | Yes |
| Inheritance | Yes | Limited | Yes |
| Methods | Yes | Yes | Yes |
| Memory | Normal | Efficient | Normal |
| Hashable | If frozen | Yes | If you implement |
| Tuple unpacking | No | Yes | No |
| Default factory | `field()` | Not directly | Manual |

---

[← Back to Exercises](../exercises/ex_09_modern_structs.md) | [← Back to Chapter](../09_modern_structs.md) | [← Back to Module 2](../README.md)
