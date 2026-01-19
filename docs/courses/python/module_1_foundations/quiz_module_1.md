# Module 1 Quiz: Python Foundations

Test your understanding of Python basics: variables, data types, control flow, functions, data structures, file handling, error handling, and type hints.

**Instructions**:
- 15 questions, approximately 20 minutes
- Mix of conceptual and code-based questions
- Check your answers at the end
- Target: 80% (12/15) before proceeding to Module 2

---

## Section 1: Conceptual Questions (6 questions)

### Question 1

What is the correct way to check if a variable is `None`?

a) `if x == None:`
b) `if x is None:`
c) `if x = None:`
d) `if None(x):`

### Question 2

Which of the following is a mutable data type in Python?

a) `int`
b) `str`
c) `tuple`
d) `list`

### Question 3

What does the `//` operator do in Python?

a) Floating-point division
b) Integer (floor) division
c) Modulo (remainder)
d) Exponentiation

### Question 4

Which statement about Python functions is TRUE?

a) Functions must always return a value
b) Functions can only have one return statement
c) Default parameter values must come after required parameters
d) Functions cannot call other functions

### Question 5

What is the purpose of the `try-except` block?

a) To repeat code multiple times
b) To handle errors without crashing the program
c) To define a function
d) To create a loop

### Question 6

What does the type hint `Optional[str]` mean?

a) The parameter is optional and can be omitted
b) The value can be either `str` or `None`
c) The string is optional in the output
d) The function may or may not return a string

---

## Section 2: Code Reading (5 questions)

### Question 7

What is the output of this code?

```python
x = [1, 2, 3]
y = x
y.append(4)
print(len(x))
```

a) `3`
b) `4`
c) `7`
d) Error

### Question 8

What is the output of this code?

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))
print(greet("Bob", "Hi"))
```

a)
```
Hello, Alice!
Hi, Bob!
```

b)
```
Alice, Hello!
Bob, Hi!
```

c)
```
Hello Alice!
Hi Bob!
```

d) Error - missing argument

### Question 9

What is the output of this code?

```python
numbers = [1, 2, 3, 4, 5]
result = [x * 2 for x in numbers if x % 2 == 0]
print(result)
```

a) `[2, 4, 6, 8, 10]`
b) `[4, 8]`
c) `[1, 2, 3, 4, 5]`
d) `[2, 4]`

### Question 10

What is the output of this code?

```python
try:
    x = int("hello")
    print("Success")
except ValueError:
    print("Error A")
except TypeError:
    print("Error B")
else:
    print("No error")
finally:
    print("Done")
```

a)
```
Success
Done
```

b)
```
Error A
Done
```

c)
```
Error B
Done
```

d)
```
Error A
No error
Done
```

### Question 11

What is the output of this code?

```python
data = {"a": 1, "b": 2, "c": 3}
print(data.get("d", 0))
```

a) `None`
b) `0`
c) `"d"`
d) KeyError

---

## Section 3: Problem Solving (4 questions)

### Question 12

Which code correctly reads a file line by line?

a)
```python
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())
```

b)
```python
f = open("file.txt", "r")
for line in f:
    print(line.strip())
```

c)
```python
with open("file.txt", "r") as f:
    lines = f.read()
    for line in lines:
        print(line)
```

d)
```python
file = open("file.txt")
print(file.lines())
```

### Question 13

Which function correctly calculates the factorial of a number?

a)
```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

b)
```python
def factorial(n):
    return n * factorial(n - 1)
```

c)
```python
def factorial(n):
    if n == 0:
        return 0
    return n * factorial(n - 1)
```

d)
```python
def factorial(n):
    result = 1
    for i in range(n):
        result = result * i
    return result
```

### Question 14

What is wrong with this code?

```python
def divide(a: int, b: int) -> float:
    return a / b

result = divide(10, 0)
print(result)
```

a) Type hints are incorrect
b) Division by zero will raise an error
c) The function should return `int`, not `float`
d) Nothing is wrong

### Question 15

Which code correctly creates a dictionary from two lists?

```python
keys = ["a", "b", "c"]
values = [1, 2, 3]
```

a) `dict(keys, values)`
b) `{keys: values}`
c) `dict(zip(keys, values))`
d) `dict([keys, values])`

---

## Answers

<details>
<summary>Click to reveal answers and explanations</summary>

### Question 1: **b**
Use `is` to check for `None`, not `==`. `is` checks identity, which is the correct way to compare with singleton objects like `None`.

### Question 2: **d**
Lists are mutable (can be changed after creation). Integers, strings, and tuples are immutable.

### Question 3: **b**
`//` performs integer (floor) division, rounding down to the nearest integer. `%` is modulo, `/` is float division, `**` is exponentiation.

### Question 4: **c**
In Python function definitions, parameters with default values must come after parameters without defaults. Functions don't require return statements (they return `None` by default), can have multiple returns, and can call other functions.

### Question 5: **b**
`try-except` blocks handle exceptions (errors) gracefully, allowing the program to continue running instead of crashing.

### Question 6: **b**
`Optional[str]` from the `typing` module means the value can be either a `str` or `None`. It's equivalent to `str | None` in Python 3.10+.

### Question 7: **b**
Output is `4`. When `y = x` with a list, both variables reference the same list object. Modifying through `y` also affects `x`.

### Question 8: **a**
```
Hello, Alice!
Hi, Bob!
```
The first call uses the default greeting "Hello". The second call overrides it with "Hi".

### Question 9: **b**
Output is `[4, 8]`. The list comprehension filters for even numbers (`x % 2 == 0`), which are 2 and 4, then multiplies by 2.

### Question 10: **b**
```
Error A
Done
```
`int("hello")` raises `ValueError`. The `else` block only runs if no exception occurs. `finally` always runs.

### Question 11: **b**
Output is `0`. The `get()` method returns the default value (second argument) if the key doesn't exist, instead of raising `KeyError`.

### Question 12: **a**
Option a) is correct and best practice. It uses a context manager (`with`) which ensures the file is properly closed, and iterates line by line efficiently. Option b) works but doesn't close the file properly.

### Question 13: **a**
Option a) is the correct recursive factorial:
- Base case: `factorial(0) = 1`
- Recursive case: `n * factorial(n-1)`

Option b) has no base case (infinite recursion). Option c) returns 0 for base case (wrong). Option d) starts loop at 0, multiplying by 0.

### Question 14: **b**
Division by zero will raise a `ZeroDivisionError`. The function should validate input or handle the exception.

### Question 15: **c**
`dict(zip(keys, values))` creates `{"a": 1, "b": 2, "c": 3}`. `zip()` pairs elements from both lists, and `dict()` converts those pairs to a dictionary.

---

### Score Interpretation

- **13-15 correct**: Excellent! You have a solid foundation. Proceed to Module 2.
- **10-12 correct**: Good understanding. Review the topics you missed before continuing.
- **7-9 correct**: Fair. Re-read the relevant chapters and redo the exercises.
- **Below 7**: Review Module 1 thoroughly before attempting Module 2.

</details>

---

[← Back to Module 1](./README.md) | [Proceed to Module 2 →](../module_2_intermediate/README.md)
