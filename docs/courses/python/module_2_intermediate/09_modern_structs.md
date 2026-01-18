# Modern Data Structures

## Dataclasses

A **dataclass** is a class that's primarily used to store data. Instead of writing repetitive code for `__init__`, `__repr__`, and `__eq__`, Python generates them automatically!

### The Old Way

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Person(name={self.name!r}, age={self.age!r})"
```

### The New Way (Dataclasses)

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

p = Person("Alice", 30)
print(p)  # Person(name='Alice', age=30)
```

### Immutable Dataclasses

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float
```

## Enumerations (Enum)

An **Enum** is a set of named constants. Use Enums instead of magic strings or constants to get type safety, IDE autocomplete, and protection against typos.

### Why Strings Are a Trap

```python
# BAD: String constants invite bugs
PENDING = "pending"
ACTIVE = "active"

# Typos silently pass through
if status == "actve":  # No error, just wrong behavior
    ...

# No validation - any string is accepted
status = "whatever"  # No error at all
```

### Basic Enum Usage

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()

def check_status(status: Status):
    if status == Status.FAILED:
        print("Job failed!")

# Typos are now caught immediately
if status == Status.ACTVE:  # AttributeError!
    ...
```

### Add Behavior to Enums

Enums aren't just constants - they can have methods:

```python
from enum import Enum

class UserStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

    def can_login(self) -> bool:
        return self in {UserStatus.ACTIVE}

    def is_terminal(self) -> bool:
        return self in {UserStatus.DELETED}

# Clean, expressive code
if user.status.can_login():
    authenticate(user)
```

### JSON Serialization with `str + Enum`

Use multiple inheritance for seamless JSON serialization:

```python
from enum import Enum
import json

class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

# Works directly with json.dumps
json.dumps({"status": OrderStatus.PAID})  # '{"status": "paid"}'
```

This pattern is essential for APIs, database storage, and frontend communication.

### Validate at Boundaries

Convert strings to Enums at system boundaries (API input, config files):

```python
# BAD: Validating strings everywhere
if status not in ["created", "paid", "shipped"]:
    raise ValueError("Invalid status")

# GOOD: Convert once at the boundary
status = OrderStatus(request_data["status"])  # Raises ValueError if invalid
# Now work with type-safe Enum throughout your code
```

### Pattern Matching (Python 3.10+)

Enums work elegantly with structural pattern matching:

```python
match order.status:
    case OrderStatus.CREATED:
        prepare_payment()
    case OrderStatus.PAID:
        ship_order()
    case OrderStatus.CANCELLED:
        refund()
```

### Enums Beat Ambiguous Booleans

Replace unclear boolean flags with descriptive Enums:

```python
# BAD: What does is_active = True mean?
is_active = True  # Active how? Trial? Paid? Grace period?

# GOOD: Explicit states
class AccountState(Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    GRACE_PERIOD = "grace"
    CLOSED = "closed"
```

### When to Use Enums

Enums are ideal for:

- **Statuses** - order states, user states, job states
- **Roles** - admin, user, guest
- **Categories** - fixed classification systems
- **Modes** - debug, production, test
- **Feature flags** - finite set of options

### Common Mistakes to Avoid

1. **Treating Enums like constants only** - Add methods when behavior depends on state
2. **Comparing with `.value` everywhere** - Use `Status.ACTIVE`, not `"active"`
3. **Overusing Enums** - They model closed sets, not dynamic data
4. **Storing raw strings in database** - Store Enum values, but convert early and strictly

## attrs - Advanced Data Classes

While dataclasses are built into Python, [attrs](https://www.attrs.org/) offers more features for complex data modeling: validators, converters, and slots by default.

### Installation

```bash
uv add attrs
```

### Basic Usage

```python
import attr

@attr.define
class JobConfig:
    retries: int = attr.field(default=3)
    timeout: float = attr.field(default=5.0)
    critical: bool = False

config = JobConfig()
print(config)  # JobConfig(retries=3, timeout=5.0, critical=False)
```

### Validation

attrs provides built-in validators that run at instantiation:

```python
import attr
from attr import validators

@attr.define
class Server:
    host: str = attr.field(validator=validators.instance_of(str))
    port: int = attr.field(validator=[
        validators.instance_of(int),
        validators.ge(1),
        validators.le(65535)
    ])

Server("localhost", 8080)  # Works
Server("localhost", 70000)  # Raises ValueError
```

### Converters

Automatically convert input values:

```python
@attr.define
class Config:
    timeout: float = attr.field(converter=float)
    tags: list = attr.field(converter=list, factory=list)

config = Config(timeout="30", tags=("web", "api"))
print(config.timeout)  # 30.0 (converted from string)
print(config.tags)     # ['web', 'api'] (converted from tuple)
```

### Factory Defaults (Mutable Defaults Done Right)

```python
@attr.define
class Request:
    headers: dict = attr.field(factory=dict)  # New dict per instance
    tags: list = attr.field(factory=list)     # New list per instance
```

### Frozen (Immutable) Classes

```python
@attr.frozen
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 3.0  # Raises FrozenInstanceError
```

### When to Use attrs vs dataclasses

| Feature | dataclasses | attrs |
|---------|-------------|-------|
| Built-in | Yes | No (external) |
| Validators | Manual | Built-in |
| Converters | Manual | Built-in |
| Slots by default | No (3.10+) | Yes |
| Performance | Good | Better |

**Use dataclasses** for simple data containers in standard library-only projects.

**Use attrs** when you need validation, converters, or maximum performance
