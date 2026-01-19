# Solutions — 16: Concurrency

## Key Concepts Demonstrated

- ThreadPoolExecutor for I/O-bound tasks
- ProcessPoolExecutor for CPU-bound tasks
- Asyncio for high-concurrency I/O
- Error handling in concurrent code
- Rate limiting and retries
- Producer-consumer patterns

## Common Mistakes to Avoid

- Using threads for CPU-bound work (GIL prevents parallelism)
- Forgetting `if __name__ == "__main__"` guard for multiprocessing
- Not handling exceptions from concurrent tasks
- Creating too many threads/processes (use pool size limits)
- Blocking the event loop in async code

---

## Exercise 1 Solution

| Task | I/O or CPU? | Best Tool |
|------|-------------|-----------|
| Download 100 images from URLs | **I/O** | `ThreadPoolExecutor` or `asyncio` |
| Compress 100 large files | **CPU** | `ProcessPoolExecutor` |
| Query 50 different databases | **I/O** | `ThreadPoolExecutor` or `asyncio` |
| Calculate prime numbers up to 10 million | **CPU** | `ProcessPoolExecutor` |
| Send 1000 HTTP requests to an API | **I/O** | `asyncio` (best for many connections) |
| Resize 500 images | **CPU** | `ProcessPoolExecutor` |
| Read data from 100 CSV files | **I/O** | `ThreadPoolExecutor` |
| Train a machine learning model | **CPU** | `ProcessPoolExecutor` or native parallelism |

---

## Exercise 2 Solution

```python
import concurrent.futures
import time

def download_url(url: str) -> tuple[str, int]:
    """Download a URL and return (url, content_length)."""
    time.sleep(0.5)  # Simulate network delay
    return (url, 1000)

urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
    "https://example.com/page4",
    "https://example.com/page5",
]

def download_sequential(urls):
    results = []
    for url in urls:
        results.append(download_url(url))
    return results

def download_concurrent(urls, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Method 1: Using map (maintains order)
        results = list(executor.map(download_url, urls))
        return results

        # Method 2: Using submit (more control)
        # futures = [executor.submit(download_url, url) for url in urls]
        # return [f.result() for f in concurrent.futures.as_completed(futures)]

# Compare times
start = time.perf_counter()
results = download_sequential(urls)
print(f"Sequential: {time.perf_counter() - start:.2f}s")  # ~2.5s

start = time.perf_counter()
results = download_concurrent(urls)
print(f"Concurrent: {time.perf_counter() - start:.2f}s")  # ~0.5s
```

---

## Exercise 3 Solution

```python
import concurrent.futures
import time
import math

def is_prime(n: int) -> bool:
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
    return sum(1 for n in range(start, end) if is_prime(n))

def count_primes_parallel(limit: int, num_workers: int = 4) -> int:
    # Split range into chunks
    chunk_size = limit // num_workers
    ranges = []
    for i in range(num_workers):
        start = i * chunk_size
        end = limit if i == num_workers - 1 else (i + 1) * chunk_size
        ranges.append((start, end))

    # Process chunks in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(count_primes_in_range, start, end)
                   for start, end in ranges]
        counts = [f.result() for f in futures]

    return sum(counts)

if __name__ == "__main__":
    limit = 100000
    start = time.perf_counter()
    count = count_primes_parallel(limit)
    elapsed = time.perf_counter() - start
    print(f"Found {count} primes up to {limit} in {elapsed:.2f}s")
```

---

## Exercise 4 Solution

```python
import concurrent.futures
import random

def unreliable_task(task_id: int) -> str:
    if random.random() < 0.3:
        raise ValueError(f"Task {task_id} failed!")
    return f"Task {task_id} completed"

def run_with_error_handling(task_ids: list[int]) -> dict:
    results = {
        'successful': [],
        'failed': []
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks
        future_to_id = {
            executor.submit(unreliable_task, task_id): task_id
            for task_id in task_ids
        }

        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_id):
            task_id = future_to_id[future]
            try:
                result = future.result()
                results['successful'].append((task_id, result))
            except Exception as e:
                results['failed'].append((task_id, str(e)))

    return results

# Test
random.seed(42)  # For reproducibility
results = run_with_error_handling(list(range(10)))
print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
for task_id, error in results['failed']:
    print(f"  Task {task_id}: {error}")
```

---

## Exercise 5 Solution

```python
import asyncio
import time

async def fetch_data(name: str, delay: float) -> dict:
    print(f"Starting fetch for {name}")
    await asyncio.sleep(delay)
    print(f"Completed fetch for {name}")
    return {"name": name, "data": f"Data for {name}"}

async def fetch_all():
    # Create tasks for concurrent execution
    tasks = [
        fetch_data("api_1", 1.0),
        fetch_data("api_2", 2.0),
        fetch_data("api_3", 0.5),
        fetch_data("api_4", 1.5),
    ]

    # Run all tasks concurrently and gather results
    results = await asyncio.gather(*tasks)
    return results

# Run
start = time.perf_counter()
results = asyncio.run(fetch_all())
elapsed = time.perf_counter() - start

print(f"\nCompleted in {elapsed:.2f}s")  # ~2s (not 5s)
print(f"Results: {[r['name'] for r in results]}")
```

---

## Exercise 6 Solution

```python
import asyncio

async def slow_operation(name: str, duration: float) -> str:
    await asyncio.sleep(duration)
    return f"{name} completed"

async def fetch_with_timeout(name: str, duration: float, timeout: float) -> str:
    try:
        result = await asyncio.wait_for(
            slow_operation(name, duration),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return f"{name} timed out after {timeout}s"

async def fetch_all_with_timeouts():
    operations = [
        ("fast", 0.5),
        ("medium", 1.5),
        ("slow", 5.0),
        ("very_slow", 10.0),
    ]
    timeout = 2.0

    # Run all concurrently with timeout
    tasks = [
        fetch_with_timeout(name, duration, timeout)
        for name, duration in operations
    ]
    results = await asyncio.gather(*tasks)
    return results

# Test
results = asyncio.run(fetch_all_with_timeouts())
for r in results:
    print(r)
# Output:
# fast completed
# medium completed
# slow timed out after 2.0s
# very_slow timed out after 2.0s
```

---

## Exercise 7 Solution

```python
import anyio

async def process_item(item: str) -> str:
    await anyio.sleep(0.5)
    if item == "error":
        raise ValueError(f"Cannot process: {item}")
    return f"Processed: {item}"

async def process_all_items(items: list[str]) -> list[str]:
    results = []
    results_lock = anyio.Lock()

    async def process_and_store(item: str):
        result = await process_item(item)
        async with results_lock:
            results.append(result)

    async with anyio.create_task_group() as tg:
        for item in items:
            tg.start_soon(process_and_store, item)

    return results

# Test
items = ["apple", "banana", "cherry"]
results = anyio.run(process_all_items, items)
print(results)

# Test with error - will cancel all tasks and raise
try:
    items = ["apple", "error", "cherry"]
    results = anyio.run(process_all_items, items)
except Exception as e:
    print(f"Caught error: {e}")
```

---

## Exercise 8 Solution

```python
import asyncio
from typing import Any

async def producer(queue: asyncio.Queue, items: list[Any], delay: float = 0.1):
    for item in items:
        await asyncio.sleep(delay)
        await queue.put(item)
        print(f"Produced: {item}")

    # Signal completion by putting None for each consumer
    # Or use a sentinel value

async def consumer(queue: asyncio.Queue, name: str, process_time: float = 0.2):
    while True:
        try:
            item = await queue.get()
            await asyncio.sleep(process_time)  # Simulate processing
            print(f"{name} processed: {item}")
            queue.task_done()
        except asyncio.CancelledError:
            print(f"{name} shutting down")
            break

async def main():
    queue = asyncio.Queue(maxsize=10)

    items = [f"item_{i}" for i in range(20)]

    producer_task = asyncio.create_task(producer(queue, items))
    consumer_tasks = [
        asyncio.create_task(consumer(queue, f"consumer_{i}"))
        for i in range(3)
    ]

    await producer_task
    await queue.join()

    for task in consumer_tasks:
        task.cancel()

    # Wait for cancellation to complete
    await asyncio.gather(*consumer_tasks, return_exceptions=True)

asyncio.run(main())
```

---

## Exercise 9 Solution

```python
import asyncio
import random
import time
from dataclasses import dataclass

@dataclass
class ScrapedPage:
    url: str
    status: str
    content: str = ""
    error: str = ""

class RateLimitedScraper:
    def __init__(self, max_concurrent: int = 5, rate_limit: float = 0.1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit = rate_limit
        self.last_request = 0
        self._lock = asyncio.Lock()

    async def _wait_for_rate_limit(self):
        async with self._lock:
            now = time.time()
            wait_time = self.rate_limit - (now - self.last_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_request = time.time()

    async def fetch_page(self, url: str, retries: int = 3) -> ScrapedPage:
        for attempt in range(retries):
            async with self.semaphore:
                await self._wait_for_rate_limit()
                try:
                    status_code, content = await mock_fetch(url)
                    return ScrapedPage(
                        url=url,
                        status="success",
                        content=content
                    )
                except Exception as e:
                    if attempt == retries - 1:
                        return ScrapedPage(
                            url=url,
                            status="failed",
                            error=str(e)
                        )
                    await asyncio.sleep(0.5 * (attempt + 1))  # Backoff

    async def scrape_all(self, urls: list[str]) -> list[ScrapedPage]:
        tasks = [self.fetch_page(url) for url in urls]
        return await asyncio.gather(*tasks)

async def mock_fetch(url: str) -> tuple[int, str]:
    await asyncio.sleep(random.uniform(0.1, 0.5))
    if random.random() < 0.2:
        raise ConnectionError("Network error")
    return (200, f"Content from {url}")

async def main():
    urls = [f"https://example.com/page{i}" for i in range(20)]
    scraper = RateLimitedScraper(max_concurrent=5, rate_limit=0.1)

    start = time.perf_counter()
    results = await scraper.scrape_all(urls)
    elapsed = time.perf_counter() - start

    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "failed"]

    print(f"Completed in {elapsed:.2f}s")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

asyncio.run(main())
```

---

## Concurrency Decision Table

| Scenario | Use This | Why |
|----------|----------|-----|
| Network I/O (few) | `ThreadPoolExecutor` | Simple, works with sync code |
| Network I/O (many) | `asyncio` | Lower overhead per connection |
| CPU-heavy work | `ProcessPoolExecutor` | Bypasses GIL |
| Mixed I/O + CPU | Combination | Use right tool for each part |
| Library code | `anyio` | Backend-agnostic |

---

[← Back to Exercises](../exercises/ex_16_concurrency.md) | [← Back to Chapter](../16_concurrency.md) | [← Back to Module 3](../README.md)
