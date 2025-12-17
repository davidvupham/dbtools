# Iterators and Generators

## Iterators

An **iterable** is anything you can loop over (list, tuple, string).
An **iterator** is the object that actually does the looping (keeps track of position).

```python
# Iterable
numbers = [1, 2, 3]

# Get Iterator
it = iter(numbers)

print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # 3
# print(next(it))  # StopIteration Error
```

## Generators

Generators are functions that return an iterator. They use `yield` instead of `return`.
They are **lazy**: they generate values on the fly, saving memory.

```python
def count_up_to(max):
    count = 1
    while count <= max:
        yield count
        count += 1

counter = count_up_to(3)
print(next(counter))  # 1
print(next(counter))  # 2
```

### Generator Expressions

Like list comprehensions, but with parentheses.

```python
# List comprehension (creates full list in memory)
squares_list = [x**2 for x in range(1000000)]

# Generator expression (almost zero memory)
squares_gen = (x**2 for x in range(1000000))

print(next(squares_gen))  # 0
```

## When to use Generators?

* Working with large datasets (that don't fit in RAM).
* Infinite sequences.
* Pipelining data processing.
