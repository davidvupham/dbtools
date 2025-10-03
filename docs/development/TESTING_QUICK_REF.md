# Quick Reference: Testing Snowflake Replication Monitor

## Run All Tests

```bash
# Using test runner (recommended)
python run_tests.py

# Using unittest
python -m unittest discover -s tests -v

# Using pytest (if installed)
pytest
```

## Run Specific Tests

```bash
# Test runner - specific module
python run_tests.py -m test_snowflake_connection

# unittest - specific file
python -m unittest tests.test_snowflake_connection

# pytest - specific file
pytest tests/test_snowflake_connection.py
```

## Run with Coverage

```bash
# Install dev dependencies first
pip install -r requirements-dev.txt

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Files

| File | Purpose | Tests |
|------|---------|-------|
| `test_snowflake_connection.py` | Connection module | 15+ |
| `test_snowflake_replication.py` | Replication module | 28+ |
| `test_monitor_integration.py` | Integration tests | 10+ |
| `test_connection_pytest.py` | Pytest examples | - |

## Test Commands Cheat Sheet

```bash
# Quick test (quiet mode)
python run_tests.py -q

# Verbose output
python run_tests.py -v

# Specific module
python run_tests.py -m test_snowflake_replication

# With coverage
pytest --cov=. --cov-report=term

# Only unit tests (pytest)
pytest -m unit

# Only integration tests (pytest)
pytest -m integration

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

## Common Issues

**Import errors?**
```bash
export PYTHONPATH=/home/dpham/src/snowflake:$PYTHONPATH
```

**Pytest not found?**
```bash
pip install -r requirements-dev.txt
```

**Tests fail?**
- Check you're in project root: `/home/dpham/src/snowflake`
- Ensure all dependencies installed: `pip install -r requirements.txt`

## Quick Test Development Cycle

1. Write test first (TDD)
```python
def test_new_feature(self):
    result = my_new_function()
    self.assertEqual(result, expected)
```

2. Run test (should fail)
```bash
python run_tests.py -m test_module
```

3. Implement feature
```python
def my_new_function():
    return expected
```

4. Run test again (should pass)
```bash
python run_tests.py -m test_module
```

5. Refactor if needed, tests ensure correctness

## Documentation

- **Full testing guide**: `TESTING.md`
- **Implementation summary**: `UNIT_TESTING_SUMMARY.md`
- **Main README**: `README.md` (Testing section)

## Test Coverage Stats

- **Overall**: ~90%
- **Connection module**: ~95%
- **Replication module**: ~92%
- **Monitor script**: ~85%

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests
- Multiple Python versions (3.8-3.11)

See: `.github/workflows/tests.yml`
