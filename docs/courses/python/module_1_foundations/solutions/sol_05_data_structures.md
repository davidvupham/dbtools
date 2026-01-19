# Solutions — 05: Data Structures

## Key Concepts Demonstrated

- List operations: append, insert, remove, sort, slicing
- Dictionary CRUD operations and iteration
- Set operations: union, intersection, difference, symmetric_difference
- Tuple unpacking and immutability
- List and dictionary comprehensions
- Nested data structure navigation
- Choosing appropriate data structures for use cases

## Common Mistakes to Avoid

- Modifying a list while iterating over it (use a copy or list comprehension)
- Using mutable objects (lists, dicts) as dictionary keys (use tuples instead)
- Forgetting that `dict.keys()`, `dict.values()` are views, not lists
- Assuming dictionary order (guaranteed only in Python 3.7+)
- Using `is` instead of `==` for value comparison

---

## Exercise 1 Solution

```python
numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]

# 1. Sort in ascending order (in-place)
numbers.sort()
print(f"Sorted: {numbers}")  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 2. Find largest and smallest
print(f"Smallest: {min(numbers)}, Largest: {max(numbers)}")  # 1, 9

# 3. Sum and average
total = sum(numbers)
average = total / len(numbers)
print(f"Sum: {total}, Average: {average}")  # 45, 5.0

# 4. Remove all even numbers
numbers = [n for n in numbers if n % 2 != 0]
print(f"Odds only: {numbers}")  # [1, 3, 5, 7, 9]

# 5. Insert 10 at index 3
numbers.insert(3, 10)
print(f"After insert: {numbers}")  # [1, 3, 5, 10, 7, 9]
```

**Alternative for removing evens** (in-place, but iterating backwards):
```python
numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]
for i in range(len(numbers) - 1, -1, -1):
    if numbers[i] % 2 == 0:
        del numbers[i]
```

---

## Exercise 2 Solution

```python
# Initial inventory
inventory = {
    "apples": 50,
    "bananas": 30,
    "oranges": 25,
    "grapes": 40
}

# Add new item
inventory["mangoes"] = 15
print(f"After adding mangoes: {inventory}")

# Update existing item
inventory["bananas"] = 45
print(f"After updating bananas: {inventory}")

# Remove item
del inventory["grapes"]
# Alternative: inventory.pop("grapes")
print(f"After removing grapes: {inventory}")

# Check if item exists
if "cherries" in inventory:
    print(f"cherries: {inventory['cherries']}")
else:
    print("cherries not in inventory")

# Filter items with quantity < 40
low_stock = [(item, qty) for item, qty in inventory.items() if qty < 40]
low_stock_str = ", ".join(f"{item} ({qty})" for item, qty in low_stock)
print(f"Items with quantity < 40: {low_stock_str}")
```

**Output**:
```
After adding mangoes: {'apples': 50, 'bananas': 30, 'oranges': 25, 'grapes': 40, 'mangoes': 15}
After updating bananas: {'apples': 50, 'bananas': 45, 'oranges': 25, 'grapes': 40, 'mangoes': 15}
After removing grapes: {'apples': 50, 'bananas': 45, 'oranges': 25, 'mangoes': 15}
cherries not in inventory
Items with quantity < 40: oranges (25), mangoes (15)
```

---

## Exercise 3 Solution

```python
meeting_a = {"Alice", "Bob", "Charlie", "David", "Eve"}
meeting_b = {"Bob", "David", "Frank", "Grace", "Eve"}

# 1. Both meetings (intersection)
both = meeting_a & meeting_b  # or meeting_a.intersection(meeting_b)
print(f"Attended both: {both}")  # {'Bob', 'David', 'Eve'}

# 2. At least one meeting (union)
at_least_one = meeting_a | meeting_b  # or meeting_a.union(meeting_b)
print(f"Attended at least one: {at_least_one}")

# 3. Only meeting A (difference)
only_a = meeting_a - meeting_b  # or meeting_a.difference(meeting_b)
print(f"Only meeting A: {only_a}")  # {'Alice', 'Charlie'}

# 4. Only meeting B (difference)
only_b = meeting_b - meeting_a
print(f"Only meeting B: {only_b}")  # {'Frank', 'Grace'}

# 5. Exactly one meeting (symmetric difference)
exactly_one = meeting_a ^ meeting_b  # or meeting_a.symmetric_difference(meeting_b)
print(f"Attended exactly one: {exactly_one}")  # {'Alice', 'Charlie', 'Frank', 'Grace'}
```

---

## Exercise 4 Solution

```python
students = [
    ("Alice", 20, 85.5),
    ("Bob", 22, 92.0),
    ("Charlie", 19, 78.5),
    ("David", 21, 88.0),
    ("Eve", 20, 95.5)
]

# 1. Print each student's info using tuple unpacking
print("Student Information:")
for name, age, grade in students:
    print(f"  {name}: Age {age}, Grade {grade}")

# 2. Find student with highest grade
top_student = max(students, key=lambda s: s[2])
print(f"\nTop student: {top_student[0]} with grade {top_student[2]}")

# 3. Calculate average age
total_age = sum(age for name, age, grade in students)
avg_age = total_age / len(students)
print(f"Average age: {avg_age}")  # 20.4

# 4. Create list with only names and grades
names_grades = [(name, grade) for name, age, grade in students]
print(f"Names and grades: {names_grades}")
```

**Output**:
```
Student Information:
  Alice: Age 20, Grade 85.5
  Bob: Age 22, Grade 92.0
  Charlie: Age 19, Grade 78.5
  David: Age 21, Grade 88.0
  Eve: Age 20, Grade 95.5

Top student: Eve with grade 95.5
Average age: 20.4
Names and grades: [('Alice', 85.5), ('Bob', 92.0), ('Charlie', 78.5), ('David', 88.0), ('Eve', 95.5)]
```

---

## Exercise 5 Solution

**a) Basic list comprehension:**
```python
# Original
squares = []
for x in range(1, 11):
    squares.append(x ** 2)

# List comprehension
squares = [x ** 2 for x in range(1, 11)]
print(squares)  # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

**b) With condition:**
```python
# Original
even_squares = []
for x in range(1, 21):
    if x % 2 == 0:
        even_squares.append(x ** 2)

# List comprehension
even_squares = [x ** 2 for x in range(1, 21) if x % 2 == 0]
print(even_squares)  # [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
```

**c) Nested loop:**
```python
# Original
pairs = []
for x in range(1, 4):
    for y in range(1, 4):
        if x != y:
            pairs.append((x, y))

# List comprehension
pairs = [(x, y) for x in range(1, 4) for y in range(1, 4) if x != y]
print(pairs)  # [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]
```

**d) Words with length > 5:**
```python
words = ["hello", "world", "python", "programming"]
long_words = [(word, len(word)) for word in words if len(word) > 5]
print(long_words)  # [('python', 6), ('programming', 11)]
```

---

## Exercise 6 Solution

**a) Numbers to cubes:**
```python
cubes = {n: n ** 3 for n in range(1, 11)}
print(cubes)  # {1: 1, 2: 8, 3: 27, 4: 64, 5: 125, ...}
```

**b) Words to lengths:**
```python
words = ["apple", "banana", "cherry", "date", "elderberry"]
word_lengths = {word: len(word) for word in words}
print(word_lengths)  # {'apple': 5, 'banana': 6, 'cherry': 6, 'date': 4, 'elderberry': 10}
```

**c) Invert dictionary:**
```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)  # {1: 'a', 2: 'b', 3: 'c'}
```

**d) Filter by value:**
```python
scores = {"Alice": 85, "Bob": 42, "Charlie": 91, "David": 38, "Eve": 76}
high_scores = {name: score for name, score in scores.items() if score > 50}
print(high_scores)  # {'Alice': 85, 'Charlie': 91, 'Eve': 76}
```

---

## Exercise 7 Solution

```python
company = {
    "name": "TechCorp",
    "departments": {
        "engineering": {
            "manager": "Alice",
            "employees": ["Bob", "Charlie", "David"],
            "budget": 500000
        },
        "marketing": {
            "manager": "Eve",
            "employees": ["Frank", "Grace"],
            "budget": 300000
        },
        "sales": {
            "manager": "Henry",
            "employees": ["Ivy", "Jack", "Kate", "Leo"],
            "budget": 400000
        }
    },
    "founded": 2015
}

# 1. Company name
print(f"Company: {company['name']}")  # TechCorp

# 2. Engineering manager
eng_manager = company["departments"]["engineering"]["manager"]
print(f"Engineering Manager: {eng_manager}")  # Alice

# 3. Sales employees
sales_employees = company["departments"]["sales"]["employees"]
print(f"Sales employees: {sales_employees}")  # ['Ivy', 'Jack', 'Kate', 'Leo']

# 4. Total budget
total_budget = sum(
    dept["budget"]
    for dept in company["departments"].values()
)
print(f"Total budget: ${total_budget:,}")  # $1,200,000

# 5. Department with most employees
largest_dept = max(
    company["departments"].items(),
    key=lambda x: len(x[1]["employees"])
)
print(f"Largest department: {largest_dept[0]} ({len(largest_dept[1]['employees'])} employees)")
# sales (4 employees)

# 6. Add employee to marketing
company["departments"]["marketing"]["employees"].append("Mike")
print(f"Marketing employees: {company['departments']['marketing']['employees']}")
# ['Frank', 'Grace', 'Mike']

# 7. Flat list of all employees
all_employees = [
    employee
    for dept in company["departments"].values()
    for employee in dept["employees"]
]
print(f"All employees: {all_employees}")
# ['Bob', 'Charlie', 'David', 'Frank', 'Grace', 'Mike', 'Ivy', 'Jack', 'Kate', 'Leo']
```

---

## Exercise 8 Solution

| Scenario | Data Structure | Reasoning |
|----------|----------------|-----------|
| **1. RGB color values** | **Tuple** or **dict** | Tuple `(255, 128, 64)` for immutable ordered values, or dict `{"r": 255, "g": 128, "b": 64}` for named access |
| **2. Unique website visitors** | **Set** | Automatically handles duplicates; O(1) membership testing |
| **3. Shopping cart** | **List** or **dict** | List if order matters and duplicates allowed; dict `{item: quantity}` for item counts |
| **4. Configuration settings** | **Dictionary** | Key-value pairs with descriptive keys; easy lookup and modification |
| **5. GPS coordinates** | **Tuple** | Immutable (shouldn't change); can be used as dict key |
| **6. Function cache** | **Dictionary** | Map inputs (as tuple key) to outputs; O(1) lookup |
| **7. Game queue** | **List** or **collections.deque** | Ordered, supports append/pop; deque better for queue operations |
| **8. Valid word dictionary** | **Set** | O(1) membership testing; only need to know if word exists |

**Key principles for choosing data structures**:
- Need ordering? → List or tuple
- Need uniqueness? → Set
- Need key-value mapping? → Dictionary
- Data shouldn't change? → Tuple or frozenset
- Need fast lookup? → Set or dict (both O(1))

---

## Exercise 9 Solution

```python
import string
from collections import Counter

def word_frequency(text: str, top_n: int = 5) -> list[tuple[str, int]]:
    """
    Count word frequencies and return top N most common words.

    Args:
        text: The input text string.
        top_n: Number of top words to return.

    Returns:
        List of (word, count) tuples, sorted by count descending.
    """
    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Split into words and count
    words = text.split()
    word_counts = Counter(words)

    # Return top N
    return word_counts.most_common(top_n)


text = """
Python is a programming language. Python is easy to learn.
Programming in Python is fun. Python has many libraries.
Learning Python opens many doors. Python is powerful.
"""

result = word_frequency(text, top_n=5)
print(result)
# [('python', 6), ('is', 4), ('programming', 2), ('a', 1), ('language', 1)]

# With top_n=10
result = word_frequency(text, top_n=10)
for word, count in result:
    print(f"  {word}: {count}")
```

**Alternative without Counter:**
```python
def word_frequency_manual(text: str, top_n: int = 5) -> list[tuple[str, int]]:
    """Manual implementation without Counter."""
    text = text.lower()
    for char in string.punctuation:
        text = text.replace(char, "")

    words = text.split()

    # Count manually
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1

    # Sort by count descending
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_words[:top_n]
```

---

## Exercise 10 Solution

```python
def create_matrix(rows: int, cols: int, default: int = 0) -> list[list[int]]:
    """Create a matrix filled with default value."""
    return [[default for _ in range(cols)] for _ in range(rows)]


def matrix_add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    """Add two matrices element-wise."""
    rows = len(a)
    cols = len(a[0])

    # Validate dimensions match
    if len(b) != rows or len(b[0]) != cols:
        raise ValueError("Matrix dimensions must match")

    return [[a[i][j] + b[i][j] for j in range(cols)] for i in range(rows)]


def matrix_transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix (swap rows and columns)."""
    rows = len(matrix)
    cols = len(matrix[0])

    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


def print_matrix(matrix: list[list[int]]) -> None:
    """Print matrix in readable format."""
    for row in matrix:
        print(" ".join(f"{val:2}" for val in row))


# Test the functions
m1 = [[1, 2, 3],
      [4, 5, 6]]

m2 = [[7, 8, 9],
      [10, 11, 12]]

print("Matrix 1:")
print_matrix(m1)

print("\nMatrix 2:")
print_matrix(m2)

print("\nSum:")
print_matrix(matrix_add(m1, m2))

print("\nTranspose of Matrix 1:")
print_matrix(matrix_transpose(m1))

# Extra: Create a 3x3 identity matrix
print("\n3x3 Identity Matrix:")
identity = create_matrix(3, 3)
for i in range(3):
    identity[i][i] = 1
print_matrix(identity)
```

**Output**:
```
Matrix 1:
 1  2  3
 4  5  6

Matrix 2:
 7  8  9
10 11 12

Sum:
 8 10 12
14 16 18

Transpose of Matrix 1:
 1  4
 2  5
 3  6

3x3 Identity Matrix:
 1  0  0
 0  1  0
 0  0  1
```

**Alternative transpose using zip:**
```python
def matrix_transpose_zip(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose using zip (more Pythonic)."""
    return [list(row) for row in zip(*matrix)]
```

---

## Performance Comparison

Understanding when to use each data structure:

```python
import timeit

# Membership testing: set vs list
large_list = list(range(10000))
large_set = set(range(10000))

# List membership: O(n)
list_time = timeit.timeit(lambda: 9999 in large_list, number=1000)

# Set membership: O(1)
set_time = timeit.timeit(lambda: 9999 in large_set, number=1000)

print(f"List membership: {list_time:.4f}s")
print(f"Set membership: {set_time:.4f}s")
print(f"Set is {list_time/set_time:.1f}x faster")
```

---

[← Back to Exercises](../exercises/ex_05_data_structures.md) | [← Back to Chapter](../05_data_structures.md) | [← Back to Module 1](../README.md)
