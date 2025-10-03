# Testing Guide for Snowflake Replication Monitor

This document provides comprehensive information about testing the Snowflake Replication Monitor application.

## Overview

The test suite includes:
- **Unit Tests**: Test individual components in isolation with mocked dependencies
- **Integration Tests**: Test how components work together
- **Pytest Support**: Alternative test framework with fixtures and plugins

## Test Structure

```
snowflake/
├── tests/
│   ├── __init__.py
│   ├── test_snowflake_connection.py      # Unit tests for connection module
│   ├── test_snowflake_replication.py     # Unit tests for replication module
│   ├── test_monitor_integration.py       # Integration tests
│   └── test_connection_pytest.py         # Pytest examples
├── run_tests.py                           # Test runner script
├── pytest.ini                             # Pytest configuration
├── requirements-dev.txt                   # Development dependencies
└── test_modules.py                        # Module validation script
```

## Running Tests

### Option 1: Using the Test Runner (unittest)

The `run_tests.py` script provides a convenient way to run all tests:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run quietly (show only summary)
python run_tests.py -q

# Run specific test module
python run_tests.py -m test_snowflake_connection
python run_tests.py -m test_snowflake_replication
python run_tests.py -m test_monitor_integration
```

### Option 2: Using unittest directly

```bash
# Run all tests
python -m unittest discover -s tests -p "test*.py" -v

# Run specific test file
python -m unittest tests.test_snowflake_connection

# Run specific test class
python -m unittest tests.test_snowflake_connection.TestSnowflakeConnection

# Run specific test method
python -m unittest tests.test_snowflake_connection.TestSnowflakeConnection.test_init
```

### Option 3: Using pytest (if installed)

```bash
# Install pytest first
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_snowflake_connection.py

# Run specific test class
pytest tests/test_snowflake_connection.py::TestSnowflakeConnection

# Run specific test method
pytest tests/test_snowflake_connection.py::TestSnowflakeConnection::test_init

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run tests by marker
pytest -m unit
pytest -m integration
```

## Test Categories

### Unit Tests

Unit tests test individual components in isolation with all external dependencies mocked.

**test_snowflake_connection.py**
- Connection initialization
- Connection establishment
- Query execution
- Connection lifecycle (close, context manager)
- Error handling

**test_snowflake_replication.py**
- FailoverGroup class functionality
- Replication operations
- Cron schedule parsing
- Failure detection
- Latency calculation

### Integration Tests

Integration tests verify that components work together correctly.

**test_monitor_integration.py**
- Email notification system
- Failover group processing
- Complete monitoring cycle
- Error handling in integrated scenarios

## Writing New Tests

### Unit Test Template (unittest)

```python
import unittest
from unittest.mock import Mock, patch

class TestMyFeature(unittest.TestCase):
    """Test cases for MyFeature"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.test_data = "example"
        
    def tearDown(self):
        """Clean up after each test"""
        pass
        
    def test_something(self):
        """Test description"""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function()
        
        # Assert
        self.assertEqual(actual, expected)
        
    @patch('module.dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependency"""
        mock_dependency.return_value = "mocked"
        
        result = my_function()
        
        self.assertEqual(result, "mocked")
        mock_dependency.assert_called_once()
```

### Unit Test Template (pytest)

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def test_data():
    """Fixture providing test data"""
    return {"key": "value"}

class TestMyFeature:
    """Test cases for MyFeature"""
    
    def test_something(self, test_data):
        """Test description"""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function(test_data)
        
        # Assert
        assert actual == expected
        
    def test_with_mock(self, mocker):
        """Test with mocked dependency"""
        mock_dependency = mocker.patch('module.dependency')
        mock_dependency.return_value = "mocked"
        
        result = my_function()
        
        assert result == "mocked"
        mock_dependency.assert_called_once()
```

## Mocking Guidelines

### Mocking Snowflake Connections

```python
from unittest.mock import Mock, patch

@patch('snowflake.connector.connect')
def test_connection(mock_connect):
    mock_connection = Mock()
    mock_connect.return_value = mock_connection
    
    # Your test code here
```

### Mocking Query Results

```python
mock_cursor = Mock()
mock_cursor.fetchall.return_value = [
    ('value1',),
    ('value2',)
]

mock_connection = Mock()
mock_connection.cursor.return_value = mock_cursor
```

### Mocking Environment Variables

```python
import os
from unittest.mock import patch

@patch.dict(os.environ, {
    'SNOWFLAKE_USER': 'testuser',
    'SNOWFLAKE_PASSWORD': 'testpass'
})
def test_with_env():
    # Your test code here
```

## Code Coverage

### Generating Coverage Reports

```bash
# Using coverage with unittest
coverage run -m unittest discover
coverage report
coverage html  # Creates htmlcov/index.html

# Using pytest-cov
pytest --cov=. --cov-report=html --cov-report=term
```

### Coverage Goals

Target coverage levels:
- Overall: > 80%
- Critical modules (connection, replication): > 90%
- UI/Integration: > 70%

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        python run_tests.py
        
    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Best Practices

### Test Naming

- Use descriptive names: `test_connect_with_valid_credentials`
- Follow pattern: `test_<what>_<condition>_<expected_result>`
- Be specific: `test_parse_cron_schedule_returns_10_minutes`

### Test Organization

- One test class per class/module being tested
- Group related tests together
- Use setUp/tearDown or fixtures for common setup

### Test Independence

- Each test should be independent
- Don't rely on test execution order
- Clean up resources in tearDown/fixtures

### Mocking

- Mock external dependencies (database, network, filesystem)
- Don't mock the code you're testing
- Use realistic mock data

### Assertions

- Use specific assertions: `assertEqual`, `assertIn`, `assertRaises`
- Add assertion messages for clarity
- Test both success and failure cases

### Coverage

- Aim for high coverage, but focus on quality
- Test edge cases and error conditions
- Don't write tests just for coverage

## Troubleshooting Tests

### Common Issues

**Import Errors**
```bash
# Make sure you're in the project root
cd /home/dpham/src/snowflake

# Or set PYTHONPATH
export PYTHONPATH=/home/dpham/src/snowflake:$PYTHONPATH
```

**Mock Not Working**
- Ensure you're patching the right location
- Use `patch('module.where.used')` not `patch('module.where.defined')`

**Tests Pass Individually But Fail Together**
- Check for shared state between tests
- Use setUp/tearDown to reset state
- Make tests independent

**Flaky Tests**
- Avoid time-dependent assertions
- Use deterministic mock data
- Don't rely on external services

## Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py documentation](https://coverage.readthedocs.io/)

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all existing tests pass
3. Add tests for new functionality
4. Maintain or improve coverage
5. Update this documentation if needed
