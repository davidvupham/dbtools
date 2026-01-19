# Exercises — 15: Iterators and Generators

## Learning Objectives

After completing these exercises, you will be able to:
- Implement custom iterator classes with `__iter__` and `__next__`
- Create generator functions using `yield`
- Use generator expressions for memory efficiency
- Build data processing pipelines with generators
- Apply `itertools` for complex iteration patterns

---

## Exercise 1: Understanding Iterators (Warm-up)

**Bloom Level**: Remember

Predict the output of this code, then run it to verify:

```python
numbers = [10, 20, 30]
it = iter(numbers)

print(next(it))
print(next(it))

for num in it:
    print(num)

# What happens if you try to iterate again?
for num in it:
    print("Second loop:", num)
```

**Questions**:
1. What does each `next()` call return?
2. Why does the `for` loop only print one number?
3. Why is the second `for` loop empty?

---

## Exercise 2: Custom Iterator Class (Practice)

**Bloom Level**: Apply

Create a `Countdown` iterator that counts down from a number to 1:

```python
class Countdown:
    """Iterator that counts down from n to 1."""

    def __init__(self, start: int):
        pass

    def __iter__(self):
        pass

    def __next__(self):
        pass

# Test
for num in Countdown(5):
    print(num)
# Output: 5, 4, 3, 2, 1

# Should work multiple times
print(list(Countdown(3)))  # [3, 2, 1]
```

---

## Exercise 3: Generator Functions (Practice)

**Bloom Level**: Apply

Rewrite the `Countdown` class as a generator function:

```python
def countdown(n: int):
    """Generator that yields numbers from n down to 1."""
    pass

# Test
for num in countdown(5):
    print(num)

# Also create these generators:

def fibonacci(limit: int):
    """Yield Fibonacci numbers up to limit."""
    pass

def cycle(items, times: int):
    """Yield each item in items, repeating 'times' times."""
    pass

# Test fibonacci
print(list(fibonacci(100)))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# Test cycle
print(list(cycle(['A', 'B', 'C'], 2)))  # ['A', 'B', 'C', 'A', 'B', 'C']
```

---

## Exercise 4: Generator Expressions (Practice)

**Bloom Level**: Apply

Convert these list comprehensions to generator expressions and compare memory usage:

```python
import sys

# 1. Squares of numbers
squares_list = [x ** 2 for x in range(1000000)]
squares_gen = ???

print(f"List size: {sys.getsizeof(squares_list):,} bytes")
print(f"Generator size: {sys.getsizeof(squares_gen):,} bytes")

# 2. Process the first 5 squares without creating full list
first_5 = ???

# 3. Sum all squares (using generator expression directly in sum())
total = ???

# 4. Find first square > 1000000
first_large = ???
```

---

## Exercise 5: Infinite Generators (Practice)

**Bloom Level**: Apply

Create generators for infinite sequences (must use with `itertools.islice` or break):

```python
from itertools import islice

def natural_numbers():
    """Yield 1, 2, 3, ... forever."""
    pass

def powers_of_two():
    """Yield 1, 2, 4, 8, 16, ... forever."""
    pass

def alternating():
    """Yield 1, -1, 1, -1, ... forever."""
    pass

# Test with islice
print(list(islice(natural_numbers(), 10)))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(list(islice(powers_of_two(), 10)))    # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
print(list(islice(alternating(), 6)))       # [1, -1, 1, -1, 1, -1]
```

---

## Exercise 6: Generator Pipeline (Analyze)

**Bloom Level**: Analyze

Create a data processing pipeline using generators. Process a log file without loading it all into memory:

```python
def read_lines(filename):
    """Yield lines from a file."""
    pass

def filter_errors(lines):
    """Yield only lines containing 'ERROR'."""
    pass

def extract_timestamp(lines):
    """Yield (timestamp, message) tuples from log lines."""
    # Log format: "2024-01-15 10:30:45 ERROR: Something went wrong"
    pass

def count_by_hour(records):
    """Count errors by hour."""
    pass

# Create the pipeline
lines = read_lines("server.log")
errors = filter_errors(lines)
records = extract_timestamp(errors)
hourly_counts = count_by_hour(records)

print(hourly_counts)
```

**Question**: Why is this more memory-efficient than loading the entire file?

---

## Exercise 7: `yield from` (Practice)

**Bloom Level**: Apply

Use `yield from` to simplify nested iteration:

```python
def flatten(nested):
    """Flatten a nested list structure using yield from."""
    # Input: [[1, 2], [3, 4, 5], [6]]
    # Output: 1, 2, 3, 4, 5, 6
    pass

def deep_flatten(nested):
    """Recursively flatten arbitrarily nested lists."""
    # Input: [1, [2, [3, [4, 5]]]]
    # Output: 1, 2, 3, 4, 5
    pass

def chain(*iterables):
    """Re-implement itertools.chain using yield from."""
    pass

# Test
print(list(flatten([[1, 2], [3, 4, 5], [6]])))
print(list(deep_flatten([1, [2, [3, [4, 5]]]])))
print(list(chain([1, 2], [3, 4], [5, 6])))
```

---

## Exercise 8: Generator with State (Challenge)

**Bloom Level**: Create

Create a `RunningStats` generator that maintains running statistics as values are sent to it:

```python
def running_stats():
    """
    Generator that calculates running statistics.

    Send values using .send() and get stats back.
    Use .throw() to reset statistics.
    """
    count = 0
    total = 0
    min_val = float('inf')
    max_val = float('-inf')

    while True:
        try:
            value = yield {
                'count': count,
                'sum': total,
                'mean': total / count if count > 0 else 0,
                'min': min_val if count > 0 else None,
                'max': max_val if count > 0 else None,
            }
            # Update statistics with received value
            pass

        except GeneratorExit:
            return
        except Exception:
            # Reset on any exception
            count = 0
            total = 0
            min_val = float('inf')
            max_val = float('-inf')

# Test
stats = running_stats()
next(stats)  # Prime the generator

print(stats.send(10))  # {'count': 1, 'sum': 10, 'mean': 10, ...}
print(stats.send(20))  # {'count': 2, 'sum': 30, 'mean': 15, ...}
print(stats.send(30))  # {'count': 3, 'sum': 60, 'mean': 20, ...}

stats.throw(ValueError)  # Reset
print(stats.send(5))   # {'count': 1, 'sum': 5, 'mean': 5, ...}
```

---

## Exercise 9: Practical Application (Challenge)

**Bloom Level**: Create

Create a pagination generator that fetches data from an API in batches:

```python
from typing import Iterator, TypeVar, Callable, List

T = TypeVar('T')

def paginate(
    fetch_func: Callable[[int, int], List[T]],
    page_size: int = 100,
    max_items: int = None
) -> Iterator[T]:
    """
    Generator that handles pagination automatically.

    Args:
        fetch_func: Function that takes (offset, limit) and returns items
        page_size: Number of items per page
        max_items: Maximum total items to yield (None = unlimited)

    Yields:
        Individual items from paginated results
    """
    pass

# Simulated API
def fake_api_fetch(offset: int, limit: int) -> List[dict]:
    """Simulate fetching users from an API."""
    total_users = 350
    users = [
        {"id": i, "name": f"User {i}"}
        for i in range(offset, min(offset + limit, total_users))
    ]
    return users

# Test
for user in paginate(fake_api_fetch, page_size=100, max_items=250):
    print(user)
# Should yield 250 users, fetching 100 at a time
```

---

## Deliverables

Submit your code for all exercises. Include your analysis for Exercise 6.

---

[← Back to Chapter](../15_iterators_generators.md) | [View Solutions](../solutions/sol_15_iterators_generators.md) | [← Back to Module 3](../README.md)
