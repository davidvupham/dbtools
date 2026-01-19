# Solutions — 01: Introduction to Python

## Key Concepts Demonstrated

- Using `print()` for output
- Variable assignment and naming conventions
- F-string formatting
- Arithmetic operators
- User input with `input()`
- Type conversion with `float()` and `int()`

## Common Mistakes to Avoid

- Forgetting to convert `input()` result to a number before math operations
- Missing the `f` prefix in f-strings: `f"Hello, {name}"` not `"Hello, {name}"`
- Using `+` for string concatenation instead of f-strings (works but less readable)

---

## Exercise 1 Solution

**Explanation**: Simple use of multiple `print()` statements.

```python
# ex1_hello_world.py
print("Hello, World!")
print("Hello, Python!")
print("Hello, Programming!")
```

**Output**:
```
Hello, World!
Hello, Python!
Hello, Programming!
```

**Alternative** - Single print with multiple lines:
```python
print("Hello, World!\nHello, Python!\nHello, Programming!")
```

---

## Exercise 2 Solution

**Explanation**: Variables store data, f-strings format output.

```python
# ex2_introduction.py
name = "Alice"
age = 25
favorite_language = "Python"

print(f"Hi, my name is {name}.")
print(f"I am {age} years old.")
print(f"My favorite programming language is {favorite_language}.")
```

**Output**:
```
Hi, my name is Alice.
I am 25 years old.
My favorite programming language is Python.
```

---

## Exercise 3 Solution

**Explanation**: Demonstrates all basic arithmetic operators.

```python
# ex3_calculator.py
a = 15
b = 4

print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b}")
print(f"{a} // {b} = {a // b}")
print(f"{a} % {b} = {a % b}")
```

**Output**:
```
15 + 4 = 19
15 - 4 = 11
15 * 4 = 60
15 / 4 = 3.75
15 // 4 = 3
15 % 4 = 3
```

**Key Concepts**:
- `/` is float division (always returns a decimal)
- `//` is integer division (rounds down)
- `%` is modulo (returns the remainder)

---

## Exercise 4 Solution

**Explanation**: `input()` returns user input as a string.

```python
# ex4_greeting.py
name = input("What is your name? ")
city = input("What city do you live in? ")

print(f"Hello, {name}! {city} is a great place to live.")
```

**Example Interaction**:
```
What is your name? Alice
What city do you live in? Seattle
Hello, Alice! Seattle is a great place to live.
```

---

## Exercise 5 Solution

**Explanation**: Combines input, type conversion, and formatted output.

```python
# ex5_temperature.py
celsius_str = input("Enter temperature in Celsius: ")
celsius = float(celsius_str)

fahrenheit = (celsius * 9/5) + 32

print(f"{celsius:.1f}°C is equal to {fahrenheit:.1f}°F")
```

**Example Interaction**:
```
Enter temperature in Celsius: 25
25.0°C is equal to 77.0°F
```

**Key Concepts**:
- `float()` converts string to decimal number
- `:.1f` formats to 1 decimal place
- The formula `F = (C × 9/5) + 32` converts Celsius to Fahrenheit

**Alternative** - More concise:
```python
celsius = float(input("Enter temperature in Celsius: "))
fahrenheit = (celsius * 9/5) + 32
print(f"{celsius:.1f}°C is equal to {fahrenheit:.1f}°F")
```

---

## Exercise 6 Solution

**Explanation**: This code swaps the values of `x` and `y` without using a temporary variable.

**Step-by-step trace**:

```python
x = 5
y = 3
print(f"x = {x}, y = {y}")   # x = 5, y = 3

x = x + y      # x = 5 + 3 = 8
print(f"x = {x}, y = {y}")   # x = 8, y = 3

y = x - y      # y = 8 - 3 = 5
print(f"x = {x}, y = {y}")   # x = 8, y = 5

x = x - y      # x = 8 - 5 = 3
print(f"x = {x}, y = {y}")   # x = 3, y = 5
```

**Output**:
```
x = 5, y = 3
x = 8, y = 3
x = 8, y = 5
x = 3, y = 5
```

**Answers**:
1. Final values: `x = 3`, `y = 5`
2. This code **swaps the values** of `x` and `y`. The initial values were `x = 5` and `y = 3`; after execution, `x = 3` and `y = 5`.

**Pythonic alternative** - Python allows tuple unpacking for swaps:
```python
x = 5
y = 3
x, y = y, x  # Swap in one line!
print(f"x = {x}, y = {y}")  # x = 3, y = 5
```

---

## Alternative Approaches

### F-strings vs concatenation vs format()

```python
name = "Alice"
age = 25

# F-string (recommended)
print(f"Hello, {name}! You are {age}.")

# Concatenation (verbose)
print("Hello, " + name + "! You are " + str(age) + ".")

# format() method (older style)
print("Hello, {}! You are {}.".format(name, age))

# % formatting (very old style)
print("Hello, %s! You are %d." % (name, age))
```

F-strings are the most readable and the recommended approach in modern Python.

---

[← Back to Exercises](../exercises/ex_01_intro.md) | [← Back to Chapter](../01_intro.md) | [← Back to Module 1](../README.md)
