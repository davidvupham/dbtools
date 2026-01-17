# Immutable Data Structures

In functional programming, **immutability** is key. Instead of modifying objects in place, you create new objects with the updated values. This avoids bugs related to shared mutable state.

## Why Immutability?

* **Thread Safety:** Immutable objects are inherently thread-safe.
* **Predictability:** You don't have to worry about a list being modified by a function you passed it to.

## Tuples

The most basic immutable sequence in Python is the `tuple`.

```python
# Mutable List
my_list = [1, 2, 3]
my_list[0] = 10  # Allowed

# Immutable Tuple
my_tuple = (1, 2, 3)
# my_tuple[0] = 10  # TypeError: 'tuple' object does not support item assignment
```

## Named Tuples

`tuples` are great, but accessing items by index (`p[0]`) is less readable. `namedtuple` (from `collections`) gives you immutability *and* readable field names.

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p1 = Point(10, 20)

print(p1.x)  # 10
# p1.x = 30  # AttributeError: can't set attribute
```

**Replacing values:**
Since you can't modify it, how not to "update" it? usage the `_replace` method, which returns a *new* object.

```python
p2 = p1._replace(x=30)
print(p1)  # Point(x=10, y=20) - Original is unchanged
print(p2)  # Point(x=30, y=20) - New object
```

## Frozenset

Just as a `tuple` is an immutable `list`, a `frozenset` is an immutable `set`.

```python
vowels = frozenset({'a', 'e', 'i', 'o', 'u'})
# vowels.add('y')  # AttributeError
```

Frozensets are hashable, meaning they can be used as dictionary keys (unlike regular sets).

## The Danger of Mutable Defaults

A common "gotcha" in Python that violates functional principles is using mutable default arguments.

**Bad Practice:**

```python
def append_to(element, target=[]):
    target.append(element)  # Modifies the default object!
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2] - Surprise! It reused the same list.
```

**Functional/Pythonic Fix:**
Use `None` as the default and create the list inside the function.

```python
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target
```

*Note: In a purely functional style, you wouldn't even append. You would return a new list: `return target + [element]`.*
