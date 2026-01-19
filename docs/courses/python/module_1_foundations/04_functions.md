# Functions

Functions are reusable blocks of code that perform a specific task. They're fundamental to organizing code and avoiding repetition.

## Defining Functions

### Basic Syntax

```python
def greet(name):
    """Say hello to someone."""  # Docstring explains what it does
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # "Hello, Alice!"
```

### Return Values

Functions can return values using `return`:

```python
def add(a, b):
    return a + b

result = add(3, 5)  # result = 8

# Functions without return statement return None
def print_message(msg):
    print(msg)

x = print_message("Hello")  # Prints "Hello"
print(x)  # None
```

### Multiple Return Values

Python can return multiple values as a tuple:

```python
def divide_with_remainder(a, b):
    quotient = a // b
    remainder = a % b
    return quotient, remainder

q, r = divide_with_remainder(17, 5)  # q=3, r=2

# Or capture as tuple
result = divide_with_remainder(17, 5)  # (3, 2)
print(result[0])  # 3
```

## Parameters and Arguments

### Positional Arguments

Order matters:

```python
def describe_pet(animal_type, pet_name):
    print(f"I have a {animal_type} named {pet_name}")

describe_pet("dog", "Buddy")   # Correct order
describe_pet("Buddy", "dog")   # Wrong! "I have a Buddy named dog"
```

### Keyword Arguments

Explicitly name the parameter:

```python
# Order doesn't matter when using keywords
describe_pet(pet_name="Buddy", animal_type="dog")

# Can mix positional and keyword (positional first!)
describe_pet("dog", pet_name="Buddy")  # OK
# describe_pet(animal_type="dog", "Buddy")  # Error!
```

### Default Parameters

Provide default values for optional parameters:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))              # "Hello, Alice!"
print(greet("Bob", "Hi"))          # "Hi, Bob!"
print(greet("Charlie", greeting="Hey"))  # "Hey, Charlie!"
```

**Important**: Default parameters must come after required parameters:

```python
def func(a, b=10):    # OK
    pass

# def func(a=10, b):  # Error! Non-default after default
```

**Warning**: Avoid mutable default arguments!

```python
# BAD - The list is shared across all calls!
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))  # ['a']
print(add_item("b"))  # ['a', 'b'] - Unexpected!

# GOOD - Use None and create inside function
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item("a"))  # ['a']
print(add_item("b"))  # ['b'] - Correct!
```

## Variable Arguments

### `*args` - Variable Positional Arguments

Collect extra positional arguments as a tuple:

```python
def sum_all(*numbers):
    """Sum any number of arguments."""
    return sum(numbers)

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15
print(sum_all())               # 0

# numbers is a tuple inside the function
def show_args(*args):
    print(f"Type: {type(args)}")
    print(f"Value: {args}")

show_args(1, "hello", True)
# Type: <class 'tuple'>
# Value: (1, 'hello', True)
```

### `**kwargs` - Variable Keyword Arguments

Collect extra keyword arguments as a dictionary:

```python
def print_info(**kwargs):
    """Print any keyword arguments."""
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="Seattle")
# name: Alice
# age: 30
# city: Seattle

# kwargs is a dict inside the function
def show_kwargs(**kwargs):
    print(f"Type: {type(kwargs)}")
    print(f"Value: {kwargs}")

show_kwargs(a=1, b=2)
# Type: <class 'dict'>
# Value: {'a': 1, 'b': 2}
```

### Combining Parameters

The order must be: positional, `*args`, keyword-only, `**kwargs`:

```python
def func(a, b, *args, option=False, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"option={option}")
    print(f"kwargs={kwargs}")

func(1, 2, 3, 4, option=True, extra="value")
# a=1, b=2
# args=(3, 4)
# option=True
# kwargs={'extra': 'value'}
```

### Unpacking Arguments

Use `*` and `**` to unpack sequences and dicts as arguments:

```python
def greet(first, last):
    return f"Hello, {first} {last}!"

# Unpack list/tuple into positional arguments
names = ["Alice", "Smith"]
print(greet(*names))  # "Hello, Alice Smith!"

# Unpack dict into keyword arguments
info = {"first": "Bob", "last": "Jones"}
print(greet(**info))  # "Hello, Bob Jones!"
```

## Keyword-Only Arguments

Arguments after `*` must be provided as keywords:

```python
def safe_divide(a, b, *, raise_on_zero=False):
    """
    The * means raise_on_zero MUST be passed as a keyword.
    This prevents accidental positional usage.
    """
    if b == 0:
        if raise_on_zero:
            raise ValueError("Division by zero!")
        return None
    return a / b

safe_divide(10, 2, raise_on_zero=True)  # OK
# safe_divide(10, 2, True)  # Error! Keyword-only
```

## Positional-Only Arguments (Python 3.8+)

Arguments before `/` must be provided positionally:

```python
def power(base, exp, /):
    """
    The / means base and exp MUST be passed positionally.
    This allows the parameter names to change without breaking code.
    """
    return base ** exp

power(2, 3)      # OK: 8
# power(base=2, exp=3)  # Error! Positional-only
```

### Full Parameter Syntax

```python
def func(pos_only, /, pos_or_kw, *, kw_only):
    """
    - pos_only: Must be positional
    - pos_or_kw: Can be either
    - kw_only: Must be keyword
    """
    pass

func(1, 2, kw_only=3)       # OK
func(1, pos_or_kw=2, kw_only=3)  # OK
# func(pos_only=1, ...)     # Error!
# func(1, 2, 3)             # Error!
```

## Variable Scope

### LEGB Rule

Python searches for names in this order:
1. **L**ocal: Inside the current function
2. **E**nclosing: In enclosing functions (closures)
3. **G**lobal: Module-level
4. **B**uilt-in: Python's built-in names

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)  # "local"

    inner()
    print(x)  # "enclosing"

outer()
print(x)  # "global"
```

### `global` and `nonlocal`

```python
counter = 0

def increment():
    global counter  # Access global variable
    counter += 1

increment()
print(counter)  # 1

def outer():
    count = 0

    def inner():
        nonlocal count  # Access enclosing variable
        count += 1

    inner()
    print(count)  # 1

outer()
```

**Best practice**: Avoid `global`—use return values or classes instead.

## First-Class Functions

Functions are objects and can be:

### Assigned to Variables

```python
def greet(name):
    return f"Hello, {name}!"

say_hello = greet  # Assign function to variable
print(say_hello("Alice"))  # "Hello, Alice!"
```

### Passed as Arguments

```python
def apply_twice(func, value):
    return func(func(value))

def double(x):
    return x * 2

print(apply_twice(double, 5))  # 20 (5 * 2 * 2)
```

### Returned from Functions

```python
def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

### Stored in Data Structures

```python
operations = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "div": lambda a, b: a / b if b != 0 else None,
}

print(operations["add"](10, 5))  # 15
print(operations["mul"](10, 5))  # 50
```

## Lambda Functions

Anonymous, single-expression functions:

```python
# Regular function
def add(a, b):
    return a + b

# Lambda equivalent
add = lambda a, b: a + b

# Common use: sorting
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
students.sort(key=lambda s: s[1])  # Sort by score
# [('Charlie', 78), ('Alice', 85), ('Bob', 92)]

# Common use: filtering
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6]
```

**Best practice**: Use lambda for simple, one-off functions. For complex logic, use named functions.

## Recursion

A function that calls itself:

```python
def factorial(n):
    """Calculate n! recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120 (5 * 4 * 3 * 2 * 1)

# Trace:
# factorial(5) = 5 * factorial(4)
#              = 5 * 4 * factorial(3)
#              = 5 * 4 * 3 * factorial(2)
#              = 5 * 4 * 3 * 2 * factorial(1)
#              = 5 * 4 * 3 * 2 * 1
#              = 120
```

### Recursion with Accumulator

More efficient (tail recursion):

```python
def factorial_tail(n, accumulator=1):
    if n <= 1:
        return accumulator
    return factorial_tail(n - 1, n * accumulator)

print(factorial_tail(5))  # 120
```

### Recursion Limit

Python has a default recursion limit (~1000):

```python
import sys
print(sys.getrecursionlimit())  # 1000

# Can increase (but be careful!)
sys.setrecursionlimit(5000)

# For deep recursion, prefer iteration
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

## Docstrings

Document your functions:

```python
def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index (BMI).

    Args:
        weight: Weight in kilograms.
        height: Height in meters.

    Returns:
        The BMI value.

    Raises:
        ValueError: If weight or height is not positive.

    Examples:
        >>> calculate_bmi(70, 1.75)
        22.86
        >>> calculate_bmi(90, 1.80)
        27.78
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive")
    return round(weight / (height ** 2), 2)

# Access docstring
print(calculate_bmi.__doc__)
help(calculate_bmi)
```

## Example from Our Code

From `connection.py`:

```python
def __init__(
    self,
    account: str,                    # Required parameter
    user: Optional[str] = None,      # Optional (has default)
    warehouse: Optional[str] = None, # Optional
    role: Optional[str] = None,      # Optional
    database: Optional[str] = None   # Optional
):
    """
    Initialize connection with required and optional parameters.

    Args:
        account: Snowflake account identifier (required).
        user: Username for authentication. If not provided,
              uses SNOWFLAKE_USER environment variable.
        warehouse: Default warehouse. If not provided,
                   uses SNOWFLAKE_WAREHOUSE environment variable.
        role: Role to use. If not provided,
              uses SNOWFLAKE_ROLE environment variable.
        database: Default database. If not provided,
                  uses SNOWFLAKE_DATABASE environment variable.
    """
    self.account = account
    self.user = user or os.getenv("SNOWFLAKE_USER")
    self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
    self.role = role or os.getenv("SNOWFLAKE_ROLE")
    self.database = database or os.getenv("SNOWFLAKE_DATABASE")
```

**Why this design?**

- `account` is required—you must provide it
- Other parameters are optional—use defaults or environment variables
- Flexible: minimal required parameters, but can customize everything
- Documented: each parameter is explained in the docstring

## Best Practices Summary

1. **Use descriptive names**: `calculate_total` not `calc` or `f`
2. **Keep functions small**: Do one thing well
3. **Document with docstrings**: Explain purpose, parameters, return value
4. **Use type hints**: Make signatures clear
5. **Avoid mutable defaults**: Use `None` instead of `[]` or `{}`
6. **Return early**: Use guard clauses instead of deep nesting
7. **Prefer pure functions**: Same input → same output, no side effects
8. **Limit parameters**: More than 3-4 parameters suggests refactoring needed

---

[← Back to Module 1](./README.md) | [Next: Data Structures →](./05_data_structures.md) | [Exercises →](./exercises/ex_04_functions.md)
