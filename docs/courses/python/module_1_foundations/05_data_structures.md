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
