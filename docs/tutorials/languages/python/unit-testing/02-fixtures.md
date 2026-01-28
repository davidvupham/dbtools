# Mastering Fixtures
<!-- id: chapter-2 -->

**[← Back to Course Index](./README.md)**

> **Objective:** Understand Dependency Injection, Setup/Teardown, and `conftest.py`.
> **Time:** 20 Minutes

## What is a Fixture?
<!-- id: what-is-fixture -->

A fixture is a function that provides data, objects, or state to your tests. It is the **Arrange** phase of AAA, abstracted into a reusable function.

Think of fixtures as "Dependency Injection" for your tests.

### Why use fixtures?
- **Reusability:** Define a complex object once, use it in 100 tests.
- **Consistency:** Every test gets a fresh copy (unless scoped otherwise).
- **Cleanup:** Handles `teardown` logic automatically (using `yield`).

## The `conftest.py` File
<!-- id: conftest -->

Fixtures defined in a `conftest.py` file are automatically available to all tests in the same directory and subdirectories. You do **not** need to import them.

## Core Concepts

### 1. Basic Fixture
<!-- id: basic-fixture -->

```python
import pytest

@pytest.fixture
def user_data():
    return {"username": "jdoe", "email": "jdoe@example.com"}

def test_user_email(user_data):  # Request fixture by name
    assert user_data["email"] == "jdoe@example.com"
```

### 2. Setup and Teardown (`yield`)
<!-- id: yield-fixture -->

Use `yield` instead of `return` to run code *after* the test finishes. This replaces `setUp` and `tearDown` methods.

```python
@pytest.fixture
def db_connection():
    print("\nConnecting to DB...")
    conn = connect_to_db()
    
    yield conn  # Test runs here
    
    print("\nClosing DB...")
    conn.close()
```

### 3. Built-in Fixtures (`tmp_path`)
<!-- id: tmp-path -->

Never manually create temp files or folders. Use `tmp_path` (returns a `pathlib.Path` object).

```python
def test_file_write(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("content")
    assert p.read_text() == "content"
```

## Hands-On: Managing State
<!-- id: hands-on -->

We will simulate a Database connection lifecycle.

### 1. The Configuration (`conftest.py`)

```python
# examples/ch02_fixtures/conftest.py
import pytest

class MockDB:
    def __init__(self):
        self.status = "connected"

    def close(self):
        self.status = "closed"

@pytest.fixture(scope="function")
def db():
    """Simulates a database connection."""
    database = MockDB()
    yield database
    database.close()
```

### 2. The Test (`test_db_lifecycle.py`)

```python
# examples/ch02_fixtures/test_db_lifecycle.py
def test_db_is_connected(db):
    # 'db' fixture is automatically created before this test
    assert db.status == "connected"
    # When test ends, db.close() is called automatically
```

### 3. Using `tmp_path` (`test_files.py`)

```python
# examples/ch02_fixtures/test_files.py
import json

def test_json_save(tmp_path):
    # Arrange
    data = {"name": "Test"}
    file_path = tmp_path / "data.json"
    
    # Act
    with open(file_path, "w") as f:
        json.dump(data, f)
        
    # Assert
    assert file_path.exists()
    with open(file_path) as f:
        assert json.load(f) == data
```

## Scopes: Optimizing Performance
<!-- id: scopes -->

By default, fixtures run for **every test**. You can change this using `scope`.

| Scope | Description | Use Case |
|:---|:---|:---|
| `function` (default) | Run once per test | Mutable data (user objects) |
| `module` | Run once per file | Read-only API clients |
| `session` | Run once per test run | Docker containers, Expensive DB setup |

```python
@pytest.fixture(scope="session")
def docker_container():
    # Starts container once for the whole suite!
    ...
```

**[Next Chapter: Scaling with Parametrization →](./03-scaling-tests.md)**
