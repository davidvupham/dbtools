# Scaling Tests with Parametrization
<!-- id: chapter-3 -->

**[← Back to Course Index](./README.md)**

> **Objective:** Run 100 tests with 5 lines of code.
> **Time:** 15 Minutes

## The Code Duplication Problem
<!-- id: problem -->

Beginners often write tests like this:

```python
def test_add_1_plus_1():
    assert add(1, 1) == 2

def test_add_2_plus_2():
    assert add(2, 2) == 4

def test_add_10_plus_5():
    assert add(10, 5) == 15
```

This is **unmaintainable**. If you change the function signature, you have to fix 3 tests.

## The Solution: `@pytest.mark.parametrize`
<!-- id: solution -->

Parametrization allows you to define arguments for your test function, effectively generating multiple unique tests from one function definition.

### Basic Syntax

```python
import pytest
from calculator import add

@pytest.mark.parametrize("a, b, expected", [
    (1, 1, 2),
    (2, 2, 4),
    (10, 5, 15),
    (100, 200, 300),
])
def test_add_many(a, b, expected):
    assert add(a, b) == expected
```

When you run this, pytest reports **4 separate tests**:
- `test_add_many[1-1-2]`
- `test_add_many[2-2-4]`
- ...

## Stacked Parametrization (Combinatorial)
<!-- id: stacked -->

You can stack decorators to run every combination.

```python
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [3, 4])
def test_combinations(a, b):
    print(f"a={a}, b={b}")
```

**Runs 4 tests:**
- `a=1, b=3`
- `a=2, b=3`
- `a=1, b=4`
- `a=2, b=4`

## Hands-On: String Processor
<!-- id: hands-on -->

Let's test a function that validates usernames.

### 1. The Code (`validator.py`)
```python
# examples/ch03_scaling/validator.py
def is_valid_username(username: str) -> bool:
    if not username:
        return False
    if " " in username:
        return False
    if len(username) < 3:
        return False
    return True
```

### 2. The Test (`test_validator.py`)
```python
# examples/ch03_scaling/test_validator.py
import pytest
from validator import is_valid_username

@pytest.mark.parametrize("username, expected", [
    ("admin", True),
    ("user123", True),
    ("", False),         # Empty
    ("ab", False),       # Too short
    ("no spaces", False), # Has spaces
])
def test_username_validation(username, expected):
    assert is_valid_username(username) is expected
```

## Custom Test IDs
<!-- id: custom-ids -->

You can make the output prettier by naming the cases.

```python
@pytest.mark.parametrize("input,expected", [
    pytest.param("", False, id="empty_string"),
    pytest.param("a", False, id="too_short"),
], ids=str)
```

**[Next Chapter: The Art of Mocking →](./04-mocking.md)**
