# Advanced Functional Techniques

Once you master the basics, you can use these advanced concepts to write efficient functional code.

## Iterators and Generators (Lazy Evaluation)

In FP, **lazy evaluation** means waiting to compute a value until it's actually needed. Python supports this via generators.

**Eager (List):** Computes everything at once. Memory intensive.

```python
def get_squares_list(n):
    return [x * x for x in range(n)]
```

**Lazy (Generator):** Computes one at a time. Memory efficient.

```python
def get_squares_gen(n):
    for x in range(n):
        yield x * x
```

## The `functools` Module

### `partial`

Partial application allows you to "freeze" some arguments of a function, creating a new function with fewer arguments.

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# Create a new function that always squares
square = partial(power, exponent=2)
# Create a new function that always cubes
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125
```

### `lru_cache` (Memoization)

Memoization caches the result of expensive function calls. It's a key optimization for pure functions.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

## Recursion

Recursion is solving a problem by calling the function itself.

**Note on Python limits:** Python does **not** have Tail Call Optimization (TCO). Deep recursion will cause a `RecursionError`.

* **Use recursion** for tree traversals or algorithms where depth is limited (logarithmic).
* **Avoid recursion** for simple iteration (linear depth) on large lists; use loops or generators instead.

## External Libraries

Because Python is not purely functional, community libraries help fill the gaps.

* **`toolz`:** offering a suite of functional utilities (like `pipe`, `compose`, `curry`) that extend `itertools` and `functools`. It's highly optimized.
* **`fn.py`:** Provides Scala-inspired features like distinct `_` placeholders for lambdas and infinite streams.
