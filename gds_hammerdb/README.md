# gds-hammerdb

Automated HammerDB benchmarking for PostgreSQL and SQL Server.

## Installation

```bash
pip install -e .
```

**Dependency**: Requires `gds-benchmark` to be installed first.

## Features

- TPC-C (OLTP) benchmarks
- TPC-H (OLAP) benchmarks
- Schema build/rebuild automation
- Result parsing (NOPM, TPM)
- Baseline comparison and analysis

## Quick Start

### PostgreSQL Benchmark

```python
from gds_hammerdb.runners import PostgresRunner

runner = PostgresRunner()

config = {
    "hammerdb": {
        "db_type": "pg",
        "benchmark_type": "TPC-C",
        "virtual_users": 4,
        "rampup_minutes": 2,
        "duration_minutes": 10,
    },
    "postgres": {
        "host": "localhost",
        "port": 5432,
        "superuser": "postgres",
        "password": "your_password",
    }
}

result = runner.run(config)

for metric in result.metrics:
    print(f"{metric.name}: {metric.value} {metric.unit}")
```

### SQL Server Benchmark

```python
from gds_hammerdb.runners import MSSQLRunner

runner = MSSQLRunner()

config = {
    "hammerdb": {
        "db_type": "mssqls",
        "benchmark_type": "TPC-C",
        "virtual_users": 8,
    },
    "mssql": {
        "server": "localhost",
        "uid": "sa",
        "password": "YourStrong!Passw0rd",
    }
}

result = runner.run(config)
```

### Schema Build (Drop & Recreate)

```python
# Build schema before running
build_result = runner.build_schema(config)

# Or combined: build + run
result = runner.run_with_rebuild(config)
```

## Configuration

### HammerDB Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `db_type` | - | `pg` or `mssqls` |
| `benchmark_type` | `TPC-C` | `TPC-C` or `TPC-H` |
| `virtual_users` | 1 | Concurrent connections |
| `rampup_minutes` | 2 | Warmup time |
| `duration_minutes` | 5 | Test duration |
| `tpch_scale_factor` | 1 | TPC-H dataset size (GB) |

## Result Analysis

```python
from gds_hammerdb.analysis import ResultAnalyzer

analyzer = ResultAnalyzer()
analysis = analyzer.analyze(result, baseline_nopm=10000)

print(analysis["status"])  # PASS, REGRESSION, or IMPROVED
```

## Docker

```bash
# Build container
docker build -t gds-hammerdb -f docker/hammerdb/Dockerfile .

# Run on tool-library-network
docker run --network=tool-library-network gds-hammerdb auto /benchmarks/script.tcl
```

## Documentation

See [gds-hammerdb Usage Tutorial](../docs/tutorials/hammerdb/gds-hammerdb-usage.md) for complete documentation.

## Development

```bash
# Run tests
pytest tests/gds_hammerdb/
```
