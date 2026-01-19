# Data Structures

## Lists - Ordered Collections

Lists store multiple items in order:

```python
# Create a list
fruits = ["apple", "banana", "cherry"]

# Access items (counting starts at 0!)
first_fruit = fruits[0]   # "apple"
last_fruit = fruits[-1]   # "cherry" (negative counts from end)

# Add items
fruits.append("date")     # Add to end
fruits.insert(1, "blueberry")  # Insert at position 1

# Loop through items
for fruit in fruits:
    print(f"I like {fruit}")

# Check if item exists
if "apple" in fruits:
    print("We have apples!")
```

## Dictionaries - Key-Value Pairs

Dictionaries store data with labels (keys):

```python
# Create a dictionary
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Access values by key
print(person["name"])  # "Alice"

# Add or update values
person["email"] = "alice@example.com"
person["age"] = 31  # Update existing value

# Loop through dictionary
for key, value in person.items():
    print(f"{key}: {value}")
```

### Safe key access with `.get()`

Using `dict[key]` raises `KeyError` if the key doesn't exist. Use `.get()` for safer access:

```python
d = {"apple": 4, "orange": 5}

# Using .get() - returns None if key missing (no error)
print(d.get("apple"))   # 4
print(d.get("pear"))    # None

# Provide a default value
print(d.get("pear", 0))         # 0
print(d.get("pear", "unknown")) # "unknown"
```

### Merging dictionaries with `|` (Python 3.9+)

The `|` operator creates a new dictionary combining two dicts:

```python
d1 = {"a": 1, "b": 2}
d2 = {"c": 3, "d": 4}

d3 = d1 | d2
print(d3)  # {'a': 1, 'b': 2, 'c': 3, 'd': 4}

# With duplicate keys, rightmost dict takes precedence
d1 = {"a": 1, "b": 2, "c": 6}
d2 = {"c": 3, "d": 4, "a": 5}

d3 = d1 | d2
print(d3)  # {'a': 5, 'b': 2, 'c': 3, 'd': 4}

# Use |= to update in place
d1 |= {"e": 5}
print(d1)  # {'a': 1, 'b': 2, 'c': 6, 'e': 5}
```

### Merging with `.update()`

The `.update()` method modifies the original dictionary in place:

```python
d1 = {"a": 1, "b": 2}
d2 = {"c": 3, "d": 4}

d1.update(d2)
print(d1)  # {'a': 1, 'b': 2, 'c': 3, 'd': 4}
print(d2)  # {'c': 3, 'd': 4} (unchanged)

# With duplicate keys, the argument dict takes precedence
```

### Creating dictionaries from iterables

Pass a list of key-value tuples to `dict()`:

```python
key_value_pairs = [("a", 1), ("b", 2), ("c", 3)]
d = dict(key_value_pairs)
print(d)  # {'a': 1, 'b': 2, 'c': 3}

# Combine two lists with zip()
keys = ["a", "b", "c"]
values = [1, 2, 3]
d = dict(zip(keys, values))
print(d)  # {'a': 1, 'b': 2, 'c': 3}
```

### Iterating with `.keys()`, `.values()`, `.items()`

```python
d = {"apple": 4, "orange": 5, "pear": 6}

# Iterate over keys
for key in d.keys():
    print(key, end=" ")  # apple orange pear

# Iterate over values
for value in d.values():
    print(value, end=" ")  # 4 5 6

# Iterate over key-value pairs
for key, value in d.items():
    print(key, value, end=" ")  # apple 4 orange 5 pear 6
```

Note: `for k in d:` also iterates over keys, but `for k in d.keys():` is more explicit.

### Dictionary keys must be hashable

Only immutable (hashable) objects can be dictionary keys. Mutable objects like lists, dicts, and sets cannot be used as keys.

```python
# Valid keys (immutable types)
d = {
    4: "integer key",
    (1, 2): "tuple key",
    frozenset({1, 2, 3}): "frozenset key",
    "apple": "string key"
}

# Invalid keys (mutable types) - will raise TypeError
# d = {[1, 2]: "list key"}       # TypeError: unhashable type: 'list'
# d = {{3, 4}: "set key"}        # TypeError: unhashable type: 'set'
```

If you need a collection as a key, convert lists to tuples or sets to frozensets.

## Tuples - Immutable Collections

Tuples are like lists but can't be changed after creation:

```python
# Create a tuple
coordinates = (10.5, 20.3)
x, y = coordinates  # Unpack values

# Multiple return values use tuples
def get_status():
    return True, "Connected", 100  # Returns a tuple

success, message, code = get_status()  # Unpack
```
