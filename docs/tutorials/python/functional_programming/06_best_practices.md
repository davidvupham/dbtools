# Best Practices and Pitfalls

While functional programming (FP) offers many benefits, applying it in Python requires a pragmatic approach.

## Common Pitfalls

### 1. The Recursion Limit

Python is not optimized for deep recursion. It has a default recursion limit (usually 1000).

```python
import sys
print(sys.getrecursionlimit())  # 1000
```

**Pitfall:** Writing a recursive function for a large dataset will crash your program.
**Fix:** Use an iterative approach (loops) or generators for large linear sequences. Use recursion for tree structures or rigid divide-and-conquer algorithms (like Quicksort) where the depth is logarithmic.

### 2. Performance of Copying

Immutability often means making copies of data.

```python
# Expensive in a loop
my_tuple = (1, 2, 3)
for i in range(10000):
    my_tuple = my_tuple + (i,)  # Creates a NEW tuple every iteration!
```

**Fix:** Use mutable structures (lists) locally within a function for construction, then convert to immutable (tuple) before returning. This keeps the *interface* pure while optimizing the *implementation*.

### 3. "Un-Pythonic" Code

Writing Python like it's Haskell can confuse other developers.

**Bad (Overly functional):**

```python
# Hard to read
result = reduce(lambda a, b: a + b, map(lambda x: x*x, filter(lambda x: x > 5, numbers)))
```

**Good (Pythonic):**

```python
# Clear and readable
squares = (x * x for x in numbers if x > 5)
result = sum(squares)
```

## Debugging Functional Code

Functional code is generally easier to debug because pure functions are isolated. However, long chains of `map` and `filter` can be opaque.

**Tip:** Break chains into intermediate variables.

```python
# Hard to debug
final = process_3(process_2(process_1(data)))

# Easier to debug
step1 = process_1(data)
# print(step1)  # Inspect intermediate state
step2 = process_2(step1)
final = process_3(step2)
```

## Testing Pure Functions

Testing pure functions is a joy. You don't need `unittest.mock` to patch databases or APIs.

```python
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

## When to Use Functional Programming

**USE FP When:**

* You have complex data transformations (ETL pipelines).
* You need parallel processing (MapReduce style).
* You want high reliability and testability (core business logic).

**AVOID FP When:**

* You are writing very simple scripts where a loop is clearer.
* You are interacting heavily with stateful APIs (GUI frameworks, some database ORMs).
* Performance is critical and the overhead of copying objects is too high.

## Conclusion

Functional programming in Python is a powerful tool in your belt. You don't have to go 100% functional. Adopting **immutability** and **pure functions** where possible will make your code better, even if you still use `for` loops.
