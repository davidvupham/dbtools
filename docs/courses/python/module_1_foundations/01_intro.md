# Introduction to Python

Python is one of the most popular programming languages in the world, known for its readability, versatility, and gentle learning curve. This chapter introduces Python and gets you writing your first programs.

## What is Python?

Python is a **high-level programming language** created by Guido van Rossum and first released in 1991. It emphasizes code readability and allows you to express concepts in fewer lines of code than languages like Java or C++.

**Key characteristics**:
- **Interpreted**: Code runs directly without compilation
- **Dynamically typed**: No need to declare variable types
- **Multi-paradigm**: Supports procedural, object-oriented, and functional programming
- **Batteries included**: Rich standard library for common tasks

## Why Python?

### Readable syntax

Python code reads almost like English:

```python
# Python
if user_is_authenticated:
    print("Welcome back!")
```

Compare to Java:

```java
// Java
if (userIsAuthenticated) {
    System.out.println("Welcome back!");
}
```

Python eliminates boilerplate like curly braces and semicolons, letting you focus on the logic.

### Versatility

Python excels in many domains:

| Domain | Popular Libraries |
|--------|-------------------|
| Web development | Django, FastAPI, Flask |
| Data science | Pandas, NumPy, Scikit-learn |
| Machine learning | TensorFlow, PyTorch |
| Automation | Selenium, Playwright |
| DevOps | Ansible, Fabric |

### Strong community

- Extensive documentation
- Millions of packages on PyPI
- Active Stack Overflow community
- Regular releases with improvements

## Setting up Python

### Checking your installation

Open a terminal and run:

```bash
python --version
# or
python3 --version
```

You should see something like `Python 3.11.5` or higher.

### The Python REPL

The REPL (Read-Eval-Print Loop) lets you run Python interactively:

```bash
$ python
Python 3.11.5 (main, Sep 11 2023, 08:31:25)
>>> 2 + 2
4
>>> print("Hello!")
Hello!
>>> exit()
```

The `>>>` prompt indicates Python is waiting for input. Type `exit()` or press Ctrl+D to quit.

### Running Python files

Save your code in a file with the `.py` extension:

```python
# hello.py
print("Hello from a file!")
```

Run it:

```bash
python hello.py
# Output: Hello from a file!
```

## Your first Python program

Let's write a simple program that demonstrates Python's core concepts:

```python
# my_first_program.py

# This is a comment - Python ignores lines starting with #
# Comments explain what code does to other developers (and future you!)

# Print text to the screen
print("Hello, World!")

# Store data in a variable (no type declaration needed)
name = "Alice"
age = 25

# Use f-strings for formatted output
print(f"My name is {name} and I am {age} years old.")

# Simple math
x = 10
y = 3
print(f"{x} + {y} = {x + y}")
print(f"{x} * {y} = {x * y}")
print(f"{x} / {y} = {x / y}")    # Float division
print(f"{x} // {y} = {x // y}")  # Integer division

# Get user input
user_name = input("What's your name? ")
print(f"Nice to meet you, {user_name}!")
```

**Running the program**:

```bash
$ python my_first_program.py
Hello, World!
My name is Alice and I am 25 years old.
10 + 3 = 13
10 * 3 = 30
10 / 3 = 3.3333333333333335
10 // 3 = 3
What's your name? Bob
Nice to meet you, Bob!
```

## Key concepts

### Comments

Comments explain your code and are ignored by Python:

```python
# This is a single-line comment

"""
This is a multi-line comment (docstring).
It can span multiple lines.
Often used to document functions and classes.
"""
```

### The print function

`print()` displays output to the console:

```python
print("Hello")                    # Simple string
print("Hello", "World")           # Multiple arguments (space-separated)
print("Hello", "World", sep="-")  # Custom separator: Hello-World
print("Line 1", end=" ")          # Custom line ending (default is \n)
print("Line 2")                   # Output: Line 1 Line 2
```

### Variables

Variables store data for later use:

```python
message = "Hello"        # Create a variable
print(message)           # Use the variable
message = "Goodbye"      # Reassign (change the value)
print(message)           # Output: Goodbye
```

Variable naming rules:
- Must start with a letter or underscore
- Can contain letters, numbers, and underscores
- Case-sensitive (`name` and `Name` are different)
- Cannot be a reserved keyword (`if`, `for`, `class`, etc.)

**Convention**: Use `snake_case` for variable names:

```python
# Good
user_name = "Alice"
total_count = 42
is_valid = True

# Bad (but valid)
userName = "Alice"    # camelCase (used in Java/JavaScript)
TotalCount = 42       # PascalCase (used for classes)
```

### F-strings (formatted strings)

F-strings let you embed expressions in strings:

```python
name = "Alice"
age = 25

# Basic usage
print(f"Hello, {name}!")

# Expressions in braces
print(f"Next year, {name} will be {age + 1}")

# Formatting numbers
pi = 3.14159
print(f"Pi is approximately {pi:.2f}")  # 2 decimal places: 3.14

price = 1234.5
print(f"Price: ${price:,.2f}")  # With comma: $1,234.50

# Padding and alignment
print(f"{'left':<10}")   # Left align:  "left      "
print(f"{'right':>10}")  # Right align: "     right"
print(f"{'center':^10}") # Center:      "  center  "
```

### Getting user input

The `input()` function reads text from the user:

```python
name = input("Enter your name: ")
print(f"Hello, {name}!")

# input() always returns a string
age_str = input("Enter your age: ")
age = int(age_str)  # Convert to integer
print(f"In 10 years, you'll be {age + 10}")
```

## Python philosophy

Python has a set of guiding principles called "The Zen of Python." You can view them by typing:

```python
>>> import this
```

Key principles:

> **Beautiful is better than ugly.**
> Write clean, readable code.

> **Explicit is better than implicit.**
> Make your intentions clear.

> **Simple is better than complex.**
> Choose straightforward solutions.

> **Readability counts.**
> Code is read more often than it's written.

## Example from our code

From the dbtools codebase, here's how a simple script might look:

```python
# scripts/check_connection.py
"""Script to verify database connectivity."""

import sys

def main():
    """Entry point for the connection checker."""
    print("Database Connection Checker")
    print("-" * 30)

    db_host = input("Enter database host: ")
    db_port = input("Enter port (default 5432): ") or "5432"

    print(f"\nAttempting connection to {db_host}:{db_port}...")

    # Connection logic would go here
    print("Connection successful!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Why this design?**
- Docstrings explain what the script and function do
- `main()` function keeps code organized
- `if __name__ == "__main__"` lets the file be imported without running
- `sys.exit()` returns a status code to the shell

## Best practices summary

1. **Use meaningful variable names**: `user_count` not `x`
2. **Add comments for non-obvious code**: Explain *why*, not *what*
3. **Use f-strings for formatting**: Cleaner than concatenation
4. **Follow PEP 8 style guide**: Consistent formatting
5. **Keep lines under 80-120 characters**: Improves readability
6. **Use snake_case for variables and functions**: Python convention

---

[← Back to Module 1](./README.md) | [Next: Variables and Data Types →](./02_variables.md)
