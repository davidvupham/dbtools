# Python Concurrency: Speed Up Your Scripts

Concurrency allows your program to deal with multiple things at once. If you've ever waited for a script to download a hundred files one by one, you know why this is useful.

This guide will help you choose the right tool for the job: **Threading**, **Asyncio**, or **Multiprocessing**.

---

## The Golden Rule: I/O vs. CPU

Before writing code, ask: **"What is slowing my program down?"**

1.  **I/O Bound (Input/Output)**: Your program spends most of its time **waiting** for external things (Network requests, Database queries, Disk operations).
    *   ***Solution**: use `threading` or `asyncio`.*
2.  **CPU Bound**: Your program spends most of its time **calculating** (Number crunching, Image processing, Complex algorithms).
    *   ***Solution**: use `multiprocessing`.*

---

## 1. I/O Bound: Waiting for the Web

Imagine downloading 10 web pages.
*   **Synchronous**: Request Site A -> Wait 1s -> Request Site B -> Wait 1s ... (Total: 10s)
*   **Concurrent**: Request Site A, B, C... all at once -> Wait 1s -> All done. (Total: ~1s)

### Option A: Threading (Pre-emptive Multitasking)

Threading is great because it's **easy to add** to existing synchronous code. The Operating System switches between threads automatically.

**Use when**: You want to speed up simple I/O tasks with minimal code changes.

```python
import concurrent.futures
import time

def slow_task(n):
    print(f"Task {n}: Starting...")
    time.sleep(2)  # Simulate network request
    print(f"Task {n}: Done!")
    return n * n

def main():
    start = time.perf_counter()

    # Run 5 tasks using a Thread Pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(slow_task, range(5))

    finish = time.perf_counter()

    print(f"Finished in {finish-start:.2f} seconds")
    # Takes ~2 seconds, not 10!

if __name__ == "__main__":
    main()
```

### Option B: Asyncio (Cooperative Multitasking)

Asyncio uses a single thread and an "event loop". Tasks voluntarily "await" when they need to pause (like waiting for a response), letting other tasks run.

**Use when**: You need high performance handling thousands of connections (e.g., web servers, scraping). it requires keywords `async` and `await`.

```python
import asyncio
import time

async def slow_task(n):
    print(f"Task {n}: Starting...")
    await asyncio.sleep(2)  # Non-blocking sleep
    print(f"Task {n}: Done!")
    return n * n

async def main():
    start = time.perf_counter()

    # Create a list of tasks
    tasks = [slow_task(n) for n in range(5)]

    # Run them all concurrently
    await asyncio.gather(*tasks)

    finish = time.perf_counter()
    print(f"Finished in {finish-start:.2f} seconds")

if __name__ == "__main__":
    # asyncio.run() acts as the entry point
    asyncio.run(main())
```

---

## 2. CPU Bound: Heavy Calculation

Imagine calculating a massive number. Threads won't help here because of the **Global Interpreter Lock (GIL)**. Python only allows one thread to hold the CPU at a time.

### The Fail: Threading on CPU Tasks
If you use `ThreadPoolExecutor` for CPU work, it might actually be **slower** than a normal loop due to overhead!

### The Solution: Multiprocessing

Multiprocessing creates separate Python processes, each with its own memory and CPU core. They run in **parallel**.

```python
import concurrent.futures
import time

def cpu_heavy_task(n):
    # Simulate a heavy calculation
    count = 0
    for i in range(10**7):
        count += i
    return count

def main():
    start = time.perf_counter()

    # ProcessPoolExecutor creates actual separate processes
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # We need check if this is effectively using multiple cores in Task Manager
        results = executor.map(cpu_heavy_task, range(5))

    finish = time.perf_counter()
    print(f"Finished in {finish-start:.2f} seconds")

if __name__ == "__main__":
    # This guard is REQUIRED for multiprocessing on Windows
    main()
```

---

## Summary Cheat Sheet

| Bottleneck | Problem | Best Tool | Why? |
| :--- | :--- | :--- | :--- |
| **I/O** | Network Request | `concurrent.futures.ThreadPoolExecutor` | Easiest to implement. |
| **I/O** | 10k+ Connections | `asyncio` | Lowest memory overhead. |
| **CPU** | Math/Image Processing | `concurrent.futures.ProcessPoolExecutor` | Bypasses the GIL, uses multiple cores. |

---

## 3. anyio - Async Compatibility Layer

[anyio](https://anyio.readthedocs.io/) provides a unified async API that works with both `asyncio` and `trio`. Write your async code once, run it on any backend.

### Installation

```bash
uv add anyio
```

### Basic Usage

```python
import anyio

async def worker():
    print("Starting work...")
    await anyio.sleep(1)
    print("Done!")

anyio.run(worker)
```

### Why anyio?

1. **Backend agnostic** - Code works with asyncio and trio without changes
2. **Structured concurrency** - Task groups ensure proper cleanup
3. **Better cancellation** - Predictable, reliable task cancellation
4. **Unified API** - One interface for timers, locks, events, channels

### Task Groups (Structured Concurrency)

Task groups ensure all child tasks complete (or are cancelled) before the parent continues:

```python
import anyio

async def fetch(url: str) -> str:
    await anyio.sleep(1)  # Simulate network request
    return f"Data from {url}"

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch, "https://api1.example.com")
        tg.start_soon(fetch, "https://api2.example.com")
        tg.start_soon(fetch, "https://api3.example.com")
    # All tasks guaranteed complete here
    print("All fetches done!")

anyio.run(main)
```

### Timeouts

```python
import anyio

async def slow_operation():
    await anyio.sleep(10)

async def main():
    with anyio.move_on_after(2):  # Cancel after 2 seconds
        await slow_operation()
        print("This won't print")
    print("Continued after timeout")

anyio.run(main)
```

### Cancellation Scopes

```python
import anyio

async def main():
    with anyio.CancelScope() as scope:
        await anyio.sleep(1)
        scope.cancel()  # Cancel everything in this scope
        await anyio.sleep(10)  # Never executes
    print("Scope cancelled cleanly")

anyio.run(main)
```

### When to Use anyio vs asyncio

| Scenario | Use asyncio | Use anyio |
|----------|------------|-----------|
| Simple scripts | Yes | Either |
| Libraries (reusable code) | No | Yes |
| Need trio compatibility | No | Yes |
| Structured concurrency | Limited | Built-in |
| Complex cancellation | Manual | Automatic |

**Use asyncio** for simple applications or when minimizing dependencies.

**Use anyio** for libraries, complex workflows, or when you need structured concurrency guarantees
