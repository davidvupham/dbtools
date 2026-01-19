# Solutions — 10: Functional Programming Basics

## Key Concepts Demonstrated

- `map()`, `filter()`, `reduce()` usage
- Lambda functions for short operations
- `functools.partial` for function specialization
- `functools.lru_cache` for memoization
- `itertools` for efficient iteration
- Function composition patterns
- Data pipelines

## Common Mistakes to Avoid

- Using complex lambdas (use named functions instead)
- Forgetting `reduce()` requires import from `functools`
- Not converting `map()` and `filter()` results to list
- Overusing functional style when loops are clearer

---

## Exercise 1 Solution

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# 1. Square all numbers
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# 2. Filter even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# 3. Sum all numbers
total = reduce(lambda a, b: a + b, numbers)
print(total)  # 15

# 4. Find maximum
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5

# 5. Sum of squares of even numbers
result = reduce(
    lambda a, b: a + b,
    map(
        lambda x: x ** 2,
        filter(lambda x: x % 2 == 0, numbers)
    )
)
print(result)  # 20
```

---

## Exercise 2 Solution

```python
# 1. Sort list of tuples by second element
pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
sorted_pairs = sorted(pairs, key=lambda x: x[1])
print(sorted_pairs)  # [(2, 'a'), (1, 'b'), (3, 'c')]

# 2. Sort strings by length, then alphabetically
words = ["cat", "elephant", "dog", "ant", "bear"]
sorted_words = sorted(words, key=lambda x: (len(x), x))
print(sorted_words)  # ['ant', 'cat', 'dog', 'bear', 'elephant']

# 3. Filter strings that start with vowel
words = ["apple", "banana", "orange", "cherry", "avocado"]
vowel_words = list(filter(lambda w: w[0].lower() in 'aeiou', words))
print(vowel_words)  # ['apple', 'orange', 'avocado']

# 4. Convert list of dicts to list of values
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
names = list(map(lambda u: u["name"], users))
print(names)  # ['Alice', 'Bob']

# 5. Create a function that checks if number is in range
in_range = lambda x, lo, hi: lo <= x <= hi
print(in_range(5, 1, 10))   # True
print(in_range(15, 1, 10))  # False
```

---

## Exercise 3 Solution

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

def log_message(level, message, timestamp=None):
    ts = timestamp or "NOW"
    return f"[{ts}] {level}: {message}"

def format_number(number, decimal_places=2, prefix="", suffix=""):
    return f"{prefix}{number:.{decimal_places}f}{suffix}"

# 1. Create square and cube functions
square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5))  # 25
print(cube(3))    # 27

# 2. Create specialized loggers
debug = partial(log_message, "DEBUG")
error = partial(log_message, "ERROR")
print(debug("Starting process"))  # [NOW] DEBUG: Starting process
print(error("Connection failed")) # [NOW] ERROR: Connection failed

# 3. Create currency formatters
format_usd = partial(format_number, prefix="$")
format_percent = partial(format_number, decimal_places=2, suffix="%", number=lambda x: x * 100)

# Actually, for percent we need a different approach:
def format_percent(value):
    return format_number(value * 100, decimal_places=2, suffix="%")

print(format_usd(1234.5))    # $1234.50
print(format_percent(0.156)) # 15.60%
```

---

## Exercise 4 Solution

```python
from functools import lru_cache
import time

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

# Test performance
start = time.time()
result = fib(35)
print(f"fib(35) = {result}, time = {time.time() - start:.4f}s")
# fib(35) = 9227465, time = 0.0001s (much faster with cache!)

@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(10))  # 3628800

@lru_cache(maxsize=32)
def expensive_query(query: str) -> str:
    """Simulate expensive database query."""
    time.sleep(0.1)
    return f"Result for: {query}"

# First call is slow
start = time.time()
print(expensive_query("SELECT * FROM users"))
print(f"First call: {time.time() - start:.3f}s")

# Second call is cached
start = time.time()
print(expensive_query("SELECT * FROM users"))
print(f"Cached call: {time.time() - start:.3f}s")

print(expensive_query.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=32, currsize=1)
```

---

## Exercise 5 Solution

```python
from itertools import (
    count, cycle, repeat,
    chain, islice,
    takewhile, dropwhile,
    groupby, accumulate,
    product, permutations, combinations
)

# 1. Generate odd numbers
odd_numbers = list(islice(count(1, 2), 10))
print(odd_numbers)  # [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

# 2. Chain multiple iterables
list1 = [1, 2, 3]
list2 = [4, 5, 6]
list3 = [7, 8, 9]
combined = list(chain(list1, list2, list3))
print(combined)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 3. Take while condition is true
numbers = [2, 4, 6, 8, 1, 3, 5, 7]
even_prefix = list(takewhile(lambda x: x % 2 == 0, numbers))
print(even_prefix)  # [2, 4, 6, 8]

# 4. Running total
values = [1, 2, 3, 4, 5]
running_sum = list(accumulate(values))
print(running_sum)  # [1, 3, 6, 10, 15]

# Running product
from operator import mul
running_product = list(accumulate(values, mul))
print(running_product)  # [1, 2, 6, 24, 120]

# 5. Group by key
data = [
    ("A", 1), ("A", 2), ("B", 3),
    ("B", 4), ("A", 5), ("C", 6)
]
sorted_data = sorted(data, key=lambda x: x[0])
for key, group in groupby(sorted_data, key=lambda x: x[0]):
    print(f"{key}: {list(group)}")
# A: [('A', 1), ('A', 2), ('A', 5)]
# B: [('B', 3), ('B', 4)]
# C: [('C', 6)]

# 6. Generate all pairs
colors = ["red", "blue"]
sizes = ["S", "M", "L"]
variants = list(product(colors, sizes))
print(variants)
# [('red', 'S'), ('red', 'M'), ('red', 'L'), ('blue', 'S'), ('blue', 'M'), ('blue', 'L')]
```

---

## Exercise 6 Solution

```python
from functools import reduce
from typing import Callable

def compose(*functions: Callable) -> Callable:
    """Compose functions right-to-left."""
    def composed(x):
        return reduce(lambda acc, f: f(acc), reversed(functions), x)
    return composed

def pipe(*functions: Callable) -> Callable:
    """Pipe functions left-to-right."""
    def piped(x):
        return reduce(lambda acc, f: f(acc), functions, x)
    return piped

# Test functions
def add_one(x): return x + 1
def double(x): return x * 2
def square(x): return x ** 2

# compose: right to left
composed = compose(add_one, double, square)
print(composed(3))  # 19 (square(3)=9, double(9)=18, add_one(18)=19)

# pipe: left to right
piped = pipe(square, double, add_one)
print(piped(3))  # 19 (same result, different order)
```

---

## Exercise 7 Solution

```python
from typing import Callable, Iterable, TypeVar
from functools import reduce

T = TypeVar('T')
U = TypeVar('U')

class Pipeline:
    """A composable data processing pipeline."""

    def __init__(self, data: Iterable[T]):
        self.data = list(data)

    def map(self, func: Callable[[T], U]) -> "Pipeline":
        return Pipeline(map(func, self.data))

    def filter(self, predicate: Callable[[T], bool]) -> "Pipeline":
        return Pipeline(filter(predicate, self.data))

    def reduce(self, func: Callable[[T, T], T], initial: T = None):
        if initial is not None:
            return reduce(func, self.data, initial)
        return reduce(func, self.data)

    def take(self, n: int) -> "Pipeline":
        return Pipeline(self.data[:n])

    def skip(self, n: int) -> "Pipeline":
        return Pipeline(self.data[n:])

    def sort(self, key: Callable[[T], any] = None, reverse: bool = False) -> "Pipeline":
        return Pipeline(sorted(self.data, key=key, reverse=reverse))

    def unique(self) -> "Pipeline":
        seen = set()
        result = []
        for item in self.data:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return Pipeline(result)

    def collect(self) -> list[T]:
        return self.data

# Test
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

result = (
    Pipeline(numbers)
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x ** 2)
    .take(3)
    .reduce(lambda a, b: a + b)
)
print(result)  # 56

words = ["hello", "world", "hello", "python", "world", "code"]
result = (
    Pipeline(words)
    .unique()
    .map(str.upper)
    .filter(lambda w: len(w) > 4)
    .sort(key=len)
    .collect()
)
print(result)  # ['HELLO', 'WORLD', 'PYTHON']
```

---

## Exercise 8 Solution

```python
from itertools import groupby
from functools import reduce

data = [
    {"name": "Alice", "age": 30, "department": "Engineering"},
    {"name": "Bob", "age": 25, "department": "Marketing"},
    {"name": "Charlie", "age": 35, "department": "Engineering"},
    {"name": "Diana", "age": 28, "department": "Marketing"},
    {"name": "Eve", "age": 32, "department": "Engineering"},
]

# Task 1: Names of engineers over 30
result_functional = list(map(
    lambda p: p["name"],
    filter(
        lambda p: p["department"] == "Engineering" and p["age"] > 30,
        data
    )
))
print(result_functional)  # ['Charlie', 'Eve']

# Evaluation: Both are equally readable for simple cases.
# The functional version chains well but can get hard to read.
# Prefer: List comprehension is clearest:
# [p["name"] for p in data if p["department"] == "Engineering" and p["age"] > 30]

# Task 2: Average age per department
sorted_data = sorted(data, key=lambda p: p["department"])
avg_functional = {
    dept: sum(p["age"] for p in people) / len(list(people))
    for dept, people in groupby(sorted_data, key=lambda p: p["department"])
}
# Note: This has a bug! groupby returns iterator that gets exhausted.

# Better functional approach:
from collections import defaultdict
def avg_by_dept(data):
    groups = defaultdict(list)
    for p in data:
        groups[p["department"]].append(p["age"])
    return {dept: sum(ages) / len(ages) for dept, ages in groups.items()}

avg_functional = avg_by_dept(data)
print(avg_functional)  # {'Engineering': 32.33..., 'Marketing': 26.5}

# Evaluation: Imperative is clearer here. The groupby approach is tricky.

# Task 3: Find oldest person
oldest_functional = reduce(
    lambda a, b: a if a["age"] > b["age"] else b,
    data
)
print(oldest_functional)  # {'name': 'Charlie', 'age': 35, ...}

# Alternative using max
oldest_functional = max(data, key=lambda p: p["age"])
print(oldest_functional)

# Evaluation: max() with key is the clearest and most Pythonic.
```

### Summary: When to Use Functional Style

| Task | Best Approach |
|------|---------------|
| Simple transforms | `map()` or list comprehension |
| Simple filtering | `filter()` or list comprehension |
| Aggregation to single value | `reduce()` or built-ins (`sum`, `max`) |
| Complex multi-step | List comprehension or explicit loops |
| Performance-critical iteration | `itertools` |

---

[← Back to Exercises](../exercises/ex_10_functional_basics.md) | [← Back to Chapter](../10_functional_basics.md) | [← Back to Module 2](../README.md)
