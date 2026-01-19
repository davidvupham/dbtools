# Exercises — 19: Testing

## Learning Objectives

After completing these exercises, you will be able to:
- Write effective unit tests with pytest
- Use fixtures for test setup and teardown
- Parametrize tests for multiple inputs
- Mock external dependencies
- Measure and interpret code coverage
- Follow testing best practices

---

## Exercise 1: Basic pytest Tests (Warm-up)

**Bloom Level**: Apply

Write tests for this simple calculator module:

```python
# calculator.py
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(base, exponent):
    return base ** exponent
```

```python
# test_calculator.py
import pytest
from calculator import add, subtract, multiply, divide, power

def test_add_positive_numbers():
    pass

def test_add_negative_numbers():
    pass

def test_subtract():
    pass

def test_multiply():
    pass

def test_divide():
    pass

def test_divide_by_zero_raises():
    """Test that dividing by zero raises ValueError."""
    pass

def test_power():
    pass
```

---

## Exercise 2: Fixtures (Practice)

**Bloom Level**: Apply

Create fixtures for testing a user management system:

```python
# user.py
class User:
    def __init__(self, name, email, role="user"):
        self.name = name
        self.email = email
        self.role = role
        self.active = True

    def deactivate(self):
        self.active = False

    def promote(self):
        if self.role == "user":
            self.role = "admin"

class UserDatabase:
    def __init__(self):
        self.users = {}

    def add_user(self, user):
        self.users[user.email] = user

    def get_user(self, email):
        return self.users.get(email)

    def delete_user(self, email):
        if email in self.users:
            del self.users[email]
            return True
        return False

    def count(self):
        return len(self.users)
```

```python
# test_user.py
import pytest
from user import User, UserDatabase

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    pass

@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    pass

@pytest.fixture
def user_db():
    """Create a user database with some users."""
    pass

# Write tests using these fixtures
def test_user_creation(sample_user):
    pass

def test_user_deactivate(sample_user):
    pass

def test_user_promote(sample_user):
    pass

def test_admin_cannot_promote(admin_user):
    pass

def test_db_add_user(user_db, sample_user):
    pass

def test_db_get_user(user_db):
    pass

def test_db_delete_user(user_db):
    pass
```

---

## Exercise 3: Parametrization (Practice)

**Bloom Level**: Apply

Use parametrization to test multiple cases:

```python
# validators.py
import re

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Password must:
    - Be at least 8 characters
    - Contain uppercase and lowercase
    - Contain at least one number
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True

def validate_age(age):
    """Age must be between 0 and 150."""
    return isinstance(age, int) and 0 <= age <= 150
```

```python
# test_validators.py
import pytest
from validators import validate_email, validate_password, validate_age

@pytest.mark.parametrize("email,expected", [
    # Add test cases: valid emails, invalid emails, edge cases
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected

@pytest.mark.parametrize("password,expected", [
    # Add test cases covering all password rules
])
def test_validate_password(password, expected):
    assert validate_password(password) == expected

@pytest.mark.parametrize("age,expected", [
    # Add test cases: valid ages, invalid ages, edge cases
])
def test_validate_age(age, expected):
    assert validate_age(age) == expected
```

---

## Exercise 4: Mocking External Services (Practice)

**Bloom Level**: Apply

Test code that depends on external services using mocks:

```python
# weather_service.py
import requests

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.weather.example.com"

    def get_temperature(self, city):
        response = requests.get(
            f"{self.base_url}/current",
            params={"city": city, "key": self.api_key}
        )
        response.raise_for_status()
        data = response.json()
        return data["temperature"]

    def get_forecast(self, city, days=5):
        response = requests.get(
            f"{self.base_url}/forecast",
            params={"city": city, "days": days, "key": self.api_key}
        )
        response.raise_for_status()
        return response.json()["forecast"]
```

```python
# test_weather_service.py
import pytest
from unittest.mock import patch, Mock
from weather_service import WeatherService

@pytest.fixture
def weather_service():
    return WeatherService(api_key="test-key")

def test_get_temperature_success(weather_service):
    """Test successful temperature fetch."""
    pass

def test_get_temperature_api_error(weather_service):
    """Test handling of API errors."""
    pass

def test_get_forecast(weather_service):
    """Test forecast retrieval."""
    pass

def test_get_forecast_custom_days(weather_service):
    """Test forecast with custom number of days."""
    pass
```

---

## Exercise 5: Testing Exceptions (Practice)

**Bloom Level**: Apply

Write tests that verify exception handling:

```python
# bank.py
class InsufficientFundsError(Exception):
    pass

class InvalidAmountError(Exception):
    pass

class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount}, balance is {self.balance}"
            )
        self.balance -= amount

    def transfer(self, other_account, amount):
        self.withdraw(amount)
        other_account.deposit(amount)
```

```python
# test_bank.py
import pytest
from bank import BankAccount, InsufficientFundsError, InvalidAmountError

def test_deposit_negative_raises():
    """Depositing negative amount should raise InvalidAmountError."""
    pass

def test_withdraw_insufficient_funds():
    """Withdrawing more than balance should raise InsufficientFundsError."""
    pass

def test_exception_message():
    """Verify exception contains useful information."""
    pass

def test_transfer_fails_insufficient_funds():
    """Transfer should fail if source has insufficient funds."""
    pass

def test_transfer_rollback():
    """If transfer fails, source balance should be unchanged."""
    pass
```

---

## Exercise 6: Fixture Scope and Cleanup (Analyze)

**Bloom Level**: Analyze

Understand fixture scope and proper cleanup:

```python
# test_fixture_scope.py
import pytest

@pytest.fixture(scope="session")
def database_connection():
    """
    Session-scoped fixture - created once for entire test session.
    """
    print("\n[SESSION] Creating database connection")
    conn = {"connected": True}
    yield conn
    print("\n[SESSION] Closing database connection")
    conn["connected"] = False

@pytest.fixture(scope="module")
def module_data():
    """Module-scoped fixture - created once per test module."""
    print("\n[MODULE] Loading test data")
    yield {"data": [1, 2, 3]}
    print("\n[MODULE] Cleaning up test data")

@pytest.fixture(scope="function")
def function_state():
    """Function-scoped fixture - created for each test."""
    print("\n[FUNCTION] Setting up state")
    state = {"count": 0}
    yield state
    print(f"\n[FUNCTION] Cleaning up (count was {state['count']})")

def test_first(database_connection, module_data, function_state):
    function_state["count"] += 1
    assert database_connection["connected"]

def test_second(database_connection, module_data, function_state):
    function_state["count"] += 1
    assert function_state["count"] == 1  # Fresh fixture

def test_third(database_connection, function_state):
    function_state["count"] += 1
    assert database_connection["connected"]
```

**Questions**:
1. In what order are the setup/teardown messages printed?
2. Why does `test_second` see `count == 1` despite `test_first` incrementing it?
3. What happens to `database_connection` between tests?

---

## Exercise 7: Factory Fixtures (Challenge)

**Bloom Level**: Create

Create factory fixtures for flexible test data:

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
    """Factory fixture for creating products."""
    counter = [0]

    def _make_product(name="Test Product", price=10.0):
        counter[0] += 1
        return Product(id=counter[0], name=name, price=price)

    return _make_product

@pytest.fixture
def make_order():
    """Factory fixture for creating orders with products."""
    pass

# Write tests using factory fixtures
def test_order_total(make_order, make_product):
    """Test that order total is calculated correctly."""
    pass

def test_empty_order(make_order):
    """Test order with no products."""
    pass

def test_order_with_multiple_products(make_order, make_product):
    """Test order with many products."""
    pass
```

---

## Exercise 8: Integration Test Pattern (Challenge)

**Bloom Level**: Create

Write an integration test for a complete feature:

```python
# test_integration.py
import pytest
import tempfile
import json
from pathlib import Path

# The module under test
class TaskManager:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.tasks = []
        self._load()

    def _load(self):
        if self.storage_path.exists():
            self.tasks = json.loads(self.storage_path.read_text())

    def _save(self):
        self.storage_path.write_text(json.dumps(self.tasks))

    def add_task(self, title, priority="normal"):
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        self._save()
        return task

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self._save()
                return task
        raise ValueError(f"Task {task_id} not found")

    def get_pending_tasks(self):
        return [t for t in self.tasks if not t["completed"]]

@pytest.fixture
def task_manager(tmp_path):
    """Provide a TaskManager with temporary storage."""
    pass

def test_full_task_workflow(task_manager):
    """
    Integration test for complete task workflow:
    1. Add tasks
    2. Complete a task
    3. Verify persistence (create new manager, check data exists)
    """
    pass

def test_data_persists_across_instances(tmp_path):
    """
    Verify that data persists when creating new TaskManager instance.
    """
    pass
```

---

## Deliverables

Submit your test files for all exercises. Include your answers for Exercise 6.

---

[← Back to Chapter](../19_testing.md) | [View Solutions](../solutions/sol_19_testing.md) | [← Back to Module 3](../README.md)
