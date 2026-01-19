# Exercises — 01: Introduction to Python

## Learning Objectives

After completing these exercises, you will be able to:
- Write and run Python programs
- Use `print()` to display output
- Create and use variables
- Format strings using f-strings
- Get user input with `input()`

---

## Exercise 1: Hello World Variations (Warm-up)

**Bloom Level**: Remember

Write a Python script that prints the following output exactly:

```
Hello, World!
Hello, Python!
Hello, Programming!
```

**Hint**: Use three `print()` statements.

---

## Exercise 2: Personal Introduction (Practice)

**Bloom Level**: Apply

Create a program that:
1. Stores your name in a variable called `name`
2. Stores your age in a variable called `age`
3. Stores your favorite programming language in a variable called `favorite_language`
4. Prints a formatted introduction using f-strings

**Expected Output** (example):
```
Hi, my name is Alice.
I am 25 years old.
My favorite programming language is Python.
```

---

## Exercise 3: Simple Calculator (Practice)

**Bloom Level**: Apply

Write a program that:
1. Defines two variables: `a = 15` and `b = 4`
2. Prints the result of:
   - Addition (`a + b`)
   - Subtraction (`a - b`)
   - Multiplication (`a * b`)
   - Division (`a / b`)
   - Integer division (`a // b`)
   - Modulo/remainder (`a % b`)

**Expected Output**:
```
15 + 4 = 19
15 - 4 = 11
15 * 4 = 60
15 / 4 = 3.75
15 // 4 = 3
15 % 4 = 3
```

---

## Exercise 4: Interactive Greeting (Practice)

**Bloom Level**: Apply

Create an interactive program that:
1. Asks the user for their name using `input()`
2. Asks the user for their city using `input()`
3. Prints a personalized greeting

**Example Interaction**:
```
What is your name? Alice
What city do you live in? Seattle
Hello, Alice! Seattle is a great place to live.
```

---

## Exercise 5: Temperature Converter (Challenge)

**Bloom Level**: Analyze/Create

Build a temperature converter that:
1. Asks the user to enter a temperature in Celsius
2. Converts it to Fahrenheit using the formula: `F = (C × 9/5) + 32`
3. Displays both temperatures formatted to 1 decimal place

**Example Interaction**:
```
Enter temperature in Celsius: 25
25.0°C is equal to 77.0°F
```

**Hint**: Remember that `input()` returns a string. You'll need to convert it to a number using `float()`.

---

## Exercise 6: Code Tracing (Analyze)

**Bloom Level**: Understand

What does the following code print? Write your answer before running it.

```python
x = 5
y = 3
print(f"x = {x}, y = {y}")

x = x + y
print(f"x = {x}, y = {y}")

y = x - y
print(f"x = {x}, y = {y}")

x = x - y
print(f"x = {x}, y = {y}")
```

**Questions**:
1. What are the final values of `x` and `y`?
2. What does this code accomplish? (Hint: Look at the initial and final values)

---

## Deliverables

Submit your code for exercises 1-5. For exercise 6, submit your predicted output and answers to the questions.

---

[← Back to Chapter](../01_intro.md) | [View Solutions](../solutions/sol_01_intro.md) | [← Back to Module 1](../README.md)
