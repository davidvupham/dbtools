# Faker Tutorial

Generate realistic test data for Python applications.

## Overview

**Faker** is a Python library that generates fake but realistic-looking data for testing, development, and data anonymization. It can create names, addresses, emails, dates, text, and much more.

| | |
|---|---|
| **Package** | `faker` |
| **Install** | `pip install Faker` |
| **Documentation** | [faker.readthedocs.io](https://faker.readthedocs.io/) |
| **GitHub** | [joke2k/faker](https://github.com/joke2k/faker) |

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Standard Providers](#standard-providers)
4. [Localization](#localization)
5. [Seeding for Reproducibility](#seeding-for-reproducibility)
6. [Custom Providers](#custom-providers)
7. [Integration with pytest](#integration-with-pytest)
8. [Factory Patterns](#factory-patterns)
9. [Performance Tips](#performance-tips)
10. [Best Practices](#best-practices)

---

## Installation

```bash
pip install Faker
```

For specific locales (optional):

```bash
pip install Faker[zh_CN]  # Chinese
pip install Faker[ja_JP]  # Japanese
```

---

## Quick Start

```python
from faker import Faker

# Create a Faker instance
fake = Faker()

# Generate fake data
print(fake.name())          # 'John Smith'
print(fake.email())         # 'john.smith@example.com'
print(fake.address())       # '123 Main St, Anytown, USA'
print(fake.date())          # '2023-05-15'
print(fake.text())          # Lorem ipsum paragraph
```

### Generate Multiple Records

```python
from faker import Faker

fake = Faker()

# Generate 10 fake users
users = []
for _ in range(10):
    user = {
        'name': fake.name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.address(),
        'company': fake.company(),
        'job': fake.job(),
    }
    users.append(user)

for user in users:
    print(f"{user['name']} - {user['email']}")
```

---

## Standard Providers

Faker includes many built-in providers for common data types.

### Person Data

```python
fake.name()             # Full name
fake.first_name()       # First name only
fake.last_name()        # Last name only
fake.prefix()           # Mr., Mrs., Dr., etc.
fake.suffix()           # Jr., Sr., PhD, etc.
```

### Contact Information

```python
fake.email()            # Email address
fake.safe_email()       # Email with safe domain (example.com)
fake.phone_number()     # Phone number
fake.address()          # Full address
fake.street_address()   # Street only
fake.city()             # City name
fake.state()            # State/Province
fake.country()          # Country name
fake.postcode()         # Postal/ZIP code
```

### Internet Data

```python
fake.url()              # URL
fake.domain_name()      # Domain name
fake.ipv4()             # IPv4 address
fake.ipv6()             # IPv6 address
fake.user_agent()       # Browser user agent
fake.mac_address()      # MAC address
fake.user_name()        # Username
fake.password()         # Password
```

### Date and Time

```python
fake.date()                    # Date string
fake.time()                    # Time string
fake.date_time()               # DateTime object
fake.date_between('-30y', 'today')  # Date in range
fake.date_of_birth()           # Realistic birth date
fake.future_date()             # Future date
fake.past_date()               # Past date
```

### Text Data

```python
fake.text()             # Paragraph of text
fake.sentence()         # Single sentence
fake.paragraph()        # Single paragraph
fake.word()             # Single word
fake.words(5)           # List of 5 words
fake.catch_phrase()     # Business catchphrase
fake.bs()               # Business buzzword
```

### Financial Data

```python
fake.credit_card_number()       # Credit card number
fake.credit_card_provider()     # Visa, MasterCard, etc.
fake.credit_card_expire()       # Expiration date
fake.credit_card_security_code()  # CVV
fake.iban()                     # IBAN number
fake.bban()                     # BBAN number
fake.currency()                 # Currency tuple (code, name)
fake.cryptocurrency()           # Cryptocurrency tuple
```

### File Data

```python
fake.file_name()        # Filename with extension
fake.file_extension()   # File extension
fake.file_path()        # Full file path
fake.mime_type()        # MIME type
```

### Miscellaneous

```python
fake.uuid4()            # UUID
fake.boolean()          # True or False
fake.md5()              # MD5 hash
fake.sha256()           # SHA256 hash
fake.color_name()       # Color name
fake.hex_color()        # Hex color code
fake.json()             # Random JSON object
```

---

## Localization

Faker supports many locales for generating culturally appropriate data.

### Single Locale

```python
from faker import Faker

# German locale
fake_de = Faker('de_DE')
print(fake_de.name())    # 'Hans Müller'
print(fake_de.address()) # German-formatted address

# Japanese locale
fake_ja = Faker('ja_JP')
print(fake_ja.name())    # '山田 太郎'

# French locale
fake_fr = Faker('fr_FR')
print(fake_fr.name())    # 'Jean Dupont'
```

### Multiple Locales

```python
from faker import Faker

# Create instance with multiple locales
fake = Faker(['en_US', 'de_DE', 'ja_JP'])

# Randomly picks from available locales
for _ in range(5):
    print(fake.name())
```

### Weighted Locales

```python
from faker import Faker

# 70% US, 20% UK, 10% Australia
fake = Faker({
    'en_US': 0.7,
    'en_GB': 0.2,
    'en_AU': 0.1,
})
```

### Common Locales

| Locale | Language/Country |
|--------|-----------------|
| `en_US` | English (USA) |
| `en_GB` | English (UK) |
| `de_DE` | German (Germany) |
| `fr_FR` | French (France) |
| `es_ES` | Spanish (Spain) |
| `it_IT` | Italian (Italy) |
| `ja_JP` | Japanese (Japan) |
| `zh_CN` | Chinese (Simplified) |
| `ko_KR` | Korean (South Korea) |
| `pt_BR` | Portuguese (Brazil) |

---

## Seeding for Reproducibility

Set a seed to generate the same data every time.

```python
from faker import Faker

fake = Faker()
Faker.seed(12345)  # Global seed

# These will always produce the same values
print(fake.name())   # Always 'Adam Bryan'
print(fake.email())  # Always 'adam.bryan@example.com'
```

### Instance-Level Seeding

```python
from faker import Faker

fake1 = Faker()
fake2 = Faker()

fake1.seed_instance(1234)
fake2.seed_instance(1234)

# Both produce identical sequences
print(fake1.name())  # 'John Doe'
print(fake2.name())  # 'John Doe' (same!)
```

### Use Case: Reproducible Tests

```python
import pytest
from faker import Faker

@pytest.fixture
def fake():
    """Provide a seeded Faker instance for reproducible tests."""
    f = Faker()
    f.seed_instance(42)
    return f

def test_user_creation(fake):
    # Same data every test run
    name = fake.name()
    email = fake.email()
    assert '@' in email
```

---

## Custom Providers

Create your own providers for domain-specific data.

### Basic Custom Provider

```python
from faker import Faker
from faker.providers import BaseProvider

class DatabaseProvider(BaseProvider):
    """Custom provider for database-related fake data."""

    def database_name(self):
        prefixes = ['prod', 'dev', 'staging', 'test']
        names = ['users', 'orders', 'inventory', 'analytics']
        return f"{self.random_element(prefixes)}_{self.random_element(names)}_db"

    def table_name(self):
        tables = ['users', 'orders', 'products', 'sessions', 'logs']
        return self.random_element(tables)

    def column_name(self):
        columns = ['id', 'created_at', 'updated_at', 'name', 'email', 'status']
        return self.random_element(columns)

# Register and use
fake = Faker()
fake.add_provider(DatabaseProvider)

print(fake.database_name())  # 'prod_users_db'
print(fake.table_name())     # 'orders'
print(fake.column_name())    # 'created_at'
```

### Provider with Dependencies

```python
from faker import Faker
from faker.providers import BaseProvider

class ServerProvider(BaseProvider):
    """Provider for server/infrastructure data."""

    def server_name(self):
        environments = ['prod', 'stg', 'dev']
        roles = ['web', 'db', 'cache', 'worker']
        number = self.random_int(1, 99)
        return f"{self.random_element(environments)}-{self.random_element(roles)}-{number:02d}"

    def server_ip(self):
        # Use built-in ipv4 from internet provider
        return self.generator.ipv4_private()

    def server_port(self):
        common_ports = [22, 80, 443, 3306, 5432, 6379, 8080, 8443]
        return self.random_element(common_ports)

fake = Faker()
fake.add_provider(ServerProvider)

print(fake.server_name())  # 'prod-web-42'
print(fake.server_ip())    # '10.0.0.123'
print(fake.server_port())  # 5432
```

---

## Integration with pytest

### Using pytest-faker

```bash
pip install pytest-faker
```

```python
# test_users.py
def test_user_model(faker):
    """pytest-faker provides a 'faker' fixture automatically."""
    user = User(
        name=faker.name(),
        email=faker.email(),
        created_at=faker.date_time()
    )
    assert user.name is not None
    assert '@' in user.email
```

### Custom Fixture with Seeding

```python
# conftest.py
import pytest
from faker import Faker

@pytest.fixture(scope='session')
def fake():
    """Session-scoped Faker with consistent seed."""
    f = Faker()
    f.seed_instance(42)
    return f

@pytest.fixture
def user_data(fake):
    """Generate consistent user test data."""
    return {
        'name': fake.name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
    }
```

### Parametrized Tests with Faker

```python
import pytest
from faker import Faker

fake = Faker()
fake.seed_instance(123)

# Generate test data once
test_emails = [fake.email() for _ in range(5)]

@pytest.mark.parametrize("email", test_emails)
def test_email_validation(email):
    assert '@' in email
    assert len(email) > 5
```

---

## Factory Patterns

Combine Faker with factory patterns for complex test data.

### Using factory_boy

```bash
pip install factory_boy
```

```python
import factory
from faker import Faker
from myapp.models import User, Order

fake = Faker()

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    created_at = factory.LazyFunction(fake.date_time_this_year)

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    amount = factory.LazyFunction(lambda: fake.pydecimal(min_value=10, max_value=1000))
    status = factory.LazyFunction(lambda: fake.random_element(['pending', 'complete', 'cancelled']))

# Usage
user = UserFactory()
order = OrderFactory(user=user)

# Batch creation
users = UserFactory.build_batch(10)
```

### Simple Factory Pattern

```python
from dataclasses import dataclass
from datetime import datetime
from faker import Faker

fake = Faker()
fake.seed_instance(42)

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime

class UserFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides) -> User:
        cls._counter += 1
        defaults = {
            'id': cls._counter,
            'name': fake.name(),
            'email': fake.email(),
            'created_at': fake.date_time_this_year(),
        }
        defaults.update(overrides)
        return User(**defaults)

    @classmethod
    def create_batch(cls, count: int, **overrides) -> list[User]:
        return [cls.create(**overrides) for _ in range(count)]

# Usage
user = UserFactory.create()
user_with_custom_email = UserFactory.create(email='test@example.com')
users = UserFactory.create_batch(5)
```

---

## Performance Tips

### Avoid Recreating Instances

```python
# ❌ Bad - creates new instance each time
def get_fake_user():
    fake = Faker()  # Expensive!
    return fake.name()

# ✅ Good - reuse instance
fake = Faker()

def get_fake_user():
    return fake.name()
```

### Use unique Carefully

```python
fake = Faker()

# unique guarantees no duplicates but tracks all values in memory
# Can be slow/memory-intensive for large datasets
emails = [fake.unique.email() for _ in range(1000)]

# Clear unique cache when done
fake.unique.clear()
```

### Batch Generation

```python
from faker import Faker

fake = Faker()

# Generate large datasets efficiently
def generate_users(count: int) -> list[dict]:
    """Generate users without creating unnecessary objects."""
    return [
        {
            'name': fake.name(),
            'email': fake.email(),
        }
        for _ in range(count)
    ]

# For very large datasets, use a generator
def generate_users_lazy(count: int):
    """Memory-efficient generator for large datasets."""
    for _ in range(count):
        yield {
            'name': fake.name(),
            'email': fake.email(),
        }
```

---

## Best Practices

### 1. Seed in Tests

Always seed Faker in tests for reproducibility:

```python
@pytest.fixture(autouse=True)
def seed_faker():
    Faker.seed(42)
```

### 2. Use Appropriate Locales

Match the locale to your target audience:

```python
# Testing European compliance
fake_eu = Faker('de_DE')

# Testing US-specific features
fake_us = Faker('en_US')
```

### 3. Create Reusable Factories

Don't scatter Faker calls everywhere:

```python
# ❌ Scattered throughout codebase
def test_something():
    fake = Faker()
    user = {'name': fake.name(), 'email': fake.email()}

# ✅ Centralized in factories
from tests.factories import UserFactory

def test_something():
    user = UserFactory.create()
```

### 4. Clear Unique Constraints

Prevent memory leaks in long-running processes:

```python
for batch in range(100):
    emails = [fake.unique.email() for _ in range(100)]
    process(emails)
    fake.unique.clear()  # Clear after each batch
```

### 5. Document Custom Providers

```python
class PaymentProvider(BaseProvider):
    """
    Custom provider for payment-related test data.

    Methods:
        transaction_id(): Generate a realistic transaction ID
        payment_status(): Random payment status

    Usage:
        fake.add_provider(PaymentProvider)
        fake.transaction_id()
    """
```

---

## Quick Reference

| Method | Output Example |
|--------|----------------|
| `fake.name()` | 'John Smith' |
| `fake.email()` | '<jsmith@example.com>' |
| `fake.phone_number()` | '555-123-4567' |
| `fake.address()` | '123 Main St, City, ST 12345' |
| `fake.date()` | '2023-05-15' |
| `fake.uuid4()` | 'a1b2c3d4-...' |
| `fake.boolean()` | True |
| `fake.random_int(1, 100)` | 42 |
| `fake.random_element(['a', 'b'])` | 'a' |
| `fake.text(max_nb_chars=50)` | 'Lorem ipsum...' |

---

## See Also

- [Faker Official Documentation](https://faker.readthedocs.io/)
- [pytest-faker Plugin](https://pypi.org/project/pytest-faker/)
- [factory_boy Documentation](https://factoryboy.readthedocs.io/)
- [Pandas Tutorial](../pandas/README.md) - Use Faker data with Pandas DataFrames

---

[← Back to Modules Index](../README.md)
