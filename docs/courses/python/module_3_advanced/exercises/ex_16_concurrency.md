# Exercises — 16: Concurrency

## Learning Objectives

After completing these exercises, you will be able to:
- Choose between threading, multiprocessing, and asyncio
- Use `ThreadPoolExecutor` for I/O-bound tasks
- Use `ProcessPoolExecutor` for CPU-bound tasks
- Write async functions with `async`/`await`
- Handle concurrent task results and exceptions
- Apply timeouts and cancellation

---

## Exercise 1: I/O vs CPU Bound (Warm-up)

**Bloom Level**: Understand

Classify each task as I/O-bound or CPU-bound and choose the best concurrency approach:

| Task | I/O or CPU? | Best Tool |
|------|-------------|-----------|
| Download 100 images from URLs | ? | ? |
| Compress 100 large files | ? | ? |
| Query 50 different databases | ? | ? |
| Calculate prime numbers up to 10 million | ? | ? |
| Send 1000 HTTP requests to an API | ? | ? |
| Resize 500 images | ? | ? |
| Read data from 100 CSV files | ? | ? |
| Train a machine learning model | ? | ? |

---

## Exercise 2: ThreadPoolExecutor Basics (Practice)

**Bloom Level**: Apply

Use `ThreadPoolExecutor` to speed up downloading multiple URLs:

```python
import concurrent.futures
import time
from urllib.request import urlopen

def download_url(url: str) -> tuple[str, int]:
    """Download a URL and return (url, content_length)."""
    # Simulate network delay
    time.sleep(0.5)
    # In real code: response = urlopen(url)
    return (url, 1000)  # Simulated response size

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
    "https://example.com/page4",
    "https://example.com/page5",
]

# Sequential (slow)
def download_sequential(urls):
    pass

# Concurrent with ThreadPoolExecutor
def download_concurrent(urls, max_workers=5):
    pass

# Compare times
start = time.perf_counter()
results = download_sequential(urls)
print(f"Sequential: {time.perf_counter() - start:.2f}s")

start = time.perf_counter()
results = download_concurrent(urls)
print(f"Concurrent: {time.perf_counter() - start:.2f}s")
```

---

## Exercise 3: ProcessPoolExecutor for CPU Tasks (Practice)

**Bloom Level**: Apply

Use multiprocessing to speed up CPU-intensive calculations:

```python
import concurrent.futures
import time
import math

def is_prime(n: int) -> bool:
    """Check if n is prime (CPU intensive for large n)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def count_primes_in_range(start: int, end: int) -> int:
    """Count primes in range [start, end)."""
    return sum(1 for n in range(start, end) if is_prime(n))

# Split range into chunks and process in parallel
def count_primes_parallel(limit: int, num_workers: int = 4) -> int:
    """Count all primes up to limit using multiple processes."""
    pass

# Test
limit = 100000
start = time.perf_counter()
count = count_primes_parallel(limit)
elapsed = time.perf_counter() - start
print(f"Found {count} primes up to {limit} in {elapsed:.2f}s")
```

---

## Exercise 4: Handling Errors in Concurrent Code (Analyze)

**Bloom Level**: Analyze

Handle exceptions properly when using concurrent execution:

```python
import concurrent.futures
import random

def unreliable_task(task_id: int) -> str:
    """Simulates a task that sometimes fails."""
    if random.random() < 0.3:  # 30% failure rate
        raise ValueError(f"Task {task_id} failed!")
    return f"Task {task_id} completed"

def run_with_error_handling(task_ids: list[int]) -> dict:
    """
    Run tasks concurrently and handle errors gracefully.

    Returns:
        dict with keys:
        - 'successful': list of (task_id, result) tuples
        - 'failed': list of (task_id, exception) tuples
    """
    pass

# Test
results = run_with_error_handling(list(range(10)))
print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
for task_id, error in results['failed']:
    print(f"  Task {task_id}: {error}")
```

---

## Exercise 5: Basic Asyncio (Practice)

**Bloom Level**: Apply

Write async functions to fetch data concurrently:

```python
import asyncio
import time

async def fetch_data(name: str, delay: float) -> dict:
    """Simulate fetching data from an API."""
    print(f"Starting fetch for {name}")
    await asyncio.sleep(delay)  # Simulated network delay
    print(f"Completed fetch for {name}")
    return {"name": name, "data": f"Data for {name}"}

async def fetch_all():
    """Fetch data from multiple sources concurrently."""
    pass

# Run the async code
start = time.perf_counter()
results = asyncio.run(fetch_all())
elapsed = time.perf_counter() - start

print(f"\nCompleted in {elapsed:.2f}s")
print(f"Results: {results}")

# Expected: Should complete in ~1s (the longest delay), not 1+2+0.5+1.5=5s
```

---

## Exercise 6: Asyncio with Timeouts (Practice)

**Bloom Level**: Apply

Add timeout handling to async operations:

```python
import asyncio

async def slow_operation(name: str, duration: float) -> str:
    """Simulates a slow operation."""
    await asyncio.sleep(duration)
    return f"{name} completed"

async def fetch_with_timeout(name: str, duration: float, timeout: float) -> str:
    """
    Fetch with a timeout. Return error message if timeout exceeded.
    """
    pass

async def fetch_all_with_timeouts():
    """Fetch multiple items, some will timeout."""
    operations = [
        ("fast", 0.5),
        ("medium", 1.5),
        ("slow", 5.0),
        ("very_slow", 10.0),
    ]
    timeout = 2.0

    # Run all with timeout
    results = []
    for name, duration in operations:
        result = await fetch_with_timeout(name, duration, timeout)
        results.append(result)

    return results

# Test
results = asyncio.run(fetch_all_with_timeouts())
for r in results:
    print(r)
```

---

## Exercise 7: Task Groups with anyio (Practice)

**Bloom Level**: Apply

Use anyio for structured concurrency:

```python
import anyio

async def process_item(item: str) -> str:
    """Process a single item."""
    await anyio.sleep(0.5)
    if item == "error":
        raise ValueError(f"Cannot process: {item}")
    return f"Processed: {item}"

async def process_all_items(items: list[str]) -> list[str]:
    """
    Process all items concurrently using anyio task group.

    If any item fails, cancel remaining and raise the exception.
    """
    results = []

    async with anyio.create_task_group() as tg:
        for item in items:
            # How do you collect results from task group?
            pass

    return results

# Test
items = ["apple", "banana", "cherry"]
results = anyio.run(process_all_items, items)
print(results)

# Test with error
try:
    items = ["apple", "error", "cherry"]
    results = anyio.run(process_all_items, items)
except ValueError as e:
    print(f"Caught error: {e}")
```

---

## Exercise 8: Producer-Consumer Pattern (Challenge)

**Bloom Level**: Create

Implement a producer-consumer pattern using asyncio queues:

```python
import asyncio
from typing import Any

async def producer(queue: asyncio.Queue, items: list[Any], delay: float = 0.1):
    """Produce items and put them on the queue."""
    pass

async def consumer(queue: asyncio.Queue, name: str, process_time: float = 0.2):
    """Consume items from the queue and process them."""
    pass

async def main():
    queue = asyncio.Queue(maxsize=10)

    # Create items to process
    items = [f"item_{i}" for i in range(20)]

    # Create one producer and multiple consumers
    producer_task = asyncio.create_task(producer(queue, items))
    consumer_tasks = [
        asyncio.create_task(consumer(queue, f"consumer_{i}"))
        for i in range(3)
    ]

    # Wait for producer to finish
    await producer_task

    # Wait for queue to be fully processed
    await queue.join()

    # Cancel consumers (they're in infinite loop)
    for task in consumer_tasks:
        task.cancel()

asyncio.run(main())
```

---

## Exercise 9: Real-World Scenario (Challenge)

**Bloom Level**: Create

Build a concurrent web scraper that:
1. Fetches multiple pages concurrently
2. Respects rate limits
3. Retries failed requests
4. Collects and aggregates results

```python
import asyncio
import random
from dataclasses import dataclass

@dataclass
class ScrapedPage:
    url: str
    status: str
    content: str = ""
    error: str = ""

class RateLimitedScraper:
    def __init__(self, max_concurrent: int = 5, rate_limit: float = 0.1):
        """
        Args:
            max_concurrent: Maximum concurrent requests
            rate_limit: Minimum seconds between requests
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit = rate_limit
        self.last_request = 0

    async def fetch_page(self, url: str, retries: int = 3) -> ScrapedPage:
        """Fetch a single page with rate limiting and retries."""
        pass

    async def scrape_all(self, urls: list[str]) -> list[ScrapedPage]:
        """Scrape all URLs concurrently."""
        pass

# Simulated fetch (replace with real HTTP client in production)
async def mock_fetch(url: str) -> tuple[int, str]:
    """Simulate fetching a URL."""
    await asyncio.sleep(random.uniform(0.1, 0.5))
    if random.random() < 0.2:
        raise ConnectionError("Network error")
    return (200, f"Content from {url}")

# Test
async def main():
    urls = [f"https://example.com/page{i}" for i in range(20)]
    scraper = RateLimitedScraper(max_concurrent=5, rate_limit=0.1)

    results = await scraper.scrape_all(urls)

    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]

    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

asyncio.run(main())
```

---

## Deliverables

Submit your code for all exercises. Include your classification table for Exercise 1.

---

[← Back to Chapter](../16_concurrency.md) | [View Solutions](../solutions/sol_16_concurrency.md) | [← Back to Module 3](../README.md)
