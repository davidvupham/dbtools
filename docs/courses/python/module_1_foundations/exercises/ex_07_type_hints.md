# Exercises — 07: Type Hints

## Learning Objectives

After completing these exercises, you will be able to:
- Add type hints to function signatures
- Use common types from the `typing` module
- Create type aliases for complex types
- Use Optional, Union, and Literal types
- Understand generic types and TypeVar
- Apply type hints to classes and methods

---

## Exercise 1: Basic Type Hints (Warm-up)

**Bloom Level**: Apply

Add type hints to the following functions:

```python
# Add type hints to all parameters and return values

def greet(name):
    """Return a greeting string."""
    return f"Hello, {name}!"

def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    return length * width

def is_even(number):
    """Check if a number is even."""
    return number % 2 == 0

def get_initials(first_name, last_name):
    """Get initials from first and last name."""
    return f"{first_name[0]}.{last_name[0]}."

def repeat_string(text, times):
    """Repeat a string n times."""
    return text * times

def sum_list(numbers):
    """Sum all numbers in a list."""
    return sum(numbers)

def count_words(text):
    """Count words in a text."""
    return len(text.split())

def merge_dicts(dict1, dict2):
    """Merge two dictionaries."""
    return {**dict1, **dict2}
```

---

## Exercise 2: Optional and Union Types (Practice)

**Bloom Level**: Apply

Add appropriate type hints using `Optional` and `Union`:

```python
from typing import Optional, Union

def find_user(user_id):
    """
    Find a user by ID.

    Returns:
        User dict if found, None if not found.
    """
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return users.get(user_id)

def parse_value(value):
    """
    Parse a string to int or float.

    Returns:
        int if value is whole number, float otherwise, None if invalid.
    """
    try:
        num = float(value)
        return int(num) if num.is_integer() else num
    except ValueError:
        return None

def get_config(key, default):
    """
    Get a config value with a default.

    Args:
        key: Configuration key.
        default: Default value if key not found (can be any type).

    Returns:
        The config value or default.
    """
    config = {"debug": True, "port": 8080}
    return config.get(key, default)

def process_input(data):
    """
    Process input that can be string, list of strings, or None.

    Returns:
        Processed string or None.
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data.upper()
    return " ".join(data).upper()
```

---

## Exercise 3: Collection Types (Practice)

**Bloom Level**: Apply

Add type hints for collections:

```python
from typing import List, Dict, Set, Tuple

def unique_words(sentences):
    """
    Get unique words from a list of sentences.

    Args:
        sentences: List of sentence strings.

    Returns:
        Set of unique words.
    """
    words = set()
    for sentence in sentences:
        words.update(sentence.lower().split())
    return words

def group_by_length(words):
    """
    Group words by their length.

    Args:
        words: List of words.

    Returns:
        Dictionary mapping length to list of words.
    """
    result = {}
    for word in words:
        length = len(word)
        if length not in result:
            result[length] = []
        result[length].append(word)
    return result

def parse_csv_row(row):
    """
    Parse a CSV row into a tuple of (name, age, city).

    Args:
        row: Comma-separated string.

    Returns:
        Tuple of (name, age, city).
    """
    parts = row.split(",")
    return (parts[0].strip(), int(parts[1].strip()), parts[2].strip())

def create_user_index(users):
    """
    Create an index of users by their ID.

    Args:
        users: List of user dictionaries with 'id' and 'name' keys.

    Returns:
        Dictionary mapping user ID to user name.
    """
    return {user["id"]: user["name"] for user in users}
```

---

## Exercise 4: Callable Types (Practice)

**Bloom Level**: Apply

Add type hints for functions that accept or return other functions:

```python
from typing import Callable

def apply_to_all(items, func):
    """
    Apply a function to all items.

    Args:
        items: List of items.
        func: Function that takes one item and returns a transformed item.

    Returns:
        List of transformed items.
    """
    return [func(item) for item in items]

def create_multiplier(factor):
    """
    Create a function that multiplies by a factor.

    Args:
        factor: The multiplication factor.

    Returns:
        A function that takes a number and returns it multiplied by factor.
    """
    def multiplier(x):
        return x * factor
    return multiplier

def compose(f, g):
    """
    Compose two functions: compose(f, g)(x) = f(g(x)).

    Args:
        f: Outer function.
        g: Inner function.

    Returns:
        Composed function.
    """
    def composed(x):
        return f(g(x))
    return composed

def retry_on_failure(func, max_attempts):
    """
    Wrap a function to retry on failure.

    Args:
        func: Function that takes no arguments and returns a result or raises.
        max_attempts: Maximum number of attempts.

    Returns:
        A function that retries the original function.
    """
    def wrapper():
        for _ in range(max_attempts):
            try:
                return func()
            except Exception:
                continue
        raise RuntimeError("All attempts failed")
    return wrapper
```

---

## Exercise 5: TypedDict and Literal (Practice)

**Bloom Level**: Apply

Use TypedDict and Literal for more precise types:

```python
from typing import TypedDict, Literal

# Define a TypedDict for a User
# Fields: id (str), name (str), email (str), role ("admin" | "user" | "guest")

class User(TypedDict):
    pass  # Define the fields

# Define a TypedDict for an API Response
# Fields: status ("success" | "error"), data (optional dict), message (optional str)

class ApiResponse(TypedDict, total=False):
    pass  # Define the fields

def create_user(id, name, email, role):
    """Create a user dictionary."""
    return User(id=id, name=name, email=email, role=role)

def make_response(status, data, message):
    """Create an API response."""
    response = {"status": status}
    if data is not None:
        response["data"] = data
    if message is not None:
        response["message"] = message
    return response

def get_user_role(user):
    """Get the role from a user."""
    return user["role"]

# Test your types
user = create_user("1", "Alice", "alice@example.com", "admin")
response = make_response("success", {"user": user}, None)
role = get_user_role(user)
```

---

## Exercise 6: Generic Types (Analyze)

**Bloom Level**: Analyze

Use TypeVar to create generic functions:

```python
from typing import TypeVar, List, Optional

# Define type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

def first(items):
    """
    Get the first item from a list.

    Should work with any list type and return that type.
    """
    if not items:
        return None
    return items[0]

def last(items):
    """
    Get the last item from a list.

    Should work with any list type and return that type.
    """
    if not items:
        return None
    return items[-1]

def find_by_key(items, key, value):
    """
    Find first item where item[key] equals value.

    Args:
        items: List of dictionaries.
        key: Key to look up.
        value: Value to match.

    Returns:
        First matching item or None.
    """
    for item in items:
        if item.get(key) == value:
            return item
    return None

def swap(pair):
    """
    Swap elements of a pair.

    Args:
        pair: Tuple of two elements.

    Returns:
        Tuple with elements swapped.
    """
    return (pair[1], pair[0])

def merge(list1, list2):
    """
    Merge two lists of the same type.

    Args:
        list1: First list.
        list2: Second list.

    Returns:
        Combined list.
    """
    return list1 + list2
```

---

## Exercise 7: Class Type Hints (Practice)

**Bloom Level**: Apply

Add type hints to this class:

```python
from typing import List, Optional, ClassVar
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    """A product in the inventory."""

    id: ...          # str
    name: ...        # str
    price: ...       # float
    quantity: ...    # int
    category: ...    # str (optional, default None)

class Inventory:
    """Manages product inventory."""

    _instance = None  # Class variable for singleton

    def __init__(self):
        self._products = {}  # Dict[str, Product]

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_product(self, product):
        """Add a product to inventory."""
        self._products[product.id] = product

    def get_product(self, product_id):
        """Get a product by ID."""
        return self._products.get(product_id)

    def search(self, category, min_price, max_price):
        """
        Search products by category and price range.

        Args:
            category: Category to filter by (None for all).
            min_price: Minimum price (None for no minimum).
            max_price: Maximum price (None for no maximum).

        Returns:
            List of matching products.
        """
        results = []
        for product in self._products.values():
            if category and product.category != category:
                continue
            if min_price and product.price < min_price:
                continue
            if max_price and product.price > max_price:
                continue
            results.append(product)
        return results

    def total_value(self):
        """Calculate total value of inventory."""
        return sum(p.price * p.quantity for p in self._products.values())

    def low_stock(self, threshold):
        """Get products with quantity below threshold."""
        return [p for p in self._products.values() if p.quantity < threshold]
```

---

## Exercise 8: Protocol Types (Challenge)

**Bloom Level**: Create

Use Protocol to define structural typing:

```python
from typing import Protocol, runtime_checkable

# Define a Protocol for objects that can be serialized to dict
@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict:
        """Convert object to dictionary."""
        ...

# Define a Protocol for objects that can be compared
class Comparable(Protocol):
    def __lt__(self, other) -> bool:
        ...

    def __eq__(self, other) -> bool:
        ...

# Define a Protocol for objects that can be logged
class Loggable(Protocol):
    @property
    def log_name(self) -> str:
        """Name for logging purposes."""
        ...

    def get_log_data(self) -> dict:
        """Get data to include in logs."""
        ...

# Implement classes that satisfy these protocols
class User:
    """A user that implements Serializable and Loggable."""

    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    # Implement protocol methods
    pass

class Task:
    """A task that implements Serializable and Comparable."""

    def __init__(self, id: str, title: str, priority: int):
        self.id = id
        self.title = title
        self.priority = priority

    # Implement protocol methods
    pass

# Functions that accept protocol types
def save_to_json(obj: Serializable) -> str:
    """Save any Serializable object to JSON string."""
    import json
    return json.dumps(obj.to_dict())

def sort_items(items):
    """Sort any list of Comparable items."""
    return sorted(items)

def log_object(obj: Loggable) -> None:
    """Log any Loggable object."""
    print(f"[{obj.log_name}] {obj.get_log_data()}")

# Test
user = User("1", "Alice", "alice@example.com")
print(f"User is Serializable: {isinstance(user, Serializable)}")
print(save_to_json(user))

task1 = Task("1", "Write docs", 2)
task2 = Task("2", "Fix bug", 1)
sorted_tasks = sort_items([task1, task2])
```

---

## Exercise 9: Type Checking a Module (Challenge)

**Bloom Level**: Evaluate

Add complete type hints to this module and run mypy to verify:

```python
"""
User management module.

Run mypy to check types:
    mypy this_file.py --strict
"""
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class User:
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    metadata: Dict[str, str] = field(default_factory=dict)

class UserRepository(Protocol):
    def get(self, user_id: str) -> Optional[User]: ...
    def save(self, user: User) -> None: ...
    def delete(self, user_id: str) -> bool: ...
    def find_by_email(self, email: str) -> Optional[User]: ...
    def list_all(self) -> List[User]: ...

class InMemoryUserRepository:
    """In-memory implementation of UserRepository."""

    def __init__(self):
        self._users = {}  # Add type hint

    def get(self, user_id):  # Add type hints
        return self._users.get(user_id)

    def save(self, user):  # Add type hints
        self._users[user.id] = user

    def delete(self, user_id):  # Add type hints
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def find_by_email(self, email):  # Add type hints
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def list_all(self):  # Add type hints
        return list(self._users.values())

class UserService:
    """Service for user operations."""

    def __init__(self, repository):  # Add type hint
        self._repo = repository

    def create_user(self, username, email, role):  # Add type hints
        """Create a new user."""
        user_id = str(len(self._repo.list_all()) + 1)
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role
        )
        self._repo.save(user)
        return user

    def authenticate(self, email):  # Add type hints
        """Authenticate user by email and update last_login."""
        user = self._repo.find_by_email(email)
        if user:
            user.last_login = datetime.now()
            self._repo.save(user)
        return user

    def get_users_by_role(self, role):  # Add type hints
        """Get all users with a specific role."""
        return [u for u in self._repo.list_all() if u.role == role]

    def update_metadata(self, user_id, key, value):  # Add type hints
        """Update user metadata."""
        user = self._repo.get(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        user.metadata[key] = value
        self._repo.save(user)

# Test the implementation
if __name__ == "__main__":
    repo = InMemoryUserRepository()
    service = UserService(repo)

    # Create users
    alice = service.create_user("alice", "alice@example.com", UserRole.ADMIN)
    bob = service.create_user("bob", "bob@example.com", UserRole.USER)

    # Authenticate
    user = service.authenticate("alice@example.com")
    if user:
        print(f"Authenticated: {user.username}, last login: {user.last_login}")

    # Get by role
    admins = service.get_users_by_role(UserRole.ADMIN)
    print(f"Admins: {[u.username for u in admins]}")
```

---

## Deliverables

Submit your code for all exercises. Run `mypy` on Exercise 9 and include the output.

---

[← Back to Chapter](../07_type_hints.md) | [View Solutions](../solutions/sol_07_type_hints.md) | [← Back to Module 1](../README.md)
