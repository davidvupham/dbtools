# Control Flow

Control flow determines the order in which code executes. Python provides conditionals for decision-making and loops for repetition.

## Conditional Statements

### Basic `if` Statement

```python
x = 10
if x > 0:
    print("Positive")
elif x < 0:
    print("Negative")
else:
    print("Zero")
```

### Comparison Operators

| Operator | Description |
|----------|-------------|
| `==` | Equal to |
| `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `is` | Identity (same object) |
| `in` | Membership |

```python
# Chained comparisons
x = 5
if 0 < x < 10:
    print("x is between 0 and 10")

# Multiple conditions
if x > 0 and x < 10:
    print("Same result")

# Membership testing
if x in [1, 3, 5, 7, 9]:
    print("x is odd and less than 10")
```

### Boolean Operators

| Operator | Description |
|----------|-------------|
| `and` | True if both are true |
| `or` | True if at least one is true |
| `not` | Inverts boolean value |

```python
age = 25
has_license = True

# and: both must be true
if age >= 18 and has_license:
    print("Can drive")

# or: at least one must be true
if age < 18 or not has_license:
    print("Cannot drive")

# Short-circuit evaluation
def check():
    print("check called")
    return True

# check() is never called because first condition is False
if False and check():
    pass

# check() is never called because first condition is True
if True or check():
    pass
```

### Conditional Expressions (Ternary)

```python
age = 20
status = "adult" if age >= 18 else "minor"
print(status)  # "adult"

# Can be nested (but don't overdo it)
score = 85
grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"
```

### The Walrus Operator (Python 3.8+)

The `:=` operator assigns and returns a value in one expression:

```python
# Without walrus operator
data = input("Enter data: ")
if len(data) > 10:
    print(f"Data too long: {len(data)} characters")

# With walrus operator
if (n := len(data := input("Enter data: "))) > 10:
    print(f"Data too long: {n} characters")

# Useful in while loops
while (line := input("Enter line (empty to quit): ")):
    print(f"You entered: {line}")

# Useful in list comprehensions
numbers = [1, 2, 3, 4, 5]
results = [y for x in numbers if (y := x * 2) > 4]
print(results)  # [6, 8, 10]
```

## Pattern Matching (Python 3.10+)

The `match` statement provides structural pattern matching:

### Basic Pattern Matching

```python
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Internal Server Error"
        case _:
            return "Unknown"

print(http_status(200))  # "OK"
print(http_status(999))  # "Unknown"
```

### Pattern Matching with OR

```python
def classify_response(status):
    match status:
        case 200 | 201 | 204:
            return "Success"
        case 400 | 401 | 403 | 404:
            return "Client Error"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return "Unknown"
```

### Pattern Matching with Guards

```python
def describe_point(point):
    match point:
        case (0, 0):
            return "Origin"
        case (x, 0):
            return f"On x-axis at {x}"
        case (0, y):
            return f"On y-axis at {y}"
        case (x, y) if x == y:
            return f"On diagonal at ({x}, {y})"
        case (x, y):
            return f"Point at ({x}, {y})"

print(describe_point((0, 0)))   # "Origin"
print(describe_point((5, 0)))   # "On x-axis at 5"
print(describe_point((3, 3)))   # "On diagonal at (3, 3)"
```

### Pattern Matching with Classes

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Circle:
    center: Point
    radius: int

def describe_shape(shape):
    match shape:
        case Point(x=0, y=0):
            return "Origin point"
        case Point(x, y):
            return f"Point at ({x}, {y})"
        case Circle(center=Point(0, 0), radius=r):
            return f"Circle at origin with radius {r}"
        case Circle(center, radius):
            return f"Circle at {center} with radius {radius}"

print(describe_shape(Point(0, 0)))              # "Origin point"
print(describe_shape(Circle(Point(0, 0), 5)))   # "Circle at origin with radius 5"
```

## Loops

### `for` Loop

Iterate over any sequence (list, string, range, etc.):

```python
# Iterate over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}")

# Iterate over a string
for char in "Hello":
    print(char)

# Iterate over a range
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# range with start, stop, step
for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
    print(i)

# Iterate over dictionary
person = {"name": "Alice", "age": 30}
for key in person:
    print(f"{key}: {person[key]}")

# Better: iterate over items
for key, value in person.items():
    print(f"{key}: {value}")
```

### `enumerate()` for Index and Value

```python
fruits = ["apple", "banana", "cherry"]

# Instead of this:
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Use enumerate:
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Start from a different index
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")  # 1: apple, 2: banana, 3: cherry
```

### `zip()` for Parallel Iteration

```python
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]

for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# zip stops at shortest sequence
short = [1, 2]
long = [1, 2, 3, 4]
for a, b in zip(short, long):
    print(a, b)  # Only prints 2 pairs

# Use zip_longest to include all
from itertools import zip_longest
for a, b in zip_longest(short, long, fillvalue=None):
    print(a, b)
```

### `while` Loop

Repeat while a condition is true:

```python
count = 5
while count > 0:
    print(count)
    count -= 1
print("Blastoff!")

# Common pattern: infinite loop with break
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == "quit":
        break
    print(f"You entered: {user_input}")
```

### Loop Control

#### `break`: Exit the loop immediately

```python
for i in range(10):
    if i == 5:
        break
    print(i)
# Output: 0, 1, 2, 3, 4
```

#### `continue`: Skip to next iteration

```python
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
# Output: 1, 3, 5, 7, 9 (odd numbers only)
```

#### `pass`: Do nothing (placeholder)

```python
for i in range(5):
    if i == 3:
        pass  # TODO: handle this case later
    else:
        print(i)
```

### The `else` Clause on Loops

The `else` block runs if the loop completes **without** hitting `break`:

```python
# Search example
def find_prime(numbers):
    for n in numbers:
        if is_prime(n):
            print(f"Found prime: {n}")
            break
    else:
        print("No primes found")

# Successful search (break is hit, else doesn't run)
find_prime([4, 6, 7, 8])  # "Found prime: 7"

# Failed search (loop completes, else runs)
find_prime([4, 6, 8, 10])  # "No primes found"
```

```python
# Authentication example
def authenticate(attempts_allowed=3):
    for attempt in range(attempts_allowed):
        password = input("Enter password: ")
        if password == "secret":
            print("Access granted")
            break
    else:
        print("Access denied: too many attempts")
```

## Comprehensions

Concise syntax for creating collections:

### List Comprehension

```python
# Basic
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
even_squares = [x**2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]

# Nested (flatten a matrix)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [num for row in matrix for num in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Dictionary Comprehension

```python
# Basic
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Swap keys and values
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}
```

### Set Comprehension

```python
# Get unique word lengths
words = ["hello", "world", "python", "code"]
lengths = {len(word) for word in words}
# {4, 5, 6}
```

### Generator Expression

Like a list comprehension but creates a generator (lazy evaluation):

```python
# Generator expression (uses parentheses)
gen = (x**2 for x in range(1000000))
# Memory efficient: computes values on demand

# Use in functions that accept iterables
total = sum(x**2 for x in range(100))

# Iterate over generator
for value in gen:
    if value > 100:
        break
    print(value)
```

## Example from Our Code

From `connection.py` - authentication flow:

```python
def connect(self, max_attempts: int = 3) -> bool:
    """
    Attempt to connect with retry logic.

    The for-else pattern is perfect here: if we successfully
    connect, we break out. If all attempts fail, the else
    block runs to handle the failure.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_attempts}")
            self._establish_connection()
            logger.info("Connection established")
            return True  # Success, exit the loop
        except ConnectionError as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                time.sleep(2 ** attempt)  # Exponential backoff
    else:
        logger.error("All connection attempts failed")
        return False
```

## Best Practices Summary

1. **Use `elif` for mutually exclusive conditions**: Clearer than nested `if`
2. **Prefer `for` over `while` when iterating**: Less error-prone
3. **Use `enumerate()` for index+value**: Don't use `range(len())`
4. **Use `zip()` for parallel iteration**: Clean and readable
5. **Use comprehensions for simple transformations**: More readable than loops
6. **Use `for-else` for search patterns**: Natural way to handle "not found"
7. **Use `match` for complex conditionals**: Clearer than long `if-elif` chains (3.10+)
8. **Avoid deep nesting**: Extract to functions or use early returns

---

[← Back to Module 1](./README.md) | [Next: Functions →](./04_functions.md) | [Exercises →](./exercises/ex_03_control_flow.md)
