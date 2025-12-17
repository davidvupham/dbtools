# Type Hints

## What are Type Hints?

Type hints tell Python (and developers) what type of data a variable or function expects. They don't change how Python runs, but they help catch errors and make code clearer.

## Basic Type Hints

```python
# Without type hints
def greet(name):
    return f"Hello, {name}!"

# With type hints
def greet(name: str) -> str:
    return f"Hello, {name}!"
    # name: str means "name should be a string"
    # -> str means "this function returns a string"
```

## Common Type Hints

```python
from typing import Optional, List, Dict, Tuple, Any, Union

# Basic types
def add(a: int, b: int) -> int:
    return a + b

# Optional (can be None)
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

# Lists
def get_names() -> List[str]:
    return ["Alice", "Bob"]

# Dictionaries
def get_user() -> Dict[str, Any]:
    return {"name": "Alice", "age": 30}

# Union (Multiple types)
def process_id(id: Union[int, str]) -> str:
    return str(id)
```

## Benefits

1. **Catch Errors Early**: IDE warns before running code
2. **Better Documentation**: Clear what functions expect
3. **Improved Autocomplete**: IDE knows available methods
