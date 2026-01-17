# Prometheus Docker Setup for GDS Metrics

This directory contains a Docker Compose setup for Prometheus and Grafana to test and visualize metrics from `gds_metrics`.

## Files Overview

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main configuration (use on host Docker) |
| `docker-compose.devcontainer.yml` | Override for VS Code dev containers |
| `Dockerfile` | Builds Prometheus with baked-in config (dev container only) |
| `config/prometheus.yml` | Prometheus scrape configuration |
| `grafana/provisioning/` | Grafana datasource auto-configuration |

## Quick Start

### Which environment are you in?

| Environment | How to tell | Which command |
|-------------|-------------|---------------|
| **Host Docker** | Running Docker directly on your machine (macOS, Linux, Windows) | `docker compose up -d` |
| **Dev Container** | Inside VS Code with "Dev Containers" extension | Use override file (see below) |

---

### Option 1: Host Docker (Production-like)

Use this when running Docker directly on your machine. This is the **recommended** approach for production-like testing.

```bash
cd docker/prometheus

# Create shared network (one-time setup)
docker network create devcontainer-network 2>/dev/null || true

# Start services
docker compose up -d

# Verify
docker compose ps
curl http://localhost:9090/-/healthy
```

**Updating configuration:**

```bash
# Edit config/prometheus.yml, then:
docker compose restart prometheus
```

---

### Option 2: Dev Container (Docker-in-Docker)

Use this when working inside a VS Code dev container. Bind mounts don't work in Docker-in-Docker, so we build the config into the image.

```bash
cd docker/prometheus

# Build and start (includes override file)
docker compose -f docker-compose.yml -f docker-compose.devcontainer.yml build
docker compose -f docker-compose.yml -f docker-compose.devcontainer.yml up -d

# Verify
docker compose ps
```

**Updating configuration:**

```bash
# Edit config/prometheus.yml, then rebuild:
docker compose -f docker-compose.yml -f docker-compose.devcontainer.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.devcontainer.yml up -d
```

---

## URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | <http://localhost:9090> | None |
| Grafana | <http://localhost:3001> | admin / admin |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Python Application with gds_metrics                    │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │  from gds_metrics import PrometheusMetrics      │   │ │
│  │  │  metrics = PrometheusMetrics(port=8080)         │   │ │
│  │  │  metrics.increment("requests")                   │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                         │                               │ │
│  │                   :8080/metrics                        │ │
│  └─────────────────────────│───────────────────────────────┘ │
│                            │                                 │
│  ┌─────────────────────────│───────────────────────────────┐ │
│  │  Docker Network (devcontainer-network)                  │ │
│  │  ┌──────────────────────▼──────────────────────────┐   │ │
│  │  │  Prometheus (localhost:9090)                     │   │ │
│  │  │  Scrapes host.docker.internal:8080/metrics      │   │ │
│  │  └──────────────────────│──────────────────────────┘   │ │
│  │                         │                               │ │
│  │  ┌──────────────────────▼──────────────────────────┐   │ │
│  │  │  Grafana (localhost:3001)                        │   │ │
│  │  │  Queries Prometheus for visualization            │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Testing gds_metrics

### 1. Start Prometheus Stack

```bash
# Host Docker
docker compose up -d

# Or Dev Container
docker compose -f docker-compose.yml -f docker-compose.devcontainer.yml up -d
```

### 2. Run Test Application

```python
# test_prometheus_integration.py
from gds_metrics import PrometheusMetrics
import time

# Create metrics (starts HTTP server on port 8080)
metrics = PrometheusMetrics(prefix="test", port=8080)

# Generate some metrics
for i in range(100):
    metrics.increment("requests_total", labels={"status": "200"})
    metrics.gauge("active_connections", i % 10)
    metrics.histogram("request_duration_seconds", 0.1 + (i % 5) * 0.05)
    metrics.timing("query_time_ms", 50 + i % 100)
    time.sleep(0.1)

print("Metrics exposed at http://localhost:8080/metrics")
print("View in Prometheus at http://localhost:9090")
input("Press Enter to exit...")
```

### 3. Verify in Prometheus

1. Open <http://localhost:9090>
2. Go to Status → Targets
3. Check that `gds_metrics` target is UP
4. Query metrics:
   - `test_requests_total`
   - `test_active_connections`
   - `test_request_duration_seconds_bucket`

## Configuration

### prometheus.yml

The Prometheus configuration includes scrape targets for:

| Job | Port | Description |
|-----|------|-------------|
| `gds_metrics` | 8080 | Default gds_metrics test endpoint |
| `gds_vault` | 8081 | gds_vault metrics |
| `gds_database` | 8082 | gds_database metrics |
| `gds_mongodb` | 8083 | gds_mongodb metrics |
| `hashicorp_vault` | 8200 | Native Vault metrics |

### Custom Ports

To use a different port, update `prometheus.yml`:

```yaml
- job_name: 'my_app'
  static_configs:
    - targets: ['host.docker.internal:9000']
```

Then reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

## Grafana Dashboards

### Default Login

- URL: <http://localhost:3000>
- Username: `admin`
- Password: `admin`

### Creating a Dashboard

1. Click "+" → "New Dashboard"
2. Add a new panel
3. Use PromQL queries:

```promql
# Request rate
rate(test_requests_total[5m])

# Active connections
test_active_connections

# Request duration 95th percentile
histogram_quantile(0.95, rate(test_request_duration_seconds_bucket[5m]))
```

## Cleanup

```bash
# Stop containers
docker compose down

# Remove volumes (data)
docker compose down -v
```

## Troubleshooting

### Target Not Reachable

If Prometheus shows `gds_metrics` target as DOWN:

1. Ensure your Python app is running with `PrometheusMetrics(port=8080)`
2. Verify the metrics endpoint: `curl http://localhost:8080/metrics`
3. Check Docker network: `docker network inspect prometheus_prometheus-network`

### host.docker.internal Not Working

On Linux, you may need to add this to `docker-compose.yml`:

```yaml
services:
  prometheus:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### Port Conflicts

If port 9090 or 3000 is in use:

```yaml
services:
  prometheus:
    ports:
      - "9091:9090"  # Change host port
```

## Podman alternative

Replace `docker` with `podman` for all commands on RHEL/CentOS systems:

```bash
# Create network
podman network create devcontainer-network

# Start services
podman-compose up -d

# With override file for dev container
podman-compose -f docker-compose.yml -f docker-compose.devcontainer.yml up -d

# Check status
podman-compose ps

# View logs
podman logs prometheus
podman logs grafana

# Stop services
podman-compose down
```

On RHEL/Fedora with SELinux, add `:Z` to volume mounts for proper labeling.
