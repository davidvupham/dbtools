# Container resource management

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 20 minutes

## Learning objectives

By the end of this section, you will be able to:

- Set CPU and memory limits
- Configure resource reservations
- Monitor resource usage
- Prevent resource exhaustion

---

## Why limit resources?

Without limits, a single container can:
- Consume all available CPU
- Use all system memory
- Cause OOM (Out of Memory) kills
- Impact other containers and the host

---

## Memory management

### Setting memory limits

```bash
# Docker run
docker run -d --memory 512m --memory-swap 1g nginx

# Compose
services:
  api:
    image: myapi
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Memory options

| Option | Description |
|--------|-------------|
| `--memory` / `memory` | Maximum memory |
| `--memory-swap` | Total memory + swap |
| `--memory-reservation` | Soft limit (reservation) |
| `--oom-kill-disable` | Prevent OOM killing |

### Memory calculation

```bash
# Memory values
512M    # 512 megabytes
1G      # 1 gigabyte
1073741824  # bytes (1GB)

# Swap settings
--memory 512m --memory-swap 512m   # No swap
--memory 512m --memory-swap 1g     # 512MB swap
--memory 512m --memory-swap -1     # Unlimited swap
```

---

## CPU management

### CPU limits

```bash
# Docker run
docker run -d --cpus 2.0 nginx        # Max 2 CPUs
docker run -d --cpu-shares 512 nginx  # Relative weight

# Compose
services:
  api:
    image: myapi
    deploy:
      resources:
        limits:
          cpus: '2.0'
        reservations:
          cpus: '0.5'
```

### CPU options

| Option | Description |
|--------|-------------|
| `--cpus` | Number of CPUs (e.g., 1.5) |
| `--cpu-shares` | Relative weight (default 1024) |
| `--cpu-period` | CPU CFS period (microseconds) |
| `--cpu-quota` | CPU CFS quota (microseconds) |
| `--cpuset-cpus` | Specific CPUs to use (e.g., "0,1") |

### CPU shares explained

```yaml
# CPU shares are relative weights
services:
  high-priority:
    cpu_shares: 2048    # Gets 2x CPU when competing

  normal:
    cpu_shares: 1024    # Default weight

  low-priority:
    cpu_shares: 512     # Gets 0.5x CPU when competing
```

---

## Compose resource syntax

### Deploy resources (recommended)

```yaml
services:
  api:
    image: myapi
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 128M
```

### Legacy syntax (still works)

```yaml
services:
  api:
    image: myapi
    mem_limit: 512m
    mem_reservation: 128m
    cpus: 2.0
```

---

## Monitoring resource usage

### Docker stats

```bash
# Real-time monitoring
docker stats

# Single container
docker stats mycontainer

# Custom format
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# One-time snapshot
docker stats --no-stream
```

### Output explained

```
CONTAINER   CPU %   MEM USAGE / LIMIT   MEM %   NET I/O        BLOCK I/O
api         2.50%   128MiB / 512MiB     25.00%  1.2kB / 500B   0B / 0B
worker      45.00%  256MiB / 512MiB     50.00%  2.5kB / 1kB    1MB / 2MB
```

### Inspect limits

```bash
# Check memory limit
docker inspect --format '{{.HostConfig.Memory}}' mycontainer

# Check CPU limit
docker inspect --format '{{.HostConfig.NanoCpus}}' mycontainer

# All resource config
docker inspect --format '{{json .HostConfig}}' mycontainer | jq '{
  Memory: .Memory,
  MemorySwap: .MemorySwap,
  NanoCpus: .NanoCpus,
  CpuShares: .CpuShares
}'
```

---

## Resource events

### OOM events

```bash
# Watch for OOM kills
docker events --filter event=oom

# Check if container was OOM killed
docker inspect --format '{{.State.OOMKilled}}' mycontainer
```

### Handling OOM

```yaml
services:
  api:
    image: myapi
    deploy:
      resources:
        limits:
          memory: 512M
    # Restart on OOM
    restart: unless-stopped

    # Or prevent OOM kill (use carefully)
    # oom_kill_disable: true
```

---

## Best practices

### Right-sizing containers

```yaml
# Development: generous limits
services:
  api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2.0'

# Production: tight limits based on profiling
services:
  api:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'
```

### Resource planning

1. **Profile your application** to understand baseline usage
2. **Set limits** above peak usage with headroom
3. **Set reservations** at typical usage
4. **Monitor** and adjust based on actual usage

### Database containers

```yaml
services:
  postgres:
    image: postgres:15-alpine
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    # PostgreSQL memory tuning
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
      - POSTGRES_WORK_MEM=16MB
```

---

## Practical example

```yaml
name: resource-management

services:
  # High resource needs
  api:
    build: ./api
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Medium resource needs
  worker:
    build: ./worker
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  # Low resource needs
  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.1'
          memory: 64M

  # Database with specific tuning
  postgres:
    image: postgres:15-alpine
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Update resources on running container

```bash
# Update memory limit
docker update --memory 1g mycontainer

# Update CPU limit
docker update --cpus 2 mycontainer

# Update multiple options
docker update --memory 512m --cpus 1 mycontainer
```

---

## Key takeaways

1. **Always set memory limits** to prevent OOM issues
2. **Use reservations** for scheduling and planning
3. **Monitor with docker stats** to understand usage
4. **Profile applications** before setting production limits
5. **Right-size containers** based on actual needs

---

## What's next

Learn about development workflows with containers.

Continue to: [12-development-workflows.md](12-development-workflows.md)
