# Developer Guide

This guide is intended for developers who want to contribute to the `gds_metrics` package or extend it with new metric backends.

## Development Setup

### Prerequisites

- Python 3.9+
- `pip`

### Installation

1. **Clone the repository** (if you haven't already):

    ```bash
    git clone https://github.com/gds/dbtools.git
    cd dbtools/gds_metrics
    ```

2. **Create a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the package in editable mode with dev dependencies**:

    ```bash
    pip install -e ".[dev,prometheus]"
    ```

    This installs `pytest`, `pytest-cov`, `ruff`, and the optional `prometheus-client` for full testing.

## Running Tests

We use `pytest` for testing.

To run all tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=gds_metrics tests/
```

To run a specific test file:

```bash
pytest tests/test_metrics.py
```

## Code Style & linting

We use `ruff` for linting and formatting.

To check for linting errors:

```bash
ruff check .
```

To automatically fix simple errors:

```bash
ruff check --fix .
```

To format code:

```bash
ruff format .
```

Please ensure your code passes all linting checks before submitting a PR.

## Architecture & Design

The package is built around the `MetricsCollector` protocol defined in `gds_metrics/base.py`. This allows for a pluggable architecture where different backends can be used without changing the application code.

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed overview.

## Extending the Package

To add a new metrics backend (e.g., for Datadog, StatsD, or a custom internal system), you need to implement the `MetricsCollector` protocol.

### Step 1: Create a new class

Create a new file in `gds_metrics/` (e.g., `datadog.py`) and define your class:

```python
from typing import Optional
from .base import MetricsCollector

class DatadogMetrics:
    """Datadog metrics implementation."""

    def __init__(self, api_key: str, host: str = "localhost"):
        self.api_key = api_key
        # Initialize your client library here

    def increment(
        self,
        name: str,
        value: int = 1,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        # Implementation to send counter to Datadog
        pass

    def gauge(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        # Implementation to send gauge to Datadog
        pass

    def histogram(
        self,
        name: str,
        value: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        # Implementation to send histogram/distribution
        pass

    def timing(
        self,
        name: str,
        value_ms: float,
        labels: Optional[dict[str, str]] = None
    ) -> None:
        # Implementation to send timing
        pass
```

### Step 2: Register the new backend

Add your new class to `gds_metrics/__init__.py`:

```python
from .datadog import DatadogMetrics

__all__ = [
    # ... existing
    "DatadogMetrics",
]
```

### Step 3: Add tests

Create a corresponding test file in `tests/` (e.g., `tests/test_datadog.py`) verifying that your class correctly implements the protocol and interacts with the backend client as expected.

## Release Process

(Internal use only)

1. Update version in `pyproject.toml`.
2. Update `CHANGELOG.md` (if exists).
3. Build the package:

    ```bash
    python -m build
    ```

4. Publish to internal PyPI.
