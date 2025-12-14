# Parallelism and Functional Programming

One of the biggest benefits of functional programming is that it simplifies parallel execution.

## The Problem with State

In traditional imperative programming, threads share state (variables). If two threads try to modify the same variable at the same time, you get **race conditions**. You have to use locks, semaphores, and other complex synchronization mechanisms.

## The Functional Solution

If your functions are **pure** (no side effects) and your data is **immutable**, race conditions are impossible! You can run the function on 1000 cores simultaneously without any locks.

## `concurrent.futures`

Python's standard library makes it easy to parallelize functional operations.

`ProcessPoolExecutor` bypasses the Global Interpreter Lock (GIL) by using subprocesses, making it perfect for CPU-bound tasks.

```python
import time
from concurrent.futures import ProcessPoolExecutor

def expensive_calculation(n):
    time.sleep(1) # Simulate work
    return n * n

nums = [1, 2, 3, 4, 5]

if __name__ == '__main__':
    # Sequential (takes ~5 seconds)
    # results = map(expensive_calculation, nums)

    # Parallel (takes ~1 second on multi-core machine)
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(expensive_calculation, nums))

    print(results)
```

**Note:** Because `map` applies a function to each item independently, it is trivially parallelizable ("embarrassingly parallel").
