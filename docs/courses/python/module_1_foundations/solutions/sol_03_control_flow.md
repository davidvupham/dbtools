# Solutions — 03: Control Flow

## Key Concepts Demonstrated

- Conditional branching with `if/elif/else`
- `for` loops with `range()` and iterables
- `while` loops for unknown iteration counts
- Loop control with `break` and `continue`
- Pattern matching with `match` (Python 3.10+)

## Common Mistakes to Avoid

- Using `=` (assignment) instead of `==` (comparison) in conditions
- Off-by-one errors with `range()` (it excludes the end value)
- Infinite loops - ensure `while` condition eventually becomes `False`
- Forgetting `break` after handling each case in older `if/elif` chains

---

## Exercise 1 Solution

**Explanation**: Use `elif` for mutually exclusive conditions.

```python
# ex1_grade_calculator.py
grade = float(input("Enter your grade: "))

if grade >= 90:
    letter = "A"
elif grade >= 80:
    letter = "B"
elif grade >= 70:
    letter = "C"
elif grade >= 60:
    letter = "D"
else:
    letter = "F"

print(f"Your letter grade is: {letter}")
```

**Alternative** - Using match (Python 3.10+):

```python
grade = int(input("Enter your grade: "))

match grade // 10:
    case 10 | 9:
        letter = "A"
    case 8:
        letter = "B"
    case 7:
        letter = "C"
    case 6:
        letter = "D"
    case _:
        letter = "F"

print(f"Your letter grade is: {letter}")
```

---

## Exercise 2 Solution

**Explanation**: Check divisibility with `%` (modulo). Order matters - check "both" first.

```python
# ex2_fizzbuzz.py
for i in range(1, 31):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

**Alternative** - Building the string:

```python
for i in range(1, 31):
    output = ""
    if i % 3 == 0:
        output += "Fizz"
    if i % 5 == 0:
        output += "Buzz"
    print(output or i)
```

---

## Exercise 3 Solution

**Explanation**: `while True` with `break` handles unknown iteration counts.

```python
# ex3_sum_calculator.py
total = 0.0

while True:
    user_input = input("Enter a number (or 'done' to finish): ")

    if user_input.lower() == "done":
        break

    try:
        number = float(user_input)
        total += number
    except ValueError:
        print("Invalid number, please try again.")

print(f"Total: {total}")
```

**Alternative** - Using walrus operator (Python 3.8+):

```python
total = 0.0
while (user_input := input("Enter a number (or 'done'): ")).lower() != "done":
    try:
        total += float(user_input)
    except ValueError:
        print("Invalid number, please try again.")
print(f"Total: {total}")
```

---

## Exercise 4 Solution

**Explanation**: A number is prime if it has no divisors other than 1 and itself.

```python
# ex4_prime_checker.py
def is_prime(n: int) -> bool:
    """Check if n is a prime number."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Only check odd divisors up to sqrt(n)
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

# Find all primes between 1 and 50
primes = [n for n in range(1, 51) if is_prime(n)]
print("Prime numbers between 1 and 50:")
print(", ".join(map(str, primes)))
```

**Output**:
```
Prime numbers between 1 and 50:
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47
```

**Why check up to sqrt(n)?**
If `n = a × b`, then at least one of `a` or `b` is ≤ √n. So if we haven't found a divisor by √n, we won't find one.

---

## Exercise 5 Solution

**Explanation**: Combine `while`, conditionals, and counter variable.

```python
# ex5_guessing_game.py
import random

secret = random.randint(1, 100)
guesses = 0

print("I'm thinking of a number between 1 and 100.")

while True:
    try:
        guess = int(input("Your guess: "))
        guesses += 1

        if guess < secret:
            print("Too low!")
        elif guess > secret:
            print("Too high!")
        else:
            print(f"Correct! You got it in {guesses} guesses.")
            break

    except ValueError:
        print("Please enter a valid number.")
```

**Enhanced version** with hints:

```python
import random

secret = random.randint(1, 100)
guesses = 0
max_guesses = 7

print(f"I'm thinking of a number between 1 and 100.")
print(f"You have {max_guesses} guesses.")

while guesses < max_guesses:
    try:
        guess = int(input("Your guess: "))
        guesses += 1

        diff = abs(secret - guess)

        if guess == secret:
            print(f"Correct! You got it in {guesses} guesses.")
            break
        elif guess < secret:
            hint = "Very close!" if diff <= 5 else "Too low!"
        else:
            hint = "Very close!" if diff <= 5 else "Too high!"

        remaining = max_guesses - guesses
        print(f"{hint} ({remaining} guesses left)")

    except ValueError:
        print("Please enter a valid number.")
else:
    print(f"Game over! The number was {secret}.")
```

---

## Exercise 6 Solution

**Explanation**: `match` provides clean pattern matching (Python 3.10+).

```python
# ex6_command_processor.py
def process_command(command: str) -> str:
    """Process a command and return the response."""
    match command.lower().strip():
        case "quit" | "exit":
            return "Goodbye!"
        case "help":
            return "Available commands: quit, help, status, version"
        case "status":
            return "All systems operational"
        case "version":
            return "Version 1.0.0"
        case _:
            return f"Unknown command: {command}"

# Interactive loop
while True:
    command = input("Enter command: ")
    response = process_command(command)
    print(response)

    if command.lower() in ("quit", "exit"):
        break
```

**Pre-3.10 version** (using if/elif):

```python
def process_command(command: str) -> str:
    cmd = command.lower().strip()

    if cmd in ("quit", "exit"):
        return "Goodbye!"
    elif cmd == "help":
        return "Available commands: quit, help, status, version"
    elif cmd == "status":
        return "All systems operational"
    elif cmd == "version":
        return "Version 1.0.0"
    else:
        return f"Unknown command: {command}"
```

---

## Exercise 7 Solution

**First code block**:

```python
for i in range(5):     # i = 0, 1, 2, 3, 4
    if i == 2:
        continue       # Skip when i=2
    if i == 4:
        break          # Exit when i=4
    print(i)
print("Done")
```

**Trace**:
- i=0: prints 0
- i=1: prints 1
- i=2: continue (skips print)
- i=3: prints 3
- i=4: break (exits loop)

**Output**:
```
0
1
3
Done
```

**Second code block**:

```python
x = 0
while x < 10:
    x += 1              # Increment first
    if x % 2 == 0:
        continue        # Skip even numbers
    if x > 7:
        break           # Exit when x > 7
    print(x)
print(f"Final x: {x}")
```

**Trace**:
- x=1 (odd, ≤7): prints 1
- x=2 (even): continue
- x=3 (odd, ≤7): prints 3
- x=4 (even): continue
- x=5 (odd, ≤7): prints 5
- x=6 (even): continue
- x=7 (odd, ≤7): prints 7
- x=8 (even): continue
- x=9 (odd, >7): break

**Output**:
```
1
3
5
7
Final x: 9
```

---

## Alternative Approaches

### For-else and while-else

The `else` clause runs if the loop completes without `break`:

```python
# Search for an item
def find_item(items, target):
    for item in items:
        if item == target:
            print(f"Found {target}!")
            break
    else:
        print(f"{target} not found.")

find_item([1, 2, 3, 4, 5], 3)  # Found 3!
find_item([1, 2, 3, 4, 5], 9)  # 9 not found.
```

### Enumerate for index + value

```python
fruits = ["apple", "banana", "cherry"]

# Instead of:
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Use enumerate:
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

### Zip for parallel iteration

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

---

[← Back to Exercises](../exercises/ex_03_control_flow.md) | [← Back to Chapter](../03_control_flow.md) | [← Back to Module 1](../README.md)
