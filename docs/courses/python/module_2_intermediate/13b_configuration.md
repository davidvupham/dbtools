# Configuration Management

Hardcoding values is fine... until it isn't. Professional Python applications separate configuration from code, making them environment-aware, test-friendly, and deployment-safe.

## The Problem with Global Constants

```python
# Bad: Hardcoded values scattered throughout code
DB_URL = "postgresql://localhost/dev"
API_KEY = "sk-abc123"
DEBUG = True
MAX_RETRIES = 3
```

Problems:

- Changing environments requires code changes
- Secrets might get committed to version control
- Testing requires modifying source code
- No validation that config values are correct

**Rule**: If changing environments requires code edits, your structure is wrong.

---

## Configuration Sources

Configuration should come from external sources, not code:

| Source | Use Case | Example |
|--------|----------|---------|
| Environment variables | Secrets, deployment config | `DATABASE_URL`, `API_KEY` |
| `.env` files | Local development | `.env.local`, `.env.test` |
| Config files | Complex settings | `config.yaml`, `settings.json` |
| Command-line args | Runtime overrides | `--debug`, `--port 8080` |

---

## Environment Variables

The simplest and most secure approach for secrets.

### Reading Environment Variables

```python
import os

# Basic usage
db_url = os.getenv("DATABASE_URL")

# With default value
debug = os.getenv("DEBUG", "false").lower() == "true"

# Required variable (raises if missing)
api_key = os.environ["API_KEY"]  # KeyError if not set
```

### Checking Required Variables

```python
def get_required_env(name: str) -> str:
    """Get required environment variable or raise clear error."""
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Required environment variable '{name}' is not set")
    return value

database_url = get_required_env("DATABASE_URL")
```

---

## Using `.env` Files

The `python-dotenv` package loads variables from a `.env` file into environment variables.

### Setup

```bash
uv add python-dotenv
```

### The `.env` File

```bash
# .env - DO NOT COMMIT THIS FILE
DATABASE_URL=postgresql://localhost:5432/myapp
API_KEY=sk-dev-key-12345
DEBUG=true
LOG_LEVEL=INFO
```

### Loading `.env` Variables

```python
from dotenv import load_dotenv
import os

# Load .env file (typically at app startup)
load_dotenv()

# Now environment variables are available
db_url = os.getenv("DATABASE_URL")
```

### Multiple Environment Files

```python
from dotenv import load_dotenv
import os

# Load based on environment
env = os.getenv("APP_ENV", "development")
load_dotenv(f".env.{env}")  # .env.development, .env.test, .env.production
load_dotenv(".env")  # Fallback to default .env
```

### Git Configuration

Always exclude `.env` files from version control:

```gitignore
# .gitignore
.env
.env.*
!.env.example
```

Provide an example file without secrets:

```bash
# .env.example - COMMIT THIS FILE
DATABASE_URL=postgresql://localhost:5432/myapp
API_KEY=your-api-key-here
DEBUG=false
LOG_LEVEL=INFO
```

---

## Typed Configuration with Dataclasses

Use dataclasses or Pydantic for validated, type-safe configuration.

### Dataclass Approach

```python
from dataclasses import dataclass
from os import getenv

@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass(frozen=True)
class AppConfig:
    debug: bool
    log_level: str
    database: DatabaseConfig

def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        debug=getenv("DEBUG", "false").lower() == "true",
        log_level=getenv("LOG_LEVEL", "INFO"),
        database=DatabaseConfig(
            host=getenv("DB_HOST", "localhost"),
            port=int(getenv("DB_PORT", "5432")),
            name=getenv("DB_NAME", "app"),
            user=getenv("DB_USER", "postgres"),
            password=getenv("DB_PASSWORD", ""),
        ),
    )
```

### Using the Config

```python
# Load once at startup
config = load_config()

# Pass explicitly to functions that need it
def connect_database(config: DatabaseConfig) -> Connection:
    return create_connection(config.url)

# In main.py
def main():
    config = load_config()
    db = connect_database(config.database)
    app = create_app(config)
    app.run()
```

---

## Pydantic Settings (Recommended)

Pydantic provides powerful configuration management with automatic validation.

### Setup

```bash
uv add pydantic-settings
```

### Defining Settings

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "app"
    user: str = "postgres"
    password: str = ""

    model_config = SettingsConfigDict(env_prefix="DB_")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class AppSettings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    api_key: str = Field(min_length=10)  # Validation!
    max_connections: int = Field(ge=1, le=100, default=10)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
```

### Automatic Environment Variable Loading

```python
# With env vars: DEBUG=true LOG_LEVEL=DEBUG API_KEY=sk-prod-key-123
settings = AppSettings()

print(settings.debug)      # True (parsed from string)
print(settings.log_level)  # "DEBUG"
print(settings.api_key)    # "sk-prod-key-123"
```

### Nested Settings

```python
class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

# Env vars: DATABASE__HOST=prod-db.example.com DATABASE__PORT=5433
settings = Settings()
print(settings.database.host)  # "prod-db.example.com"
```

---

## Configuration Patterns

### Pattern 1: Load Once, Pass Explicitly

```python
# config.py
_config: AppConfig | None = None

def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = load_config()
    return _config

# main.py
def main():
    config = get_config()
    app = create_app(config)
    app.run()

# services.py - config passed explicitly
def process_payment(config: AppConfig, payment_data: dict) -> bool:
    if config.debug:
        log.debug(f"Processing: {payment_data}")
    # ...
```

### Pattern 2: Dependency Injection

```python
from dataclasses import dataclass

@dataclass
class PaymentService:
    config: AppConfig
    gateway: PaymentGateway

    def process(self, amount: float) -> bool:
        if self.config.debug:
            return True  # Skip in debug mode
        return self.gateway.charge(amount)

# main.py
config = load_config()
gateway = create_gateway(config)
service = PaymentService(config=config, gateway=gateway)
```

### Pattern 3: Environment-Specific Defaults

```python
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

def load_config() -> AppConfig:
    env = Environment(getenv("APP_ENV", "development"))

    defaults = {
        Environment.DEVELOPMENT: {"debug": True, "log_level": "DEBUG"},
        Environment.TESTING: {"debug": True, "log_level": "WARNING"},
        Environment.PRODUCTION: {"debug": False, "log_level": "INFO"},
    }

    return AppConfig(
        debug=getenv("DEBUG", str(defaults[env]["debug"])).lower() == "true",
        log_level=getenv("LOG_LEVEL", defaults[env]["log_level"]),
        # ...
    )
```

---

## Testing with Configuration

### Override Config in Tests

```python
# conftest.py
import pytest
from myapp.config import AppConfig, DatabaseConfig

@pytest.fixture
def test_config() -> AppConfig:
    """Provide test configuration."""
    return AppConfig(
        debug=True,
        log_level="DEBUG",
        database=DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test",
            password="test",
        ),
    )

# test_services.py
def test_payment_processing(test_config):
    service = PaymentService(config=test_config)
    assert service.process(100.00) is True
```

### Environment Variable Mocking

```python
import pytest
from unittest.mock import patch

def test_config_from_env():
    with patch.dict("os.environ", {"DEBUG": "true", "LOG_LEVEL": "ERROR"}):
        config = load_config()
        assert config.debug is True
        assert config.log_level == "ERROR"
```

---

## Best Practices Summary

1. **Never hardcode secrets** - Use environment variables
2. **Use `.env` for development** - But never commit it
3. **Validate configuration** - Use Pydantic or dataclasses
4. **Load once, pass explicitly** - Avoid global config access
5. **Provide `.env.example`** - Document required variables
6. **Type your config** - Catch errors early
7. **Support multiple environments** - dev, test, production
8. **Test with config overrides** - Don't depend on real environment

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Dependencies](13a_dependencies.md) | [Module 2](../README.md) | [Logging](14_logging.md) |
