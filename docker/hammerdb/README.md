# HammerDB Docker Image

Dockerfile for running HammerDB benchmarks with `gds_hammerdb` automation.

## Build

From the repository root:

```bash
docker build -t gds-hammerdb -f docker/hammerdb/Dockerfile .
```

## Usage

### Interactive Shell

```bash
docker run -it --rm gds-hammerdb /bin/bash
```

### Run a Tcl Script

```bash
docker run -it --rm -v $(pwd)/scripts:/benchmarks gds-hammerdb auto /benchmarks/my_script.tcl
```

### With Python Automation

```bash
docker run -it --rm gds-hammerdb python3 -c "
from gds_hammerdb.runners import PostgresRunner
runner = PostgresRunner()
# ... configure and run
"
```

## Network Configuration

This container uses the `devcontainer-network` shared by other project containers:

```bash
# Create the network (if not exists)
docker network create devcontainer-network

# Run with docker-compose (recommended)
cd docker/hammerdb
docker-compose up -d

# Or run standalone with the network
docker run --network=devcontainer-network gds-hammerdb ...
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HAMMERDB_CLI_PATH` | `/opt/hammerdb/hammerdbcli` | Path to HammerDB CLI |
