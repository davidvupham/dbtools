# Solutions — 19: Testing

## Key Concepts Demonstrated

- Basic pytest assertions and structure
- Fixtures for setup/teardown
- Parametrization for multiple test cases
- Mocking external dependencies
- Testing exceptions
- Fixture scope management
- Factory fixtures
- Integration testing patterns

## Common Mistakes to Avoid

- Testing implementation details instead of behavior
- Not testing edge cases and error paths
- Over-mocking (mocking the thing you're testing)
- Flaky tests that depend on timing or external state
- Not cleaning up resources in fixtures

---

## Exercise 1 Solution

```python
# test_calculator.py
import pytest
from calculator import add, subtract, multiply, divide, power

def test_add_positive_numbers():
    assert add(2, 3) == 5
    assert add(0, 5) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2
    assert add(-5, 3) == -2

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(0, 0) == 0

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    assert divide(0, 5) == 0

def test_divide_by_zero_raises():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "Cannot divide by zero" in str(exc_info.value)

def test_power():
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    assert power(2, -1) == 0.5
```

---

## Exercise 2 Solution

```python
# test_user.py
import pytest
from user import User, UserDatabase

@pytest.fixture
def sample_user():
    return User("Alice", "alice@example.com")

@pytest.fixture
def admin_user():
    return User("Admin", "admin@example.com", role="admin")

@pytest.fixture
def user_db():
    db = UserDatabase()
    db.add_user(User("User1", "user1@example.com"))
    db.add_user(User("User2", "user2@example.com"))
    return db

def test_user_creation(sample_user):
    assert sample_user.name == "Alice"
    assert sample_user.email == "alice@example.com"
    assert sample_user.role == "user"
    assert sample_user.active is True

def test_user_deactivate(sample_user):
    sample_user.deactivate()
    assert sample_user.active is False

def test_user_promote(sample_user):
    assert sample_user.role == "user"
    sample_user.promote()
    assert sample_user.role == "admin"

def test_admin_cannot_promote(admin_user):
    admin_user.promote()  # Should have no effect
    assert admin_user.role == "admin"

def test_db_add_user(user_db, sample_user):
    initial_count = user_db.count()
    user_db.add_user(sample_user)
    assert user_db.count() == initial_count + 1

def test_db_get_user(user_db):
    user = user_db.get_user("user1@example.com")
    assert user is not None
    assert user.name == "User1"

def test_db_delete_user(user_db):
    assert user_db.delete_user("user1@example.com") is True
    assert user_db.get_user("user1@example.com") is None
    assert user_db.delete_user("nonexistent@example.com") is False
```

---

## Exercise 3 Solution

```python
# test_validators.py
import pytest
from validators import validate_email, validate_password, validate_age

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("user.name@example.com", True),
    ("user@sub.example.com", True),
    ("user_name@example.co.uk", True),
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
    ("user@.com", False),
    ("", False),
    ("user@@example.com", False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected

@pytest.mark.parametrize("password,expected", [
    ("Password1", True),        # Meets all requirements
    ("Abcdefg1", True),         # Exactly 8 chars
    ("password1", False),       # No uppercase
    ("PASSWORD1", False),       # No lowercase
    ("Password", False),        # No number
    ("Pass1", False),           # Too short
    ("", False),                # Empty
    ("ABCdef123", True),        # Multiple numbers
])
def test_validate_password(password, expected):
    assert validate_password(password) == expected

@pytest.mark.parametrize("age,expected", [
    (0, True),
    (25, True),
    (150, True),
    (-1, False),
    (151, False),
    (25.5, False),   # Float not allowed
    ("25", False),   # String not allowed
    (None, False),   # None not allowed
])
def test_validate_age(age, expected):
    assert validate_age(age) == expected
```

---

## Exercise 4 Solution

```python
# test_weather_service.py
import pytest
from unittest.mock import patch, Mock
from weather_service import WeatherService
import requests

@pytest.fixture
def weather_service():
    return WeatherService(api_key="test-key")

@patch("weather_service.requests.get")
def test_get_temperature_success(mock_get, weather_service):
    mock_response = Mock()
    mock_response.json.return_value = {"temperature": 72}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    temp = weather_service.get_temperature("New York")

    assert temp == 72
    mock_get.assert_called_once_with(
        "https://api.weather.example.com/current",
        params={"city": "New York", "key": "test-key"}
    )

@patch("weather_service.requests.get")
def test_get_temperature_api_error(mock_get, weather_service):
    mock_get.return_value.raise_for_status.side_effect = (
        requests.exceptions.HTTPError("404 Not Found")
    )

    with pytest.raises(requests.exceptions.HTTPError):
        weather_service.get_temperature("InvalidCity")

@patch("weather_service.requests.get")
def test_get_forecast(mock_get, weather_service):
    mock_response = Mock()
    mock_response.json.return_value = {
        "forecast": [{"day": 1, "temp": 70}, {"day": 2, "temp": 72}]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    forecast = weather_service.get_forecast("Boston")

    assert len(forecast) == 2
    assert forecast[0]["temp"] == 70

@patch("weather_service.requests.get")
def test_get_forecast_custom_days(mock_get, weather_service):
    mock_response = Mock()
    mock_response.json.return_value = {"forecast": []}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    weather_service.get_forecast("Boston", days=10)

    mock_get.assert_called_once_with(
        "https://api.weather.example.com/forecast",
        params={"city": "Boston", "days": 10, "key": "test-key"}
    )
```

---

## Exercise 5 Solution

```python
# test_bank.py
import pytest
from bank import BankAccount, InsufficientFundsError, InvalidAmountError

def test_deposit_negative_raises():
    account = BankAccount(100)
    with pytest.raises(InvalidAmountError):
        account.deposit(-50)
    with pytest.raises(InvalidAmountError):
        account.deposit(0)

def test_withdraw_insufficient_funds():
    account = BankAccount(50)
    with pytest.raises(InsufficientFundsError):
        account.withdraw(100)

def test_exception_message():
    account = BankAccount(50)
    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(100)
    assert "100" in str(exc_info.value)
    assert "50" in str(exc_info.value)

def test_transfer_fails_insufficient_funds():
    source = BankAccount(50)
    dest = BankAccount(0)

    with pytest.raises(InsufficientFundsError):
        source.transfer(dest, 100)

def test_transfer_rollback():
    source = BankAccount(50)
    dest = BankAccount(0)

    try:
        source.transfer(dest, 100)
    except InsufficientFundsError:
        pass

    # Source balance should be unchanged
    assert source.balance == 50
    assert dest.balance == 0
```

---

## Exercise 6 Solution

**Answers**:

1. **Order of messages**:
   ```
   [SESSION] Creating database connection
   [MODULE] Loading test data
   [FUNCTION] Setting up state
   # test_first runs
   [FUNCTION] Cleaning up (count was 1)
   [FUNCTION] Setting up state
   # test_second runs
   [FUNCTION] Cleaning up (count was 1)
   [FUNCTION] Setting up state
   # test_third runs
   [FUNCTION] Cleaning up (count was 1)
   [MODULE] Cleaning up test data
   [SESSION] Closing database connection
   ```

2. **Why count == 1**: Function-scoped fixtures are created fresh for each test. Each test gets a new `function_state` dictionary with `count: 0`.

3. **database_connection between tests**: It stays connected throughout all tests. Session-scoped fixtures are created once and shared across all tests.

---

## Exercise 7 Solution

```python
# test_orders.py
import pytest
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Product:
    id: int
    name: str
    price: float

@dataclass
class Order:
    id: int
    customer: str
    products: List[Product]
    created_at: datetime
    status: str = "pending"

    @property
    def total(self):
        return sum(p.price for p in self.products)

@pytest.fixture
def make_product():
    counter = [0]

    def _make_product(name="Test Product", price=10.0):
        counter[0] += 1
        return Product(id=counter[0], name=name, price=price)

    return _make_product

@pytest.fixture
def make_order(make_product):
    counter = [0]

    def _make_order(customer="Test Customer", products=None, status="pending"):
        counter[0] += 1
        if products is None:
            products = [make_product()]
        return Order(
            id=counter[0],
            customer=customer,
            products=products,
            created_at=datetime.now(),
            status=status
        )

    return _make_order

def test_order_total(make_order, make_product):
    products = [
        make_product(price=10.0),
        make_product(price=20.0),
        make_product(price=15.0),
    ]
    order = make_order(products=products)
    assert order.total == 45.0

def test_empty_order(make_order):
    order = make_order(products=[])
    assert order.total == 0

def test_order_with_multiple_products(make_order, make_product):
    products = [make_product(price=5.0) for _ in range(10)]
    order = make_order(products=products)
    assert order.total == 50.0
    assert len(order.products) == 10
```

---

## Exercise 8 Solution

```python
# test_integration.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def task_manager(tmp_path):
    storage = tmp_path / "tasks.json"
    return TaskManager(storage)

def test_full_task_workflow(task_manager):
    # 1. Add tasks
    task1 = task_manager.add_task("Buy groceries", priority="high")
    task2 = task_manager.add_task("Clean house")
    task3 = task_manager.add_task("Call mom")

    assert task_manager.get_pending_tasks() == [task1, task2, task3]

    # 2. Complete a task
    task_manager.complete_task(task1["id"])

    # 3. Verify state
    pending = task_manager.get_pending_tasks()
    assert len(pending) == 2
    assert task1 not in pending

def test_data_persists_across_instances(tmp_path):
    storage = tmp_path / "tasks.json"

    # Create first instance and add data
    manager1 = TaskManager(storage)
    manager1.add_task("Persistent task")
    del manager1

    # Create second instance and verify data exists
    manager2 = TaskManager(storage)
    assert len(manager2.tasks) == 1
    assert manager2.tasks[0]["title"] == "Persistent task"
```

---

## Testing Best Practices Summary

| Practice | Do | Don't |
|----------|----|----- |
| Test names | `test_user_with_invalid_email_raises` | `test_1`, `test_email` |
| Assertions | One concept per test | Dozens of unrelated asserts |
| Fixtures | Share setup, isolate state | Share mutable state |
| Mocking | Mock at boundaries | Mock the code under test |
| Coverage | 80-90% meaningful coverage | 100% trivial coverage |

---

[← Back to Exercises](../exercises/ex_19_testing.md) | [← Back to Chapter](../19_testing.md) | [← Back to Module 3](../README.md)
