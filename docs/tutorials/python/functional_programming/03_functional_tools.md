# Functional Tools

Python provides several built-in tools that support functional programming.

## Lambda Functions

`lambda` creates small, anonymous functions. They are restricted to a single expression.

```python
# Named function
def square(x):
    return x * x

# Equivalent Lambda
square_lambda = lambda x: x * x

print(square_lambda(5))  # 25
```

**Best Practice:** Use lambdas for simple, throwaway functions (e.g., inside `map` or `sort`). If it's complex, define a named function.

## Map, Filter, and Reduce

These are the "big three" of functional programming.

### 1. `map(function, iterable)`

Applies a function to every item in an iterable.

```python
nums = [1, 2, 3, 4]
squared = map(lambda x: x * x, nums)
print(list(squared))  # [1, 4, 9, 16]
```

### 2. `filter(function, iterable)`

Keeps items where the function returns `True`.

```python
nums = [1, 2, 3, 4, 5, 6]
evens = filter(lambda x: x % 2 == 0, nums)
print(list(evens))  # [2, 4, 6]
```

### 3. `reduce(function, iterable)`

Reduces an iterable to a single value. It's in the `functools` module (in Python 3).

```python
from functools import reduce

nums = [1, 2, 3, 4]
# (((1 + 2) + 3) + 4)
total = reduce(lambda a, b: a + b, nums)
print(total)  # 10
```

## List Comprehensions vs. Functional Tools

Python developers often prefer **List Comprehensions** over `map` and `filter` because they are arguably more readable.

**Map with List Comp:**

```python
squared = [x * x for x in nums]
```

**Filter with List Comp:**

```python
evens = [x for x in nums if x % 2 == 0]
```

**Which to use?**

* If you have a pre-existing function, `map(my_func, data)` is often cleaner.
* If you need to define a lambda, `[my_func(x) for x in data]` is often cleaner.
