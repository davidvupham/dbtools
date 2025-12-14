# Core Concepts

Functional programming (FP) is a programming paradigm where programs are constructed by applying and composing functions. It is a declarative style of programming rather than an imperative one.

## What is Functional Programming?

At its heart, functional programming treats computation as the evaluation of mathematical functions and avoids **changing-state** and **mutable data**.

Key tenets include:

* **Pure Functions:** Functions that have no side effects and return the same output for the same input.
* **Immutability:** Data cannot be modified after it's created.
* **First-Class Functions:** Functions are treated as values.

## Functional Style vs. "Pythonic" Code

Python is a multi-paradigm language, not a purely functional one like Haskell. "Pythonic" code emphasizes readability and leveraging Python's idioms.

Sometimes, a functional approach is "Pythonic" (e.g., list comprehensions). Other times, forcing a functional style (like deep recursion or complex `lambda` chains) can be un-Pythonic because it hurts readability.

**Goal:** Use functional features when they make your code cleaner, safer, and easier to test. Don't fight the language.

## Imperative vs. Declarative

* **Imperative:** You tell the computer *how* to do things, step-by-step.
* **Declarative:** You tell the computer *what* you want.

**Example: Filtering a list**

*Imperative:*

```python
numbers = [1, 2, 3, 4, 5]
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
```

*Declarative (Functional):*

```python
numbers = [1, 2, 3, 4, 5]
evens = list(filter(lambda n: n % 2 == 0, numbers))
# Or, more Pythonic:
evens = [n for n in numbers if n % 2 == 0]
```

## Pure Functions

A **pure function** has two properties:

1. **Idempotence:** It always returns the same result for the same arguments.
2. **No Side Effects:** It does not modify arguments, global variables, or input/output streams (like printing or writing to files).

**Impure Function:**

```python
total = 0
def add_to_total(n):
    global total
    total += n  # Side effect: modifies global state
    return total
```

**Pure Function:**

```python
def add(a, b):
    return a + b  # Depends only on inputs, no side effects
```

**Why Pure Functions?**

* **Easier to Test:** You don't need to mock global state.
* **Easier to Debug:** No hidden dependencies.
* **Parallelizable:** Since they don't share state, they can run on multiple cores without race conditions.

## Functions as First-Class Citizens

In Python, functions are objects. This means you can:

1. Assign them to variables.
2. Pass them as arguments to other functions.
3. Return them from other functions.

**Assigning to Variables:**

```python
def yell(text):
    return text.upper() + "!"

my_func = yell
print(my_func("hello"))  # OUTPUT: HELLO!
```

**Passing as Arguments (Higher-Order Functions):**

```python
def apply_func(func, value):
    return func(value)

print(apply_func(len, "Python"))  # OUTPUT: 6
```
