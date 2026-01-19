# Solutions — 18: Performance and Optimization

## Key Concepts Demonstrated

- Profiling with cProfile
- Big-O complexity analysis
- Data structure selection
- String optimization
- Caching with lru_cache
- Generator-based memory optimization
- Micro-benchmarking with timeit

## Common Mistakes to Avoid

- Optimizing without profiling first
- Micro-optimizing cold paths
- Using lists for membership testing
- String concatenation in loops
- Creating unnecessary intermediate lists

---

## Exercise 1 Solution

```python
import cProfile
import pstats
from io import StringIO
import time

def process_data(data):
    result = []
    for item in data:
        transformed = transform(item)
        validated = validate(transformed)
        if validated:
            result.append(validated)
    return result

def transform(item):
    time.sleep(0.001)
    return item * 2

def validate(item):
    return item if item > 0 else None

data = list(range(100))

# Profile
profiler = cProfile.Profile()
profiler.enable()
process_data(data)
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

**Answers**:
1. **Bottleneck**: `transform()` function (due to `time.sleep`)
2. **Percentage**: ~99% of time in `transform`
3. **Optimization**: Remove/reduce the sleep, or batch the operations, or use async for I/O

---

## Exercise 2 Solution

| Function | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| A (index access) | O(1) | O(1) |
| B (linear search) | O(n) | O(1) |
| C (nested loops) | O(n²) | O(1) |
| D (sort + median) | O(n log n) | O(n) |
| E (naive fibonacci) | O(2ⁿ) | O(n) - call stack |
| F (binary search) | O(log n) | O(1) |

---

## Exercise 3 Solution

```python
from collections import deque, Counter
import bisect

# Scenario 1: User ID lookup - use SET for O(1) lookup
user_ids = set()  # Not list!

def user_exists(user_id):
    return user_id in user_ids  # O(1) vs O(n) for list

# Scenario 2: FIFO queue - use DEQUE for O(1) operations at both ends
task_queue = deque()

def add_task(task):
    task_queue.append(task)  # O(1)

def get_next_task():
    return task_queue.popleft()  # O(1) vs O(n) for list.pop(0)

# Scenario 3: Word counting - use COUNTER
word_counts = Counter()

def count_words(text):
    word_counts.update(text.split())
    # Or: word_counts = Counter(text.split())

# Scenario 4: Sorted insertions - use BISECT
sorted_data = []

def insert_sorted(value):
    bisect.insort(sorted_data, value)  # O(n) but maintains order
```

---

## Exercise 4 Solution

```python
import timeit

# Problem 1: String concatenation
def build_report_slow(items):
    result = ""
    for item in items:
        result += f"Item: {item}\n"  # O(n²) - creates new string each time
    return result

def build_report_fast(items):
    """Use join for O(n) performance."""
    lines = [f"Item: {item}" for item in items]
    return "\n".join(lines) + "\n"

# Problem 2: String searching
def find_all_positions_slow(text, pattern):
    positions = []
    for i in range(len(text)):
        if text[i:i+len(pattern)] == pattern:
            positions.append(i)
    return positions

def find_all_positions_fast(text, pattern):
    """Use str.find() which is C-optimized."""
    positions = []
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions

# Benchmark
items = [f"data_{i}" for i in range(10000)]
text = "the quick brown fox jumps over the lazy dog " * 1000
pattern = "fox"

print("String concatenation:")
print(f"  Slow: {timeit.timeit(lambda: build_report_slow(items), number=10):.4f}s")
print(f"  Fast: {timeit.timeit(lambda: build_report_fast(items), number=10):.4f}s")
# Fast is ~10-100x faster
```

---

## Exercise 5 Solution

```python
from functools import lru_cache
import time

# Problem 1: Use lru_cache
@lru_cache(maxsize=128)
def expensive_calculation_cached(n):
    time.sleep(0.1)
    return n * n

def process_with_cache(numbers):
    return [expensive_calculation_cached(n) for n in numbers]

# Problem 2: Cached API function
@lru_cache(maxsize=256)
def fetch_user_data(user_id, include_details=False, format="json"):
    time.sleep(0.1)
    return {"user_id": user_id, "details": include_details, "format": format}

# Test
numbers = [1, 2, 3, 1, 2, 3, 4, 5, 1, 2]
start = time.time()
results = process_with_cache(numbers)
print(f"Processed {len(numbers)} numbers in {time.time() - start:.2f}s")
# Only 5 unique values, so only 5 cache misses = 0.5s instead of 1.0s
```

---

## Exercise 6 Solution

```python
import sys

def read_lines_generator(filename):
    """Yields lines one at a time - O(1) memory."""
    with open(filename) as f:
        for line in f:
            yield line

def process_pipeline_generator(data):
    """Chain generators - no intermediate lists."""
    step1 = (x * 2 for x in data)
    step2 = (x for x in step1 if x > 10)
    step3 = (str(x) for x in step2)
    return step3  # Returns generator, not list

# Memory comparison
data = range(1000000)

# List approach creates 3 intermediate lists
# Memory: O(3n) = O(n)

# Generator approach creates no intermediate lists
# Memory: O(1) - only one item at a time
```

---

## Exercise 7 Solution

```python
import timeit

# Results:
print("Sum comparison:")
# List comp: ~0.85s
# Generator: ~0.90s (slightly slower - no memory benefit for sum)

print("\nLookup comparison:")
# List: ~2.5s (O(n) - must scan to end)
# Set:  ~0.001s (O(1) - hash lookup)
# Set is ~2500x faster!

print("\nString formatting:")
# %:      ~0.025s
# format: ~0.035s
# f-str:  ~0.020s (fastest)
```

**Answers**:

1. **List comp is slightly faster for sum** because `sum()` needs to iterate through all elements anyway. The generator has overhead from pausing/resuming. However, for memory-constrained scenarios, generator is better.

2. **Set lookup is ~2500x faster** because set uses hash table (O(1)) while list uses linear search (O(n)).

3. **F-strings are fastest** because they're optimized at compile time. The `%` format is second, and `.format()` is slowest due to method call overhead.

---

## Exercise 8 Solution

```python
import math
from functools import lru_cache

def optimized_function(n):
    """Optimized version with proper prime checking."""

    # Combine steps 1 & 2 with generator (no intermediate lists)
    even_squares = (i * i for i in range(n) if (i * i) % 2 == 0)

    # Efficient prime check
    def is_prime(num):
        if num < 2:
            return False
        if num == 2:
            return True
        if num % 2 == 0:
            return False
        # Only check odd numbers up to sqrt
        for i in range(3, int(math.sqrt(num)) + 1, 2):
            if num % i == 0:
                return False
        return True

    # Single pass through data
    return [num for num in even_squares if num > 1 and is_prime(num)]

# The key optimizations:
# 1. Combined generation and filtering (no intermediate lists)
# 2. Prime check only goes to sqrt(n), not n
# 3. Skip even numbers in prime check
# Speedup: ~100-1000x depending on n
```

---

## Performance Checklist

Before optimizing:
- [ ] Code is correct and tested
- [ ] Performance is actually a problem
- [ ] Profiled to find the real bottleneck

When optimizing:
- [ ] Focus on hot paths (frequently executed code)
- [ ] Consider algorithmic improvements first
- [ ] Choose appropriate data structures
- [ ] Measure before and after each change

Common quick wins:
- [ ] Use set for membership testing
- [ ] Use deque for queue operations
- [ ] Use join() for string building
- [ ] Use generators for large data
- [ ] Use lru_cache for repeated computations

---

[← Back to Exercises](../exercises/ex_18_performance.md) | [← Back to Chapter](../18_performance.md) | [← Back to Module 3](../README.md)
