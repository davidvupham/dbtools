# Solutions — 04: Functions

## Key Concepts Demonstrated

- Function definition and calling
- Positional and keyword arguments
- Default parameter values
- Variable arguments (*args, **kwargs)
- Return values and multiple returns
- Variable scope (local, enclosing, global)
- Docstrings and type hints

## Common Mistakes to Avoid

- Mutable default arguments (use `None` and create inside function)
- Forgetting to return a value (function returns `None` by default)
- Modifying global variables without `global` keyword
- Putting non-default parameters after default parameters

---

## Exercise 1 Solution

```python
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"

# Test
print(greet("Alice"))  # Hello, Alice!
print(greet("World"))  # Hello, World!
```

---

## Exercise 2 Solution

```python
def calculate_rectangle(length: float, width: float) -> dict:
    """
    Calculate area and perimeter of a rectangle.

    Args:
        length: The length of the rectangle.
        width: The width of the rectangle.

    Returns:
        Dictionary with 'area' and 'perimeter' keys.
    """
    return {
        "area": length * width,
        "perimeter": 2 * (length + width)
    }

# Test
result = calculate_rectangle(5, 3)
print(result)  # {'area': 15, 'perimeter': 16}
```

---

## Exercise 3 Solution

```python
def create_profile(
    name: str,
    age: int,
    city: str = "Unknown",
    occupation: str = "Unspecified"
) -> str:
    """
    Create a formatted profile string.

    Args:
        name: Person's name (required).
        age: Person's age (required).
        city: City of residence (optional, default "Unknown").
        occupation: Job title (optional, default "Unspecified").

    Returns:
        Formatted profile string.
    """
    return f"{name}, {age} years old, from {city}, works as {occupation}"

# Tests
print(create_profile("Alice", 25))
# Alice, 25 years old, from Unknown, works as Unspecified

print(create_profile("Bob", 30, city="Seattle", occupation="Engineer"))
# Bob, 30 years old, from Seattle, works as Engineer

print(create_profile("Charlie", 28, occupation="Designer"))
# Charlie, 28 years old, from Unknown, works as Designer
```

---

## Exercise 4 Solution

**Part a) - Variable positional arguments:**

```python
def average(*numbers: float) -> float:
    """
    Calculate the average of any number of values.

    Args:
        *numbers: Variable number of numeric arguments.

    Returns:
        The average of all numbers, or 0 if no arguments.
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# Tests
print(average(10, 20, 30))  # 20.0
print(average(5))            # 5.0
print(average())             # 0
print(average(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))  # 5.5
```

**Part b) - Variable keyword arguments:**

```python
def build_query(**filters: str) -> str:
    """
    Build a SQL-like WHERE clause from keyword arguments.

    Args:
        **filters: Field=value pairs for the WHERE clause.

    Returns:
        SQL WHERE clause string.
    """
    if not filters:
        return ""

    conditions = [f"{key}='{value}'" for key, value in filters.items()]
    return "WHERE " + " AND ".join(conditions)

# Tests
print(build_query(name="Alice", age=25, city="Seattle"))
# WHERE name='Alice' AND age='25' AND city='Seattle'

print(build_query(status="active"))
# WHERE status='active'

print(build_query())
# (empty string)
```

---

## Exercise 5 Solution

```python
from typing import Callable

def apply_operation(
    numbers: list[float],
    operation: Callable[[float], float]
) -> list[float]:
    """
    Apply a function to each element in a list.

    Args:
        numbers: List of numbers to process.
        operation: Function to apply to each number.

    Returns:
        New list with operation applied to each element.
    """
    return [operation(n) for n in numbers]

def double(x: float) -> float:
    """Return x multiplied by 2."""
    return x * 2

def square(x: float) -> float:
    """Return x squared."""
    return x ** 2

# Tests
numbers = [1, 2, 3, 4, 5]
print(apply_operation(numbers, double))  # [2, 4, 6, 8, 10]
print(apply_operation(numbers, square))  # [1, 4, 9, 16, 25]

# With lambda
print(apply_operation(numbers, lambda x: x + 10))  # [11, 12, 13, 14, 15]
```

---

## Exercise 6 Solution

**Original code output prediction:**

```python
x = 10

def outer():
    x = 20

    def inner():
        x = 30
        print(f"inner: x = {x}")

    inner()
    print(f"outer: x = {x}")

outer()
print(f"global: x = {x}")
```

**Output:**
```
inner: x = 30
outer: x = 20
global: x = 10
```

Each function has its own local `x` variable. They don't affect each other.

**Modified to use nonlocal:**

```python
x = 10

def outer():
    x = 20

    def inner():
        nonlocal x  # Refers to outer's x
        x = 30
        print(f"inner: x = {x}")

    inner()
    print(f"outer: x = {x}")  # Now 30!

outer()
print(f"global: x = {x}")  # Still 10

# Output:
# inner: x = 30
# outer: x = 30
# global: x = 10
```

**Using global:**

```python
x = 10

def modify_global():
    global x
    x = 50

modify_global()
print(f"global: x = {x}")  # 50
```

---

## Exercise 7 Solution

```python
def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.

    Args:
        celsius: Temperature in Celsius.

    Returns:
        Temperature in Fahrenheit.
    """
    return celsius * 9/5 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit to Celsius.

    Args:
        fahrenheit: Temperature in Fahrenheit.

    Returns:
        Temperature in Celsius.
    """
    return (fahrenheit - 32) * 5/9


def celsius_to_kelvin(celsius: float) -> float:
    """
    Convert Celsius to Kelvin.

    Args:
        celsius: Temperature in Celsius.

    Returns:
        Temperature in Kelvin.
    """
    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """
    Convert Kelvin to Celsius.

    Args:
        kelvin: Temperature in Kelvin.

    Returns:
        Temperature in Celsius.
    """
    return kelvin - 273.15


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: The temperature value to convert.
        from_unit: Source unit ("C", "F", or "K").
        to_unit: Target unit ("C", "F", or "K").

    Returns:
        Converted temperature value.

    Raises:
        ValueError: If invalid unit is provided.

    Examples:
        >>> convert_temperature(100, "C", "F")
        212.0
        >>> convert_temperature(32, "F", "C")
        0.0
    """
    valid_units = {"C", "F", "K"}
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit not in valid_units:
        raise ValueError(f"Invalid from_unit: {from_unit}. Must be C, F, or K.")
    if to_unit not in valid_units:
        raise ValueError(f"Invalid to_unit: {to_unit}. Must be C, F, or K.")

    if from_unit == to_unit:
        return value

    # Convert to Celsius first (as intermediate)
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = fahrenheit_to_celsius(value)
    else:  # K
        celsius = kelvin_to_celsius(value)

    # Convert from Celsius to target
    if to_unit == "C":
        return celsius
    elif to_unit == "F":
        return celsius_to_fahrenheit(celsius)
    else:  # K
        return celsius_to_kelvin(celsius)


# Tests
print(convert_temperature(100, "C", "F"))   # 212.0
print(convert_temperature(32, "F", "C"))    # 0.0
print(convert_temperature(0, "C", "K"))     # 273.15
print(convert_temperature(373.15, "K", "C"))  # 100.0
print(convert_temperature(212, "F", "K"))   # 373.15

# Error handling
try:
    convert_temperature(100, "X", "C")
except ValueError as e:
    print(f"Error: {e}")  # Error: Invalid from_unit: X. Must be C, F, or K.
```

---

## Alternative Approaches

### Using a dictionary for dispatch

```python
def convert_temperature_v2(value: float, from_unit: str, to_unit: str) -> float:
    """Alternative using a conversion table."""

    # Conversion functions to Celsius
    to_celsius = {
        "C": lambda x: x,
        "F": lambda x: (x - 32) * 5/9,
        "K": lambda x: x - 273.15,
    }

    # Conversion functions from Celsius
    from_celsius = {
        "C": lambda x: x,
        "F": lambda x: x * 9/5 + 32,
        "K": lambda x: x + 273.15,
    }

    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit not in to_celsius:
        raise ValueError(f"Invalid from_unit: {from_unit}")
    if to_unit not in from_celsius:
        raise ValueError(f"Invalid to_unit: {to_unit}")

    celsius = to_celsius[from_unit](value)
    return from_celsius[to_unit](celsius)
```

### Mutable default argument pitfall

```python
# BAD - Mutable default argument
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))  # ['a']
print(add_item("b"))  # ['a', 'b'] - Unexpected!

# GOOD - Use None and create inside function
def add_item_fixed(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item_fixed("a"))  # ['a']
print(add_item_fixed("b"))  # ['b'] - Correct!
```

---

[← Back to Exercises](../exercises/ex_04_functions.md) | [← Back to Chapter](../04_functions.md) | [← Back to Module 1](../README.md)
