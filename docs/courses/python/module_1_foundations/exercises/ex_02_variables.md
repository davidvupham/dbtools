# Exercises — 02: Variables and Data Types

## Learning Objectives

After completing these exercises, you will be able to:
- Create variables of different types (str, int, float, bool, None)
- Use `type()` to check variable types
- Understand mutability and references
- Use `is` vs `==` correctly
- Work with None values

---

## Exercise 1: Type Detective (Warm-up)

**Bloom Level**: Remember

For each value, predict its type, then verify using `type()`:

```python
a = 42
b = 3.14
c = "Hello"
d = True
e = None
f = [1, 2, 3]
g = {"name": "Alice"}
```

Write a program that prints each variable and its type:
```
a = 42, type: <class 'int'>
b = 3.14, type: <class 'float'>
...
```

---

## Exercise 2: Type Conversion (Practice)

**Bloom Level**: Apply

Write a program that:
1. Creates a string `num_str = "42"`
2. Converts it to an integer and stores in `num_int`
3. Converts it to a float and stores in `num_float`
4. Creates a float `pi = 3.14159`
5. Converts `pi` to an integer (note what happens to the decimal)
6. Converts `num_int` to a string

Print each result with its type.

**Expected Output**:
```
num_str = '42', type: str
num_int = 42, type: int
num_float = 42.0, type: float
pi = 3.14159, type: float
pi_int = 3, type: int
num_str_again = '42', type: str
```

---

## Exercise 3: Reference vs Value (Practice)

**Bloom Level**: Analyze

Predict the output of this code, then run it to verify:

```python
# Part 1: Integers
x = 10
y = x
x = 20
print(f"x = {x}, y = {y}")

# Part 2: Lists
a = [1, 2, 3]
b = a
a.append(4)
print(f"a = {a}, b = {b}")

# Part 3: Lists with copy
c = [1, 2, 3]
d = c.copy()
c.append(4)
print(f"c = {c}, d = {d}")
```

**Questions**:
1. Why does changing `x` not affect `y`?
2. Why does modifying `a` also change `b`?
3. Why does modifying `c` not affect `d`?

---

## Exercise 4: Identity vs Equality (Practice)

**Bloom Level**: Analyze

Predict whether each comparison is `True` or `False`:

```python
# Equality (==)
print([1, 2] == [1, 2])
print("hello" == "hello")
print(1 == 1.0)
print(None == False)

# Identity (is)
a = [1, 2]
b = [1, 2]
c = a

print(a is b)
print(a is c)
print(a == b)

# Special cases
print(None is None)
print(True is True)
```

---

## Exercise 5: Working with None (Practice)

**Bloom Level**: Apply

Create a function simulation (using just variables and conditionals) that:
1. Starts with `result = None`
2. Asks the user for a number
3. If the number is positive, set `result` to `"positive"`
4. If the number is negative, set `result` to `"negative"`
5. If the number is zero, leave `result` as `None`
6. Print whether `result` is None or has a value

**Example Interactions**:
```
Enter a number: 5
Result: positive

Enter a number: -3
Result: negative

Enter a number: 0
No result (value is None)
```

---

## Exercise 6: Build a User Profile (Challenge)

**Bloom Level**: Create

Create a program that builds a user profile dictionary:
1. Ask for the user's name (string)
2. Ask for their age (integer)
3. Ask for their height in meters (float)
4. Ask if they are a student (yes/no → boolean)
5. Store all values in appropriate types
6. Print the profile with each value's type

**Example Interaction**:
```
Enter your name: Alice
Enter your age: 25
Enter your height in meters: 1.65
Are you a student? (yes/no): yes

=== User Profile ===
Name: Alice (str)
Age: 25 (int)
Height: 1.65 (float)
Student: True (bool)
```

---

## Deliverables

Submit your code for all exercises. For exercises 3 and 4, include your predictions before running the code.

---

[← Back to Chapter](../02_variables.md) | [View Solutions](../solutions/sol_02_variables.md) | [← Back to Module 1](../README.md)
