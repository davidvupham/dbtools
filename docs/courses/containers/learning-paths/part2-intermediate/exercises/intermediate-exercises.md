# Part 2 intermediate exercises

> **Level:** Intermediate | **Time:** 60-90 minutes

Complete these exercises to reinforce your Docker Compose and intermediate container skills.

---

## Exercise 1: Multi-service application

**Objective:** Build a complete application stack with Compose.

### Requirements

Create a `compose.yaml` for an application with:
- Flask/Node.js API
- PostgreSQL database
- Redis cache
- Nginx reverse proxy

### Steps

1. Create the directory structure:
   ```
   exercise1/
   ├── compose.yaml
   ├── .env
   ├── api/
   │   ├── Dockerfile
   │   └── app.py (or index.js)
   ├── nginx/
   │   └── nginx.conf
   └── init-db.sql
   ```

2. Implement health checks for all services

3. Configure proper dependencies with `depends_on`

4. Use environment variables for configuration

### Validation

```bash
# Start the stack
docker compose up -d

# All services should be healthy
docker compose ps

# API should respond
curl http://localhost/api/health

# Database should be accessible through API
curl http://localhost/api/users
```

---

## Exercise 2: Development environment

**Objective:** Set up a development workflow with hot reloading.

### Requirements

- Base compose.yaml for production
- compose.override.yaml for development
- Multi-stage Dockerfile with dev and prod targets
- Volume mounts for source code

### Steps

1. Create a multi-stage Dockerfile:
   ```dockerfile
   # Dockerfile
   FROM node:20-alpine AS base
   # ... base setup

   FROM base AS development
   # ... dev configuration

   FROM base AS production
   # ... prod configuration
   ```

2. Create compose files:
   ```yaml
   # compose.yaml (production base)
   services:
     api:
       build:
         context: .
         target: production
   ```

   ```yaml
   # compose.override.yaml (development)
   services:
     api:
       build:
         target: development
       volumes:
         - ./src:/app/src
   ```

### Validation

```bash
# Development mode (auto-loads override)
docker compose up -d
# Make a code change - should auto-reload

# Production mode (explicit file)
docker compose -f compose.yaml up -d
```

---

## Exercise 3: Custom network architecture

**Objective:** Implement network isolation between services.

### Requirements

Create a setup with:
- Public network (frontend, API)
- Private network (API, database, cache)
- Database not accessible from outside

### Architecture

```
Internet
    │
┌───▼───┐
│ nginx │  ─── public network
└───┬───┘
    │
┌───▼───┐
│  api  │  ─── public + private networks
└───┬───┘
    │
┌───▼───┐  ┌─────────┐
│  db   │  │  redis  │  ─── private network (internal)
└───────┘  └─────────┘
```

### Validation

```bash
# nginx can reach api
docker compose exec nginx ping api

# api can reach db
docker compose exec api ping db

# nginx CANNOT reach db
docker compose exec nginx ping db  # Should fail
```

---

## Exercise 4: Image optimization

**Objective:** Reduce image size using best practices.

### Requirements

Start with a naive Dockerfile and optimize it:

1. Use appropriate base image
2. Implement multi-stage build
3. Order layers for caching
4. Remove unnecessary files
5. Run as non-root user

### Starting point

```dockerfile
# Naive Dockerfile - optimize this
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "index.js"]
```

### Target

Reduce image size by at least 50%.

### Validation

```bash
# Build both versions
docker build -t myapp:naive -f Dockerfile.naive .
docker build -t myapp:optimized -f Dockerfile.optimized .

# Compare sizes
docker images | grep myapp
```

---

## Exercise 5: Secrets management

**Objective:** Properly manage secrets in Compose.

### Requirements

- Store database password in secrets file
- Configure application to read from secret file
- Use environment variables with _FILE suffix
- Don't commit secrets to git

### Implementation

```yaml
# compose.yaml
services:
  api:
    secrets:
      - db_password
    environment:
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password

  db:
    secrets:
      - db_password
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

```python
# Application code
import os

def get_secret(env_var):
    file_path = os.environ.get(env_var)
    if file_path and os.path.exists(file_path):
        with open(file_path) as f:
            return f.read().strip()
    return os.environ.get(env_var.replace('_FILE', ''))
```

### Validation

```bash
# Verify secrets are mounted
docker compose exec api cat /run/secrets/db_password

# Verify .gitignore
cat .gitignore | grep secrets
```

---

## Exercise 6: Health checks and dependencies

**Objective:** Implement robust startup ordering.

### Requirements

- Database with health check
- Migrations that run once
- API that waits for healthy database and completed migrations

### Implementation

```yaml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  migrations:
    build: ./migrations
    depends_on:
      db:
        condition: service_healthy
    restart: "no"

  api:
    build: ./api
    depends_on:
      db:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully
```

### Validation

```bash
# Clean start
docker compose down -v
docker compose up -d

# Watch startup order
docker compose logs -f

# Verify API waits for everything
docker compose ps
```

---

## Exercise 7: Resource limits

**Objective:** Configure and monitor resource usage.

### Requirements

- Set memory limits for all services
- Set CPU limits
- Monitor with docker stats
- Trigger and observe OOM behavior

### Implementation

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

  memory-hog:
    image: alpine
    command: |
      sh -c 'while true; do
        dd if=/dev/zero of=/dev/null bs=1M count=100
        sleep 0.1
      done'
    deploy:
      resources:
        limits:
          memory: 50M
    profiles:
      - test
```

### Validation

```bash
# Monitor resources
docker stats

# Test OOM (will restart)
docker compose --profile test up -d memory-hog
docker compose logs memory-hog
```

---

## Exercise 8: Production readiness

**Objective:** Prepare a compose file for production.

### Checklist

- [ ] All services run as non-root
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Secrets properly managed
- [ ] Logging configured
- [ ] Restart policies set
- [ ] Networks properly isolated
- [ ] No sensitive data in environment

### Template

Create `compose.prod.yaml` following all production best practices.

### Validation

```bash
# Validate configuration
docker compose -f compose.prod.yaml config

# Security check
docker compose -f compose.prod.yaml config | grep -E "(privileged|root)"
# Should return nothing

# Check resource limits
docker compose -f compose.prod.yaml config | grep -A5 resources
```

---

## Bonus challenges

### Challenge A: Zero-downtime deployment

Implement a blue-green deployment using Compose:
1. Run "blue" version
2. Deploy "green" version alongside
3. Switch traffic
4. Remove "blue" version

### Challenge B: Local development with HTTPS

Set up local development with:
- Self-signed certificates
- Nginx with SSL termination
- Automatic certificate generation with mkcert

### Challenge C: Database backup automation

Create a backup service that:
- Runs on a schedule
- Backs up PostgreSQL to a volume
- Keeps last 7 days of backups
- Can restore from backup

---

## Solutions

Solutions are available in the `solutions/` directory. Try to complete the exercises before checking the solutions.

```bash
ls solutions/
# exercise1/
# exercise2/
# ...
```
