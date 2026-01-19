# Solutions — 07: Type Hints

## Key Concepts Demonstrated

- Basic type hints for parameters and return values
- Optional and Union types for nullable/multi-type values
- Collection types (List, Dict, Set, Tuple)
- Callable types for functions as parameters
- TypedDict and Literal for structured data
- TypeVar for generic functions
- Protocol for structural typing
- Class attributes and method type hints

## Common Mistakes to Avoid

- Using `list` instead of `List[T]` in Python < 3.9
- Forgetting `Optional` when None is a valid value
- Using mutable default arguments in typed functions
- Not importing types from `typing` module
- Over-specifying types (e.g., `List[Any]` when specific type known)

---

## Exercise 1 Solution

```python
def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"

def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width

def is_even(number: int) -> bool:
    """Check if a number is even."""
    return number % 2 == 0

def get_initials(first_name: str, last_name: str) -> str:
    """Get initials from first and last name."""
    return f"{first_name[0]}.{last_name[0]}."

def repeat_string(text: str, times: int) -> str:
    """Repeat a string n times."""
    return text * times

def sum_list(numbers: list[float]) -> float:
    """Sum all numbers in a list."""
    return sum(numbers)

def count_words(text: str) -> int:
    """Count words in a text."""
    return len(text.split())

def merge_dicts(dict1: dict[str, str], dict2: dict[str, str]) -> dict[str, str]:
    """Merge two dictionaries."""
    return {**dict1, **dict2}
```

**Note**: For Python 3.9+, you can use `list[T]` and `dict[K, V]` directly. For earlier versions, use `List[T]` and `Dict[K, V]` from `typing`.

---

## Exercise 2 Solution

```python
from typing import Optional, Union

def find_user(user_id: str) -> Optional[dict[str, str]]:
    """
    Find a user by ID.

    Returns:
        User dict if found, None if not found.
    """
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return users.get(user_id)

def parse_value(value: str) -> Optional[Union[int, float]]:
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

# Modern Python 3.10+ syntax
def parse_value_modern(value: str) -> int | float | None:
    """Same function with modern union syntax."""
    try:
        num = float(value)
        return int(num) if num.is_integer() else num
    except ValueError:
        return None

from typing import TypeVar
T = TypeVar('T')

def get_config(key: str, default: T) -> Union[bool, int, T]:
    """
    Get a config value with a default.

    Args:
        key: Configuration key.
        default: Default value if key not found (can be any type).

    Returns:
        The config value or default.
    """
    config: dict[str, Union[bool, int]] = {"debug": True, "port": 8080}
    return config.get(key, default)

def process_input(data: Optional[Union[str, list[str]]]) -> Optional[str]:
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

## Exercise 3 Solution

```python
from typing import List, Dict, Set, Tuple

def unique_words(sentences: List[str]) -> Set[str]:
    """
    Get unique words from a list of sentences.

    Args:
        sentences: List of sentence strings.

    Returns:
        Set of unique words.
    """
    words: Set[str] = set()
    for sentence in sentences:
        words.update(sentence.lower().split())
    return words

def group_by_length(words: List[str]) -> Dict[int, List[str]]:
    """
    Group words by their length.

    Args:
        words: List of words.

    Returns:
        Dictionary mapping length to list of words.
    """
    result: Dict[int, List[str]] = {}
    for word in words:
        length = len(word)
        if length not in result:
            result[length] = []
        result[length].append(word)
    return result

def parse_csv_row(row: str) -> Tuple[str, int, str]:
    """
    Parse a CSV row into a tuple of (name, age, city).

    Args:
        row: Comma-separated string.

    Returns:
        Tuple of (name, age, city).
    """
    parts = row.split(",")
    return (parts[0].strip(), int(parts[1].strip()), parts[2].strip())

def create_user_index(users: List[Dict[str, str]]) -> Dict[str, str]:
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

## Exercise 4 Solution

```python
from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')
S = TypeVar('S')

def apply_to_all(items: list[T], func: Callable[[T], R]) -> list[R]:
    """
    Apply a function to all items.

    Args:
        items: List of items.
        func: Function that takes one item and returns a transformed item.

    Returns:
        List of transformed items.
    """
    return [func(item) for item in items]

def create_multiplier(factor: float) -> Callable[[float], float]:
    """
    Create a function that multiplies by a factor.

    Args:
        factor: The multiplication factor.

    Returns:
        A function that takes a number and returns it multiplied by factor.
    """
    def multiplier(x: float) -> float:
        return x * factor
    return multiplier

def compose(
    f: Callable[[R], S],
    g: Callable[[T], R]
) -> Callable[[T], S]:
    """
    Compose two functions: compose(f, g)(x) = f(g(x)).

    Args:
        f: Outer function.
        g: Inner function.

    Returns:
        Composed function.
    """
    def composed(x: T) -> S:
        return f(g(x))
    return composed

def retry_on_failure(
    func: Callable[[], T],
    max_attempts: int
) -> Callable[[], T]:
    """
    Wrap a function to retry on failure.

    Args:
        func: Function that takes no arguments and returns a result or raises.
        max_attempts: Maximum number of attempts.

    Returns:
        A function that retries the original function.
    """
    def wrapper() -> T:
        for _ in range(max_attempts):
            try:
                return func()
            except Exception:
                continue
        raise RuntimeError("All attempts failed")
    return wrapper
```

---

## Exercise 5 Solution

```python
from typing import TypedDict, Literal, Optional

class User(TypedDict):
    id: str
    name: str
    email: str
    role: Literal["admin", "user", "guest"]

class ApiResponse(TypedDict, total=False):
    status: Literal["success", "error"]
    data: Optional[dict]
    message: Optional[str]

# Note: For required fields in a partial TypedDict, use:
class ApiResponseRequired(TypedDict):
    status: Literal["success", "error"]

class ApiResponseOptional(ApiResponseRequired, total=False):
    data: dict
    message: str

def create_user(
    id: str,
    name: str,
    email: str,
    role: Literal["admin", "user", "guest"]
) -> User:
    """Create a user dictionary."""
    return User(id=id, name=name, email=email, role=role)

def make_response(
    status: Literal["success", "error"],
    data: Optional[dict],
    message: Optional[str]
) -> ApiResponse:
    """Create an API response."""
    response: ApiResponse = {"status": status}
    if data is not None:
        response["data"] = data
    if message is not None:
        response["message"] = message
    return response

def get_user_role(user: User) -> Literal["admin", "user", "guest"]:
    """Get the role from a user."""
    return user["role"]

# Test
user = create_user("1", "Alice", "alice@example.com", "admin")
response = make_response("success", {"user": user}, None)
role = get_user_role(user)
print(f"User: {user}")
print(f"Response: {response}")
print(f"Role: {role}")
```

---

## Exercise 6 Solution

```python
from typing import TypeVar, List, Optional, Tuple, Dict

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
A = TypeVar('A')
B = TypeVar('B')

def first(items: List[T]) -> Optional[T]:
    """
    Get the first item from a list.

    Should work with any list type and return that type.
    """
    if not items:
        return None
    return items[0]

def last(items: List[T]) -> Optional[T]:
    """
    Get the last item from a list.

    Should work with any list type and return that type.
    """
    if not items:
        return None
    return items[-1]

def find_by_key(
    items: List[Dict[K, V]],
    key: K,
    value: V
) -> Optional[Dict[K, V]]:
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

def swap(pair: Tuple[A, B]) -> Tuple[B, A]:
    """
    Swap elements of a pair.

    Args:
        pair: Tuple of two elements.

    Returns:
        Tuple with elements swapped.
    """
    return (pair[1], pair[0])

def merge(list1: List[T], list2: List[T]) -> List[T]:
    """
    Merge two lists of the same type.

    Args:
        list1: First list.
        list2: Second list.

    Returns:
        Combined list.
    """
    return list1 + list2

# Test generic functions
numbers = [1, 2, 3, 4, 5]
print(f"first(numbers): {first(numbers)}")  # 1
print(f"last(numbers): {last(numbers)}")    # 5

strings = ["a", "b", "c"]
print(f"first(strings): {first(strings)}")  # "a"

users = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
print(f"find_by_key: {find_by_key(users, 'name', 'Bob')}")

print(f"swap: {swap((1, 'hello'))}")  # ('hello', 1)
print(f"merge: {merge([1, 2], [3, 4])}")  # [1, 2, 3, 4]
```

---

## Exercise 7 Solution

```python
from typing import List, Dict, Optional, ClassVar
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Product:
    """A product in the inventory."""

    id: str
    name: str
    price: float
    quantity: int
    category: Optional[str] = None

class Inventory:
    """Manages product inventory."""

    _instance: ClassVar[Optional["Inventory"]] = None

    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}

    @classmethod
    def get_instance(cls) -> "Inventory":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_product(self, product: Product) -> None:
        """Add a product to inventory."""
        self._products[product.id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID."""
        return self._products.get(product_id)

    def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Product]:
        """
        Search products by category and price range.

        Args:
            category: Category to filter by (None for all).
            min_price: Minimum price (None for no minimum).
            max_price: Maximum price (None for no maximum).

        Returns:
            List of matching products.
        """
        results: List[Product] = []
        for product in self._products.values():
            if category and product.category != category:
                continue
            if min_price and product.price < min_price:
                continue
            if max_price and product.price > max_price:
                continue
            results.append(product)
        return results

    def total_value(self) -> float:
        """Calculate total value of inventory."""
        return sum(p.price * p.quantity for p in self._products.values())

    def low_stock(self, threshold: int) -> List[Product]:
        """Get products with quantity below threshold."""
        return [p for p in self._products.values() if p.quantity < threshold]

# Test
inventory = Inventory()
inventory.add_product(Product("1", "Widget", 9.99, 100, "tools"))
inventory.add_product(Product("2", "Gadget", 19.99, 50, "electronics"))
inventory.add_product(Product("3", "Gizmo", 14.99, 5, "tools"))

print(f"Total value: ${inventory.total_value():.2f}")
print(f"Low stock: {inventory.low_stock(10)}")
print(f"Tools: {inventory.search(category='tools')}")
```

---

## Exercise 8 Solution

```python
from typing import Protocol, runtime_checkable
import json

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict:
        """Convert object to dictionary."""
        ...

class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...

class Loggable(Protocol):
    @property
    def log_name(self) -> str:
        """Name for logging purposes."""
        ...

    def get_log_data(self) -> dict:
        """Get data to include in logs."""
        ...

class User:
    """A user that implements Serializable and Loggable."""

    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    @property
    def log_name(self) -> str:
        return f"User:{self.id}"

    def get_log_data(self) -> dict:
        return {"name": self.name, "email": self.email}

class Task:
    """A task that implements Serializable and Comparable."""

    def __init__(self, id: str, title: str, priority: int) -> None:
        self.id = id
        self.title = title
        self.priority = priority

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority
        }

    def __lt__(self, other: "Task") -> bool:
        return self.priority < other.priority

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.priority == other.priority

    def __repr__(self) -> str:
        return f"Task({self.id!r}, {self.title!r}, priority={self.priority})"

def save_to_json(obj: Serializable) -> str:
    """Save any Serializable object to JSON string."""
    return json.dumps(obj.to_dict())

def sort_items(items: list[Comparable]) -> list[Comparable]:
    """Sort any list of Comparable items."""
    return sorted(items)

def log_object(obj: Loggable) -> None:
    """Log any Loggable object."""
    print(f"[{obj.log_name}] {obj.get_log_data()}")

# Test
user = User("1", "Alice", "alice@example.com")
print(f"User is Serializable: {isinstance(user, Serializable)}")
print(f"JSON: {save_to_json(user)}")
log_object(user)

task1 = Task("1", "Write docs", 2)
task2 = Task("2", "Fix bug", 1)
task3 = Task("3", "Review PR", 3)
sorted_tasks = sort_items([task1, task2, task3])
print(f"Sorted tasks: {sorted_tasks}")
```

---

## Exercise 9 Solution

```python
"""
User management module with complete type hints.
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

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def get(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user

    def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def list_all(self) -> List[User]:
        return list(self._users.values())

class UserService:
    """Service for user operations."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def create_user(
        self,
        username: str,
        email: str,
        role: UserRole
    ) -> User:
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

    def authenticate(self, email: str) -> Optional[User]:
        """Authenticate user by email and update last_login."""
        user = self._repo.find_by_email(email)
        if user:
            user.last_login = datetime.now()
            self._repo.save(user)
        return user

    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        return [u for u in self._repo.list_all() if u.role == role]

    def update_metadata(
        self,
        user_id: str,
        key: str,
        value: str
    ) -> None:
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

**mypy output** (should be clean):
```
$ mypy this_file.py --strict
Success: no issues found in 1 source file
```

---

## Type Hints Quick Reference

### Basic Types

| Type | Example | Description |
|------|---------|-------------|
| `int` | `x: int = 5` | Integer |
| `float` | `x: float = 3.14` | Floating point |
| `str` | `x: str = "hello"` | String |
| `bool` | `x: bool = True` | Boolean |
| `None` | `x: None = None` | None type |

### Collection Types

| Type | Example | Description |
|------|---------|-------------|
| `list[T]` | `x: list[int] = [1, 2]` | List of T |
| `dict[K, V]` | `x: dict[str, int] = {}` | Dict with K keys, V values |
| `set[T]` | `x: set[str] = set()` | Set of T |
| `tuple[T, ...]` | `x: tuple[int, str]` | Tuple with specific types |

### Special Types

| Type | Example | Description |
|------|---------|-------------|
| `Optional[T]` | `Optional[str]` | T or None |
| `Union[T, U]` | `Union[int, str]` | T or U |
| `Literal["a"]` | `Literal["yes", "no"]` | Specific values only |
| `Callable[[Args], Return]` | `Callable[[int], str]` | Function type |
| `TypeVar('T')` | `T = TypeVar('T')` | Generic type variable |

---

[← Back to Exercises](../exercises/ex_07_type_hints.md) | [← Back to Chapter](../07_type_hints.md) | [← Back to Module 1](../README.md)
