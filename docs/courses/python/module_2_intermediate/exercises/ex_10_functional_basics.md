# Exercises — 10: Functional Programming Basics

## Learning Objectives

After completing these exercises, you will be able to:
- Use `map()`, `filter()`, and `reduce()` effectively
- Write and use lambda functions appropriately
- Apply `functools` utilities (partial, lru_cache, reduce)
- Use `itertools` for efficient iteration
- Compose functions and build pipelines
- Choose between functional and imperative approaches

---

## Exercise 1: Map, Filter, Reduce (Warm-up)

**Bloom Level**: Apply

Rewrite each loop using functional tools:

```python
from functools import reduce

# 1. Square all numbers
numbers = [1, 2, 3, 4, 5]
# Loop version:
# squared = []
# for n in numbers:
#     squared.append(n ** 2)
squared = # Use map()

# 2. Filter even numbers
# Loop version:
# evens = []
# for n in numbers:
#     if n % 2 == 0:
#         evens.append(n)
evens = # Use filter()

# 3. Sum all numbers
# Loop version:
# total = 0
# for n in numbers:
#     total += n
total = # Use reduce()

# 4. Find maximum
maximum = # Use reduce()

# 5. Combine: sum of squares of even numbers
result = # Chain map, filter, reduce

print(squared)   # [1, 4, 9, 16, 25]
print(evens)     # [2, 4]
print(total)     # 15
print(maximum)   # 5
print(result)    # 20 (4 + 16)
```

---

## Exercise 2: Lambda Functions (Practice)

**Bloom Level**: Apply

Write lambda functions for each task:

```python
# 1. Sort list of tuples by second element
pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
sorted_pairs = sorted(pairs, key=...)  # [(2, 'a'), (1, 'b'), (3, 'c')]

# 2. Sort strings by length, then alphabetically
words = ["cat", "elephant", "dog", "ant", "bear"]
sorted_words = sorted(words, key=...)  # ['ant', 'cat', 'dog', 'bear', 'elephant']

# 3. Filter strings that start with vowel
words = ["apple", "banana", "orange", "cherry", "avocado"]
vowel_words = list(filter(..., words))  # ['apple', 'orange', 'avocado']

# 4. Convert list of dicts to list of values
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
names = list(map(..., users))  # ['Alice', 'Bob']

# 5. Create a function that checks if number is in range
in_range = lambda x, lo, hi: ...
print(in_range(5, 1, 10))   # True
print(in_range(15, 1, 10))  # False
```

---

## Exercise 3: functools.partial (Practice)

**Bloom Level**: Apply

Use `functools.partial` to create specialized functions:

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

def log_message(level, message, timestamp=None):
    ts = timestamp or "NOW"
    return f"[{ts}] {level}: {message}"

def format_number(number, decimal_places=2, prefix="", suffix=""):
    return f"{prefix}{number:.{decimal_places}f}{suffix}"

# 1. Create square and cube functions using partial
square = partial(...)
cube = partial(...)
print(square(5))  # 25
print(cube(3))    # 27

# 2. Create specialized loggers
debug = partial(...)
error = partial(...)
print(debug("Starting process"))  # [NOW] DEBUG: Starting process
print(error("Connection failed")) # [NOW] ERROR: Connection failed

# 3. Create currency formatters
format_usd = partial(...)
format_percent = partial(...)
print(format_usd(1234.5))    # $1234.50
print(format_percent(0.156)) # 15.60%
```

---

## Exercise 4: functools.lru_cache (Practice)

**Bloom Level**: Apply

Use memoization to optimize recursive functions:

```python
from functools import lru_cache
import time

# 1. Fibonacci with memoization
@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Calculate nth Fibonacci number."""
    pass

# Test performance
start = time.time()
result = fib(35)
print(f"fib(35) = {result}, time = {time.time() - start:.4f}s")

# 2. Memoized factorial
@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    pass

# 3. Expensive computation simulation
@lru_cache(maxsize=32)
def expensive_query(query: str) -> str:
    """Simulate expensive database query."""
    time.sleep(0.1)  # Simulate delay
    return f"Result for: {query}"

# First call is slow
print(expensive_query("SELECT * FROM users"))
# Second call is cached (fast)
print(expensive_query("SELECT * FROM users"))

# Check cache stats
print(expensive_query.cache_info())
```

---

## Exercise 5: itertools Basics (Practice)

**Bloom Level**: Apply

Use `itertools` functions:

```python
from itertools import (
    count, cycle, repeat,
    chain, islice,
    takewhile, dropwhile,
    groupby, accumulate,
    product, permutations, combinations
)

# 1. Generate infinite sequence and take first 10
# count(start, step) -> count(1, 2) gives 1, 3, 5, 7, ...
odd_numbers = list(islice(count(1, 2), 10))
print(odd_numbers)  # [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

# 2. Chain multiple iterables
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]
combined = list(chain(...))
print(combined)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 3. Take while condition is true
numbers = [2, 4, 6, 8, 1, 3, 5, 7]
even_prefix = list(takewhile(lambda x: x % 2 == 0, numbers))
print(even_prefix)  # [2, 4, 6, 8]

# 4. Running total (accumulate)
values = [1, 2, 3, 4, 5]
running_sum = list(accumulate(values))
print(running_sum)  # [1, 3, 6, 10, 15]

# 5. Group by key
data = [
    ("A", 1), ("A", 2), ("B", 3),
    ("B", 4), ("A", 5), ("C", 6)
]
# First sort by key, then group
sorted_data = sorted(data, key=lambda x: x[0])
for key, group in groupby(sorted_data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")

# 6. Generate all pairs (Cartesian product)
colors = ["red", "blue"]
sizes = ["S", "M", "L"]
variants = list(product(colors, sizes))
print(variants)  # [('red', 'S'), ('red', 'M'), ...]
```

---

## Exercise 6: Function Composition (Analyze)

**Bloom Level**: Analyze

Create a function composition utility:

```python
from functools import reduce
from typing import Callable, TypeVar

T = TypeVar('T')

def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions: compose(f, g, h)(x) = f(g(h(x)))
    Functions are applied right-to-left.
    """
    pass

def pipe(*functions: Callable) -> Callable:
    """
    Pipe multiple functions: pipe(f, g, h)(x) = h(g(f(x)))
    Functions are applied left-to-right.
    """
    pass

# Test functions
def add_one(x): return x + 1
def double(x): return x * 2
def square(x): return x ** 2

# compose: right to left
# compose(add_one, double, square)(3) = add_one(double(square(3)))
# = add_one(double(9)) = add_one(18) = 19
composed = compose(add_one, double, square)
print(composed(3))  # 19

# pipe: left to right
# pipe(square, double, add_one)(3) = add_one(double(square(3))) = 19
piped = pipe(square, double, add_one)
print(piped(3))  # 19
```

---

## Exercise 7: Data Pipeline (Challenge)

**Bloom Level**: Create

Build a data processing pipeline:

```python
from typing import Callable, Iterable, TypeVar
from functools import reduce
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Pipeline:
    """A composable data processing pipeline."""

    def __init__(self, data: Iterable[T]):
        self.data = list(data)

    def map(self, func: Callable[[T], U]) -> "Pipeline":
        """Apply function to each element."""
        return Pipeline(map(func, self.data))

    def filter(self, predicate: Callable[[T], bool]) -> "Pipeline":
        """Keep elements that satisfy predicate."""
        return Pipeline(filter(predicate, self.data))

    def reduce(self, func: Callable[[T, T], T], initial: T = None):
        """Reduce to single value."""
        if initial is not None:
            return reduce(func, self.data, initial)
        return reduce(func, self.data)

    def take(self, n: int) -> "Pipeline":
        """Take first n elements."""
        pass

    def skip(self, n: int) -> "Pipeline":
        """Skip first n elements."""
        pass

    def sort(self, key: Callable[[T], any] = None, reverse: bool = False) -> "Pipeline":
        """Sort elements."""
        pass

    def unique(self) -> "Pipeline":
        """Remove duplicates (preserving order)."""
        pass

    def collect(self) -> list[T]:
        """Return final list."""
        return self.data

# Test
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

result = (
    Pipeline(numbers)
    .filter(lambda x: x % 2 == 0)    # [2, 4, 6, 8, 10]
    .map(lambda x: x ** 2)           # [4, 16, 36, 64, 100]
    .take(3)                         # [4, 16, 36]
    .reduce(lambda a, b: a + b)      # 56
)
print(result)  # 56

# Another example
words = ["hello", "world", "hello", "python", "world", "code"]
result = (
    Pipeline(words)
    .unique()                        # ['hello', 'world', 'python', 'code']
    .map(str.upper)                  # ['HELLO', 'WORLD', 'PYTHON', 'CODE']
    .filter(lambda w: len(w) > 4)    # ['HELLO', 'WORLD', 'PYTHON']
    .sort(key=len)                   # ['HELLO', 'WORLD', 'PYTHON']
    .collect()
)
print(result)  # ['HELLO', 'WORLD', 'PYTHON']
```

---

## Exercise 8: Functional vs Imperative (Evaluate)

**Bloom Level**: Evaluate

For each task, write both functional and imperative versions. Then evaluate which is more readable and appropriate:

```python
data = [
    {"name": "Alice", "age": 30, "department": "Engineering"},
    {"name": "Bob", "age": 25, "department": "Marketing"},
    {"name": "Charlie", "age": 35, "department": "Engineering"},
    {"name": "Diana", "age": 28, "department": "Marketing"},
    {"name": "Eve", "age": 32, "department": "Engineering"},
]

# Task 1: Get names of engineers over 30
# Imperative version:
result_imperative = []
for person in data:
    if person["department"] == "Engineering" and person["age"] > 30:
        result_imperative.append(person["name"])

# Functional version:
result_functional = # Your implementation

# Task 2: Calculate average age per department
# Imperative version:
dept_totals = {}
dept_counts = {}
for person in data:
    dept = person["department"]
    if dept not in dept_totals:
        dept_totals[dept] = 0
        dept_counts[dept] = 0
    dept_totals[dept] += person["age"]
    dept_counts[dept] += 1
avg_imperative = {d: dept_totals[d] / dept_counts[d] for d in dept_totals}

# Functional version (hint: use itertools.groupby):
avg_functional = # Your implementation

# Task 3: Find the oldest person
# Imperative version:
oldest_imperative = None
for person in data:
    if oldest_imperative is None or person["age"] > oldest_imperative["age"]:
        oldest_imperative = person

# Functional version:
oldest_functional = # Your implementation

# Compare and explain which version is better for each task
```

---

## Deliverables

Submit your code for all exercises. Include evaluations for Exercise 8.

---

[← Back to Chapter](../10_functional_basics.md) | [View Solutions](../solutions/sol_10_functional_basics.md) | [← Back to Module 2](../README.md)
