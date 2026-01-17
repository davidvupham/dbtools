# Compose services deep dive

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Define and configure multiple services
- Manage service dependencies
- Configure resource limits
- Use profiles for conditional services

---

## Service definition anatomy

### Basic service structure

```yaml
# compose.yaml
services:
  webapp:
    image: nginx:alpine
    container_name: my-webapp
    hostname: webapp
    ports:
      - "8080:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
```

### Build vs image

```yaml
services:
  # Use pre-built image
  redis:
    image: redis:7-alpine

  # Build from Dockerfile
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      args:
        - BUILD_VERSION=1.0.0

  # Simple build syntax
  frontend:
    build: ./frontend
```

---

## Service dependencies

### Basic dependencies

```yaml
services:
  db:
    image: postgres:15-alpine

  api:
    image: myapi:latest
    depends_on:
      - db        # Starts db before api
      - redis

  redis:
    image: redis:7-alpine
```

### Health-based dependencies

```yaml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: myapi:latest
    depends_on:
      db:
        condition: service_healthy  # Wait for health check
      redis:
        condition: service_started  # Just wait for start
```

### Dependency conditions

| Condition | Description |
|-----------|-------------|
| `service_started` | Wait for container to start (default) |
| `service_healthy` | Wait for health check to pass |
| `service_completed_successfully` | Wait for container to exit 0 |

---

## Environment configuration

### Inline variables

```yaml
services:
  api:
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
      - DEBUG=false
      - LOG_LEVEL=info
```

### Environment file

```yaml
services:
  api:
    env_file:
      - .env
      - .env.local
    environment:
      # Override specific values
      - DEBUG=true
```

### Variable substitution

```yaml
# compose.yaml
services:
  db:
    image: postgres:${POSTGRES_VERSION:-15}-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?Database password required}
```

```bash
# .env file
POSTGRES_VERSION=15
DB_PASSWORD=secretpassword
```

**Substitution syntax:**

| Syntax | Description |
|--------|-------------|
| `${VAR}` | Value of VAR |
| `${VAR:-default}` | Default if unset or empty |
| `${VAR-default}` | Default if unset only |
| `${VAR:?error}` | Error if unset or empty |
| `${VAR?error}` | Error if unset only |

---

## Resource management

### Memory limits

```yaml
services:
  api:
    image: myapi:latest
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### CPU limits

```yaml
services:
  worker:
    image: myworker:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Max 2 CPUs
        reservations:
          cpus: '0.5'      # Reserve 0.5 CPU
```

### Combined example

```yaml
services:
  api:
    image: myapi:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

---

## Service profiles

Profiles allow conditional service inclusion:

```yaml
services:
  api:
    image: myapi:latest
    # No profile = always starts

  db:
    image: postgres:15-alpine
    # No profile = always starts

  adminer:
    image: adminer
    profiles:
      - debug
    ports:
      - "8080:8080"

  prometheus:
    image: prom/prometheus
    profiles:
      - monitoring

  grafana:
    image: grafana/grafana
    profiles:
      - monitoring
```

```bash
# Start default services only
docker compose up -d

# Start with debug profile
docker compose --profile debug up -d

# Start with monitoring profile
docker compose --profile monitoring up -d

# Start with multiple profiles
docker compose --profile debug --profile monitoring up -d
```

---

## Scaling services

### Static scaling

```yaml
services:
  worker:
    image: myworker:latest
    deploy:
      replicas: 3
```

### Dynamic scaling

```bash
# Scale a service
docker compose up -d --scale worker=5

# Check scaled services
docker compose ps

# Scale back down
docker compose up -d --scale worker=2
```

**Note:** Scaled services cannot use fixed host ports.

```yaml
services:
  worker:
    image: myworker:latest
    # ports:
    #   - "8080:80"  # Won't work with scaling
    expose:
      - "80"         # Internal only - works with scaling
```

---

## Restart policies

```yaml
services:
  api:
    image: myapi:latest
    restart: unless-stopped

  worker:
    image: myworker:latest
    restart: on-failure

  oneshot:
    image: migration:latest
    restart: "no"
```

| Policy | Description |
|--------|-------------|
| `no` | Never restart (default) |
| `always` | Always restart |
| `on-failure` | Restart on non-zero exit |
| `unless-stopped` | Always, except manual stop |

---

## Labels and metadata

```yaml
services:
  api:
    image: myapi:latest
    labels:
      - "com.example.description=API Service"
      - "com.example.department=Engineering"
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.example.com`)"
```

---

## Practical example: Multi-tier application

```yaml
# compose.yaml
name: multi-tier-app

services:
  # Database tier
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-appdb}
      POSTGRES_USER: ${DB_USER:-appuser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB password required}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-appuser}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M

  # Cache tier
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 128M

  # Application tier
  api:
    build: ./api
    environment:
      DATABASE_URL: postgres://${DB_USER:-appuser}:${DB_PASSWORD}@postgres:5432/${DB_NAME:-appdb}
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY:-dev-secret}
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 256M

  # Worker tier
  worker:
    build: ./worker
    environment:
      DATABASE_URL: postgres://${DB_USER:-appuser}:${DB_PASSWORD}@postgres:5432/${DB_NAME:-appdb}
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 256M

  # Debug tools (optional)
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    profiles:
      - debug

volumes:
  postgres_data:
  redis_data:
```

---

## Key takeaways

1. **Use health-based dependencies** for reliable startup ordering
2. **Environment files** keep secrets out of compose files
3. **Resource limits** prevent runaway containers
4. **Profiles** allow conditional services for different environments
5. **Scaling** works best with internal-only ports

---

## What's next

Learn about networking in Docker Compose.

Continue to: [03-compose-networking.md](03-compose-networking.md)
