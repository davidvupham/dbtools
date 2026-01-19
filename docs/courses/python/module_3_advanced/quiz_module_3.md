# Module 3 Quiz: Advanced Python

Test your understanding of advanced Python concepts including iterators, generators, concurrency, metaprogramming, performance, and testing.

**Instructions**:
- 20 questions, ~30 minutes
- Mix of conceptual and code questions
- Check answers at the end
- Target: 80% (16/20) to proceed

---

## Section 1: Iterators and Generators (5 questions)

### Question 1

What is the output of this code?

```python
def gen():
    yield 1
    yield 2
    yield 3

g = gen()
print(next(g))
print(next(g))
g2 = gen()
print(next(g2))
```

a) `1, 2, 3`
b) `1, 2, 1`
c) `1, 1, 1`
d) `1, 2, 2`

---

### Question 2

What is the primary advantage of generators over lists?

a) Generators are faster for all operations
b) Generators use less memory by yielding values one at a time
c) Generators can store more items
d) Generators provide faster random access

---

### Question 3

What does `yield from` do?

a) Creates a new generator
b) Delegates iteration to another iterable
c) Yields multiple values at once as a tuple
d) Converts a generator to a list

---

### Question 4

What is the output?

```python
squares = (x**2 for x in range(5))
print(sum(squares))
print(sum(squares))
```

a) `30, 30`
b) `30, 0`
c) `0, 30`
d) Error

---

### Question 5

Which is NOT a valid way to create a generator?

a) Using `yield` in a function
b) Using a generator expression `(x for x in items)`
c) Using the `generator` keyword
d) Implementing `__iter__` and `__next__`

---

## Section 2: Concurrency (4 questions)

### Question 6

For downloading 100 web pages, which approach is most appropriate?

a) `ProcessPoolExecutor` - for true parallelism
b) `ThreadPoolExecutor` or `asyncio` - I/O-bound task
c) Sequential loop - simplest solution
d) Multiprocessing with `Pool.map()`

---

### Question 7

What prevents Python threads from achieving true parallelism for CPU-bound tasks?

a) The Python interpreter is single-threaded
b) The Global Interpreter Lock (GIL)
c) Thread context switching overhead
d) Memory limitations

---

### Question 8

What is the output?

```python
import asyncio

async def greet():
    print("Hello")
    await asyncio.sleep(0)
    print("World")

asyncio.run(greet())
```

a) `Hello, World`
b) `World, Hello`
c) Only `Hello`
d) Error - missing `async def main()`

---

### Question 9

In `asyncio`, what does `asyncio.gather()` do?

a) Runs tasks sequentially
b) Runs tasks concurrently and returns results in order
c) Cancels all tasks
d) Creates a new event loop

---

## Section 3: Metaprogramming (4 questions)

### Question 10

Which dunder method makes an object callable like a function?

a) `__init__`
b) `__call__`
c) `__invoke__`
d) `__run__`

---

### Question 11

When is `__getattr__` called?

a) Every time an attribute is accessed
b) Only when the attribute is not found through normal lookup
c) Only for private attributes
d) When setting an attribute

---

### Question 12

What does `__slots__` do?

a) Limits which methods can be called
b) Restricts allowed attribute names and saves memory
c) Makes the class thread-safe
d) Enables multiple inheritance

---

### Question 13

Which is the correct descriptor protocol?

a) `__get__`, `__set__`, `__del__`
b) `__get__`, `__set__`, `__delete__`
c) `__read__`, `__write__`, `__remove__`
d) `__access__`, `__modify__`, `__clear__`

---

## Section 4: Performance (4 questions)

### Question 14

What is the time complexity of checking if an element is in a Python `set`?

a) O(n)
b) O(log n)
c) O(1) average case
d) O(n²)

---

### Question 15

Which string operation is most efficient for building a large string from many parts?

a) `result += part` in a loop
b) `"".join(parts)`
c) `result = result + part` in a loop
d) They are all equivalent

---

### Question 16

What does `functools.lru_cache` do?

a) Limits CPU usage
b) Caches function results based on arguments
c) Reduces memory usage
d) Speeds up all function calls automatically

---

### Question 17

Which approach should you take FIRST when optimizing slow code?

a) Use a faster programming language
b) Add more caching
c) Profile to find the actual bottleneck
d) Rewrite using list comprehensions

---

## Section 5: Testing (3 questions)

### Question 18

In pytest, what is the purpose of fixtures?

a) Fix bugs in the code being tested
b) Provide reusable setup/teardown for tests
c) Make tests run in a fixed order
d) Fix flaky tests automatically

---

### Question 19

What does `pytest.raises()` do?

a) Raises an exception
b) Verifies that code raises a specific exception
c) Prevents exceptions from stopping tests
d) Counts the number of exceptions

---

### Question 20

Which testing pattern is described: "Set up preconditions, execute the action, verify results"?

a) Test-Driven Development (TDD)
b) Behavior-Driven Development (BDD)
c) Arrange-Act-Assert (AAA)
d) Given-When-Then

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **b**
`1, 2, 1`

`g` and `g2` are separate generator instances. `g` yields 1, then 2. Creating `g2` starts fresh, so it yields 1.

---

### Question 2: **b**
Generators use less memory by yielding values one at a time

Generators are "lazy" - they produce values on demand rather than storing everything in memory. This is crucial for large datasets.

---

### Question 3: **b**
Delegates iteration to another iterable

`yield from iterable` is equivalent to `for item in iterable: yield item` but more efficient and supports coroutine communication.

---

### Question 4: **b**
`30, 0`

Generators are exhausted after one iteration. The first `sum()` consumes all values (0+1+4+9+16=30). The second `sum()` gets nothing (0).

---

### Question 5: **c**
Using the `generator` keyword

There is no `generator` keyword in Python. Generators are created with `yield`, generator expressions, or custom iterator classes.

---

### Question 6: **b**
`ThreadPoolExecutor` or `asyncio` - I/O-bound task

Network I/O is waiting time, not CPU time. Threading or asyncio allows concurrent waiting for responses.

---

### Question 7: **b**
The Global Interpreter Lock (GIL)

The GIL ensures only one thread executes Python bytecode at a time, preventing true parallelism for CPU-bound code.

---

### Question 8: **a**
`Hello, World`

The async function runs correctly with `asyncio.run()`. It prints "Hello", briefly yields control (sleep(0)), then prints "World".

---

### Question 9: **b**
Runs tasks concurrently and returns results in order

`gather(*tasks)` runs all tasks concurrently and returns a list of results in the same order the tasks were passed.

---

### Question 10: **b**
`__call__`

Implementing `__call__(self, ...)` makes instances of a class callable like functions: `obj()`.

---

### Question 11: **b**
Only when the attribute is not found through normal lookup

`__getattr__` is a fallback. `__getattribute__` is called for every access, but it's rarely needed and easy to break.

---

### Question 12: **b**
Restricts allowed attribute names and saves memory

`__slots__` defines a fixed set of attributes, eliminating the per-instance `__dict__` and saving memory.

---

### Question 13: **b**
`__get__`, `__set__`, `__delete__`

The descriptor protocol consists of these three methods. Note it's `__delete__`, not `__del__` (which is the finalizer).

---

### Question 14: **c**
O(1) average case

Sets use hash tables, providing constant-time average case for membership testing. Lists are O(n).

---

### Question 15: **b**
`"".join(parts)`

String concatenation in a loop is O(n²) because strings are immutable. `join()` is O(n).

---

### Question 16: **b**
Caches function results based on arguments

`lru_cache` stores results for argument combinations, returning cached values for repeated calls with the same arguments.

---

### Question 17: **c**
Profile to find the actual bottleneck

"Premature optimization is the root of all evil." Always measure first - the bottleneck is often not where you expect.

---

### Question 18: **b**
Provide reusable setup/teardown for tests

Fixtures create test preconditions (like database connections, sample data) and can clean up afterward using `yield`.

---

### Question 19: **b**
Verifies that code raises a specific exception

`with pytest.raises(ValueError):` asserts that the code block raises a `ValueError`. The test fails if no exception is raised.

---

### Question 20: **c**
Arrange-Act-Assert (AAA)

AAA is a pattern for structuring tests: Arrange (setup), Act (execute), Assert (verify). Given-When-Then is similar but from BDD.

---

### Score Interpretation

- **18-20**: Excellent! You've mastered advanced Python concepts.
- **14-17**: Good understanding. Review the topics you missed.
- **10-13**: Adequate foundation. Revisit the chapters before proceeding.
- **<10**: Re-read Module 3 and redo the exercises.

</details>

---

[← Back to Module 3](./README.md) | [Continue to Module 4 →](../module_4_applied/README.md)
