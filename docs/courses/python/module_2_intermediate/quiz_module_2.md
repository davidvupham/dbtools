# Module 2 Quiz: Intermediate Python

Test your understanding of intermediate Python concepts including OOP, modern data structures, functional programming, decorators, context managers, modules, and logging.

**Instructions**:
- 20 questions, ~30 minutes
- Mix of conceptual and code questions
- Check answers at the end
- Target: 80% (16/20) to proceed to Module 3

---

## Section 1: Object-Oriented Programming (5 questions)

### Question 1

What is the output of this code?

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

animals = [Dog(), Cat(), Animal()]
result = [a.speak() for a in animals]
print(result)
```

a) `['...', '...', '...']`
b) `['Woof!', 'Meow!', '...']`
c) `['Woof!', 'Meow!', 'Woof!']`
d) Error: Animal cannot be instantiated

---

### Question 2

Which statement about Python's `super()` is correct?

a) `super()` always calls the parent class's `__init__` method automatically
b) `super()` returns the parent class itself
c) `super()` returns a proxy object that delegates method calls to the parent class
d) `super()` can only be used inside `__init__` methods

---

### Question 3

What is the output of this code?

```python
class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1
        self.id = Counter.count

a = Counter()
b = Counter()
c = Counter()
print(a.count, b.count, c.count)
```

a) `1 2 3`
b) `3 3 3`
c) `1 1 1`
d) Error: count is not defined

---

### Question 4

Which dunder method should you implement to make an object work with the `len()` function?

a) `__size__`
b) `__length__`
c) `__len__`
d) `__count__`

---

### Question 5

What is the difference between composition and inheritance?

a) Composition creates "is-a" relationships; inheritance creates "has-a" relationships
b) Composition creates "has-a" relationships; inheritance creates "is-a" relationships
c) They are the same thing with different syntax
d) Composition is faster than inheritance

---

## Section 2: Modern Data Structures (3 questions)

### Question 6

What is the output of this code?

```python
from dataclasses import dataclass, field

@dataclass
class Item:
    name: str
    price: float = 0.0
    tags: list = field(default_factory=list)

item1 = Item("Widget")
item2 = Item("Gadget")
item1.tags.append("sale")
print(item2.tags)
```

a) `['sale']`
b) `[]`
c) `None`
d) Error: list cannot be a default

---

### Question 7

Which decorator makes a dataclass immutable (prevents attribute modification after creation)?

a) `@dataclass(immutable=True)`
b) `@dataclass(frozen=True)`
c) `@dataclass(readonly=True)`
d) `@dataclass(const=True)`

---

### Question 8

What is a key advantage of `NamedTuple` over a regular tuple?

a) NamedTuple is faster
b) NamedTuple allows mutable fields
c) NamedTuple provides named access to fields and better documentation
d) NamedTuple can store more elements

---

## Section 3: Functional Programming (3 questions)

### Question 9

What is the output of this code?

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]
result = reduce(lambda acc, x: acc + x, numbers, 10)
print(result)
```

a) `15`
b) `25`
c) `10`
d) Error: reduce requires only 2 arguments

---

### Question 10

What does `functools.lru_cache` do?

a) Limits the number of times a function can be called
b) Caches function results based on arguments to avoid recomputation
c) Makes a function run in a separate thread
d) Converts a function to use lazy evaluation

---

### Question 11

Which `itertools` function would you use to create all possible pairs from two lists?

a) `itertools.combinations(list1 + list2, 2)`
b) `itertools.product(list1, list2)`
c) `itertools.pairs(list1, list2)`
d) `itertools.chain(list1, list2)`

---

## Section 4: Decorators (4 questions)

### Question 12

What is the output of this code?

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
```

a) `Hello, Alice!`
b) `Before`, `Hello, Alice!`, `After`
c) `After`, `Hello, Alice!`, `Before`
d) Error: wrapper is not callable

---

### Question 13

What is the purpose of `@functools.wraps(func)` in a decorator?

a) It makes the decorator run faster
b) It preserves the original function's name, docstring, and metadata
c) It allows the decorator to accept arguments
d) It ensures the function can only be called once

---

### Question 14

What is the correct way to write a decorator that accepts arguments?

a) Two levels of nesting: `def decorator(arg): def wrapper(func): ...`
b) Three levels of nesting: `def decorator(arg): def actual_decorator(func): def wrapper(*args): ...`
c) One level: `def decorator(func, arg): ...`
d) Use a class with `__init__` and `__call__`

---

### Question 15

In what order are stacked decorators applied?

```python
@decorator_a
@decorator_b
@decorator_c
def func():
    pass
```

a) Top to bottom: a, then b, then c wraps func
b) Bottom to top: c wraps func, then b wraps result, then a wraps result
c) Random order
d) All at once in parallel

---

## Section 5: Context Managers (2 questions)

### Question 16

What must a context manager class implement?

a) `__enter__` and `__exit__`
b) `__start__` and `__stop__`
c) `__open__` and `__close__`
d) `__begin__` and `__end__`

---

### Question 17

What should `__exit__` return to suppress an exception that occurred inside the `with` block?

a) `None`
b) `False`
c) `True`
d) The exception object

---

## Section 6: Modules and Logging (3 questions)

### Question 18

What does `__all__` control in a Python module?

a) Which names are imported with `from module import *`
b) Which names can be accessed at all
c) The order in which names are defined
d) Which names are private

---

### Question 19

What is the correct order of Python logging levels from least to most severe?

a) DEBUG, INFO, WARNING, ERROR, CRITICAL
b) INFO, DEBUG, WARNING, ERROR, CRITICAL
c) DEBUG, WARNING, INFO, ERROR, CRITICAL
d) CRITICAL, ERROR, WARNING, INFO, DEBUG

---

### Question 20

Why is `logger.info("User %s", user_id)` preferred over `logger.info(f"User {user_id}")`?

a) The first syntax is faster
b) The first syntax only formats the string if the log level is enabled (lazy evaluation)
c) The first syntax is more readable
d) The f-string syntax doesn't work with logging

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **b**
`['Woof!', 'Meow!', '...']`

Each object calls its own class's `speak()` method (polymorphism). Dog returns "Woof!", Cat returns "Meow!", and the base Animal returns "...".

---

### Question 2: **c**
`super()` returns a proxy object that delegates method calls to the parent class

`super()` doesn't call anything automatically—it returns a proxy that allows you to call parent methods. It works with the Method Resolution Order (MRO) for multiple inheritance.

---

### Question 3: **b**
`3 3 3`

`count` is a **class variable** shared by all instances. After creating 3 instances, `Counter.count` is 3. When you access `a.count`, Python looks up the class variable since `a` doesn't have its own `count` instance variable.

---

### Question 4: **c**
`__len__`

The `len()` function calls the object's `__len__` method. This is part of Python's data model for sequence-like objects.

---

### Question 5: **b**
Composition creates "has-a" relationships; inheritance creates "is-a" relationships

- Inheritance: "A Dog **is a** Animal"
- Composition: "A Car **has a** Engine"

Composition is often preferred as it's more flexible and avoids tight coupling.

---

### Question 6: **b**
`[]`

Using `field(default_factory=list)` creates a **new list for each instance**. Without `default_factory`, all instances would share the same list (which would give answer a).

---

### Question 7: **b**
`@dataclass(frozen=True)`

The `frozen=True` parameter makes the dataclass immutable. Attempting to modify attributes after creation raises `FrozenInstanceError`.

---

### Question 8: **c**
NamedTuple provides named access to fields and better documentation

NamedTuples allow you to access elements by name (`point.x`) instead of index (`point[0]`), making code more readable and self-documenting.

---

### Question 9: **b**
`25`

`reduce` takes an initial value of 10, then adds each number: 10 + 1 + 2 + 3 + 4 + 5 = 25.

---

### Question 10: **b**
Caches function results based on arguments to avoid recomputation

`lru_cache` (Least Recently Used cache) stores function results so repeated calls with the same arguments return cached values instead of recomputing.

---

### Question 11: **b**
`itertools.product(list1, list2)`

`product` gives the Cartesian product—all pairs combining one element from each list. `combinations` is for selecting from a single iterable.

---

### Question 12: **b**
`Before`, `Hello, Alice!`, `After`

The decorator wrapper runs "Before", then calls the original function (which prints the greeting), then runs "After".

---

### Question 13: **b**
It preserves the original function's name, docstring, and metadata

Without `@wraps`, the decorated function would have `wrapper`'s name and docstring instead of the original function's metadata.

---

### Question 14: **b**
Three levels of nesting: `def decorator(arg): def actual_decorator(func): def wrapper(*args): ...`

When a decorator takes arguments, you need an extra level:
1. Outer function receives decorator arguments
2. Middle function receives the function to decorate
3. Inner function is the actual wrapper

Option d (class with `__init__` and `__call__`) also works and is an alternative pattern.

---

### Question 15: **b**
Bottom to top: c wraps func, then b wraps result, then a wraps result

Decorators are applied bottom-to-top:
```python
func = decorator_a(decorator_b(decorator_c(func)))
```

During execution, a's wrapper runs first (outermost), then b's, then c's, then the original function.

---

### Question 16: **a**
`__enter__` and `__exit__`

These are the two methods that define the context manager protocol. `__enter__` sets up the resource, `__exit__` cleans it up.

---

### Question 17: **c**
`True`

Returning `True` from `__exit__` tells Python to suppress the exception. Returning `False` or `None` allows the exception to propagate.

---

### Question 18: **a**
Which names are imported with `from module import *`

`__all__` is a list of strings specifying which names are public and should be exported with wildcard imports. It doesn't prevent direct imports.

---

### Question 19: **a**
DEBUG, INFO, WARNING, ERROR, CRITICAL

This is the standard order from least to most severe. The default level is WARNING, meaning DEBUG and INFO messages are hidden by default.

---

### Question 20: **b**
The first syntax only formats the string if the log level is enabled (lazy evaluation)

With `logger.info("User %s", user_id)`, the string formatting only happens if INFO level is enabled. With f-strings, the formatting always happens even if the message is never logged, wasting CPU cycles.

---

### Score Interpretation

- **18-20**: Excellent! You've mastered intermediate Python concepts.
- **14-17**: Good understanding. Review the topics you missed.
- **10-13**: Adequate foundation. Revisit the chapters before proceeding.
- **<10**: Re-read Module 2 and redo the exercises before continuing.

</details>

---

[← Back to Module 2](./README.md) | [Continue to Module 3 →](../module_3_advanced/README.md)
