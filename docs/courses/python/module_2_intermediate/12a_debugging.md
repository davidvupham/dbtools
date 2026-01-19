# Debugging

Debugging is the process of finding and fixing errors in your code. Every developer spends significant time debugging, so mastering these techniques will make you more effective.

## Types of errors

### Syntax errors

Errors in code structure that prevent Python from running:

```python
# SyntaxError: Missing colon
if x > 5
    print("big")

# SyntaxError: Unclosed parenthesis
print("hello"

# SyntaxError: Invalid syntax
x = = 5
```

Python tells you exactly where syntax errors occur. Read the error message carefully.

### Runtime errors (Exceptions)

Errors that occur while the program is running:

```python
# ZeroDivisionError
result = 10 / 0

# IndexError
my_list = [1, 2, 3]
print(my_list[5])

# KeyError
my_dict = {"a": 1}
print(my_dict["b"])

# TypeError
result = "5" + 5

# FileNotFoundError
with open("nonexistent.txt") as f:
    content = f.read()
```

### Logic errors

The hardest to find—code runs but produces wrong results:

```python
# Bug: Should be total / len(numbers), not len(numbers) / total
def average(numbers):
    total = sum(numbers)
    return len(numbers) / total  # Wrong!

print(average([10, 20, 30]))  # Returns 0.15 instead of 20
```

## Print debugging

The simplest debugging technique—add print statements to see what's happening:

```python
def calculate_discount(price, discount_percent):
    print(f"DEBUG: price={price}, discount_percent={discount_percent}")

    discount = price * discount_percent
    print(f"DEBUG: discount={discount}")

    final_price = price - discount
    print(f"DEBUG: final_price={final_price}")

    return final_price

# Bug: discount_percent should be 0.20, not 20
result = calculate_discount(100, 20)
# DEBUG: price=100, discount_percent=20
# DEBUG: discount=2000  <- Problem! Discount is bigger than price
# DEBUG: final_price=-1900
```

### Better print debugging

```python
# Use f-strings with variable names
x, y, z = 10, 20, 30
print(f"{x=}, {y=}, {z=}")  # x=10, y=20, z=30 (Python 3.8+)

# Print type information
data = "123"
print(f"data={data!r}, type={type(data).__name__}")
# data='123', type=str

# Print with context
def process_items(items):
    print(f"[process_items] Starting with {len(items)} items")
    for i, item in enumerate(items):
        print(f"[process_items] Processing item {i}: {item!r}")
        # ... process item
    print(f"[process_items] Done")
```

### Conditional debugging

```python
DEBUG = True  # Set to False in production

def calculate(x, y):
    if DEBUG:
        print(f"calculate({x}, {y})")

    result = x + y

    if DEBUG:
        print(f"  -> {result}")

    return result
```

## The Python debugger (pdb)

Python's built-in debugger lets you pause execution and inspect state.

### Starting the debugger

```python
# Method 1: Insert breakpoint in code
def calculate(x, y):
    breakpoint()  # Program pauses here (Python 3.7+)
    result = x + y
    return result

# Method 2: Older syntax
import pdb
def calculate(x, y):
    pdb.set_trace()  # Program pauses here
    result = x + y
    return result

# Method 3: Run script in debugger mode
# $ python -m pdb script.py
```

### pdb commands

| Command | Description |
|---------|-------------|
| `n` (next) | Execute next line |
| `s` (step) | Step into function call |
| `c` (continue) | Continue until next breakpoint |
| `l` (list) | Show current code location |
| `p expr` | Print expression value |
| `pp expr` | Pretty-print expression |
| `w` (where) | Show call stack |
| `u` (up) | Go up one stack frame |
| `d` (down) | Go down one stack frame |
| `b line` | Set breakpoint at line |
| `cl` | Clear breakpoints |
| `q` (quit) | Exit debugger |
| `h` (help) | Show help |

### Example debugging session

```python
def find_average(numbers):
    total = 0
    for num in numbers:
        breakpoint()  # Let's debug here
        total += num
    return total / len(numbers)

result = find_average([10, 20, 30])
```

Session:
```
> /path/to/script.py(4)find_average()
-> total += num
(Pdb) p num
10
(Pdb) p total
0
(Pdb) n
> /path/to/script.py(3)find_average()
-> for num in numbers:
(Pdb) p total
10
(Pdb) c  # Continue to next breakpoint iteration
> /path/to/script.py(4)find_average()
-> total += num
(Pdb) p num
20
(Pdb) p total
10
```

### Post-mortem debugging

Debug after an exception occurs:

```python
import pdb

try:
    result = 10 / 0
except:
    pdb.post_mortem()  # Debug at the point of failure
```

Or from command line:
```bash
python -m pdb -c continue script.py
# Debugger activates automatically on exception
```

## IDE debugging

Modern IDEs provide visual debugging with:
- **Breakpoints**: Click in the gutter to set
- **Variable inspection**: See all variables and their values
- **Watch expressions**: Monitor specific expressions
- **Call stack**: See how you got to the current line
- **Step controls**: Next, step into, step out, continue

### VS Code debugging

1. Click in the gutter to set a breakpoint (red dot)
2. Press F5 or click "Run and Debug"
3. Use the debug toolbar: Continue, Step Over, Step Into, Step Out, Restart, Stop
4. Hover over variables to see values
5. Use the Debug Console to evaluate expressions

### PyCharm debugging

1. Click in the gutter to set a breakpoint
2. Right-click and select "Debug"
3. Use the debugger panel to:
   - View variables
   - Evaluate expressions
   - Step through code

## Debugging strategies

### Binary search debugging

Narrow down the problem by testing at the midpoint:

```python
def process_data(data):
    step1 = transform(data)      # Works?
    step2 = validate(step1)      # Works?
    step3 = enrich(step2)        # Bug here!
    step4 = format_output(step3)
    return step4

# Test at midpoint
def process_data(data):
    step1 = transform(data)
    step2 = validate(step1)
    print(f"After step2: {step2}")  # Check here first
    return step2  # Temporarily return early

# If step2 looks good, bug is in step3 or step4
# If step2 looks bad, bug is in step1 or step2
```

### Rubber duck debugging

Explain the code line by line to someone (or something) else:

1. Get a rubber duck (or any object)
2. Explain what each line of code does
3. Often, you'll find the bug while explaining

This works because explaining forces you to think through every assumption.

### Simplify and isolate

Create a minimal example that reproduces the bug:

```python
# Original complex code with bug
def complex_function(data, options, config):
    # 100 lines of code...
    pass

# Simplified reproduction
def minimal_reproduction():
    """Smallest code that shows the bug."""
    data = [1, 2, 3]  # Minimal data
    result = buggy_function(data)
    print(result)  # Shows unexpected behavior
```

### Check your assumptions

Common false assumptions:
- "This variable is definitely an integer" → Check with `print(type(x))`
- "This list has at least one item" → Check with `print(len(items))`
- "This key exists in the dict" → Check with `print(key in my_dict)`
- "This function returns a value" → Check with `print(repr(result))`

```python
def debug_assumptions(data):
    print(f"Type: {type(data)}")
    print(f"Value: {data!r}")
    print(f"Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
    print(f"Truthy: {bool(data)}")
```

## Logging for debugging

Better than print statements for production code:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_order(order):
    logger.debug(f"Processing order: {order}")

    if not order.get('items'):
        logger.warning(f"Order has no items: {order.get('id')}")
        return None

    total = sum(item['price'] for item in order['items'])
    logger.info(f"Order {order.get('id')} total: ${total}")

    return total
```

Benefits over print:
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Timestamps automatic
- Can write to files
- Easy to enable/disable
- Function names included

## Common debugging scenarios

### Finding where an exception occurs

```python
import traceback

try:
    result = complex_operation()
except Exception as e:
    print("Full traceback:")
    traceback.print_exc()

    print(f"\nException type: {type(e).__name__}")
    print(f"Exception message: {e}")
```

### Debugging loops

```python
def find_item(items, target):
    for i, item in enumerate(items):
        # Debug first few iterations only
        if i < 3:
            print(f"Iteration {i}: checking {item!r} against {target!r}")

        if item == target:
            print(f"Found at index {i}")
            return i

    print(f"Not found after {len(items)} items")
    return -1
```

### Debugging recursion

```python
def factorial(n, depth=0):
    indent = "  " * depth
    print(f"{indent}factorial({n})")

    if n <= 1:
        print(f"{indent}  -> returning 1")
        return 1

    result = n * factorial(n - 1, depth + 1)
    print(f"{indent}  -> returning {result}")
    return result

factorial(4)
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1)
#         -> returning 1
#       -> returning 2
#     -> returning 6
#   -> returning 24
```

## Example from our code

The dbtools codebase uses structured logging for debugging:

```python
# python/gds_database/src/gds_database/connection.py
import structlog

logger = structlog.get_logger()

class DatabaseConnection:
    def connect(self, host: str, port: int):
        logger.debug("Attempting connection", host=host, port=port)

        try:
            self._conn = self._create_connection(host, port)
            logger.info("Connection established", host=host, port=port)
        except Exception as e:
            logger.error(
                "Connection failed",
                host=host,
                port=port,
                error=str(e),
                exc_info=True
            )
            raise
```

## Best practices summary

1. **Read error messages carefully**: They often tell you exactly what's wrong
2. **Reproduce the bug**: Create a minimal example
3. **Check your assumptions**: Print types, lengths, and values
4. **Use the right tool**: Print for quick checks, pdb for complex issues, IDE for visual debugging
5. **Binary search**: Narrow down the problem location
6. **Explain the code**: Rubber duck debugging works
7. **Use logging**: Better than print for production
8. **Write tests**: Prevent bugs from coming back
9. **Take breaks**: Fresh eyes catch bugs faster
10. **Version control**: `git diff` shows what changed

---

[← Back to Module 2](./README.md) | [Next: Modules and Packages →](./13_modules_packages.md)
