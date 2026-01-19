# Exercises — 06: Error Handling

## Learning Objectives

After completing these exercises, you will be able to:
- Use try/except blocks to handle exceptions
- Catch specific exception types appropriately
- Use else and finally clauses effectively
- Raise exceptions with meaningful messages
- Create custom exception classes
- Apply error handling best practices

---

## Exercise 1: Basic Exception Handling (Warm-up)

**Bloom Level**: Apply

Write a function that safely converts user input to different types:

```python
def safe_convert(value: str, target_type: str) -> tuple[bool, any]:
    """
    Safely convert a string to the specified type.

    Args:
        value: The string to convert.
        target_type: One of "int", "float", "bool".

    Returns:
        Tuple of (success: bool, converted_value or error_message).

    Examples:
        >>> safe_convert("42", "int")
        (True, 42)
        >>> safe_convert("hello", "int")
        (False, "Cannot convert 'hello' to int")
        >>> safe_convert("3.14", "float")
        (True, 3.14)
        >>> safe_convert("true", "bool")
        (True, True)
    """
    pass

# Test cases
test_cases = [
    ("42", "int"),
    ("hello", "int"),
    ("3.14", "float"),
    ("not_a_float", "float"),
    ("true", "bool"),
    ("false", "bool"),
    ("yes", "bool"),
    ("", "int"),
]

for value, target in test_cases:
    success, result = safe_convert(value, target)
    status = "✓" if success else "✗"
    print(f"{status} safe_convert({value!r}, {target!r}) = {result}")
```

---

## Exercise 2: Multiple Exception Types (Practice)

**Bloom Level**: Apply

Write a function that reads a configuration value and handles various errors:

```python
def get_config_value(config: dict, key: str, expected_type: type) -> any:
    """
    Get a configuration value with type checking.

    Args:
        config: Configuration dictionary.
        key: Key to look up.
        expected_type: Expected type of the value.

    Returns:
        The configuration value.

    Raises:
        KeyError: If key doesn't exist.
        TypeError: If value is not the expected type.
        ValueError: If value is empty or invalid.
    """
    pass

# Test with this config
config = {
    "port": 8080,
    "host": "localhost",
    "debug": True,
    "timeout": "30",  # Wrong type (should be int)
    "name": "",       # Empty value
}

test_cases = [
    ("port", int),      # Should succeed
    ("host", str),      # Should succeed
    ("missing", str),   # Should raise KeyError
    ("timeout", int),   # Should raise TypeError
    ("name", str),      # Should raise ValueError (empty)
]

for key, expected_type in test_cases:
    try:
        value = get_config_value(config, key, expected_type)
        print(f"✓ config[{key!r}] = {value!r}")
    except (KeyError, TypeError, ValueError) as e:
        print(f"✗ config[{key!r}]: {type(e).__name__}: {e}")
```

---

## Exercise 3: The finally Clause (Practice)

**Bloom Level**: Apply

Implement a resource manager that ensures cleanup always happens:

```python
class DatabaseConnection:
    """Simulated database connection for testing."""

    def __init__(self, host: str):
        self.host = host
        self.connected = False
        self.queries_run = 0

    def connect(self):
        print(f"Connecting to {self.host}...")
        if self.host == "invalid":
            raise ConnectionError(f"Cannot connect to {self.host}")
        self.connected = True
        print("Connected!")

    def execute(self, query: str):
        if not self.connected:
            raise RuntimeError("Not connected to database")
        print(f"Executing: {query}")
        if "ERROR" in query:
            raise RuntimeError("Query execution failed")
        self.queries_run += 1
        return f"Result of {query}"

    def disconnect(self):
        print(f"Disconnecting from {self.host}...")
        self.connected = False
        print("Disconnected!")


def run_database_operation(host: str, queries: list[str]) -> list[str]:
    """
    Run database queries with guaranteed cleanup.

    Must:
    1. Connect to the database
    2. Execute all queries
    3. ALWAYS disconnect, even if errors occur
    4. Return list of results (or partial results if error)

    Use try/except/finally to ensure disconnect always runs.
    """
    pass

# Test cases
print("Test 1: Normal operation")
print("-" * 40)
results = run_database_operation("localhost", ["SELECT 1", "SELECT 2"])
print(f"Results: {results}\n")

print("Test 2: Query error (should still disconnect)")
print("-" * 40)
results = run_database_operation("localhost", ["SELECT 1", "ERROR query", "SELECT 3"])
print(f"Results: {results}\n")

print("Test 3: Connection error")
print("-" * 40)
results = run_database_operation("invalid", ["SELECT 1"])
print(f"Results: {results}\n")
```

---

## Exercise 4: Exception Chaining (Analyze)

**Bloom Level**: Analyze

Understand and implement exception chaining:

```python
class DataProcessingError(Exception):
    """Error during data processing."""
    pass

class ValidationError(Exception):
    """Error during data validation."""
    pass

def validate_data(data: dict) -> None:
    """Validate data structure."""
    required_fields = ["name", "age", "email"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
        if not data[field]:
            raise ValidationError(f"Empty value for field: {field}")

def transform_data(data: dict) -> dict:
    """Transform data (may fail)."""
    try:
        return {
            "full_name": data["name"].upper(),
            "age_in_months": data["age"] * 12,
            "contact": data["email"].lower(),
        }
    except (KeyError, TypeError, AttributeError) as e:
        raise DataProcessingError("Failed to transform data") from e

def process_record(data: dict) -> dict:
    """
    Process a data record with proper exception chaining.

    Should:
    1. Validate the data
    2. Transform the data
    3. Chain exceptions to preserve context

    Use 'raise ... from ...' for exception chaining.
    """
    pass

# Test cases
test_records = [
    {"name": "Alice", "age": 30, "email": "alice@example.com"},  # Valid
    {"name": "Bob", "age": 25},  # Missing email
    {"name": "Charlie", "age": "thirty", "email": "c@example.com"},  # Invalid age type
    {"name": "", "age": 40, "email": "d@example.com"},  # Empty name
]

for i, record in enumerate(test_records):
    print(f"\nRecord {i + 1}: {record}")
    try:
        result = process_record(record)
        print(f"  ✓ Processed: {result}")
    except (ValidationError, DataProcessingError) as e:
        print(f"  ✗ {type(e).__name__}: {e}")
        if e.__cause__:
            print(f"    Caused by: {type(e.__cause__).__name__}: {e.__cause__}")
```

---

## Exercise 5: Custom Exceptions (Practice)

**Bloom Level**: Apply

Create a custom exception hierarchy for a banking application:

```python
# Define your exception hierarchy here
class BankingError(Exception):
    """Base exception for banking operations."""
    pass

# Add more specific exceptions:
# - InsufficientFundsError
# - InvalidAccountError
# - TransactionLimitError
# - AccountLockedError

class BankAccount:
    """Simple bank account with error handling."""

    DAILY_LIMIT = 1000

    def __init__(self, account_number: str, balance: float = 0):
        self.account_number = account_number
        self.balance = balance
        self.daily_withdrawn = 0
        self.locked = False

    def deposit(self, amount: float) -> float:
        """Deposit money into account."""
        if self.locked:
            raise AccountLockedError(self.account_number)
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        """
        Withdraw money from account.

        Raises:
            AccountLockedError: If account is locked.
            InsufficientFundsError: If balance is too low.
            TransactionLimitError: If daily limit exceeded.
            ValueError: If amount is not positive.
        """
        pass

    def transfer(self, to_account: "BankAccount", amount: float) -> None:
        """
        Transfer money to another account.

        Should handle all possible errors and provide clear messages.
        """
        pass

# Test the implementation
accounts = {
    "123": BankAccount("123", balance=500),
    "456": BankAccount("456", balance=100),
    "789": BankAccount("789", balance=1000),
}
accounts["789"].locked = True

test_operations = [
    ("123", "withdraw", 100),     # Should succeed
    ("123", "withdraw", 500),     # Should fail: insufficient funds (only 400 left)
    ("456", "withdraw", 50),      # Should succeed
    ("456", "withdraw", 1000),    # Should fail: insufficient funds
    ("123", "withdraw", 950),     # Should fail: daily limit
    ("789", "withdraw", 100),     # Should fail: account locked
]

for account_num, operation, amount in test_operations:
    account = accounts.get(account_num)
    try:
        if operation == "withdraw":
            result = account.withdraw(amount)
            print(f"✓ Withdrew ${amount} from {account_num}, balance: ${result}")
    except BankingError as e:
        print(f"✗ {type(e).__name__}: {e}")
```

---

## Exercise 6: Context Managers for Error Handling (Analyze)

**Bloom Level**: Analyze

Implement error handling with context managers:

```python
from contextlib import contextmanager
import time

@contextmanager
def error_boundary(operation_name: str, reraise: bool = True):
    """
    Context manager that catches and logs errors.

    Args:
        operation_name: Name of the operation (for logging).
        reraise: If True, re-raise the exception after logging.

    Usage:
        with error_boundary("database query"):
            run_query()
    """
    pass

@contextmanager
def timed_operation(operation_name: str, warn_threshold: float = 1.0):
    """
    Context manager that times an operation and warns if slow.

    Args:
        operation_name: Name of the operation.
        warn_threshold: Warn if operation takes longer (seconds).
    """
    pass

@contextmanager
def transaction(conn, auto_rollback: bool = True):
    """
    Context manager for database transactions.

    - Commits on success
    - Rolls back on error (if auto_rollback=True)
    - Always ensures connection is in clean state
    """
    pass

# Test error_boundary
print("Test 1: error_boundary with successful operation")
with error_boundary("calculation", reraise=True):
    result = 10 / 2
    print(f"Result: {result}")

print("\nTest 2: error_boundary with error (reraise=False)")
with error_boundary("risky operation", reraise=False):
    result = 10 / 0  # This will error but not crash

print("\nTest 3: timed_operation")
with timed_operation("slow task", warn_threshold=0.1):
    time.sleep(0.2)  # Simulate slow operation
    print("Task completed")
```

---

## Exercise 7: Retry Logic (Challenge)

**Bloom Level**: Create

Implement a robust retry mechanism:

```python
import random
import time
from typing import Callable, TypeVar

T = TypeVar('T')

class RetryError(Exception):
    """Raised when all retry attempts fail."""

    def __init__(self, message: str, attempts: int, last_error: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[int, Exception], None] = None,
) -> Callable:
    """
    Decorator that retries a function on failure.

    Args:
        max_attempts: Maximum number of attempts.
        delay: Initial delay between retries (seconds).
        backoff: Multiplier for delay after each retry.
        exceptions: Tuple of exceptions to catch and retry.
        on_retry: Optional callback called on each retry.

    Usage:
        @retry(max_attempts=3, delay=1.0)
        def flaky_function():
            ...
    """
    pass

# Test with a flaky function
call_count = 0

@retry(max_attempts=5, delay=0.1, backoff=1.5, exceptions=(ConnectionError, TimeoutError))
def flaky_api_call():
    """Simulates a flaky API that fails randomly."""
    global call_count
    call_count += 1
    print(f"  Attempt {call_count}...")

    if random.random() < 0.7:  # 70% chance of failure
        if random.random() < 0.5:
            raise ConnectionError("Connection refused")
        else:
            raise TimeoutError("Request timed out")

    return {"status": "success", "data": [1, 2, 3]}

# Run multiple times to see retry behavior
for i in range(3):
    call_count = 0
    print(f"\nTest run {i + 1}:")
    try:
        result = flaky_api_call()
        print(f"  Success: {result}")
    except RetryError as e:
        print(f"  Failed after {e.attempts} attempts: {e.last_error}")
```

---

## Exercise 8: Error Handling Best Practices (Evaluate)

**Bloom Level**: Evaluate

Review this code and identify all error handling issues:

```python
# BAD CODE - Find all the problems!
def process_user_data(user_id):
    try:
        # Fetch user from database
        user = database.get_user(user_id)

        # Process user data
        user['age'] = int(user['age'])
        user['email'] = user['email'].lower()

        # Save to file
        with open(f'/tmp/{user_id}.json', 'w') as f:
            f.write(str(user))

        # Send notification
        send_email(user['email'], "Profile updated")

        return True
    except:
        print("Something went wrong")
        return False
```

Rewrite this function with proper error handling:

```python
import json
from pathlib import Path
from typing import Optional

class UserProcessingError(Exception):
    """Error during user processing."""
    pass

class UserNotFoundError(UserProcessingError):
    """User not found in database."""
    pass

class DataValidationError(UserProcessingError):
    """User data validation failed."""
    pass

def process_user_data(user_id: str) -> dict:
    """
    Process user data with proper error handling.

    Args:
        user_id: The user's ID.

    Returns:
        The processed user data.

    Raises:
        UserNotFoundError: If user doesn't exist.
        DataValidationError: If user data is invalid.
        UserProcessingError: For other processing errors.
    """
    pass

# List of issues in the original code:
# 1. _______________
# 2. _______________
# 3. _______________
# ... (find at least 7 issues)
```

---

## Deliverables

Submit your code for all exercises. Include the list of issues found in Exercise 8.

---

[← Back to Chapter](../06_error_handling.md) | [View Solutions](../solutions/sol_06_error_handling.md) | [← Back to Module 1](../README.md)
