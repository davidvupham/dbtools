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
