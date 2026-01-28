# Advanced Patterns
<!-- id: chapter-5 -->

**[← Back to Course Index](./README.md)**

> **Objective:** Master test selection, skipping, and coverage reports.
> **Time:** 15 Minutes

## Markers: Categorizing Tests
<!-- id: markers -->

As your test suite grows, you won't always want to run every test. Markers allow you to tag tests.

### Common Markers
- `@pytest.mark.slow`: Tests that take time.
- `@pytest.mark.integration`: Tests that hit real systems.
- `@pytest.mark.skip`: Don't run this test.
- `@pytest.mark.xfail`: Expected to fail (documenting a bug).

### Example (`test_markers.py`)

```python
# examples/ch05_advanced/test_markers.py
import pytest
import time

@pytest.mark.slow
def test_heavy_computation():
    time.sleep(0.1)  # Imagine this is 10 seconds
    assert True

@pytest.mark.skip(reason="Obsolete feature, removing soon")
def test_old_feature():
    assert False

@pytest.mark.xfail(reason="Bug #1234: Division by zero not handled")
def test_buggy_feature():
    assert 1 / 0 == 0
```

### Running Markers

```bash
# Run ONLY slow tests
pytest -v -m slow

# Run everything EXCEPT slow tests
pytest -v -m "not slow"
```

> [!IMPORTANT]
> You should register markers in `pytest.ini` or `pyproject.toml` to avoid warnings.
> ```toml
> [tool.pytest.ini_options]
> markers = [
>     "slow: marks tests as slow",
> ]
> ```

## Code Coverage
<!-- id: coverage -->

Coverage tells you which lines of code your tests touched. High coverage gives you confidence to refactor.

### Running Coverage

We use `pytest-cov`, which is standard in this repository.

```bash
# Run tests and show report in terminal
pytest --cov=my_package

# Generate HTML report (great for visual inspection)
pytest --cov=my_package --cov-report=html
```

## Continuous Integration (CI)
<!-- id: ci -->

Your tests should run automatically on every Pull Request.

**Golden Rule:** If tests fail, do not merge.

## Conclusion
<!-- id: conclusion -->

You have completed the **Python Unit Testing Master Class**.

### Recap
1.  **AAA Pattern**: Arrange, Act, Assert.
2.  **Fixtures**: Clean dependency injection.
3.  **Parametrization**: Maximum coverage, minimum code.
4.  **Mocking**: Isolated, fast tests.
5.  **Markers**: Organized test suites.

**[Return to Course Index](./README.md)**
