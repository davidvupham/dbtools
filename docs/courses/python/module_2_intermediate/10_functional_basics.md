# Functional Programming Basics

## Lambda Functions

Lambdas are anonymous, single-line functions.

```python
# Regular function
def add(x, y):
    return x + y

# Lambda equivalent
add = lambda x, y: x + y

print(add(5, 3))  # 8
```

## List Comprehensions

A concise way to create lists.

```python
# Squares
squares = [x**2 for x in range(10)]

# Filtering (Even numbers)
evens = [x for x in range(20) if x % 2 == 0]

# Conditional Logic
labels = ["Even" if x % 2 == 0 else "Odd" for x in range(5)]
```

## Map, Filter, Reduce

```python
numbers = [1, 2, 3, 4]

# Map: Apply function to all items
doubled = list(map(lambda x: x * 2, numbers))  # [2, 4, 6, 8]

# Filter: Keep items where function is True
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# Reduce: Combine items
from functools import reduce
sum_all = reduce(lambda x, y: x + y, numbers)  # 10
```

## Dictionary Comprehensions

```python
names = ["Alice", "Bob"]
name_lengths = {name: len(name) for name in names}
# {'Alice': 5, 'Bob': 3}
```
