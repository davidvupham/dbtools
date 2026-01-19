# Testing and CI

This guide covers testing requirements and CI integration for Python packages.

## Testing Requirements

### Minimum Requirements

Every package must have:

- [ ] `tests/` directory at package root
- [ ] `tests/conftest.py` for shared fixtures
- [ ] At least one test file (`test_*.py`)
- [ ] Tests pass with `pytest`

### Coverage Targets

| Package Type | Minimum Coverage |
|--------------|------------------|
| Core libraries (`gds_database`) | 90% |
| Service clients (`gds_vault`) | 80% |
| Utilities | 70% |
| New packages | Start at 70%, increase over time |

---

## Test Structure

### Directory Layout

```
python/gds_vault/
├── src/gds_vault/
│   ├── __init__.py
│   ├── client.py
│   └── auth.py
└── tests/
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── test_client.py        # Tests for client.py
    ├── test_auth.py          # Tests for auth.py
    └── integration/          # Optional: integration tests
        ├── conftest.py
        └── test_live_vault.py
```

### Test File Naming

| Pattern | Purpose |
|---------|---------|
| `test_<module>.py` | Unit tests for a module |
| `test_<feature>.py` | Feature-specific tests |
| `integration/test_*.py` | Integration tests |
| `conftest.py` | Shared fixtures |

---

## Writing Tests

### Basic Test Structure

```python
"""Tests for gds_vault.client module."""

import pytest
from gds_vault import VaultClient
from gds_vault.exceptions import VaultError


class TestVaultClient:
    """Tests for VaultClient class."""

    def test_init_with_valid_config(self, mock_config):
        """Client initializes with valid configuration."""
        client = VaultClient(**mock_config)
        assert client.host == mock_config["host"]

    def test_init_missing_host_raises(self):
        """Client raises ValueError when host is missing."""
        with pytest.raises(ValueError, match="host is required"):
            VaultClient(host=None)

    def test_read_secret_returns_data(self, mock_client, mock_response):
        """Reading a secret returns the expected data."""
        result = mock_client.read("secret/data/test")
        assert result == mock_response["data"]
```

### Fixtures

```python
# conftest.py
"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_config():
    """Provide test configuration."""
    return {
        "host": "https://vault.example.com",
        "token": "test-token",
        "timeout": 30,
    }


@pytest.fixture
def mock_client(mock_config):
    """Provide a configured mock client."""
    with patch("gds_vault.client.requests") as mock_requests:
        mock_requests.get.return_value.json.return_value = {"data": {"key": "value"}}
        client = VaultClient(**mock_config)
        yield client


@pytest.fixture
def mock_response():
    """Provide a mock API response."""
    return {
        "data": {"key": "value"},
        "metadata": {"version": 1},
    }
```

### Parameterized Tests

```python
import pytest


@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("MiXeD", "MIXED"),
])
def test_uppercase_conversion(input_value, expected):
    """String is converted to uppercase correctly."""
    assert input_value.upper() == expected


@pytest.mark.parametrize("invalid_input", [
    None,
    123,
    [],
    {},
])
def test_uppercase_rejects_non_strings(invalid_input):
    """Non-string inputs raise AttributeError."""
    with pytest.raises(AttributeError):
        invalid_input.upper()
```

### Async Tests

```python
import pytest


@pytest.mark.asyncio
async def test_async_read_secret(async_client):
    """Async client reads secrets correctly."""
    result = await async_client.read("secret/data/test")
    assert result["key"] == "value"


@pytest.mark.asyncio
async def test_async_write_secret(async_client):
    """Async client writes secrets correctly."""
    await async_client.write("secret/data/test", {"new": "data"})
    result = await async_client.read("secret/data/test")
    assert result["new"] == "data"
```

---

## Test Markers

### Standard Markers

```python
import pytest


@pytest.mark.unit
def test_fast_unit_test():
    """Quick unit test."""
    assert True


@pytest.mark.integration
def test_database_connection():
    """Requires database connection."""
    pass


@pytest.mark.slow
def test_large_dataset():
    """Takes a long time to run."""
    pass


@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Placeholder for future work."""
    pass


@pytest.mark.skipif(
    condition=True,
    reason="Skipped in CI environment"
)
def test_local_only():
    """Only runs locally."""
    pass
```

### Running by Marker

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

### Registering Markers

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests requiring external services",
    "slow: Tests that take a long time",
]
```

---

## Mocking

### External Services

```python
from unittest.mock import patch, Mock


def test_api_call():
    """Mock external API calls."""
    with patch("mymodule.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": "value"}
        mock_get.return_value.status_code = 200

        result = my_function()

        mock_get.assert_called_once_with("https://api.example.com/data")
        assert result == {"data": "value"}
```

### Database Connections

```python
@pytest.fixture
def mock_db():
    """Provide a mock database connection."""
    mock = Mock()
    mock.execute.return_value.fetchall.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    return mock


def test_query_users(mock_db):
    """Query returns user data."""
    result = get_users(mock_db)
    assert len(result) == 2
    mock_db.execute.assert_called_once()
```

### Environment Variables

```python
import os


def test_reads_config_from_env(monkeypatch):
    """Configuration reads from environment variables."""
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example.com")
    monkeypatch.setenv("VAULT_TOKEN", "test-token")

    config = load_config()

    assert config.vault_addr == "https://vault.example.com"
    assert config.vault_token == "test-token"
```

---

## Running Tests

### Local Development

```bash
# Run all tests
make test

# Run specific package tests
pytest python/gds_vault/tests/ -v

# Run single test file
pytest python/gds_vault/tests/test_client.py -v

# Run single test
pytest python/gds_vault/tests/test_client.py::TestVaultClient::test_init -v

# Run with coverage
pytest python/gds_vault/tests/ --cov=gds_vault --cov-report=html

# Run in parallel
pytest python/gds_vault/tests/ -n auto
```

### CI Configuration

Tests run automatically on:
- Pull request creation
- Push to main branch
- Manual trigger

```yaml
# .github/workflows/test.yml (example)
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --all-groups
      - run: make lint
      - run: make test
```

---

## Coverage

### Generating Reports

```bash
# Terminal report
pytest --cov=gds_vault --cov-report=term-missing

# HTML report
pytest --cov=gds_vault --cov-report=html
open htmlcov/index.html

# XML for CI
pytest --cov=gds_vault --cov-report=xml
```

### Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=gds_vault",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]
```

### Excluding Code from Coverage

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .types import SomeType


def debug_only():  # pragma: no cover
    """Only used during debugging."""
    print("Debug info")
```

---

## Pre-Commit Hooks

### Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### Running Hooks

```bash
# Run all hooks
make pre-commit

# Run specific hook
pre-commit run ruff --all-files

# Install hooks (runs automatically on commit)
pre-commit install
```

---

## Best Practices

### Do

- Write tests before or alongside code
- Test behavior, not implementation
- Use descriptive test names that explain what's tested
- Keep tests independent (no shared state between tests)
- Use fixtures for common setup
- Mock external dependencies
- Test edge cases and error conditions

### Don't

- Test private methods directly
- Share state between tests
- Make tests depend on execution order
- Mock too much (if everything is mocked, what are you testing?)
- Ignore flaky tests (fix or remove them)
- Write tests that take minutes to run

### Test Naming

```python
# Good: Describes behavior
def test_read_secret_returns_data_when_path_exists():
    pass

def test_read_secret_raises_not_found_when_path_missing():
    pass

# Bad: Vague names
def test_read():
    pass

def test_error():
    pass
```

---

## Troubleshooting

### Import Errors in Tests

**Problem**: `ModuleNotFoundError` when running tests

**Solution**: Ensure PYTHONPATH includes src directories:

```bash
PYTHONPATH=.:python/gds_vault/src pytest python/gds_vault/tests/ -v
```

Or configure in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = [".", "python/gds_vault/src"]
```

### Fixture Not Found

**Problem**: `fixture 'my_fixture' not found`

**Solution**:
1. Check fixture is in `conftest.py`
2. Check `conftest.py` is in correct directory
3. Check fixture name matches

### Async Test Not Running

**Problem**: Async test completes immediately without running

**Solution**: Add the `asyncio` marker:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected
```

And ensure pytest-asyncio is installed:

```toml
[dependency-groups]
test = ["pytest-asyncio>=0.21"]
```
