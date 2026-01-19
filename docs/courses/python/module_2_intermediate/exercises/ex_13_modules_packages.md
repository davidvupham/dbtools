# Exercises — 13: Modules and Packages

## Learning Objectives

After completing these exercises, you will be able to:
- Create and import Python modules
- Build packages with `__init__.py` files
- Use absolute and relative imports
- Control what gets exported with `__all__`
- Avoid circular import issues
- Organize code into a clean package structure

---

## Exercise 1: Basic Module Import (Warm-up)

**Bloom Level**: Remember

Create a module `math_utils.py` with the following functions, then import and use them in different ways:

```python
# math_utils.py
def add(a, b):
    """Return sum of a and b."""
    pass

def multiply(a, b):
    """Return product of a and b."""
    pass

PI = 3.14159

def circle_area(radius):
    """Return area of circle."""
    pass
```

```python
# main.py
# Import the entire module
# Import specific functions
# Import with alias
# Import all public names

# Test all import styles
```

**Expected Output**:
```
Using module prefix: add(2, 3) = 5
Using direct import: multiply(4, 5) = 20
Using alias: mu.PI = 3.14159
Circle area with radius 5: 78.53975
```

---

## Exercise 2: Creating a Package (Practice)

**Bloom Level**: Apply

Create a package called `shapes` with the following structure:

```
shapes/
    __init__.py
    circle.py
    rectangle.py
    triangle.py
```

Each module should contain a class and helper functions:

```python
# circle.py
class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        pass

    def perimeter(self):
        pass

def create_circle(radius):
    """Factory function."""
    pass
```

```python
# rectangle.py
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        pass

    def perimeter(self):
        pass
```

```python
# triangle.py
class Triangle:
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        pass
```

Create an `__init__.py` that exports the main classes:

```python
# __init__.py
# Export classes so users can do:
# from shapes import Circle, Rectangle, Triangle
```

**Test**:
```python
from shapes import Circle, Rectangle, Triangle

c = Circle(5)
r = Rectangle(4, 6)
t = Triangle(3, 4)

print(f"Circle area: {c.area():.2f}")
print(f"Rectangle area: {r.area()}")
print(f"Triangle area: {t.area()}")
```

---

## Exercise 3: Relative Imports (Practice)

**Bloom Level**: Apply

Create a package with subpackages and use relative imports:

```
myproject/
    __init__.py
    core/
        __init__.py
        base.py
        utils.py
    features/
        __init__.py
        feature_a.py
        feature_b.py
```

```python
# core/base.py
class BaseProcessor:
    def process(self, data):
        return f"Processed: {data}"
```

```python
# core/utils.py
def validate(data):
    return data is not None and len(data) > 0

def transform(data):
    return data.upper() if isinstance(data, str) else data
```

```python
# features/feature_a.py
# Use relative imports to import from core
# from ..core.base import BaseProcessor
# from ..core.utils import validate, transform

class FeatureA(BaseProcessor):
    def process(self, data):
        if not validate(data):
            raise ValueError("Invalid data")
        transformed = transform(data)
        return super().process(transformed)
```

```python
# features/feature_b.py
# Import from sibling module
# from .feature_a import FeatureA

class FeatureB:
    def __init__(self):
        self.processor = FeatureA()

    def run(self, data):
        return self.processor.process(data)
```

**Test**:
```python
from myproject.features.feature_b import FeatureB

fb = FeatureB()
result = fb.run("hello")
print(result)  # Processed: HELLO
```

---

## Exercise 4: The `__all__` Variable (Practice)

**Bloom Level**: Apply

Create a module that controls what gets exported with `from module import *`:

```python
# api.py

# Public functions
def get_user(user_id):
    """Get user by ID - PUBLIC."""
    return _fetch_user(user_id)

def create_user(name, email):
    """Create new user - PUBLIC."""
    _validate_email(email)
    return _save_user(name, email)

def delete_user(user_id):
    """Delete user - PUBLIC."""
    return _remove_user(user_id)

# Private helpers (should not be exported)
def _validate_email(email):
    """Internal validation."""
    if "@" not in email:
        raise ValueError("Invalid email")

def _fetch_user(user_id):
    """Internal database fetch."""
    return {"id": user_id, "name": "Test"}

def _save_user(name, email):
    """Internal database save."""
    return {"id": 1, "name": name, "email": email}

def _remove_user(user_id):
    """Internal database delete."""
    return True

# Configuration (should not be exported)
_DATABASE_URL = "postgresql://localhost/mydb"
_API_KEY = "secret-key"

# Define __all__ to control exports
__all__ = ???
```

**Test**:
```python
from api import *

# These should work
print(get_user(1))
print(create_user("Alice", "alice@example.com"))

# These should NOT be accessible
try:
    print(_validate_email)  # Should raise NameError
except NameError:
    print("_validate_email not exported (correct!)")

try:
    print(_DATABASE_URL)  # Should raise NameError
except NameError:
    print("_DATABASE_URL not exported (correct!)")
```

---

## Exercise 5: Avoiding Circular Imports (Analyze)

**Bloom Level**: Analyze

The following code has a circular import problem. Identify the issue and fix it:

```python
# models.py
from services import UserService

class User:
    def __init__(self, name):
        self.name = name

    def save(self):
        service = UserService()
        service.save_user(self)
```

```python
# services.py
from models import User

class UserService:
    def get_user(self, name):
        return User(name)

    def save_user(self, user):
        print(f"Saving {user.name}")
```

**Questions**:
1. Why does this cause a circular import?
2. What error would you see when trying to import either module?
3. Provide at least two different solutions to fix this problem.

---

## Exercise 6: Package with Subpackages (Challenge)

**Bloom Level**: Create

Create a complete package structure for a simple e-commerce system:

```
ecommerce/
    __init__.py
    models/
        __init__.py
        product.py
        user.py
        order.py
    services/
        __init__.py
        cart.py
        checkout.py
    utils/
        __init__.py
        validators.py
        formatters.py
```

Requirements:
1. `Product` class with name, price, and stock
2. `User` class with name, email, and cart
3. `Order` class that contains user and list of products
4. `CartService` that manages adding/removing products
5. `CheckoutService` that creates orders
6. Validators for email and price
7. Formatters for currency

The package should support these import patterns:

```python
# Direct class imports
from ecommerce.models import Product, User, Order

# Service imports
from ecommerce.services import CartService, CheckoutService

# Utility imports
from ecommerce.utils import validate_email, format_currency

# Or import everything from top level
from ecommerce import Product, User, CartService
```

**Test**:
```python
from ecommerce import Product, User, CartService, CheckoutService

# Create products
laptop = Product("Laptop", 999.99, stock=10)
mouse = Product("Mouse", 29.99, stock=50)

# Create user
user = User("Alice", "alice@example.com")

# Use cart service
cart = CartService(user)
cart.add(laptop, quantity=1)
cart.add(mouse, quantity=2)
print(f"Cart total: ${cart.total():.2f}")

# Checkout
checkout = CheckoutService()
order = checkout.create_order(user, cart)
print(f"Order created: {order.id}")
```

---

## Exercise 7: Dynamic Imports (Challenge)

**Bloom Level**: Create

Create a plugin system that dynamically loads modules:

```python
# plugins/__init__.py
import importlib
import pkgutil

def discover_plugins():
    """Discover all plugins in the plugins directory."""
    pass

def load_plugin(name):
    """Load a specific plugin by name."""
    pass
```

```python
# plugins/base.py
from abc import ABC, abstractmethod

class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, data):
        pass
```

```python
# plugins/uppercase_plugin.py
from .base import Plugin

class UppercasePlugin(Plugin):
    @property
    def name(self):
        return "uppercase"

    def execute(self, data):
        return data.upper()
```

```python
# plugins/reverse_plugin.py
from .base import Plugin

class ReversePlugin(Plugin):
    @property
    def name(self):
        return "reverse"

    def execute(self, data):
        return data[::-1]
```

**Test**:
```python
from plugins import discover_plugins, load_plugin

# Discover all available plugins
plugins = discover_plugins()
print(f"Available plugins: {plugins}")

# Load and use a specific plugin
uppercase = load_plugin("uppercase")
print(uppercase.execute("hello"))  # HELLO

reverse = load_plugin("reverse")
print(reverse.execute("hello"))  # olleh
```

---

## Exercise 8: Module Introspection (Analyze)

**Bloom Level**: Analyze

Write a function that analyzes a module and reports its contents:

```python
def analyze_module(module):
    """
    Analyze a module and return information about its contents.

    Returns dict with:
    - 'functions': list of function names
    - 'classes': list of class names
    - 'constants': list of uppercase variable names
    - 'private': list of names starting with _
    - 'docstring': module docstring
    """
    pass

# Test with a standard library module
import json
analysis = analyze_module(json)
print(f"Functions: {analysis['functions']}")
print(f"Classes: {analysis['classes']}")
print(f"Docstring: {analysis['docstring'][:100]}...")
```

**Hints**:
- Use `dir(module)` to get all names
- Use `inspect.isfunction()` and `inspect.isclass()`
- Use `getattr(module, name)` to get values
- Check `module.__doc__` for docstring

---

## Deliverables

Submit your code for all exercises. Include your analysis for Exercise 5.

---

[← Back to Chapter](../13_modules_packages.md) | [View Solutions](../solutions/sol_13_modules_packages.md) | [← Back to Module 2](../README.md)
