# Getting Started with Pytest
<!-- id: chapter-1 -->

**[← Back to Course Index](./README.md)**

> **Objective:** Write your first robust test using the Arrange-Act-Assert (AAA) pattern.
> **Time:** 15 Minutes

## Why Pytest?
<!-- id: why-pytest -->

The Python ecosystem has standardized on `pytest` for a reason: **Developer Experience**.
- **No Boilerplate:** Write simple functions, not classes (unlike `unittest`).
- **Detailed Info:** Failure reports show exactly *why* a test failed, without needing special assert methods like `assertEquals`.
- **Scalable:** It handles 10 tests or 10,000 tests with equal ease.

## The AAA Pattern
<!-- id: aaa-pattern -->

Every unit test—no matter how complex—should follow the **AAA** structure. This is the single most important habit to build.

1.  **Arrange:** Prepare the environment (create objects, set variables).
2.  **Act:** Call the function you want to test.
3.  **Assert:** Verify the result is what you expected.

### ❌ The Bad Way (Unstructured)
```python
def test_calculator_bad():
    # Everything mixed together
    calc = Calculator()
    assert calc.add(1, 1) == 2
    assert calc.subtract(2, 1) == 1  # Testing two things!
```

### ✅ The Best Way (AAA)
```python
def test_addition_standard():
    # Arrange
    calc = Calculator()
    
    # Act
    result = calc.add(1, 1)
    
    # Assert
    assert result == 2
```

## Hands-On: Your First Test Suite
<!-- id: hands-on -->

Let's look at a runnable example. We have a simple `calculator.py` and a test file `test_calculator.py`.

### 1. The Code (`calculator.py`)
This is the simple logic we want to verify.

```python
# examples/ch01_basics/calculator.py
def add(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b

def divide(a: int, b: int) -> float:
    """Divides equal integers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### 2. The Test (`test_calculator.py`)
This file must start with `test_` for pytest to find it automatically.

```python
# examples/ch01_basics/test_calculator.py
import pytest
from calculator import add, divide

def test_add_positive_numbers():
    # Arrange
    a, b = 10, 5
    
    # Act
    result = add(a, b)
    
    # Assert
    assert result == 15

def test_divide_by_zero():
    # Arrange
    a, b = 10, 0
    
    # Act & Assert
    # We use pytest.raises to assert that a specific Error is triggered
    with pytest.raises(ValueError) as excinfo:
        divide(a, b)
    
    # Optional: Verify the error message
    assert str(excinfo.value) == "Cannot divide by zero"
```

## Running the Tests
<!-- id: run-tests -->

In your terminal, navigate to the example directory and run `pytest`.

```bash
# -v means verbose (shows every test name)
pytest -v
```

**Output:**
```text
test_calculator.py::test_add_positive_numbers PASSED
test_calculator.py::test_divide_by_zero PASSED
```

## Key Takeaways
<!-- id: takeaways -->
- **Files**: Name test files `test_*.py`.
- **Functions**: Name test functions `test_*()`.
- **Assertion**: Just use `assert condition`.
- **Exceptions**: Use `with pytest.raises(Error):` for expected failures.

**[Next Chapter: Mastering Fixtures (Dependency Injection) →](./02-fixtures.md)**
