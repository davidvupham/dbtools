# Docker stacks

> **Module:** Part 3 - Advanced | **Level:** Advanced | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Deploy applications using Docker Stacks
- Convert Compose files to Stack format
- Manage stack lifecycle
- Implement production deployments

---

## Stacks vs Compose

| Feature | Docker Compose | Docker Stacks |
|---------|---------------|---------------|
| Target | Development, single host | Production, Swarm cluster |
| Execution | Docker Compose CLI | Docker CLI (Swarm mode) |
| Scaling | Manual, per-service | Declarative, orchestrated |
| Build | Supports `build:` | Pre-built images only |
| Networks | Bridge default | Overlay networks |
| Secrets | File-based | Swarm secrets |

---

## Stack file format

Stacks use Compose file format with Swarm-specific options:

```yaml
# stack.yaml
version: '3.8'

services:
  api:
    image: myregistry/api:v1.0.0
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      placement:
        constraints:
          - node.role == worker
    ports:
      - "5000:5000"
    networks:
      - frontend
      - backend
    secrets:
      - api_secret
    configs:
      - source: api_config
        target: /app/config.yaml

networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay
    internal: true

secrets:
  api_secret:
    external: true

configs:
  api_config:
    file: ./config/api.yaml
```

---

## Deploying stacks

### Basic deployment

```bash
# Deploy stack
docker stack deploy -c stack.yaml myapp

# Deploy with multiple files
docker stack deploy \
    -c stack.yaml \
    -c stack.prod.yaml \
    myapp
```

### Stack commands

```bash
# List stacks
docker stack ls

# List stack services
docker stack services myapp

# List stack tasks
docker stack ps myapp

# Inspect stack
docker stack ps myapp --no-trunc

# Remove stack
docker stack rm myapp
```

---

## Converting Compose to Stack

### What changes

**Not supported in stacks:**
- `build:` - must use pre-built images
- `container_name:` - auto-generated
- `depends_on:` - use health checks instead
- `links:` - deprecated
- Host networking mode

**Stack-specific options:**
```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
  resources:
    limits:
      memory: 512M
  placement:
    constraints:
      - node.role == worker
```

### Conversion example

**Compose (development):**
```yaml
services:
  api:
    build: ./api
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://db:5432/app
    volumes:
      - ./api:/app
    ports:
      - "5000:5000"
```

**Stack (production):**
```yaml
services:
  api:
    image: myregistry/api:v1.0.0
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
    environment:
      - DATABASE_URL=postgres://db:5432/app
    secrets:
      - db_password
    ports:
      - "5000:5000"
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Secrets in stacks

### Create secrets first

```bash
# Create secrets
echo "dbpassword" | docker secret create db_password -
echo "apisecret" | docker secret create api_secret -

# From file
docker secret create ssl_cert ./certs/server.crt
docker secret create ssl_key ./certs/server.key
```

### Reference in stack

```yaml
services:
  api:
    image: myapi:latest
    secrets:
      - db_password
      - source: api_secret
        target: /run/secrets/secret_key
        mode: 0400

secrets:
  db_password:
    external: true
  api_secret:
    external: true
```

---

## Configs in stacks

### Inline config

```yaml
configs:
  nginx_config:
    file: ./nginx.conf

services:
  nginx:
    image: nginx:alpine
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
```

### External config

```bash
# Create config
docker config create nginx_config_v1 nginx.conf
```

```yaml
configs:
  nginx_config:
    external: true
    name: nginx_config_v1
```

### Config rotation

```bash
# Create new config version
docker config create nginx_config_v2 nginx.conf

# Update stack file to use new config
# Then redeploy
docker stack deploy -c stack.yaml myapp
```

---

## Networks in stacks

```yaml
services:
  frontend:
    image: nginx:alpine
    networks:
      - public

  api:
    image: myapi:latest
    networks:
      - public
      - private

  db:
    image: postgres:15-alpine
    networks:
      - private

networks:
  public:
    driver: overlay

  private:
    driver: overlay
    internal: true  # No external access
    attachable: true  # Allow standalone containers
```

---

## Volumes in stacks

```yaml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      placement:
        constraints:
          - node.labels.storage == ssd

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/data/postgres
      o: bind
```

**Note:** For distributed storage, use a volume plugin like:
- Portworx
- GlusterFS
- NFS

---

## Full stack example

```yaml
# stack.yaml
version: '3.8'

services:
  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    secrets:
      - ssl_cert
      - ssl_key
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == manager
    networks:
      - frontend

  # API service
  api:
    image: myregistry/api:${VERSION:-latest}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      placement:
        constraints:
          - node.role == worker
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    secrets:
      - db_password
      - api_secret
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # Background workers
  worker:
    image: myregistry/worker:${VERSION:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
    environment:
      - DATABASE_URL=postgres://postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    secrets:
      - db_password
    networks:
      - backend

  # PostgreSQL database
  postgres:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.storage == ssd
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    deploy:
      replicas: 1
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay
    internal: true

volumes:
  postgres_data:
  redis_data:

secrets:
  db_password:
    external: true
  api_secret:
    external: true
  ssl_cert:
    external: true
  ssl_key:
    external: true

configs:
  nginx_config:
    file: ./nginx.conf
```

---

## Deployment workflow

```bash
#!/bin/bash
# deploy.sh

set -e

STACK_NAME=myapp
VERSION=${1:-latest}

# Create secrets if they don't exist
if ! docker secret inspect db_password >/dev/null 2>&1; then
    echo "Creating db_password secret..."
    echo "$DB_PASSWORD" | docker secret create db_password -
fi

# Deploy/update stack
echo "Deploying stack with version $VERSION..."
VERSION=$VERSION docker stack deploy -c stack.yaml $STACK_NAME

# Wait for services to be ready
echo "Waiting for services..."
sleep 10

# Check service status
docker stack services $STACK_NAME

# Verify health
docker stack ps $STACK_NAME --filter "desired-state=running"
```

---

## Monitoring stacks

```bash
# Service status
docker stack services myapp

# Tasks across all nodes
docker stack ps myapp

# Filter failed tasks
docker stack ps myapp --filter "desired-state=shutdown"

# Service logs
docker service logs myapp_api

# Real-time updates
watch docker stack ps myapp
```

---

## Key takeaways

1. **Stacks** are the production deployment unit for Swarm
2. **Use pre-built images** - no build support in stacks
3. **External secrets** must be created before deployment
4. **Update configs** enable zero-downtime updates
5. **Network isolation** with overlay networks

---

## What's next

Learn about advanced orchestration patterns.

Continue to: [04-orchestration-patterns.md](04-orchestration-patterns.md)
