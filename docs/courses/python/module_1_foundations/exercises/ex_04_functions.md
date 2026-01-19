# Exercises — 04: Functions

## Learning Objectives

After completing these exercises, you will be able to:
- Define and call functions with parameters
- Use default parameter values
- Work with *args and **kwargs
- Write functions that return values
- Understand variable scope
- Write docstrings and use type hints

---

## Exercise 1: Basic Function (Warm-up)

**Bloom Level**: Apply

Write a function `greet(name)` that:
- Takes a name as a parameter
- Returns a greeting string "Hello, {name}!"
- Call it with your name and print the result

```python
# Your function here

print(greet("Alice"))  # Should print: Hello, Alice!
```

---

## Exercise 2: Multiple Parameters (Practice)

**Bloom Level**: Apply

Write a function `calculate_rectangle(length, width)` that:
- Takes length and width as parameters
- Returns a dictionary with keys: "area", "perimeter"
- Include a docstring describing the function

**Example**:
```python
result = calculate_rectangle(5, 3)
print(result)  # {"area": 15, "perimeter": 16}
```

---

## Exercise 3: Default Parameters (Practice)

**Bloom Level**: Apply

Write a function `create_profile(name, age, city="Unknown", occupation="Unspecified")` that:
- Has required parameters `name` and `age`
- Has optional parameters `city` and `occupation` with defaults
- Returns a formatted profile string

**Examples**:
```python
print(create_profile("Alice", 25))
# Alice, 25 years old, from Unknown, works as Unspecified

print(create_profile("Bob", 30, city="Seattle", occupation="Engineer"))
# Bob, 30 years old, from Seattle, works as Engineer
```

---

## Exercise 4: Variable Arguments (Practice)

**Bloom Level**: Apply

Write two functions:

**a)** `average(*numbers)` that:
- Accepts any number of numeric arguments
- Returns their average
- Returns 0 if no arguments provided

```python
print(average(10, 20, 30))  # 20.0
print(average(5))            # 5.0
print(average())             # 0
```

**b)** `build_query(**filters)` that:
- Accepts any number of keyword arguments
- Returns a SQL-like WHERE clause string

```python
print(build_query(name="Alice", age=25, city="Seattle"))
# WHERE name='Alice' AND age='25' AND city='Seattle'
```

---

## Exercise 5: Higher-Order Functions (Practice)

**Bloom Level**: Analyze

Write a function `apply_operation(numbers, operation)` that:
- Takes a list of numbers and a function as parameters
- Applies the function to each number
- Returns a new list with the results

Then create helper functions `double(x)` and `square(x)`.

```python
numbers = [1, 2, 3, 4, 5]

def double(x):
    return x * 2

def square(x):
    return x ** 2

print(apply_operation(numbers, double))  # [2, 4, 6, 8, 10]
print(apply_operation(numbers, square))  # [1, 4, 9, 16, 25]
```

---

## Exercise 6: Scope Investigation (Analyze)

**Bloom Level**: Analyze

Predict the output of this code before running it:

```python
x = 10

def outer():
    x = 20

    def inner():
        x = 30
        print(f"inner: x = {x}")

    inner()
    print(f"outer: x = {x}")

outer()
print(f"global: x = {x}")
```

Then modify the code to make `inner()` modify the `outer()` function's `x` variable (hint: use `nonlocal`).

---

## Exercise 7: Temperature Converter Suite (Challenge)

**Bloom Level**: Create

Create a temperature conversion module with:

1. `celsius_to_fahrenheit(celsius)` - Convert C to F
2. `fahrenheit_to_celsius(fahrenheit)` - Convert F to C
3. `celsius_to_kelvin(celsius)` - Convert C to K
4. `convert_temperature(value, from_unit, to_unit)` - General converter

The general converter should:
- Accept units: "C", "F", "K"
- Raise `ValueError` for invalid units
- Include type hints and docstrings

**Formulas**:
- F = C × 9/5 + 32
- C = (F - 32) × 5/9
- K = C + 273.15

```python
print(convert_temperature(100, "C", "F"))  # 212.0
print(convert_temperature(32, "F", "C"))   # 0.0
print(convert_temperature(0, "C", "K"))    # 273.15
```

---

## Deliverables

Submit your code for all exercises with docstrings and type hints where appropriate.

---

[← Back to Chapter](../04_functions.md) | [View Solutions](../solutions/sol_04_functions.md) | [← Back to Module 1](../README.md)
