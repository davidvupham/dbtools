# OOP Intermediate Exercises

This file contains practical exercises that bridge the gap between basic OOP concepts and advanced patterns. These exercises are designed for learners who have completed the fundamentals and are ready for more complex challenges.

**Prerequisites:**
- Completed [oop_guide.md](./oop_guide.md) basics (Classes, Inheritance, Polymorphism)
- Familiar with SOLID principles
- Basic understanding of design patterns

**How to use this:**
- Each exercise builds on previous concepts
- Solutions are provided at the end
- Try to solve each exercise before looking at the solution
- Focus on writing clean, well-designed code

---

## Table of Contents

1. [Exercise 1: Shopping Cart System](#exercise-1-shopping-cart-system)
2. [Exercise 2: Plugin System](#exercise-2-plugin-system)
3. [Exercise 3: Notification Service](#exercise-3-notification-service)
4. [Exercise 4: Caching Layer](#exercise-4-caching-layer)
5. [Exercise 5: Task Queue System](#exercise-5-task-queue-system)
6. [Exercise 6: Configuration Manager](#exercise-6-configuration-manager)
7. [Exercise 7: Logging Framework](#exercise-7-logging-framework)
8. [Exercise 8: Data Validation Framework](#exercise-8-data-validation-framework)
9. [Exercise 9: State Machine](#exercise-9-state-machine)
10. [Exercise 10: Event System](#exercise-10-event-system)
11. [Solutions](#solutions)

---

## Exercise 1: Shopping Cart System

**Difficulty:** ⭐⭐☆☆☆

**Concepts:** Encapsulation, Composition, Properties

**Task:**
Create a shopping cart system with the following features:

1. `Product` class with name, price, and stock quantity
2. `CartItem` class representing a product and quantity in cart
3. `ShoppingCart` class that can:
   - Add items (check stock availability)
   - Remove items
   - Update quantities
   - Calculate subtotal, tax (8%), and total
   - Clear the cart
4. Apply proper encapsulation (private attributes with properties)
5. Handle edge cases (negative quantities, insufficient stock)

**Starter Code:**
```python
class Product:
    """Represents a product in the store."""
    # TODO: Implement

class CartItem:
    """Represents an item in the cart."""
    # TODO: Implement

class ShoppingCart:
    """Shopping cart that holds items."""
    # TODO: Implement

# Test your implementation
if __name__ == "__main__":
    # Create products
    laptop = Product("Laptop", 1200.00, stock=5)
    mouse = Product("Mouse", 25.00, stock=10)

    # Create cart and add items
    cart = ShoppingCart()
    cart.add_item(laptop, 1)
    cart.add_item(mouse, 2)

    print(f"Subtotal: ${cart.subtotal:.2f}")
    print(f"Tax: ${cart.tax:.2f}")
    print(f"Total: ${cart.total:.2f}")

    # Try to add too many items
    try:
        cart.add_item(laptop, 10)  # Should fail - insufficient stock
    except ValueError as e:
        print(f"Error: {e}")
```

**Learning Goals:**
- Practice encapsulation with properties
- Handle business logic and validation
- Work with composition (Cart contains Items)

---

## Exercise 2: Plugin System

**Difficulty:** ⭐⭐⭐☆☆

**Concepts:** Abstract Base Classes, Factory Pattern, Registration

**Task:**
Create a plugin system where plugins can be dynamically loaded and executed:

1. `Plugin` abstract base class with:
   - `name` property
   - `version` property
   - `execute()` abstract method
2. `PluginRegistry` class decorator for auto-registration
3. At least three concrete plugins (e.g., DataExporter, DataValidator, DataTransformer)
4. `PluginManager` class that can:
   - List available plugins
   - Get plugin by name
   - Execute a plugin

**Starter Code:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class Plugin(ABC):
    """Base class for all plugins."""
    # TODO: Implement

def register_plugin(name: str):
    """Decorator to register a plugin."""
    # TODO: Implement

class PluginManager:
    """Manages plugin lifecycle."""
    # TODO: Implement

# Create some plugins
@register_plugin("csv_exporter")
class CSVExporter(Plugin):
    # TODO: Implement

@register_plugin("json_exporter")
class JSONExporter(Plugin):
    # TODO: Implement

# Test
if __name__ == "__main__":
    manager = PluginManager()
    print("Available plugins:", manager.list_plugins())

    plugin = manager.get_plugin("csv_exporter")
    result = plugin.execute({"data": [1, 2, 3]})
    print(result)
```

**Learning Goals:**
- Use ABCs to define interfaces
- Implement class decorators for registration
- Apply the Factory pattern

---

## Exercise 3: Notification Service

**Difficulty:** ⭐⭐⭐☆☆

**Concepts:** Strategy Pattern, Dependency Injection, Protocols

**Task:**
Create a flexible notification system:

1. `Notifier` Protocol with `send(message, recipient)` method
2. Multiple concrete notifiers:
   - `EmailNotifier`
   - `SMSNotifier`
   - `PushNotifier`
3. `NotificationService` class that:
   - Can use any notifier (dependency injection)
   - Supports multiple notifiers at once
   - Can send notifications through all configured notifiers
   - Has retry logic (max 3 attempts)
4. Add a `LoggingNotifier` decorator that logs all notifications

**Starter Code:**
```python
from typing import Protocol, List
from abc import ABC, abstractmethod

class Notifier(Protocol):
    """Protocol for notification senders."""
    def send(self, message: str, recipient: str) -> bool:
        ...

class EmailNotifier:
    # TODO: Implement

class SMSNotifier:
    # TODO: Implement

class NotificationService:
    """Service that sends notifications."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    email = EmailNotifier()
    sms = SMSNotifier()

    service = NotificationService([email, sms])
    service.notify("Hello!", "user@example.com")
```

**Learning Goals:**
- Use Protocols for structural typing
- Implement Strategy pattern
- Practice dependency injection
- Add cross-cutting concerns (logging)

---

## Exercise 4: Caching Layer

**Difficulty:** ⭐⭐⭐⭐☆

**Concepts:** Descriptors, Context Managers, Decorator Pattern

**Task:**
Create a caching system with:

1. `CachedProperty` descriptor for lazy-loaded, cached properties
2. `Cache` class with:
   - Time-based expiration (TTL)
   - Maximum size limit (LRU eviction)
   - `get`, `set`, `delete` methods
   - Context manager support for batch operations
3. `@cached` function decorator that caches function results
4. Statistics tracking (hits, misses, evictions)

**Starter Code:**
```python
import time
from typing import Any, Optional, Callable

class CachedProperty:
    """Descriptor for cached properties."""
    # TODO: Implement

class Cache:
    """In-memory cache with expiration."""
    # TODO: Implement

def cached(ttl: int = 60):
    """Decorator that caches function results."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    cache = Cache(max_size=100, default_ttl=5)

    cache.set("key1", "value1")
    print(cache.get("key1"))  # "value1"

    time.sleep(6)
    print(cache.get("key1"))  # None (expired)

    print(cache.stats())  # {hits: 1, misses: 1, ...}
```

**Learning Goals:**
- Implement descriptors for reusable attribute behavior
- Work with time-based caching
- Create decorators that modify behavior
- Track statistics

---

## Exercise 5: Task Queue System

**Difficulty:** ⭐⭐⭐⭐☆

**Concepts:** Observer Pattern, State Pattern, Async/Threading

**Task:**
Create a task queue system:

1. `Task` class with:
   - Unique ID
   - Priority (0-10)
   - Status (pending, running, completed, failed)
   - Execute method
2. `TaskQueue` class that:
   - Stores tasks sorted by priority
   - Can add/remove tasks
   - Process tasks in order
3. `TaskObserver` protocol for status notifications
4. At least one concrete observer (e.g., `LoggingObserver`)

**Starter Code:**
```python
from typing import Protocol, List, Callable
from enum import Enum
import time

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskObserver(Protocol):
    def on_status_change(self, task_id: str, old_status: TaskStatus, new_status: TaskStatus):
        ...

class Task:
    """Represents a task to be executed."""
    # TODO: Implement

class TaskQueue:
    """Priority queue for tasks."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    queue = TaskQueue()

    task1 = Task("task1", lambda: print("Task 1"), priority=5)
    task2 = Task("task2", lambda: print("Task 2"), priority=10)

    queue.add(task1)
    queue.add(task2)

    queue.process_all()  # Should process task2 first (higher priority)
```

**Learning Goals:**
- Implement Observer pattern
- Work with priority queues
- Handle state transitions
- Use enums for type safety

---

## Exercise 6: Configuration Manager

**Difficulty:** ⭐⭐⭐☆☆

**Concepts:** Singleton Pattern, Type Validation, Context Managers

**Task:**
Create a configuration management system:

1. `ConfigManager` singleton class that:
   - Loads config from files (JSON/YAML)
   - Validates config against schema
   - Provides type-safe access to config values
   - Supports nested configuration
2. `@config_value` decorator for easy access to config values
3. Context manager for temporary config changes
4. Type validation for config values

**Starter Code:**
```python
from typing import Any, Dict, Optional
import json

class ConfigManager:
    """Singleton configuration manager."""
    # TODO: Implement

def config_value(key: str, default: Any = None):
    """Decorator to inject config values."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    config = ConfigManager()
    config.load_from_dict({
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "debug": True
    })

    print(config.get("database.host"))  # "localhost"
    print(config.get("database.port"))  # 5432

    with config.temporary_set("debug", False):
        print(config.get("debug"))  # False
    print(config.get("debug"))  # True (restored)
```

**Learning Goals:**
- Implement Singleton pattern correctly
- Work with nested data structures
- Create context managers for temporary changes
- Add type validation

---

## Exercise 7: Logging Framework

**Difficulty:** ⭐⭐⭐☆☆

**Concepts:** Class Decorators, Multiple Inheritance, Mixins

**Task:**
Create a simple logging framework:

1. `Logger` class with different log levels (DEBUG, INFO, WARNING, ERROR)
2. `LogHandler` abstract class with concrete implementations:
   - `ConsoleHandler`
   - `FileHandler`
3. `@logged` class decorator that adds logging to all methods
4. `LoggableMixin` that classes can inherit to get logging capability
5. Formatting support for log messages

**Starter Code:**
```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40

class LogHandler(ABC):
    """Base class for log handlers."""
    # TODO: Implement

class Logger:
    """Main logger class."""
    # TODO: Implement

def logged(cls):
    """Class decorator that adds logging to all methods."""
    # TODO: Implement

class LoggableMixin:
    """Mixin that provides logging capability."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    logger = Logger("myapp")
    logger.add_handler(ConsoleHandler())

    logger.info("Application started")
    logger.error("An error occurred!")
```

**Learning Goals:**
- Create class decorators
- Work with mixins
- Implement the Strategy pattern for handlers
- Format output strings

---

## Exercise 8: Data Validation Framework

**Difficulty:** ⭐⭐⭐⭐☆

**Concepts:** Descriptors, Type Hints, Dataclasses

**Task:**
Create a data validation framework:

1. Validation descriptors:
   - `String(min_length, max_length, pattern)`
   - `Integer(min_value, max_value)`
   - `Email()`
   - `URL()`
2. `Validator` base class
3. `@validated` class decorator that adds validation
4. Collect all validation errors (don't fail on first error)
5. Custom error messages

**Starter Code:**
```python
from typing import Any, List, Optional
import re

class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")

class Field:
    """Base field descriptor."""
    # TODO: Implement

class String(Field):
    # TODO: Implement

class Integer(Field):
    # TODO: Implement

class Email(Field):
    # TODO: Implement

@validated
class User:
    name = String(min_length=2, max_length=50)
    age = Integer(min_value=0, max_value=150)
    email = Email()

    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

# Test
if __name__ == "__main__":
    try:
        user = User("A", -5, "invalid")  # Multiple errors
    except ValidationError as e:
        for error in e.errors:
            print(error)
```

**Learning Goals:**
- Create reusable descriptors
- Implement comprehensive validation
- Collect and report multiple errors
- Use regular expressions

---

## Exercise 9: State Machine

**Difficulty:** ⭐⭐⭐⭐☆

**Concepts:** State Pattern, Enums, Type Safety

**Task:**
Create a state machine for an order system:

1. States: Created, Paid, Shipped, Delivered, Cancelled
2. `OrderState` abstract base class with transition methods
3. Concrete state classes for each state
4. `Order` class that maintains current state
5. Valid transitions:
   - Created → Paid, Cancelled
   - Paid → Shipped, Cancelled
   - Shipped → Delivered
   - Delivered → (terminal state)
   - Cancelled → (terminal state)
6. Prevent invalid transitions

**Starter Code:**
```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class OrderStatus(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderState(ABC):
    """Base class for order states."""
    # TODO: Implement

class Order:
    """Order with state machine."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    order = Order("ORDER123")
    print(order.status)  # CREATED

    order.pay()
    print(order.status)  # PAID

    order.ship()
    print(order.status)  # SHIPPED

    try:
        order.pay()  # Should fail - already paid
    except ValueError as e:
        print(e)
```

**Learning Goals:**
- Implement State pattern
- Handle state transitions
- Prevent invalid operations
- Use enums for type safety

---

## Exercise 10: Event System

**Difficulty:** ⭐⭐⭐⭐⭐

**Concepts:** Observer Pattern, Weak References, Async/Callbacks

**Task:**
Create a flexible event system:

1. `EventBus` class that:
   - Registers event listeners (with weak references)
   - Publishes events
   - Supports priority for listeners
   - Allows asynchronous event handling
2. `Event` base class with timestamp and data
3. Multiple event types (inherit from Event)
4. Listener can subscribe to specific event types
5. Support for event filtering

**Starter Code:**
```python
from typing import Callable, List, Any, Type
from datetime import datetime
import weakref

class Event:
    """Base class for events."""
    def __init__(self, data: Any = None):
        self.timestamp = datetime.now()
        self.data = data

class EventBus:
    """Central event bus for pub/sub."""
    # TODO: Implement

# Test
if __name__ == "__main__":
    bus = EventBus()

    def on_user_created(event):
        print(f"User created: {event.data}")

    bus.subscribe("user_created", on_user_created)
    bus.publish("user_created", {"name": "Alice"})
```

**Learning Goals:**
- Implement Observer pattern at scale
- Use weak references to prevent memory leaks
- Support filtering and priorities
- Handle async events

---

## Solutions

### Solution 1: Shopping Cart System

```python
class Product:
    """Represents a product in the store."""

    def __init__(self, name: str, price: float, stock: int):
        self._name = name
        self._price = price
        self._stock = stock

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def stock(self) -> int:
        return self._stock

    def reduce_stock(self, quantity: int) -> None:
        if quantity > self._stock:
            raise ValueError(f"Insufficient stock. Available: {self._stock}")
        self._stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        self._stock += quantity

class CartItem:
    """Represents an item in the cart."""

    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self._product = product
        self._quantity = quantity

    @property
    def product(self) -> Product:
        return self._product

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if value <= 0:
            raise ValueError("Quantity must be positive")
        self._quantity = value

    @property
    def subtotal(self) -> float:
        return self._product.price * self._quantity

class ShoppingCart:
    """Shopping cart that holds items."""

    def __init__(self):
        self._items: List[CartItem] = []
        self._tax_rate = 0.08  # 8% tax

    def add_item(self, product: Product, quantity: int) -> None:
        """Add product to cart."""
        if quantity > product.stock:
            raise ValueError(
                f"Cannot add {quantity} of {product.name}. "
                f"Only {product.stock} available."
            )

        # Check if product already in cart
        for item in self._items:
            if item.product is product:
                item.quantity += quantity
                return

        # Add new item
        self._items.append(CartItem(product, quantity))

    def remove_item(self, product: Product) -> None:
        """Remove product from cart."""
        self._items = [item for item in self._items if item.product is not product]

    def update_quantity(self, product: Product, quantity: int) -> None:
        """Update quantity of a product in cart."""
        if quantity <= 0:
            self.remove_item(product)
            return

        for item in self._items:
            if item.product is product:
                if quantity > product.stock:
                    raise ValueError(f"Insufficient stock for {product.name}")
                item.quantity = quantity
                return
        raise ValueError(f"{product.name} not in cart")

    @property
    def subtotal(self) -> float:
        """Calculate subtotal before tax."""
        return sum(item.subtotal for item in self._items)

    @property
    def tax(self) -> float:
        """Calculate tax amount."""
        return self.subtotal * self._tax_rate

    @property
    def total(self) -> float:
        """Calculate total including tax."""
        return self.subtotal + self.tax

    def clear(self) -> None:
        """Clear all items from cart."""
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
```

### Solution 2: Plugin System

```python
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Type

# Global registry
_plugin_registry: Dict[str, Type['Plugin']] = {}

class Plugin(ABC):
    """Base class for all plugins."""

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

def register_plugin(plugin_name: str):
    """Decorator to register a plugin."""
    def decorator(plugin_class: Type[Plugin]):
        _plugin_registry[plugin_name] = plugin_class
        return plugin_class
    return decorator

class PluginManager:
    """Manages plugin lifecycle."""

    def list_plugins(self) -> list[str]:
        """List all registered plugin names."""
        return list(_plugin_registry.keys())

    def get_plugin(self, name: str) -> Plugin:
        """Get a plugin instance by name."""
        plugin_class = _plugin_registry.get(name)
        if not plugin_class:
            raise ValueError(f"Plugin '{name}' not found")
        return plugin_class()

    def execute_plugin(self, name: str, data: Any) -> Any:
        """Execute a plugin by name."""
        plugin = self.get_plugin(name)
        return plugin.execute(data)

@register_plugin("csv_exporter")
class CSVExporter(Plugin):
    @property
    def name(self) -> str:
        return "CSV Exporter"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> str:
        """Export data as CSV."""
        if isinstance(data, dict) and "data" in data:
            items = data["data"]
            return ",".join(str(item) for item in items)
        return str(data)

@register_plugin("json_exporter")
class JSONExporter(Plugin):
    @property
    def name(self) -> str:
        return "JSON Exporter"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, data: Any) -> str:
        """Export data as JSON."""
        import json
        return json.dumps(data)
```

*(Additional solutions would continue for other exercises...)*

---

## Additional Practice Ideas

Once you've completed these exercises, try:

1. **Combine Exercises**: Create a system that uses multiple patterns together
2. **Add Tests**: Write unit tests for each exercise using `pytest`
3. **Add Type Hints**: Ensure all code has proper type annotations
4. **Add Documentation**: Write comprehensive docstrings
5. **Optimize Performance**: Profile and optimize critical code paths
6. **Add CLI**: Create command-line interfaces for your systems
7. **Add Persistence**: Add database or file storage
8. **Add Concurrency**: Make systems thread-safe or async

---

## Next Steps

After completing these exercises:

1. Review the [Advanced OOP Concepts](./advanced_oop_concepts.md) guide
2. Study the [OOP Anti-Patterns](./appendix_oop_antipatterns.md) to avoid common mistakes
3. Work on the 30-day lesson plan capstone project
4. Build your own project applying these concepts

**Remember:** The goal isn't just to make code work, but to make it well-designed, maintainable, and extensible!
