# Solutions — 15: Iterators and Generators

## Key Concepts Demonstrated

- Iterator protocol (`__iter__`, `__next__`)
- Generator functions with `yield`
- Generator expressions for memory efficiency
- `yield from` for delegation
- Coroutine-style generators with `send()`
- Data processing pipelines

## Common Mistakes to Avoid

- Forgetting to handle `StopIteration` in custom iterators
- Trying to iterate over a generator twice (they're exhausted after one pass)
- Using list comprehensions when generators would be more memory efficient
- Not priming coroutine-style generators with `next()` before `send()`

---

## Exercise 1 Solution

```python
numbers = [10, 20, 30]
it = iter(numbers)

print(next(it))  # 10
print(next(it))  # 20

for num in it:
    print(num)   # 30 (only remaining item)

for num in it:
    print("Second loop:", num)  # Nothing prints
```

**Answers**:
1. First `next()` returns 10, second returns 20
2. The `for` loop only prints 30 because 10 and 20 were already consumed by `next()` calls
3. The second loop is empty because iterators are exhausted after one complete pass

---

## Exercise 2 Solution

```python
class Countdown:
    """Iterator that counts down from n to 1."""

    def __init__(self, start: int):
        self.start = start

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

# Test
for num in Countdown(5):
    print(num)  # 5, 4, 3, 2, 1

print(list(Countdown(3)))  # [3, 2, 1]
```

---

## Exercise 3 Solution

```python
def countdown(n: int):
    """Generator that yields numbers from n down to 1."""
    while n > 0:
        yield n
        n -= 1

def fibonacci(limit: int):
    """Yield Fibonacci numbers up to limit."""
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b

def cycle(items, times: int):
    """Yield each item in items, repeating 'times' times."""
    for _ in range(times):
        for item in items:
            yield item
    # Or using yield from:
    # for _ in range(times):
    #     yield from items

# Test
for num in countdown(5):
    print(num)  # 5, 4, 3, 2, 1

print(list(fibonacci(100)))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
print(list(cycle(['A', 'B', 'C'], 2)))  # ['A', 'B', 'C', 'A', 'B', 'C']
```

---

## Exercise 4 Solution

```python
import sys

# 1. Squares of numbers
squares_list = [x ** 2 for x in range(1000000)]
squares_gen = (x ** 2 for x in range(1000000))

print(f"List size: {sys.getsizeof(squares_list):,} bytes")  # ~8,000,000 bytes
print(f"Generator size: {sys.getsizeof(squares_gen):,} bytes")  # ~200 bytes

# 2. Process the first 5 squares without creating full list
first_5 = [next(squares_gen) for _ in range(5)]
print(first_5)  # [0, 1, 4, 9, 16]

# 3. Sum all squares (fresh generator)
total = sum(x ** 2 for x in range(1000000))
print(total)

# 4. Find first square > 1000000
first_large = next(x ** 2 for x in range(1000000) if x ** 2 > 1000000)
print(first_large)  # 1002001 (1001 ** 2)
```

---

## Exercise 5 Solution

```python
from itertools import islice

def natural_numbers():
    """Yield 1, 2, 3, ... forever."""
    n = 1
    while True:
        yield n
        n += 1

def powers_of_two():
    """Yield 1, 2, 4, 8, 16, ... forever."""
    power = 1
    while True:
        yield power
        power *= 2

def alternating():
    """Yield 1, -1, 1, -1, ... forever."""
    sign = 1
    while True:
        yield sign
        sign *= -1

# Test with islice
print(list(islice(natural_numbers(), 10)))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(list(islice(powers_of_two(), 10)))    # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
print(list(islice(alternating(), 6)))       # [1, -1, 1, -1, 1, -1]
```

---

## Exercise 6 Solution

```python
from collections import defaultdict
from typing import Iterator, Tuple, Dict

def read_lines(filename: str) -> Iterator[str]:
    """Yield lines from a file."""
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()

def filter_errors(lines: Iterator[str]) -> Iterator[str]:
    """Yield only lines containing 'ERROR'."""
    for line in lines:
        if 'ERROR' in line:
            yield line

def extract_timestamp(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    """Yield (timestamp, message) tuples from log lines."""
    for line in lines:
        parts = line.split(' ', 3)
        if len(parts) >= 4:
            timestamp = f"{parts[0]} {parts[1]}"
            message = parts[3] if len(parts) > 3 else ""
            yield (timestamp, message)

def count_by_hour(records: Iterator[Tuple[str, str]]) -> Dict[str, int]:
    """Count errors by hour."""
    counts = defaultdict(int)
    for timestamp, message in records:
        hour = timestamp.split(':')[0]  # "2024-01-15 10"
        counts[hour] += 1
    return dict(counts)

# Demo without actual file
def demo():
    # Simulate log lines
    log_lines = [
        "2024-01-15 10:30:45 ERROR: Connection failed",
        "2024-01-15 10:31:00 INFO: Retrying",
        "2024-01-15 10:31:05 ERROR: Connection failed",
        "2024-01-15 11:00:00 ERROR: Timeout",
        "2024-01-15 11:15:30 INFO: Success",
    ]

    # Create the pipeline (using list instead of file)
    lines = iter(log_lines)
    errors = filter_errors(lines)
    records = extract_timestamp(errors)
    hourly_counts = count_by_hour(records)

    print(hourly_counts)
    # {'2024-01-15 10': 2, '2024-01-15 11': 1}

demo()
```

**Why is this memory-efficient?**

Each generator processes one item at a time. At any moment, only one log line is held in memory regardless of file size. A 10GB log file uses the same memory as a 10KB file.

With lists, you would need to store:
1. All lines in memory
2. All error lines in memory
3. All timestamp records in memory

With generators:
1. Only current line in memory
2. Processed immediately, discarded
3. Results accumulated only in final `count_by_hour` dictionary

---

## Exercise 7 Solution

```python
from typing import Iterator, Any

def flatten(nested):
    """Flatten a nested list structure using yield from."""
    for item in nested:
        yield from item

def deep_flatten(nested) -> Iterator[Any]:
    """Recursively flatten arbitrarily nested lists."""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from deep_flatten(item)
        else:
            yield item

def chain(*iterables):
    """Re-implement itertools.chain using yield from."""
    for iterable in iterables:
        yield from iterable

# Test
print(list(flatten([[1, 2], [3, 4, 5], [6]])))       # [1, 2, 3, 4, 5, 6]
print(list(deep_flatten([1, [2, [3, [4, 5]]]])))     # [1, 2, 3, 4, 5]
print(list(chain([1, 2], [3, 4], [5, 6])))           # [1, 2, 3, 4, 5, 6]

# Additional: flatten with arbitrary depth limit
def flatten_to_depth(nested, max_depth: int) -> Iterator[Any]:
    """Flatten up to a specific depth."""
    for item in nested:
        if isinstance(item, (list, tuple)) and max_depth > 0:
            yield from flatten_to_depth(item, max_depth - 1)
        else:
            yield item

print(list(flatten_to_depth([1, [2, [3, [4]]]], 2)))  # [1, 2, 3, [4]]
```

---

## Exercise 8 Solution

```python
def running_stats():
    """
    Generator that calculates running statistics.
    """
    count = 0
    total = 0.0
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

            if value is not None:
                count += 1
                total += value
                min_val = min(min_val, value)
                max_val = max(max_val, value)

        except GeneratorExit:
            return
        except Exception:
            # Reset on any exception
            count = 0
            total = 0.0
            min_val = float('inf')
            max_val = float('-inf')

# Test
stats = running_stats()
next(stats)  # Prime the generator

print(stats.send(10))
# {'count': 1, 'sum': 10.0, 'mean': 10.0, 'min': 10, 'max': 10}

print(stats.send(20))
# {'count': 2, 'sum': 30.0, 'mean': 15.0, 'min': 10, 'max': 20}

print(stats.send(30))
# {'count': 3, 'sum': 60.0, 'mean': 20.0, 'min': 10, 'max': 30}

stats.throw(ValueError)  # Reset

print(stats.send(5))
# {'count': 1, 'sum': 5.0, 'mean': 5.0, 'min': 5, 'max': 5}
```

---

## Exercise 9 Solution

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
    """
    offset = 0
    items_yielded = 0

    while True:
        # Fetch a page
        items = fetch_func(offset, page_size)

        # If no items returned, we've reached the end
        if not items:
            break

        for item in items:
            yield item
            items_yielded += 1

            # Check max_items limit
            if max_items is not None and items_yielded >= max_items:
                return

        # Move to next page
        offset += page_size

        # If we got fewer items than requested, we've reached the end
        if len(items) < page_size:
            break

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
users = list(paginate(fake_api_fetch, page_size=100, max_items=250))
print(f"Total users fetched: {len(users)}")  # 250
print(f"First user: {users[0]}")             # {'id': 0, 'name': 'User 0'}
print(f"Last user: {users[-1]}")             # {'id': 249, 'name': 'User 249'}

# Test without limit
all_users = list(paginate(fake_api_fetch, page_size=100))
print(f"All users: {len(all_users)}")  # 350
```

---

## Generator Pattern Summary

| Pattern | Use Case |
|---------|----------|
| Generator function | Custom iteration logic |
| Generator expression | Memory-efficient comprehension |
| `yield from` | Delegate to sub-iterator |
| Coroutine with `send()` | Two-way communication |
| Pipeline | Chain transformations |
| Pagination | Handle large/infinite data |

---

[← Back to Exercises](../exercises/ex_15_iterators_generators.md) | [← Back to Chapter](../15_iterators_generators.md) | [← Back to Module 3](../README.md)
