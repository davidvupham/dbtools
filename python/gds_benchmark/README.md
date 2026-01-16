# gds-benchmark

Generic benchmarking interfaces and models for GDS tools.

## Installation

```bash
pip install -e .
```

## Overview

This package provides abstract base classes and data models for implementing benchmark automation tools.

## Components

### BenchmarkRunner (Abstract Base Class)

```python
from gds_benchmark.interfaces import BenchmarkRunner

class MyRunner(BenchmarkRunner):
    def run(self, config: dict) -> BenchmarkResult:
        # Implement benchmark execution
        pass

    def validate_config(self, config: dict) -> bool:
        # Validate configuration
        return True
```

### BenchmarkResult

```python
from gds_benchmark.models import BenchmarkResult, BenchmarkStatus

result = BenchmarkResult(
    run_id="run-001",
    tool_name="my-tool",
    status=BenchmarkStatus.COMPLETED,
    start_time=datetime.now(),
)

result.add_metric("NOPM", 12500, "orders/min", "New Orders Per Minute")
```

### BenchmarkStatus

| Status | Description |
|--------|-------------|
| `PENDING` | Not yet started |
| `RUNNING` | Currently executing |
| `COMPLETED` | Finished successfully |
| `FAILED` | Execution failed |

## Implementations

- **[gds-hammerdb](../gds_hammerdb)**: HammerDB benchmarking for PostgreSQL and SQL Server

## Development

```bash
# Run tests
pytest tests/gds_benchmark/
```
