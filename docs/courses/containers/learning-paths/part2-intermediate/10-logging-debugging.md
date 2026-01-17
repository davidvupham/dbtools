# Logging and debugging containers

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Configure container logging effectively
- Debug running and stopped containers
- Use common troubleshooting techniques
- Implement structured logging

---

## Container log basics

### Viewing logs

```bash
# All logs
docker logs mycontainer

# Follow logs (stream)
docker logs -f mycontainer

# Last N lines
docker logs --tail 100 mycontainer

# With timestamps
docker logs -t mycontainer

# Since specific time
docker logs --since 1h mycontainer
docker logs --since "2024-01-15T10:00:00" mycontainer

# Combined
docker logs -f --tail 50 -t mycontainer
```

### Compose logging

```bash
# All services
docker compose logs

# Follow all
docker compose logs -f

# Specific service
docker compose logs -f api

# Multiple services
docker compose logs -f api worker
```

---

## Logging configuration

### Logging drivers

```yaml
# compose.yaml
services:
  api:
    image: myapi
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

| Driver | Description |
|--------|-------------|
| `json-file` | Default, local JSON files |
| `local` | Optimized local format |
| `syslog` | System syslog |
| `journald` | systemd journal |
| `fluentd` | Fluentd collector |
| `awslogs` | AWS CloudWatch |
| `gcplogs` | Google Cloud Logging |
| `none` | Disable logging |

### Log rotation

```yaml
services:
  api:
    image: myapi
    logging:
      driver: json-file
      options:
        max-size: "10m"   # Max file size
        max-file: "5"     # Number of files to keep
        compress: "true"  # Compress rotated files
```

### Global logging (daemon)

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## Application logging best practices

### Write to stdout/stderr

```dockerfile
# Redirect application logs to stdout
FROM nginx:alpine
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log
```

```python
# Python: Log to stdout
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Structured logging (JSON)

```python
# Python with structlog
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()
log.info("user_login", user_id=123, ip="192.168.1.1")
# Output: {"event": "user_login", "user_id": 123, "ip": "192.168.1.1", "timestamp": "..."}
```

```javascript
// Node.js with pino
const pino = require('pino');
const logger = pino();

logger.info({ userId: 123, action: 'login' }, 'User logged in');
// Output: {"level":30,"time":...,"userId":123,"action":"login","msg":"User logged in"}
```

---

## Debugging techniques

### Execute commands in running container

```bash
# Interactive shell
docker exec -it mycontainer sh
docker exec -it mycontainer bash

# Run specific command
docker exec mycontainer ps aux
docker exec mycontainer cat /etc/hosts
docker exec mycontainer env

# As different user
docker exec -u root mycontainer whoami
```

### Inspect container

```bash
# Full inspection
docker inspect mycontainer

# Specific fields
docker inspect --format '{{.State.Status}}' mycontainer
docker inspect --format '{{json .Config.Env}}' mycontainer | jq
docker inspect --format '{{.NetworkSettings.IPAddress}}' mycontainer
docker inspect --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' mycontainer
```

### Debug stopped container

```bash
# Create new container from image for debugging
docker run -it --entrypoint sh myimage:latest

# Copy files from stopped container
docker cp mycontainer:/app/logs ./logs

# Export filesystem
docker export mycontainer > container_fs.tar
```

### Debugging with ephemeral container

```bash
# Add debug container to running container's namespace
docker run -it --rm \
    --pid=container:mycontainer \
    --network=container:mycontainer \
    nicolaka/netshoot

# Inside debug container, you can use tools like:
# - tcpdump, netstat, curl, dig
# - ps, top, strace
```

---

## Network debugging

### Check connectivity

```bash
# From inside container
docker exec mycontainer ping db
docker exec mycontainer nc -zv db 5432
docker exec mycontainer curl http://api:5000/health

# DNS resolution
docker exec mycontainer nslookup db
docker exec mycontainer cat /etc/resolv.conf
```

### Network inspection

```bash
# List networks
docker network ls

# Inspect network
docker network inspect myapp_default

# Find container IP
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mycontainer
```

### Tcpdump in container

```bash
# Using netshoot
docker run -it --rm \
    --network container:mycontainer \
    nicolaka/netshoot tcpdump -i any port 80
```

---

## Resource debugging

### Check resource usage

```bash
# Real-time stats
docker stats mycontainer

# One-time snapshot
docker stats --no-stream mycontainer

# Formatted output
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### View processes

```bash
# List processes in container
docker top mycontainer

# From inside container
docker exec mycontainer ps aux
```

### Check events

```bash
# Watch container events
docker events

# Filter by container
docker events --filter container=mycontainer

# Filter by event type
docker events --filter event=die
docker events --filter event=oom
```

---

## Common issues and solutions

### Container exits immediately

```bash
# Check exit code
docker inspect --format '{{.State.ExitCode}}' mycontainer

# Check logs
docker logs mycontainer

# Common causes:
# Exit 0 - Normal exit, command completed
# Exit 1 - Application error
# Exit 137 - OOM killed (128 + 9)
# Exit 139 - Segfault (128 + 11)
```

### Out of memory

```bash
# Check if OOM killed
docker inspect --format '{{.State.OOMKilled}}' mycontainer

# Check memory limit
docker inspect --format '{{.HostConfig.Memory}}' mycontainer

# Increase memory limit
docker update --memory 1g mycontainer
```

### Permission denied

```bash
# Check user running in container
docker exec mycontainer id

# Check file permissions
docker exec mycontainer ls -la /app

# Run as root temporarily
docker exec -u root mycontainer ls -la /app
```

### Can't connect to service

```bash
# Check if service is listening
docker exec mycontainer netstat -tlnp
docker exec mycontainer ss -tlnp

# Check if port is mapped
docker port mycontainer

# Check network connectivity
docker exec mycontainer ping otherservice
```

---

## Practical debugging workflow

### 1. Check status

```bash
docker ps -a | grep myapp
docker compose ps
```

### 2. Check logs

```bash
docker compose logs --tail 100 api
```

### 3. Check health

```bash
docker inspect --format '{{json .State.Health}}' myapp-api-1 | jq
```

### 4. Interactive debugging

```bash
docker exec -it myapp-api-1 sh
# Inside container:
ps aux
cat /etc/hosts
curl localhost:5000/health
env | grep DATABASE
```

### 5. Network debugging

```bash
docker network inspect myapp_default
docker exec myapp-api-1 ping db
docker exec myapp-api-1 nc -zv db 5432
```

---

## Logging in Compose example

```yaml
name: logging-demo

services:
  api:
    build: ./api
    ports:
      - "5000:5000"
    environment:
      - LOG_LEVEL=debug
      - LOG_FORMAT=json
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
        labels: "service"
        env: "LOG_LEVEL"
    labels:
      service: "api"

  worker:
    build: ./worker
    logging:
      driver: json-file
      options:
        max-size: "5m"
        max-file: "3"

  # Centralized logging with Loki
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    profiles:
      - monitoring

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail-config.yaml:/etc/promtail/config.yaml:ro
    profiles:
      - monitoring
```

---

## Key takeaways

1. **Always log to stdout/stderr** for container log collection
2. **Use structured logging** (JSON) for easier parsing
3. **Configure log rotation** to prevent disk fill
4. **Use exec for debugging** running containers
5. **Network tools** help diagnose connectivity issues
6. **Check exit codes** and OOM status for crashes

---

## What's next

Learn about container resource management.

Continue to: [11-resource-management.md](11-resource-management.md)
