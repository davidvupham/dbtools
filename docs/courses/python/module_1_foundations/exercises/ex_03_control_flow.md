# Exercises — 03: Control Flow

## Learning Objectives

After completing these exercises, you will be able to:
- Write conditional statements with `if`, `elif`, `else`
- Use `for` loops to iterate over sequences
- Use `while` loops for conditional iteration
- Apply `break`, `continue`, and `pass` statements
- Use the `match` statement for pattern matching (Python 3.10+)

---

## Exercise 1: Grade Calculator (Warm-up)

**Bloom Level**: Apply

Write a program that:
1. Asks the user for a numeric grade (0-100)
2. Prints the letter grade based on this scale:
   - 90-100: A
   - 80-89: B
   - 70-79: C
   - 60-69: D
   - Below 60: F

**Example**:
```
Enter your grade: 85
Your letter grade is: B
```

---

## Exercise 2: FizzBuzz (Practice)

**Bloom Level**: Apply

Write a program that prints numbers from 1 to 30, but:
- For multiples of 3, print "Fizz" instead of the number
- For multiples of 5, print "Buzz" instead of the number
- For multiples of both 3 and 5, print "FizzBuzz"

**Expected Output** (partial):
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
...
```

---

## Exercise 3: Sum Calculator (Practice)

**Bloom Level**: Apply

Write a program that:
1. Continuously asks the user for numbers
2. Adds each number to a running total
3. Stops when the user enters "done"
4. Prints the final sum

**Example**:
```
Enter a number (or 'done' to finish): 10
Enter a number (or 'done' to finish): 20
Enter a number (or 'done' to finish): 5
Enter a number (or 'done' to finish): done
Total: 35.0
```

**Hint**: Use `while True` with a `break` statement.

---

## Exercise 4: Prime Number Checker (Practice)

**Bloom Level**: Analyze

Write a function `is_prime(n)` that returns `True` if `n` is prime, `False` otherwise.

A prime number is only divisible by 1 and itself.

Then, print all prime numbers between 1 and 50.

**Expected Output**:
```
Prime numbers between 1 and 50:
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47
```

---

## Exercise 5: Number Guessing Game (Practice)

**Bloom Level**: Apply

Create a number guessing game:
1. Generate a random number between 1 and 100 (use `import random; random.randint(1, 100)`)
2. Ask the user to guess the number
3. Tell them if they're too high or too low
4. Count the number of guesses
5. Congratulate them when they get it right

**Example**:
```
I'm thinking of a number between 1 and 100.
Your guess: 50
Too high!
Your guess: 25
Too low!
Your guess: 37
Too high!
Your guess: 30
Correct! You got it in 4 guesses.
```

---

## Exercise 6: Pattern Matching with match (Challenge)

**Bloom Level**: Apply

*Requires Python 3.10+*

Write a program using `match` that takes a command string and responds appropriately:
- "quit" or "exit" → prints "Goodbye!"
- "help" → prints "Available commands: quit, help, status, version"
- "status" → prints "All systems operational"
- "version" → prints "Version 1.0.0"
- Any other command → prints "Unknown command: {command}"

**Example**:
```
Enter command: help
Available commands: quit, help, status, version

Enter command: status
All systems operational

Enter command: foo
Unknown command: foo
```

---

## Exercise 7: Code Tracing (Analyze)

**Bloom Level**: Understand

Predict the output of this code before running it:

```python
for i in range(5):
    if i == 2:
        continue
    if i == 4:
        break
    print(i)
print("Done")
```

Also predict the output of:

```python
x = 0
while x < 10:
    x += 1
    if x % 2 == 0:
        continue
    if x > 7:
        break
    print(x)
print(f"Final x: {x}")
```

---

## Deliverables

Submit your code for exercises 1-6. For exercise 7, submit your predictions before running the code.

---

[← Back to Chapter](../03_control_flow.md) | [View Solutions](../solutions/sol_03_control_flow.md) | [← Back to Module 1](../README.md)
