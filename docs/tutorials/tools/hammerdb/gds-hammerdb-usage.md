# Benchmarking with gds_hammerdb

Automated HammerDB benchmarking for PostgreSQL and SQL Server.

## Installation

```bash
# Install both packages
cd gds_benchmark && pip install -e .
cd ../python/gds_hammerdb && pip install -e .
```

## Quick Start

### PostgreSQL TPC-C Benchmark

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

# Run benchmark
result = runner.run(config)
print(f"Status: {result.status}")
for metric in result.metrics:
    print(f"{metric.name}: {metric.value} {metric.unit}")
```

### SQL Server TPC-C Benchmark

```python
from gds_hammerdb.runners import MSSQLRunner

runner = MSSQLRunner()

config = {
    "hammerdb": {
        "db_type": "mssqls",
        "benchmark_type": "TPC-C",
        "virtual_users": 8,
        "rampup_minutes": 2,
        "duration_minutes": 10,
    },
    "mssql": {
        "server": "localhost",
        "uid": "sa",
        "password": "YourStrong!Passw0rd",
    }
}

result = runner.run(config)
```

## TPC-H (OLAP) Benchmarks

```python
# PostgreSQL TPC-H
config = {
    "hammerdb": {
        "db_type": "pg",
        "benchmark_type": "TPC-H",
        "virtual_users": 1,
        "tpch_scale_factor": 10,  # 10GB dataset
    },
    "postgres": {
        "host": "localhost",
        "superuser": "postgres",
        "password": "password",
    }
}

result = runner.run(config)
```

## Schema Build (Drop & Recreate)

Before running benchmarks, build the schema:

```python
from gds_hammerdb.runners import PostgresRunner

runner = PostgresRunner()

config = {
    "hammerdb": {
        "db_type": "pg",
        "benchmark_type": "TPC-C",
        "virtual_users": 4,  # Parallel build threads
    },
    "postgres": {
        "host": "localhost",
        "superuser": "postgres",
        "password": "password",
    }
}

# Build schema first
build_result = runner.build_schema(config)

# Then run benchmark
if build_result.status.value == "COMPLETED":
    run_result = runner.run(config)
```

### Combined Build and Run

```python
# Drops, rebuilds, then runs in one call
result = runner.run_with_rebuild(config)
```

## Interpreting Results

```python
from gds_hammerdb.analysis import ResultAnalyzer

analyzer = ResultAnalyzer()

# Compare against baseline
analysis = analyzer.analyze(result, baseline_nopm=10000)

print(f"Status: {analysis['status']}")
# PASS, REGRESSION, or IMPROVED

print(f"Findings: {analysis['findings']}")
# ['Performance regression: 15% below baseline.']
```

## Docker Usage

```bash
# Build container
docker build -t gds-hammerdb -f docker/hammerdb/Dockerfile .

# Run with network access to databases
docker run --network=devcontainer-network gds-hammerdb auto /benchmarks/script.tcl
```

## Configuration Reference

### HammerDB Config

| Parameter | Default | Description |
|-----------|---------|-------------|
| `db_type` | - | `pg` or `mssqls` |
| `benchmark_type` | `TPC-C` | `TPC-C` or `TPC-H` |
| `virtual_users` | 1 | Concurrent connections |
| `rampup_minutes` | 2 | Warmup time |
| `duration_minutes` | 5 | Test duration |
| `tpch_scale_factor` | 1 | TPC-H dataset size (GB) |

### PostgreSQL Config

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | - | Database hostname |
| `port` | 5432 | Database port |
| `superuser` | postgres | Database user |
| `password` | - | Database password |

### SQL Server Config

| Parameter | Default | Description |
|-----------|---------|-------------|
| `server` | - | Server hostname |
| `uid` | sa | Login ID |
| `password` | - | Login password |

## Result Metrics

| Metric | Benchmark | Description |
|--------|-----------|-------------|
| NOPM | TPC-C | New Orders Per Minute |
| TPM | TPC-C | Transactions Per Minute |
| QphH | TPC-H | Queries Per Hour |
