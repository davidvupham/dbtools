# Solutions — 06: Error Handling

## Key Concepts Demonstrated

- try/except/else/finally blocks
- Catching specific exception types
- Raising exceptions with meaningful messages
- Exception chaining with `raise ... from ...`
- Custom exception hierarchies
- Context managers for error handling
- Retry patterns with exponential backoff

## Common Mistakes to Avoid

- Using bare `except:` (catches everything including SystemExit, KeyboardInterrupt)
- Catching exceptions too broadly (catch specific types)
- Swallowing exceptions without logging
- Not using `finally` for cleanup
- Raising generic `Exception` instead of specific types
- Not preserving exception context with chaining

---

## Exercise 1 Solution

```python
def safe_convert(value: str, target_type: str) -> tuple[bool, any]:
    """Safely convert a string to the specified type."""
    try:
        if target_type == "int":
            return (True, int(value))
        elif target_type == "float":
            return (True, float(value))
        elif target_type == "bool":
            # Handle common boolean representations
            if value.lower() in ("true", "1", "yes", "on"):
                return (True, True)
            elif value.lower() in ("false", "0", "no", "off"):
                return (True, False)
            else:
                return (False, f"Cannot convert '{value}' to bool")
        else:
            return (False, f"Unknown target type: {target_type}")
    except ValueError:
        return (False, f"Cannot convert '{value}' to {target_type}")

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

**Output**:
```
✓ safe_convert('42', 'int') = 42
✗ safe_convert('hello', 'int') = Cannot convert 'hello' to int
✓ safe_convert('3.14', 'float') = 3.14
✗ safe_convert('not_a_float', 'float') = Cannot convert 'not_a_float' to float
✓ safe_convert('true', 'bool') = True
✓ safe_convert('false', 'bool') = False
✓ safe_convert('yes', 'bool') = True
✗ safe_convert('', 'int') = Cannot convert '' to int
```

---

## Exercise 2 Solution

```python
def get_config_value(config: dict, key: str, expected_type: type) -> any:
    """Get a configuration value with type checking."""
    # Check if key exists
    if key not in config:
        raise KeyError(f"Configuration key '{key}' not found")

    value = config[key]

    # Check for empty values
    if value is None or (isinstance(value, str) and value == ""):
        raise ValueError(f"Configuration key '{key}' has empty value")

    # Check type
    if not isinstance(value, expected_type):
        raise TypeError(
            f"Configuration key '{key}' expected {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )

    return value

# Test
config = {
    "port": 8080,
    "host": "localhost",
    "debug": True,
    "timeout": "30",
    "name": "",
}

test_cases = [
    ("port", int),
    ("host", str),
    ("missing", str),
    ("timeout", int),
    ("name", str),
]

for key, expected_type in test_cases:
    try:
        value = get_config_value(config, key, expected_type)
        print(f"✓ config[{key!r}] = {value!r}")
    except (KeyError, TypeError, ValueError) as e:
        print(f"✗ config[{key!r}]: {type(e).__name__}: {e}")
```

**Output**:
```
✓ config['port'] = 8080
✓ config['host'] = 'localhost'
✗ config['missing']: KeyError: Configuration key 'missing' not found
✗ config['timeout']: TypeError: Configuration key 'timeout' expected int, got str
✗ config['name']: ValueError: Configuration key 'name' has empty value
```

---

## Exercise 3 Solution

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
    """Run database queries with guaranteed cleanup."""
    db = DatabaseConnection(host)
    results = []

    try:
        db.connect()

        for query in queries:
            try:
                result = db.execute(query)
                results.append(result)
            except RuntimeError as e:
                print(f"Query failed: {e}")
                # Continue with remaining queries or break
                break

    except ConnectionError as e:
        print(f"Connection failed: {e}")

    finally:
        # Always disconnect if we have a connection object
        if db.connected:
            db.disconnect()

    return results

# Tests
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

## Exercise 4 Solution

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
    """Process a data record with proper exception chaining."""
    try:
        validate_data(data)
    except ValidationError:
        raise  # Re-raise validation errors as-is

    try:
        return transform_data(data)
    except DataProcessingError:
        raise  # Re-raise processing errors as-is

# Test cases
test_records = [
    {"name": "Alice", "age": 30, "email": "alice@example.com"},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": "thirty", "email": "c@example.com"},
    {"name": "", "age": 40, "email": "d@example.com"},
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

## Exercise 5 Solution

```python
class BankingError(Exception):
    """Base exception for banking operations."""
    pass

class InsufficientFundsError(BankingError):
    """Raised when account has insufficient funds."""
    def __init__(self, account_number: str, requested: float, available: float):
        self.account_number = account_number
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient funds in account {account_number}: "
            f"requested ${requested:.2f}, available ${available:.2f}"
        )

class InvalidAccountError(BankingError):
    """Raised when account is invalid or not found."""
    def __init__(self, account_number: str):
        self.account_number = account_number
        super().__init__(f"Invalid account: {account_number}")

class TransactionLimitError(BankingError):
    """Raised when transaction exceeds limits."""
    def __init__(self, account_number: str, limit: float, attempted: float):
        self.account_number = account_number
        self.limit = limit
        self.attempted = attempted
        super().__init__(
            f"Transaction limit exceeded for account {account_number}: "
            f"daily limit ${limit:.2f}, attempted ${attempted:.2f}"
        )

class AccountLockedError(BankingError):
    """Raised when account is locked."""
    def __init__(self, account_number: str):
        self.account_number = account_number
        super().__init__(f"Account {account_number} is locked")


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
        """Withdraw money from account."""
        if self.locked:
            raise AccountLockedError(self.account_number)

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.balance:
            raise InsufficientFundsError(
                self.account_number, amount, self.balance
            )

        if self.daily_withdrawn + amount > self.DAILY_LIMIT:
            raise TransactionLimitError(
                self.account_number,
                self.DAILY_LIMIT,
                self.daily_withdrawn + amount
            )

        self.balance -= amount
        self.daily_withdrawn += amount
        return self.balance

    def transfer(self, to_account: "BankAccount", amount: float) -> None:
        """Transfer money to another account."""
        # Withdraw from this account (handles all validations)
        self.withdraw(amount)

        try:
            # Deposit to target account
            to_account.deposit(amount)
        except BankingError:
            # Rollback: return money to source account
            self.balance += amount
            self.daily_withdrawn -= amount
            raise

# Test
accounts = {
    "123": BankAccount("123", balance=500),
    "456": BankAccount("456", balance=100),
    "789": BankAccount("789", balance=1000),
}
accounts["789"].locked = True

test_operations = [
    ("123", "withdraw", 100),
    ("123", "withdraw", 500),
    ("456", "withdraw", 50),
    ("456", "withdraw", 1000),
    ("123", "withdraw", 950),
    ("789", "withdraw", 100),
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

## Exercise 6 Solution

```python
from contextlib import contextmanager
import time
import traceback

@contextmanager
def error_boundary(operation_name: str, reraise: bool = True):
    """Context manager that catches and logs errors."""
    try:
        yield
    except Exception as e:
        print(f"[ERROR] {operation_name} failed: {type(e).__name__}: {e}")
        if reraise:
            raise

@contextmanager
def timed_operation(operation_name: str, warn_threshold: float = 1.0):
    """Context manager that times an operation and warns if slow."""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        if elapsed > warn_threshold:
            print(f"[WARN] {operation_name} took {elapsed:.2f}s (threshold: {warn_threshold}s)")
        else:
            print(f"[INFO] {operation_name} completed in {elapsed:.2f}s")

@contextmanager
def transaction(conn, auto_rollback: bool = True):
    """Context manager for database transactions."""
    try:
        yield conn
        conn.commit()
        print("Transaction committed")
    except Exception as e:
        if auto_rollback:
            conn.rollback()
            print(f"Transaction rolled back due to: {e}")
        raise

# Test error_boundary
print("Test 1: error_boundary with successful operation")
with error_boundary("calculation", reraise=True):
    result = 10 / 2
    print(f"Result: {result}")

print("\nTest 2: error_boundary with error (reraise=False)")
with error_boundary("risky operation", reraise=False):
    result = 10 / 0

print("\nTest 3: timed_operation")
with timed_operation("slow task", warn_threshold=0.1):
    time.sleep(0.2)
    print("Task completed")

print("\nTest 4: timed_operation (fast)")
with timed_operation("fast task", warn_threshold=1.0):
    x = sum(range(1000))
    print(f"Sum: {x}")
```

---

## Exercise 7 Solution

```python
import random
import time
from functools import wraps
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
    """Decorator that retries a function on failure."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts:
                        if on_retry:
                            on_retry(attempt, e)
                        print(f"    Retry {attempt}/{max_attempts - 1}: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise RetryError(
                f"Failed after {max_attempts} attempts",
                attempts=max_attempts,
                last_error=last_exception
            )

        return wrapper
    return decorator

# Test
call_count = 0

@retry(max_attempts=5, delay=0.1, backoff=1.5, exceptions=(ConnectionError, TimeoutError))
def flaky_api_call():
    """Simulates a flaky API that fails randomly."""
    global call_count
    call_count += 1
    print(f"  Attempt {call_count}...")

    if random.random() < 0.7:
        if random.random() < 0.5:
            raise ConnectionError("Connection refused")
        else:
            raise TimeoutError("Request timed out")

    return {"status": "success", "data": [1, 2, 3]}

# Run multiple times
random.seed(42)  # For reproducible results
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

## Exercise 8 Solution

### Issues in Original Code:

1. **Bare `except:` clause** - Catches everything including `SystemExit`, `KeyboardInterrupt`
2. **No specific exception handling** - All errors treated the same
3. **Silent failure** - Just prints "Something went wrong" with no details
4. **No logging** - Print is not proper logging
5. **Using `str(user)` for JSON** - Should use `json.dumps()`
6. **Hardcoded path** - `/tmp/` may not exist on all systems
7. **No validation** - Accessing dict keys without checking they exist
8. **No type hints** - Function signature unclear
9. **Returns `True/False`** - Should raise exceptions or return meaningful data
10. **No transaction/rollback** - If email fails, file is already written

### Corrected Code:

```python
import json
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserProcessingError(Exception):
    """Error during user processing."""
    pass

class UserNotFoundError(UserProcessingError):
    """User not found in database."""
    pass

class DataValidationError(UserProcessingError):
    """User data validation failed."""
    pass

class NotificationError(UserProcessingError):
    """Failed to send notification."""
    pass


def process_user_data(user_id: str, output_dir: Optional[Path] = None) -> dict:
    """
    Process user data with proper error handling.

    Args:
        user_id: The user's ID.
        output_dir: Directory to save processed data (optional).

    Returns:
        The processed user data.

    Raises:
        UserNotFoundError: If user doesn't exist.
        DataValidationError: If user data is invalid.
        UserProcessingError: For other processing errors.
    """
    logger.info(f"Processing user {user_id}")

    # Fetch user from database
    try:
        user = database.get_user(user_id)
    except DatabaseError as e:
        logger.error(f"Database error for user {user_id}: {e}")
        raise UserNotFoundError(f"User {user_id} not found") from e

    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")

    # Validate required fields
    required_fields = ["age", "email"]
    for field in required_fields:
        if field not in user:
            raise DataValidationError(f"Missing required field: {field}")

    # Process user data
    try:
        user["age"] = int(user["age"])
    except (ValueError, TypeError) as e:
        raise DataValidationError(f"Invalid age value: {user.get('age')}") from e

    try:
        user["email"] = user["email"].lower().strip()
    except AttributeError as e:
        raise DataValidationError(f"Invalid email value: {user.get('email')}") from e

    # Save to file (if output_dir provided)
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{user_id}.json"

        try:
            with output_file.open("w", encoding="utf-8") as f:
                json.dump(user, f, indent=2)
            logger.info(f"Saved user data to {output_file}")
        except IOError as e:
            raise UserProcessingError(f"Failed to save user data: {e}") from e

    # Send notification (non-critical, don't fail processing)
    try:
        send_email(user["email"], "Profile updated")
        logger.info(f"Notification sent to {user['email']}")
    except EmailError as e:
        logger.warning(f"Failed to send notification: {e}")
        # Don't raise - notification failure is non-critical

    logger.info(f"Successfully processed user {user_id}")
    return user


# Usage example
try:
    user_data = process_user_data("12345", output_dir=Path("./data"))
    print(f"Processed: {user_data}")
except UserNotFoundError as e:
    print(f"User error: {e}")
except DataValidationError as e:
    print(f"Validation error: {e}")
except UserProcessingError as e:
    print(f"Processing error: {e}")
```

---

## Error Handling Best Practices Summary

1. **Be specific** - Catch only the exceptions you can handle
2. **Preserve context** - Use exception chaining (`raise ... from ...`)
3. **Fail fast** - Validate inputs early
4. **Log appropriately** - Use proper logging, not print
5. **Clean up resources** - Use `finally` or context managers
6. **Create hierarchies** - Custom exceptions for your domain
7. **Document exceptions** - Include in docstrings what can be raised
8. **Don't swallow errors** - At minimum, log them
9. **Use type hints** - Make error handling expectations clear
10. **Test error paths** - Errors are part of your API

---

[← Back to Exercises](../exercises/ex_06_error_handling.md) | [← Back to Chapter](../06_error_handling.md) | [← Back to Module 1](../README.md)
