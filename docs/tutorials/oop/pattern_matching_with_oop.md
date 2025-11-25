# OOP Tutorial Enhancements - Pattern Matching Section

## Pattern Matching with OOP (Python 3.10+)

Python 3.10 introduced structural pattern matching with the `match`/`case` statement. This feature works beautifully with OOP for polymorphic dispatch and type-based branching.

### Basic Pattern Matching with Classes

```python
from dataclasses import dataclass
from typing import Union

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

Shape = Union[Circle, Rectangle, Triangle]

def calculate_area(shape: Shape) -> float:
    """Calculate area using pattern matching."""
    match shape:
        case Circle(radius=r):
            return 3.14159 * r ** 2
        case Rectangle(width=w, height=h):
            return w * h
        case Triangle(base=b, height=h):
            return 0.5 * b * h
        case _:
            raise ValueError(f"Unknown shape: {shape}")

# Usage
circle = Circle(radius=5)
rectangle = Rectangle(width=4, height=6)
triangle = Triangle(base=3, height=4)

print(calculate_area(circle))      # Output: 78.53975
print(calculate_area(rectangle))   # Output: 24.0
print(calculate_area(triangle))    # Output: 6.0
```

**Why this is powerful**: Pattern matching combines type checking and attribute extraction in one step!

### Pattern Matching with Guards

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    role: str

def check_access(person: Person) -> str:
    """Determine access level using pattern matching with guards."""
    match person:
        case Person(role="admin"):
            return "Full access granted"
        case Person(role="user", age=age) if age >= 18:
            return "Standard access granted"
        case Person(role="user", age=age) if age < 18:
            return "Limited access - parental controls enabled"
        case Person(role="guest"):
            return "Read-only access"
        case _:
            return "Access denied"

# Test
admin = Person("Alice", 30, "admin")
adult_user = Person("Bob", 25, "user")
minor_user = Person("Charlie", 15, "user")
guest = Person("Dave", 20, "guest")

print(check_access(admin))        # Output: Full access granted
print(check_access(adult_user))   # Output: Standard access granted
print(check_access(minor_user))   # Output: Limited access - parental controls enabled
print(check_access(guest))        # Output: Read-only access
```

### Matching Against Class Patterns

```python
class Command:
    pass

@dataclass
class MoveCommand(Command):
    direction: str
    distance: int

@dataclass
class RotateCommand(Command):
    angle: int

@dataclass
class StopCommand(Command):
    pass

class Robot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0

    def execute(self, command: Command) -> None:
        """Execute command using pattern matching."""
        match command:
            case MoveCommand(direction="forward", distance=d):
                self.y += d
                print(f"Moved forward {d} units to ({self.x}, {self.y})")
            case MoveCommand(direction="backward", distance=d):
                self.y -= d
                print(f"Moved backward {d} units to ({self.x}, {self.y})")
            case MoveCommand(direction="left", distance=d):
                self.x -= d
                print(f"Moved left {d} units to ({self.x}, {self.y})")
            case MoveCommand(direction="right", distance=d):
                self.x += d
                print(f"Moved right {d} units to ({self.x}, {self.y})")
            case RotateCommand(angle=a):
                self.angle = (self.angle + a) % 360
                print(f"Rotated to {self.angle}°")
            case StopCommand():
                print("Robot stopped")
            case _:
                print(f"Unknown command: {command}")

# Usage
robot = Robot()
robot.execute(MoveCommand("forward", 10))
robot.execute(MoveCommand("right", 5))
robot.execute(RotateCommand(90))
robot.execute(StopCommand())

# Output:
# Moved forward 10 units to (0, 10)
# Moved right 5 units to (5, 10)
# Rotated to 90°
# Robot stopped
```

### Pattern Matching vs Traditional OOP

**Traditional Polymorphism**:
```python
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

# Each class implements its own method
circle = Circle(5)
area = circle.area()  # Polymorphic dispatch
```

**Pattern Matching**:
```python
@dataclass
class Circle:
    radius: float

def calculate_area(shape):
    match shape:
        case Circle(radius=r):
            return 3.14159 * r ** 2
        # All logic in one place
```

**When to use which?**

| Use Polymorphism | Use Pattern Matching |
|------------------|----------------------|
| Behavior belongs to the object | Logic is external to objects |
| Classes will have many methods | Simple data classes |
| Open for extension (new classes) | Closed set of types |
| Object-oriented design | Functional-style design |

### Combining Pattern Matching with Type Hints

```python
from typing import Literal
from dataclasses import dataclass

@dataclass
class APIResponse:
    status: Literal["success", "error", "pending"]
    data: dict | None = None
    error_message: str | None = None

def handle_response(response: APIResponse) -> str:
    """Handle API response with pattern matching."""
    match response:
        case APIResponse(status="success", data=data):
            return f"Success! Data: {data}"
        case APIResponse(status="error", error_message=msg):
            return f"Error: {msg}"
        case APIResponse(status="pending"):
            return "Request is still processing..."
        case _:
            return "Unknown response type"

# Usage
success_resp = APIResponse("success", data={"user": "Alice"})
error_resp = APIResponse("error", error_message="Not found")
pending_resp = APIResponse("pending")

print(handle_response(success_resp))   # Output: Success! Data: {'user': 'Alice'}
print(handle_response(error_resp))     # Output: Error: Not found
print(handle_response(pending_resp))   # Output: Request is still processing...
```

### Best Practices

✅ **Use dataclasses with pattern matching**:
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

match user:
    case User(name=n, age=a):  # Clean extraction
        print(f"{n} is {a} years old")
```

✅ **Use guards for complex conditions**:
```python
match value:
    case int(x) if x > 0:
        print("Positive integer")
    case int(x) if x < 0:
        print("Negative integer")
```

❌ **Don't overuse pattern matching**:
```python
# This is excessive:
match x:
    case 1: return "one"
    case 2: return "two"

# Use a dictionary:
return {1: "one", 2: "two"}.get(x, "unknown")
```

### Real-World Example: Event Handler

```python
from dataclasses import dataclass
from typing import Literal

EventType = Literal["click", "keypress", "scroll"]

@dataclass
class UIEvent:
    event_type: EventType
    target: str
    data: dict

class EventHandler:
    def handle(self, event: UIEvent) -> None:
        """Handle UI events using pattern matching."""
        match event:
            case UIEvent(event_type="click", target="submit_button"):
                self.submit_form()
            case UIEvent(event_type="click", target=t) if t.startswith("nav_"):
                self.navigate(t.replace("nav_", ""))
            case UIEvent(event_type="keypress", data={"key": "Enter"}):
                self.submit_form()
            case UIEvent(event_type="keypress", data={"key": "Escape"}):
                self.cancel()
            case UIEvent(event_type="scroll", data={"position": pos}) if pos > 1000:
                self.show_back_to_top()
            case _:
                print(f"Unhandled event: {event}")

    def submit_form(self):
        print("Form submitted")

    def navigate(self, page: str):
        print(f"Navigating to {page}")

    def cancel(self):
        print("Action cancelled")

    def show_back_to_top(self):
        print("Showing 'back to top' button")

# Usage
handler = EventHandler()
handler.handle(UIEvent("click", "submit_button", {}))
handler.handle(UIEvent("keypress", "input", {"key": "Enter"}))
handler.handle(UIEvent("scroll", "page", {"position": 1500}))

# Output:
# Form submitted
# Form submitted
# Showing 'back to top' button
```

---

## Summary

Pattern matching in Python 3.10+ provides a powerful alternative to traditional polymorphism for certain use cases:

- **Dataclasses** + **Pattern Matching** = Clean, concise code
- **Guards** enable complex conditional logic
- **Type extraction** happens automatically
- **Best for**: External operations on simple data classes
- **Polymorphism still better for**: Behavior that belongs to objects

Use both techniques where appropriate for clean, maintainable OOP code!
