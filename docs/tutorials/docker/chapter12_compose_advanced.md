# Chapter 12: Advanced Compose

Beyond the basics of `docker compose up`, this chapter covers production patterns: profiles, overrides, scaling, and environment management.

## Profiles: Selective Service Startup

Profiles let you define groups of services that only start when explicitly requested.

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"

  db:
    image: postgres:15
    profiles:
      - database  # Only starts with --profile database

  debug:
    image: alpine
    command: sleep infinity
    profiles:
      - dev  # Only starts with --profile dev
```

### Usage

```bash
# Start only web (default, no profile)
docker compose up

# Start web + db
docker compose --profile database up

# Start web + db + debug
docker compose --profile database --profile dev up
```

---

## Override Files: Environment-Specific Config

Docker Compose automatically merges multiple files. Use this for environment-specific overrides.

### File Structure

```
project/
├── docker-compose.yml           # Base config
├── docker-compose.override.yml  # Auto-loaded for dev
└── docker-compose.prod.yml      # Production overrides
```

### Base File (`docker-compose.yml`)

```yaml
services:
  web:
    image: myapp:latest
    ports:
      - "8080:80"
```

### Dev Override (`docker-compose.override.yml`)

```yaml
services:
  web:
    build: .  # Build from source instead of using image
    volumes:
      - .:/app  # Hot reload
    environment:
      - DEBUG=true
```

### Production Override (`docker-compose.prod.yml`)

```yaml
services:
  web:
    deploy:
      replicas: 3
    environment:
      - DEBUG=false
```

### Usage

```bash
# Development (auto-loads override.yml)
docker compose up

# Production (explicit file)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Environment Variables

### From `.env` File

Docker Compose automatically loads a `.env` file from the project directory.

```bash
# .env
POSTGRES_PASSWORD=secretpassword
APP_VERSION=1.2.3
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  web:
    image: myapp:${APP_VERSION}
```

### From Shell Environment

```bash
export APP_VERSION=2.0.0
docker compose up  # Uses APP_VERSION=2.0.0
```

### Variable Substitution Syntax

| Syntax | Description |
| :--- | :--- |
| `${VAR}` | Use variable, error if unset |
| `${VAR:-default}` | Use default if unset |
| `${VAR:?error}` | Error with message if unset |

---

## Scaling Services

### Simple Scaling

```bash
# Scale web to 3 instances
docker compose up -d --scale web=3
```

### With Load Balancer

```yaml
services:
  web:
    image: myapp
    # No 'ports' here (handled by lb)

  lb:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web
```

---

## Health Checks and Dependencies

### Define Health Check in Compose

```yaml
services:
  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    image: myapp
    depends_on:
      db:
        condition: service_healthy  # Wait for db to be healthy
```

---

## Networking in Compose

### Default Network

All services in a Compose file automatically share a network and can reach each other by service name.

```yaml
services:
  web:
    image: nginx
  api:
    image: myapi
    # Can reach nginx at http://web:80
```

### Custom Networks

```yaml
services:
  frontend:
    image: nginx
    networks:
      - frontend-net

  backend:
    image: myapi
    networks:
      - frontend-net
      - backend-net

  db:
    image: postgres
    networks:
      - backend-net  # Not accessible to frontend

networks:
  frontend-net:
  backend-net:
```

---

## Useful Commands

```bash
# Rebuild images
docker compose build

# Rebuild and restart
docker compose up -d --build

# View logs for specific service
docker compose logs -f web

# Restart a single service
docker compose restart web

# Run a one-off command
docker compose run --rm web npm test

# Stop and remove everything (including volumes!)
docker compose down -v
```

---

## Summary

| Feature | Purpose |
| :--- | :--- |
| **Profiles** | Selective service startup (dev, test, debug) |
| **Override files** | Environment-specific config (dev vs prod) |
| **`.env` file** | Centralized variable management |
| **Scaling** | Run multiple instances of a service |
| **Health checks** | Ensure dependencies are ready |
| **Custom networks** | Control service-to-service access |

**Next Chapter:** Learn orchestration concepts in **Chapter 13: Orchestration 101 (Swarm)** or skip to **Chapter 17: Security Hardening**.
