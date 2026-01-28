# The Art of Mocking
<!-- id: chapter-4 -->

**[← Back to Course Index](./README.md)**

> **Objective:** Isolate your code from external systems (APIs, DBs) using mocks.
> **Time:** 20 Minutes

## Why Mock?
<!-- id: why-mock -->

Unit tests must be:
1.  **Fast**: No waiting for HTTP requests.
2.  **Deterministic**: No failing because the internet is down.
3.  **Isolated**: Testing *your* logic, not the API's logic.

If your test hits a real API, it is an **Integration Test**, not a Unit Test.

## The Tools: `unittest.mock` vs `pytest-mock`
<!-- id: tools -->

Python comes with `unittest.mock`. However, `pytest-mock` provides a cleaner fixture called `mocker`.

> [!TIP]
> We recommend installing `pytest-mock` for production work. For this tutorial, we will focus on standard library patterns compatibility, but the concepts are identical.

## Hands-On: Mocking an API Client
<!-- id: hands-on -->

We will test a function `get_user_data` that calls a slow external API. We want to mock that API call.

### 1. The Code (`api_client.py`)

```python
# examples/ch04_mocking/api_client.py
import time

def slow_api_call(user_id):
    """Simulates a slow network request."""
    time.sleep(5)  # We do NOT want to wait for this!
    return {"id": user_id, "active": True}

def get_user_status(user_id):
    """The function we want to test."""
    data = slow_api_call(user_id)
    if data["active"]:
        return "Active User"
    return "Inactive"
```

### 2. The Test (`test_api.py`)

We use `unittest.mock.patch` as a decorator or context manager.

```python
# examples/ch04_mocking/test_api.py
from unittest.mock import patch
from api_client import get_user_status

@patch("api_client.slow_api_call")
def test_get_user_status_mocks_api(mock_api):
    # Arrange
    # Configure the mock to return specific data WITHOUT sleeping
    mock_api.return_value = {"id": 123, "active": True}
    
    # Act
    status = get_user_status(123)
    
    # Assert
    assert status == "Active User"
    
    # Verify the mock was actually called
    mock_api.assert_called_once_with(123)
```

## Mocking Classes
<!-- id: mocking-classes -->

You can also mock entire objects.

```python
@patch("path.to.MyClass")
def test_class(mock_class):
    mock_instance = mock_class.return_value
    mock_instance.some_method.return_value = "foo"
    ...
```

## Best Practices
<!-- id: best-practices -->
1.  **Patch where it is USED, not where it is defined.**
    -   If `api_client.py` imports `requests`, patch `api_client.requests`, not `requests`.
2.  **Don't over-mock.** If you mock everything, you are testing nothing.
3.  **Use `side_effect`** for Exceptions.
    ```python
    mock_api.side_effect = TimeoutError
    ```

**[Next Chapter: Advanced Patterns →](./05-advanced-patterns.md)**
