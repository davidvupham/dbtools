# Exercises — 05: Data Structures

## Learning Objectives

After completing these exercises, you will be able to:
- Create and manipulate lists, tuples, sets, and dictionaries
- Choose the right data structure for different use cases
- Use list comprehensions and dictionary comprehensions
- Work with nested data structures
- Apply common data structure operations

---

## Exercise 1: List Operations (Warm-up)

**Bloom Level**: Apply

Given the following list of numbers, perform these operations:

```python
numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]
```

1. Sort the list in ascending order (in-place)
2. Find and print the largest and smallest values
3. Calculate the sum and average
4. Remove all even numbers
5. Insert the value `10` at index 3

Print the list after each operation.

---

## Exercise 2: Dictionary Manipulation (Practice)

**Bloom Level**: Apply

Create a program that manages a simple inventory system:

1. Create a dictionary with these items and quantities:
   - "apples": 50
   - "bananas": 30
   - "oranges": 25
   - "grapes": 40

2. Implement these operations:
   - Add a new item "mangoes" with quantity 15
   - Update "bananas" to 45
   - Remove "grapes" from inventory
   - Check if "cherries" exists (print appropriate message)
   - Print all items with quantity less than 40

**Expected Output**:
```
Inventory after adding mangoes: {'apples': 50, 'bananas': 30, 'oranges': 25, 'grapes': 40, 'mangoes': 15}
Inventory after updating bananas: {'apples': 50, 'bananas': 45, 'oranges': 25, 'grapes': 40, 'mangoes': 15}
Inventory after removing grapes: {'apples': 50, 'bananas': 45, 'oranges': 25, 'mangoes': 15}
cherries not in inventory
Items with quantity < 40: oranges (25), mangoes (15)
```

---

## Exercise 3: Set Operations (Practice)

**Bloom Level**: Apply

You have attendance records for two different meetings:

```python
meeting_a = {"Alice", "Bob", "Charlie", "David", "Eve"}
meeting_b = {"Bob", "David", "Frank", "Grace", "Eve"}
```

Using set operations, find:
1. People who attended both meetings (intersection)
2. People who attended at least one meeting (union)
3. People who attended only meeting A (difference)
4. People who attended only meeting B (difference)
5. People who attended exactly one meeting (symmetric difference)

---

## Exercise 4: Tuple Unpacking (Practice)

**Bloom Level**: Apply

Given a list of tuples representing student records (name, age, grade):

```python
students = [
    ("Alice", 20, 85.5),
    ("Bob", 22, 92.0),
    ("Charlie", 19, 78.5),
    ("David", 21, 88.0),
    ("Eve", 20, 95.5)
]
```

1. Use tuple unpacking to iterate and print each student's info
2. Find the student with the highest grade
3. Calculate the average age
4. Create a new list with only names and grades (no age)

**Hint**: Use tuple unpacking in your for loops: `for name, age, grade in students:`

---

## Exercise 5: List Comprehensions (Practice)

**Bloom Level**: Apply

Rewrite each of the following using list comprehensions:

**a)** Convert this loop to a list comprehension:
```python
squares = []
for x in range(1, 11):
    squares.append(x ** 2)
```

**b)** Convert this loop with a condition:
```python
even_squares = []
for x in range(1, 21):
    if x % 2 == 0:
        even_squares.append(x ** 2)
```

**c)** Convert this nested loop:
```python
pairs = []
for x in range(1, 4):
    for y in range(1, 4):
        if x != y:
            pairs.append((x, y))
```

**d)** Create a list comprehension that:
- Takes a list of words: `["hello", "world", "python", "programming"]`
- Returns a list of tuples: `(word, length)` for words longer than 5 characters

---

## Exercise 6: Dictionary Comprehensions (Practice)

**Bloom Level**: Apply

**a)** Create a dictionary where keys are numbers 1-10 and values are their cubes:
```python
# Expected: {1: 1, 2: 8, 3: 27, 4: 64, ...}
```

**b)** Given a list of words, create a dictionary mapping each word to its length:
```python
words = ["apple", "banana", "cherry", "date", "elderberry"]
# Expected: {"apple": 5, "banana": 6, "cherry": 6, "date": 4, "elderberry": 10}
```

**c)** Invert a dictionary (swap keys and values):
```python
original = {"a": 1, "b": 2, "c": 3}
# Expected: {1: "a", 2: "b", 3: "c"}
```

**d)** Filter a dictionary to include only items where the value is greater than 50:
```python
scores = {"Alice": 85, "Bob": 42, "Charlie": 91, "David": 38, "Eve": 76}
# Expected: {"Alice": 85, "Charlie": 91, "Eve": 76}
```

---

## Exercise 7: Nested Data Structures (Analyze)

**Bloom Level**: Analyze

Given this nested data structure representing a company:

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
```

Write code to:
1. Print the company name
2. Print the engineering department's manager
3. Print all employees in the sales department
4. Calculate the total budget across all departments
5. Find the department with the most employees
6. Add a new employee "Mike" to the marketing department
7. Create a flat list of all employees across all departments

---

## Exercise 8: Choosing Data Structures (Evaluate)

**Bloom Level**: Evaluate

For each scenario below, choose the most appropriate data structure (list, tuple, set, or dictionary) and explain why:

1. **Storing RGB color values** (e.g., red=255, green=128, blue=64)

2. **Tracking unique visitors to a website**

3. **Maintaining a shopping cart where items can be added/removed**

4. **Storing configuration settings** (e.g., {"debug": True, "timeout": 30})

5. **Recording GPS coordinates** (latitude, longitude) that shouldn't change

6. **Implementing a simple cache for function results**

7. **Storing the order of players in a game queue**

8. **Checking if a word is in a dictionary of valid words** (performance matters)

---

## Exercise 9: Word Frequency Counter (Challenge)

**Bloom Level**: Create

Write a program that:
1. Takes a text string as input
2. Counts the frequency of each word (case-insensitive)
3. Ignores punctuation
4. Returns the top N most common words

```python
text = """
Python is a programming language. Python is easy to learn.
Programming in Python is fun. Python has many libraries.
Learning Python opens many doors. Python is powerful.
"""

def word_frequency(text: str, top_n: int = 5) -> list[tuple[str, int]]:
    """
    Count word frequencies and return top N most common words.

    Args:
        text: The input text string.
        top_n: Number of top words to return.

    Returns:
        List of (word, count) tuples, sorted by count descending.
    """
    # Your implementation here
    pass

# Expected output for top_n=5:
# [('python', 6), ('is', 4), ('programming', 2), ('a', 1), ('language', 1)]
```

**Hint**: Use `str.lower()`, `str.split()`, and consider using `collections.Counter`.

---

## Exercise 10: Matrix Operations (Challenge)

**Bloom Level**: Create

Implement basic matrix operations using nested lists:

```python
def create_matrix(rows: int, cols: int, default: int = 0) -> list[list[int]]:
    """Create a matrix filled with default value."""
    pass

def matrix_add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    """Add two matrices element-wise."""
    pass

def matrix_transpose(matrix: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix (swap rows and columns)."""
    pass

def print_matrix(matrix: list[list[int]]) -> None:
    """Print matrix in readable format."""
    pass

# Test your functions:
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
```

**Expected Output**:
```
Matrix 1:
1  2  3
4  5  6

Matrix 2:
7  8   9
10 11 12

Sum:
8  10 12
14 16 18

Transpose of Matrix 1:
1 4
2 5
3 6
```

---

## Deliverables

Submit your code for all exercises. For Exercise 8, include written explanations for each choice.

---

[← Back to Chapter](../05_data_structures.md) | [View Solutions](../solutions/sol_05_data_structures.md) | [← Back to Module 1](../README.md)
