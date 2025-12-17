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

An **Enum** is a set of named constants.

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
```

### When to use Enums?

- Fixed set of values (Days of week, HTTP methods, Status codes)
- Prevent string typos (`"succeess"` vs `Status.SUCCESS`)
- Type safety
