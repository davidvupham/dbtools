# Solutions — 13: Modules and Packages

## Key Concepts Demonstrated

- Module creation and import styles
- Package structure with `__init__.py`
- Relative vs absolute imports
- Controlling exports with `__all__`
- Resolving circular imports
- Dynamic module loading with `importlib`

## Common Mistakes to Avoid

- Using `from module import *` (pollutes namespace)
- Circular imports between modules
- Forgetting `__init__.py` in packages (Python 3.3+ makes them optional but they're still useful)
- Using relative imports in scripts (only work in packages)
- Not defining `__all__` for public APIs

---

## Exercise 1 Solution

```python
# math_utils.py
def add(a, b):
    """Return sum of a and b."""
    return a + b

def multiply(a, b):
    """Return product of a and b."""
    return a * b

PI = 3.14159

def circle_area(radius):
    """Return area of circle."""
    return PI * radius ** 2
```

```python
# main.py

# Import the entire module
import math_utils
print(f"Using module prefix: add(2, 3) = {math_utils.add(2, 3)}")

# Import specific functions
from math_utils import multiply
print(f"Using direct import: multiply(4, 5) = {multiply(4, 5)}")

# Import with alias
import math_utils as mu
print(f"Using alias: mu.PI = {mu.PI}")

# Import constant and function
from math_utils import circle_area
print(f"Circle area with radius 5: {circle_area(5)}")
```

**Output**:
```
Using module prefix: add(2, 3) = 5
Using direct import: multiply(4, 5) = 20
Using alias: mu.PI = 3.14159
Circle area with radius 5: 78.53975
```

---

## Exercise 2 Solution

```python
# shapes/circle.py
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

def create_circle(radius):
    """Factory function."""
    return Circle(radius)
```

```python
# shapes/rectangle.py
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)
```

```python
# shapes/triangle.py
class Triangle:
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height
```

```python
# shapes/__init__.py
from .circle import Circle, create_circle
from .rectangle import Rectangle
from .triangle import Triangle

__all__ = ['Circle', 'Rectangle', 'Triangle', 'create_circle']
```

**Test**:
```python
from shapes import Circle, Rectangle, Triangle

c = Circle(5)
r = Rectangle(4, 6)
t = Triangle(3, 4)

print(f"Circle area: {c.area():.2f}")      # 78.54
print(f"Rectangle area: {r.area()}")        # 24
print(f"Triangle area: {t.area()}")         # 6.0
```

---

## Exercise 3 Solution

```python
# myproject/core/base.py
class BaseProcessor:
    def process(self, data):
        return f"Processed: {data}"
```

```python
# myproject/core/utils.py
def validate(data):
    return data is not None and len(data) > 0

def transform(data):
    return data.upper() if isinstance(data, str) else data
```

```python
# myproject/core/__init__.py
from .base import BaseProcessor
from .utils import validate, transform

__all__ = ['BaseProcessor', 'validate', 'transform']
```

```python
# myproject/features/feature_a.py
from ..core.base import BaseProcessor
from ..core.utils import validate, transform

class FeatureA(BaseProcessor):
    def process(self, data):
        if not validate(data):
            raise ValueError("Invalid data")
        transformed = transform(data)
        return super().process(transformed)
```

```python
# myproject/features/feature_b.py
from .feature_a import FeatureA

class FeatureB:
    def __init__(self):
        self.processor = FeatureA()

    def run(self, data):
        return self.processor.process(data)
```

```python
# myproject/features/__init__.py
from .feature_a import FeatureA
from .feature_b import FeatureB

__all__ = ['FeatureA', 'FeatureB']
```

```python
# myproject/__init__.py
from .core import BaseProcessor, validate, transform
from .features import FeatureA, FeatureB

__all__ = ['BaseProcessor', 'validate', 'transform', 'FeatureA', 'FeatureB']
```

**Test**:
```python
from myproject.features.feature_b import FeatureB

fb = FeatureB()
result = fb.run("hello")
print(result)  # Processed: HELLO
```

---

## Exercise 4 Solution

```python
# api.py

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

# Private helpers
def _validate_email(email):
    if "@" not in email:
        raise ValueError("Invalid email")

def _fetch_user(user_id):
    return {"id": user_id, "name": "Test"}

def _save_user(name, email):
    return {"id": 1, "name": name, "email": email}

def _remove_user(user_id):
    return True

# Configuration
_DATABASE_URL = "postgresql://localhost/mydb"
_API_KEY = "secret-key"

# Only export public API
__all__ = ['get_user', 'create_user', 'delete_user']
```

**Note**: `__all__` only affects `from module import *`. Direct imports like `from api import _validate_email` still work. The underscore prefix is a convention, not enforcement.

---

## Exercise 5 Solution

**Problem Analysis**:

1. **Why circular import**: When Python imports `models.py`, it tries to import `services.py` first. But `services.py` tries to import `models.py`, which is not fully loaded yet. This creates a circular dependency.

2. **Error**: `ImportError: cannot import name 'UserService' from partially initialized module 'services'`

**Solution 1: Import inside function (lazy import)**:

```python
# models.py
class User:
    def __init__(self, name):
        self.name = name

    def save(self):
        # Import inside method to avoid circular import
        from services import UserService
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

**Solution 2: Dependency injection**:

```python
# models.py
class User:
    def __init__(self, name):
        self.name = name

    def save(self, service):
        # Accept service as parameter
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

# Usage
service = UserService()
user = service.get_user("Alice")
user.save(service)
```

**Solution 3: Restructure to avoid circular dependency**:

```python
# models.py (pure data classes, no dependencies)
class User:
    def __init__(self, name):
        self.name = name
```

```python
# services.py (depends on models, but models doesn't depend on services)
from models import User

class UserService:
    def get_user(self, name):
        return User(name)

    def save_user(self, user):
        print(f"Saving {user.name}")

    def create_and_save(self, name):
        user = self.get_user(name)
        self.save_user(user)
        return user
```

**Solution 4: Use TYPE_CHECKING for type hints only**:

```python
# models.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services import UserService  # Only imported for type checking

class User:
    def __init__(self, name):
        self.name = name

    def save(self, service: "UserService"):
        service.save_user(self)
```

---

## Exercise 6 Solution

```python
# ecommerce/utils/validators.py
import re

def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_price(price: float) -> bool:
    return isinstance(price, (int, float)) and price >= 0
```

```python
# ecommerce/utils/formatters.py
def format_currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"

def format_quantity(quantity: int) -> str:
    return f"{quantity:,}"
```

```python
# ecommerce/utils/__init__.py
from .validators import validate_email, validate_price
from .formatters import format_currency, format_quantity

__all__ = ['validate_email', 'validate_price', 'format_currency', 'format_quantity']
```

```python
# ecommerce/models/product.py
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    stock: int = 0

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")
```

```python
# ecommerce/models/user.py
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product

@dataclass
class User:
    name: str
    email: str
    cart: list = field(default_factory=list)

    def __post_init__(self):
        from ..utils import validate_email
        if not validate_email(self.email):
            raise ValueError(f"Invalid email: {self.email}")
```

```python
# ecommerce/models/order.py
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import uuid

from .user import User
from .product import Product

@dataclass
class OrderItem:
    product: Product
    quantity: int
    price: float  # Price at time of order

@dataclass
class Order:
    user: User
    items: List[OrderItem] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)
```

```python
# ecommerce/models/__init__.py
from .product import Product
from .user import User
from .order import Order, OrderItem

__all__ = ['Product', 'User', 'Order', 'OrderItem']
```

```python
# ecommerce/services/cart.py
from typing import Dict
from ..models import User, Product

class CartService:
    def __init__(self, user: User):
        self.user = user
        self._items: Dict[Product, int] = {}

    def add(self, product: Product, quantity: int = 1):
        if product.stock < quantity:
            raise ValueError(f"Not enough stock for {product.name}")
        current = self._items.get(product, 0)
        self._items[product] = current + quantity

    def remove(self, product: Product, quantity: int = 1):
        if product not in self._items:
            raise ValueError(f"{product.name} not in cart")
        self._items[product] -= quantity
        if self._items[product] <= 0:
            del self._items[product]

    def total(self) -> float:
        return sum(p.price * qty for p, qty in self._items.items())

    def items(self):
        return list(self._items.items())

    def clear(self):
        self._items.clear()
```

```python
# ecommerce/services/checkout.py
from ..models import User, Order, OrderItem
from .cart import CartService

class CheckoutService:
    def create_order(self, user: User, cart: CartService) -> Order:
        if not cart.items():
            raise ValueError("Cannot checkout empty cart")

        order_items = [
            OrderItem(product=product, quantity=qty, price=product.price)
            for product, qty in cart.items()
        ]

        # Reduce stock
        for product, qty in cart.items():
            product.stock -= qty

        # Clear cart
        cart.clear()

        return Order(user=user, items=order_items)
```

```python
# ecommerce/services/__init__.py
from .cart import CartService
from .checkout import CheckoutService

__all__ = ['CartService', 'CheckoutService']
```

```python
# ecommerce/__init__.py
from .models import Product, User, Order, OrderItem
from .services import CartService, CheckoutService
from .utils import validate_email, validate_price, format_currency

__all__ = [
    'Product', 'User', 'Order', 'OrderItem',
    'CartService', 'CheckoutService',
    'validate_email', 'validate_price', 'format_currency'
]
```

**Test**:
```python
from ecommerce import Product, User, CartService, CheckoutService

laptop = Product("Laptop", 999.99, stock=10)
mouse = Product("Mouse", 29.99, stock=50)

user = User("Alice", "alice@example.com")

cart = CartService(user)
cart.add(laptop, quantity=1)
cart.add(mouse, quantity=2)
print(f"Cart total: ${cart.total():.2f}")  # $1,059.97

checkout = CheckoutService()
order = checkout.create_order(user, cart)
print(f"Order created: {order.id}")
print(f"Order total: ${order.total:.2f}")
```

---

## Exercise 7 Solution

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

```python
# plugins/__init__.py
import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional
from .base import Plugin

_plugin_cache = {}

def discover_plugins() -> List[str]:
    """Discover all plugins in the plugins directory."""
    plugins = []
    package_path = Path(__file__).parent

    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        if module_name.endswith('_plugin'):
            # Extract plugin name (remove _plugin suffix)
            plugin_name = module_name.replace('_plugin', '')
            plugins.append(plugin_name)

    return plugins

def load_plugin(name: str) -> Optional[Plugin]:
    """Load a specific plugin by name."""
    if name in _plugin_cache:
        return _plugin_cache[name]

    module_name = f".{name}_plugin"

    try:
        module = importlib.import_module(module_name, package='plugins')
    except ImportError:
        raise ValueError(f"Plugin '{name}' not found")

    # Find the Plugin subclass in the module
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and
            issubclass(attr, Plugin) and
            attr is not Plugin):
            instance = attr()
            _plugin_cache[name] = instance
            return instance

    raise ValueError(f"No Plugin class found in {name}_plugin")

def get_all_plugins() -> List[Plugin]:
    """Load and return all available plugins."""
    return [load_plugin(name) for name in discover_plugins()]

__all__ = ['Plugin', 'discover_plugins', 'load_plugin', 'get_all_plugins']
```

**Test**:
```python
from plugins import discover_plugins, load_plugin, get_all_plugins

# Discover all available plugins
plugins = discover_plugins()
print(f"Available plugins: {plugins}")  # ['uppercase', 'reverse']

# Load and use a specific plugin
uppercase = load_plugin("uppercase")
print(uppercase.execute("hello"))  # HELLO

reverse = load_plugin("reverse")
print(reverse.execute("hello"))  # olleh

# Load all plugins and run them
all_plugins = get_all_plugins()
data = "Python"
for plugin in all_plugins:
    print(f"{plugin.name}: {plugin.execute(data)}")
```

---

## Exercise 8 Solution

```python
import inspect
from types import ModuleType
from typing import Dict, List, Any

def analyze_module(module: ModuleType) -> Dict[str, Any]:
    """
    Analyze a module and return information about its contents.
    """
    functions = []
    classes = []
    constants = []
    private = []

    for name in dir(module):
        # Skip dunder names for cleaner output
        if name.startswith('__') and name.endswith('__'):
            continue

        obj = getattr(module, name)

        # Track private names
        if name.startswith('_'):
            private.append(name)
            continue

        # Categorize public names
        if inspect.isfunction(obj):
            functions.append(name)
        elif inspect.isclass(obj):
            classes.append(name)
        elif name.isupper():  # Convention for constants
            constants.append(name)

    return {
        'functions': sorted(functions),
        'classes': sorted(classes),
        'constants': sorted(constants),
        'private': sorted(private),
        'docstring': module.__doc__,
        'name': module.__name__,
        'file': getattr(module, '__file__', 'built-in'),
    }

def print_analysis(analysis: Dict[str, Any]):
    """Pretty print module analysis."""
    print(f"Module: {analysis['name']}")
    print(f"File: {analysis['file']}")
    print(f"\nDocstring:\n{analysis['docstring'][:200]}..." if analysis['docstring'] else "No docstring")
    print(f"\nFunctions ({len(analysis['functions'])}):")
    for f in analysis['functions'][:10]:
        print(f"  - {f}")
    if len(analysis['functions']) > 10:
        print(f"  ... and {len(analysis['functions']) - 10} more")
    print(f"\nClasses ({len(analysis['classes'])}):")
    for c in analysis['classes'][:10]:
        print(f"  - {c}")
    print(f"\nConstants ({len(analysis['constants'])}):")
    for c in analysis['constants'][:10]:
        print(f"  - {c}")

# Test with json module
import json
analysis = analyze_module(json)
print_analysis(analysis)

# Test with collections module
import collections
analysis = analyze_module(collections)
print_analysis(analysis)
```

**Output**:
```
Module: json
File: /usr/lib/python3.11/json/__init__.py

Docstring:
JSON (JavaScript Object Notation) <http://json.org> is a subset of
JavaScript syntax (ECMA-262 3rd edition) used as a lightweight data
interchange format....

Functions (4):
  - dump
  - dumps
  - load
  - loads

Classes (2):
  - JSONDecoder
  - JSONEncoder

Constants (0):
```

---

## Import Best Practices Summary

| Practice | Good | Bad |
|----------|------|-----|
| Import style | `from module import specific` | `from module import *` |
| Import location | Top of file | Inside functions (unless avoiding circular) |
| Relative imports | In packages: `from .sibling import x` | In scripts (won't work) |
| `__all__` | Define for public APIs | Omit (everything is public) |
| Circular imports | Restructure or lazy import | Direct circular dependencies |

---

[← Back to Exercises](../exercises/ex_13_modules_packages.md) | [← Back to Chapter](../13_modules_packages.md) | [← Back to Module 2](../README.md)
