# Exercises — 18: Performance and Optimization

## Learning Objectives

After completing these exercises, you will be able to:
- Profile Python code to find bottlenecks
- Analyze algorithmic complexity (Big-O)
- Choose appropriate data structures for performance
- Apply code-level optimizations
- Use caching effectively
- Avoid common performance anti-patterns

---

## Exercise 1: Profiling Basics (Warm-up)

**Bloom Level**: Apply

Profile this code to find the bottleneck:

```python
import cProfile
import pstats
from io import StringIO

def process_data(data):
    result = []
    for item in data:
        transformed = transform(item)
        validated = validate(transformed)
        if validated:
            result.append(validated)
    return result

def transform(item):
    import time
    time.sleep(0.001)  # Simulated work
    return item * 2

def validate(item):
    return item if item > 0 else None

# Profile this
data = list(range(100))

# Your code: Use cProfile to find which function takes the most time
```

**Questions**:
1. Which function is the bottleneck?
2. What percentage of time is spent in that function?
3. How would you optimize this code?

---

## Exercise 2: Big-O Analysis (Analyze)

**Bloom Level**: Analyze

Determine the time complexity of each function:

```python
# Function A
def function_a(items):
    return items[0] if items else None

# Function B
def function_b(items, target):
    for item in items:
        if item == target:
            return True
    return False

# Function C
def function_c(items):
    for i in items:
        for j in items:
            print(i, j)

# Function D
def function_d(items):
    sorted_items = sorted(items)
    return sorted_items[len(sorted_items) // 2]

# Function E
def function_e(n):
    if n <= 1:
        return n
    return function_e(n-1) + function_e(n-2)

# Function F
def function_f(items, target):
    left, right = 0, len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

Fill in the table:

| Function | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| A | ? | ? |
| B | ? | ? |
| C | ? | ? |
| D | ? | ? |
| E | ? | ? |
| F | ? | ? |

---

## Exercise 3: Data Structure Selection (Practice)

**Bloom Level**: Apply

Choose the optimal data structure for each scenario and explain why:

```python
# Scenario 1: Frequently check if a user ID exists
user_ids = ???  # list, set, or dict?

def user_exists(user_id):
    return user_id in user_ids

# Scenario 2: FIFO queue for task processing
from collections import deque

task_queue = ???  # list or deque?

def add_task(task):
    task_queue.???(task)

def get_next_task():
    return task_queue.???()

# Scenario 3: Count word frequencies
word_counts = ???  # dict, defaultdict, or Counter?

def count_words(text):
    for word in text.split():
        ???

# Scenario 4: Maintain sorted data with frequent insertions
import bisect

sorted_data = ???

def insert_sorted(value):
    ???
```

---

## Exercise 4: String Performance (Practice)

**Bloom Level**: Apply

Fix the performance issues in this code:

```python
# Problem 1: Slow string concatenation
def build_report_slow(items):
    result = ""
    for item in items:
        result += f"Item: {item}\n"
    return result

def build_report_fast(items):
    """Rewrite to be efficient."""
    pass

# Problem 2: Inefficient string searching
def find_all_positions_slow(text, pattern):
    positions = []
    for i in range(len(text)):
        if text[i:i+len(pattern)] == pattern:
            positions.append(i)
    return positions

def find_all_positions_fast(text, pattern):
    """Rewrite using built-in methods."""
    pass

# Benchmark
import timeit

items = [f"data_{i}" for i in range(10000)]
text = "the quick brown fox jumps over the lazy dog " * 1000
pattern = "fox"

print("String concatenation:")
print(f"  Slow: {timeit.timeit(lambda: build_report_slow(items), number=10):.4f}s")
print(f"  Fast: {timeit.timeit(lambda: build_report_fast(items), number=10):.4f}s")

print("\nString searching:")
print(f"  Slow: {timeit.timeit(lambda: find_all_positions_slow(text, pattern), number=100):.4f}s")
print(f"  Fast: {timeit.timeit(lambda: find_all_positions_fast(text, pattern), number=100):.4f}s")
```

---

## Exercise 5: Caching (Practice)

**Bloom Level**: Apply

Add caching to improve performance:

```python
from functools import lru_cache
import time

# Problem 1: Expensive computation
def expensive_calculation(n):
    """Simulate expensive work."""
    time.sleep(0.1)
    return n * n

def process_with_cache(numbers):
    """
    Process numbers, but use caching for repeated values.
    """
    pass

# Problem 2: API-like function with varied arguments
def fetch_user_data(user_id, include_details=False, format="json"):
    """
    Simulate API call. Add caching.
    Note: Only hashable arguments can be cached!
    """
    time.sleep(0.1)
    return {"user_id": user_id, "details": include_details, "format": format}

# Test
numbers = [1, 2, 3, 1, 2, 3, 4, 5, 1, 2]  # Has duplicates
start = time.time()
results = process_with_cache(numbers)
print(f"Processed {len(numbers)} numbers in {time.time() - start:.2f}s")
# Without cache: ~1s, With cache: ~0.5s (only 5 unique)
```

---

## Exercise 6: Generator vs List (Practice)

**Bloom Level**: Apply

Convert list-based code to generators for memory efficiency:

```python
import sys

# Problem 1: Reading large file
def read_lines_list(filename):
    """Returns all lines as a list."""
    with open(filename) as f:
        return f.readlines()

def read_lines_generator(filename):
    """Yields lines one at a time."""
    pass

# Problem 2: Processing pipeline
def process_pipeline_list(data):
    """Processes data creating multiple intermediate lists."""
    step1 = [x * 2 for x in data]
    step2 = [x for x in step1 if x > 10]
    step3 = [str(x) for x in step2]
    return step3

def process_pipeline_generator(data):
    """Same processing but memory efficient."""
    pass

# Compare memory usage
data = range(1000000)

# List approach
list_result = process_pipeline_list(list(data))
print(f"List result type: {type(list_result)}")

# Generator approach
gen_result = process_pipeline_generator(data)
print(f"Generator result type: {type(gen_result)}")

# What's the memory difference?
```

---

## Exercise 7: Micro-Benchmarking (Analyze)

**Bloom Level**: Analyze

Use `timeit` to compare approaches and explain the results:

```python
import timeit

# Comparison 1: List vs generator for sum
list_sum = "sum([x*x for x in range(1000)])"
gen_sum = "sum(x*x for x in range(1000))"

# Comparison 2: Dict lookup vs list search
setup = """
data_list = list(range(10000))
data_set = set(range(10000))
target = 9999
"""
list_search = "target in data_list"
set_search = "target in data_set"

# Comparison 3: String formatting
setup2 = "name = 'Alice'; age = 30"
format_percent = "'Name: %s, Age: %d' % (name, age)"
format_format = "'Name: {}, Age: {}'.format(name, age)"
format_fstring = "f'Name: {name}, Age: {age}'"

# Run benchmarks
print("Sum comparison:")
print(f"  List comp: {timeit.timeit(list_sum, number=10000):.4f}s")
print(f"  Generator: {timeit.timeit(gen_sum, number=10000):.4f}s")

print("\nLookup comparison:")
print(f"  List: {timeit.timeit(list_search, setup, number=10000):.4f}s")
print(f"  Set:  {timeit.timeit(set_search, setup, number=10000):.4f}s")

print("\nString formatting:")
print(f"  %:      {timeit.timeit(format_percent, setup2, number=100000):.4f}s")
print(f"  format: {timeit.timeit(format_format, setup2, number=100000):.4f}s")
print(f"  f-str:  {timeit.timeit(format_fstring, setup2, number=100000):.4f}s")
```

**Questions**:
1. Which is faster for sum: list comprehension or generator? Why?
2. How much faster is set lookup vs list search?
3. Which string formatting method is fastest?

---

## Exercise 8: Optimization Workflow (Challenge)

**Bloom Level**: Create

You have slow code. Follow the proper optimization workflow:

```python
import cProfile
import pstats
from io import StringIO

def slow_function(n):
    """This function is too slow. Optimize it."""
    result = []

    # Step 1: Generate numbers
    numbers = []
    for i in range(n):
        numbers.append(i * i)

    # Step 2: Filter
    filtered = []
    for num in numbers:
        if num % 2 == 0:
            filtered.append(num)

    # Step 3: Check for primes (very slow!)
    for num in filtered:
        if num > 1:
            is_prime = True
            for i in range(2, num):  # Very inefficient!
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                result.append(num)

    return result

# Step 1: Profile to find bottleneck
# Step 2: Identify the slow part
# Step 3: Optimize only the bottleneck
# Step 4: Verify improvement

def optimized_function(n):
    """Your optimized version."""
    pass

# Test correctness
assert slow_function(100) == optimized_function(100)

# Compare performance
import time
start = time.time()
slow_function(1000)
slow_time = time.time() - start

start = time.time()
optimized_function(1000)
fast_time = time.time() - start

print(f"Slow: {slow_time:.4f}s")
print(f"Fast: {fast_time:.4f}s")
print(f"Speedup: {slow_time/fast_time:.1f}x")
```

---

## Deliverables

Submit your code for all exercises. Include your Big-O analysis table and benchmark explanations.

---

[← Back to Chapter](../18_performance.md) | [View Solutions](../solutions/sol_18_performance.md) | [← Back to Module 3](../README.md)
