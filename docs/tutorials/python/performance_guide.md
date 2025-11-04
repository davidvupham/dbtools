# Python Performance Optimization Guide

Welcome to the comprehensive guide to performance optimization in Python. This document covers strategies, tools, and best practices for making your Python code faster and more memory-efficient.

---

## Table of Contents

1.  [The Philosophy of Optimization](#the-philosophy-of-optimization)
2.  [Profiling: Finding Your Bottlenecks](#profiling-finding-your-bottlenecks)
    *   [CPU Profiling with `cProfile`](#cpu-profiling-with-cprofile)
    *   [Memory Profiling with `tracemalloc`](#memory-profiling-with-tracemalloc)
    *   [Micro-benchmarking with `timeit`](#micro-benchmarking-with-timeit)
3.  [Algorithmic and Data Structure Optimization](#algorithmic-and-data-structure-optimization)
4.  [Memory Optimization Techniques](#memory-optimization-techniques)
    *   [Reducing Memory with `__slots__`](#reducing-memory-with-__slots__)
    *   [Using Generators for Streaming](#using-generators-for-streaming)
5.  [Caching Strategies](#caching-strategies)
    *   [Memoization with `@lru_cache`](#memoization-with-lru_cache)
    *   [Caching Properties with `@cached_property`](#caching-properties-with-cached_property)
6.  [Lazy Loading Patterns](#lazy-loading-patterns)
    *   [Lazy Initialization with the Proxy Pattern](#lazy-initialization-with-the-proxy-pattern)
7.  [Performance Checklist](#performance-checklist)

---

## The Philosophy of Optimization

> "Premature optimization is the root of all evil." - Donald Knuth

Before you start optimizing, remember these key principles:
1.  **Don't optimize without measuring.** Your intuition about what is slow is often wrong.
2.  **Write clear, correct code first.** Unreadable code is hard to maintain and often hides bugs.
3.  **Focus on high-impact areas.** A 50% improvement on code that runs 1% of the time is negligible. A 10% improvement on code that runs 80% of the time is a huge win.

---

## Profiling: Finding Your Bottlenecks

Never optimize without measuring. Python's built-in tools are your first stop.

### CPU Profiling with `cProfile`

`cProfile` tells you how much time is spent in each function, helping you identify CPU-bound bottlenecks.

```python
import cProfile, pstats, io
from pstats import SortKey

def slow_function():
    total = 0
    for i in range(10000):
        total += i
    return total

def fast_function():
    return sum(range(10000))

def main_workload():
    for _ in range(100):
        slow_function()
        fast_function()

# --- Running the profiler ---
pr = cProfile.Profile()
pr.enable()
main_workload()
pr.disable()

s = io.StringIO()
# Sort by cumulative time spent in the function
ps = pstats.Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
ps.print_stats(10) # Print the top 10 offenders

print(s.getvalue())
```
**How to read the output:**
- `ncalls`: Number of times the function was called.
- `tottime`: Total time spent in the function itself (excluding sub-calls).
- `cumtime`: Cumulative time spent in this function and all sub-functions. This is the most useful metric for finding bottlenecks.

### Memory Profiling with `tracemalloc`

`tracemalloc` helps you find the exact lines of code that are allocating the most memory, which is invaluable for hunting down memory leaks.

```python
import tracemalloc

def create_leaky_objects():
    leaky_list = []
    for i in range(10000):
        leaky_list.append(f"An object that takes up some memory {i}")
    return leaky_list

tracemalloc.start()

# --- Run workload ---
leaks = create_leaky_objects()
print("Objects created.")

# --- Take a snapshot and analyze ---
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("\n[ Top 10 memory-allocating lines ]")
for stat in top_stats[:10]:
    print(stat)
```
This output points you directly to the source of memory pressure.

### Micro-benchmarking with `timeit`
For comparing small snippets of code, `timeit` provides accurate measurements.

```python
import timeit

setup_code = "from __main__ import slow_function, fast_function"
print("Timing slow_function:", timeit.timeit("slow_function()", setup=setup_code, number=1000))
print("Timing fast_function:", timeit.timeit("fast_function()", setup=setup_code, number=1000))
```

---

## Algorithmic and Data Structure Optimization

This is often the source of the biggest performance gains. Before tuning class-level details, ensure you are using the right algorithms and data structures.

- **Use `set` for uniqueness and fast lookups:** Checking for an item's existence in a `list` is O(n), but in a `set` it is O(1) on average.
- **Use `dict` (hash maps) for key-value lookups:** This is also O(1) on average.
- **Understand Big-O Notation:** Choose algorithms that scale efficiently with your data.

---

## Memory Optimization Techniques

### Reducing Memory with `__slots__`

By default, Python objects store attributes in a dynamic dictionary (`__dict__`), which is flexible but memory-intensive. `__slots__` tells Python to use a more compact, fixed-size array instead.

This is covered in detail in the **[OOP Guide](oop_guide.md#reducing-memory-with-__slots__)**, but the key takeaway is to use it when creating a very large number of small objects.

```python
class SlottedPoint:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y
```
**Trade-offs:**
- **Pro:** Significant memory savings (up to 40-50%) and slightly faster attribute access.
- **Con:** You cannot add new attributes to an instance that are not listed in `__slots__`.

### Using Generators for Streaming
Generators allow you to process large datasets one item at a time without loading the entire dataset into memory.

```python
def read_large_file(file_path):
    """A generator function to read a large file line by line."""
    with open(file_path, 'r') as f:
        for line in f:
            yield line

# This processes the file without consuming large amounts of memory.
for line in read_large_file('very_large_log.txt'):
    if 'ERROR' in line:
        print(line)
```

---

## Caching Strategies

If a function or property performs an expensive computation, cache the result so it's only computed once.

### Memoization with `@lru_cache`
The `@lru_cache` (Least Recently Used) decorator from `functools` is perfect for memoizing methods that take arguments.

```python
from functools import lru_cache
import time

class ApiClient:
    @lru_cache(maxsize=128)
    def get_data(self, endpoint: str):
        """Fetches data from an API endpoint, caching the result."""
        print(f"Fetching data from {endpoint}...")
        time.sleep(1) # Simulate network latency
        return {"data": f"content from {endpoint}"}

client = ApiClient()
print(client.get_data("/users/1")) # Fetches, then prints result
print(client.get_data("/users/1")) # Immediately prints result from cache
```

### Caching Properties with `@cached_property`
For properties that are expensive to compute, `@cached_property` (Python 3.8+) computes the result once and then stores it as an instance attribute.

```python
from functools import cached_property
import time

class DataReport:
    def __init__(self, raw_data):
        self._raw_data = raw_data

    @cached_property
    def processed_data(self):
        """This is an expensive operation that should only run once."""
        print("Performing expensive data processing...")
        time.sleep(2) # Simulate heavy work
        return sum(self._raw_data)

report = DataReport([1, 2, 3, 4, 5])
print(report.processed_data) # Runs processing, then prints 15
print(report.processed_data) # Immediately prints 15 (result was cached)
```

---

## Lazy Loading Patterns

Don't initialize expensive resources until they are actually needed. This is useful for database connections, large files, or complex objects that aren't always used.

### Lazy Initialization with the Proxy Pattern
The **Proxy Pattern** provides a placeholder object that has the same interface as the real object but only creates the real object on first use.

```python
class DatabaseConnection:
    """The real, expensive object."""
    def __init__(self):
        print("Establishing expensive database connection...")
        time.sleep(2)
        self.connected = True

    def execute(self, query):
        return f"Executing '{query}'"

class LazyConnectionProxy:
    """The proxy that stands in for the real connection."""
    def __init__(self):
        self._real_connection = None

    def _get_connection(self):
        """Factory for the real object, called only when needed."""
        if self._real_connection is None:
            self._real_connection = DatabaseConnection()
        return self._real_connection

    def __getattr__(self, name):
        """Delegate all attribute access to the real object."""
        return getattr(self._get_connection(), name)

# --- Usage ---
proxy = LazyConnectionProxy()
print("Proxy created. No connection yet.")

# The first time we call a method, the real connection is established.
print(proxy.execute("SELECT * FROM users"))

# Subsequent calls are fast.
print(proxy.execute("SELECT * FROM products"))
```

---

## Performance Checklist

When you encounter a performance issue, follow this checklist:
1.  **Define a Metric:** What are you trying to improve? Latency, throughput, or memory usage?
2.  **Profile First:** Use `cProfile` for CPU issues and `tracemalloc` for memory issues. Don't guess.
3.  **Look for Algorithmic Wins:** Is there a better data structure or algorithm? This is usually the source of the biggest gains.
4.  **Apply Caching:** If you are re-computing the same expensive result, use `@lru_cache` or `@cached_property`.
5.  **Reduce I/O:** Are you making too many database calls or network requests in a loop? Batch them.
6.  **Consider Concurrency:** For I/O-bound tasks, use `asyncio` to perform work concurrently. See the **[Advanced OOP Guide](advanced_oop_concepts.md)** for examples.
7.  **Optimize Memory:** If memory is the issue, use `__slots__` or generators. For memory leaks, use `weakref`.
8.  **Re-measure:** After each change, re-run your profiler to confirm it had the desired effect.
9.  **Add Regression Tests:** For critical performance areas, add a micro-benchmark with `timeit` to prevent future regressions.
