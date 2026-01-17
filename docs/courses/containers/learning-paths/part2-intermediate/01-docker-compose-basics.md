# Docker Compose Basics

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 45 minutes

## Learning Objectives

By the end of this section, you will be able to:

- Understand what Docker Compose is and when to use it
- Write compose.yaml files for multi-container applications
- Use essential Compose commands
- Define services, networks, and volumes in Compose

---

## What is Docker Compose?

Docker Compose is a tool for defining and running multi-container applications.

### Without Compose (The Problem)

Running a web app with database:

```bash
# Create network
docker network create myapp

# Run database
docker run -d --name db \
    --network myapp \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=myapp \
    -v pgdata:/var/lib/postgresql/data \
    postgres:15

# Run backend
docker run -d --name api \
    --network myapp \
    -e DATABASE_URL=postgres://postgres:secret@db:5432/myapp \
    -p 3000:3000 \
    myapi:latest

# Run frontend
docker run -d --name web \
    --network myapp \
    -e API_URL=http://api:3000 \
    -p 80:80 \
    myfrontend:latest
```

**Problems:**
- Many commands to remember
- Easy to make mistakes
- Hard to share setup with team
- Tedious to reproduce

### With Compose (The Solution)

```yaml
# compose.yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    image: myapi:latest
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
    ports:
      - "3000:3000"
    depends_on:
      - db

  web:
    image: myfrontend:latest
    environment:
      API_URL: http://api:3000
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  pgdata:
```

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down
```

---

## Compose File Basics

### File Naming

```
compose.yaml        # Preferred (modern)
compose.yml         # Also works
docker-compose.yaml # Legacy but still supported
docker-compose.yml  # Legacy but still supported
```

### Minimal Structure

```yaml
# compose.yaml
services:
  service_name:
    image: image_name:tag
```

### Full Structure

```yaml
# compose.yaml
name: myapp  # Optional project name

services:
  service1:
    # Service definition
  service2:
    # Service definition

networks:
  mynetwork:
    # Network definition

volumes:
  myvolume:
    # Volume definition

configs:
  myconfig:
    # Config definition

secrets:
  mysecret:
    # Secret definition
```

---

## Defining Services

### Basic Service

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
```

### Service with Build

```yaml
services:
  app:
    build: .                    # Build from Dockerfile in current directory
    # OR
    build:
      context: ./src            # Build context path
      dockerfile: Dockerfile.prod
      args:
        VERSION: "1.0"
```

### Service with Environment

```yaml
services:
  app:
    image: myapp
    environment:
      - DATABASE_URL=postgres://localhost/db
      - DEBUG=true
    # OR
    environment:
      DATABASE_URL: postgres://localhost/db
      DEBUG: "true"
    # OR from file
    env_file:
      - .env
      - .env.local
```

### Service with Volumes

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data     # Named volume
      - ./init:/docker-entrypoint-initdb.d  # Bind mount
      - /host/path:/container/path:ro       # Read-only bind mount

volumes:
  pgdata:
```

### Service with Networking

```yaml
services:
  app:
    image: myapp
    networks:
      - frontend
      - backend
    ports:
      - "3000:3000"            # host:container
      - "127.0.0.1:3001:3001"  # localhost only
    expose:
      - "4000"                  # Internal only, no host mapping

networks:
  frontend:
  backend:
```

### Service Dependencies

```yaml
services:
  web:
    image: nginx
    depends_on:
      - api
      - db

  api:
    image: myapi
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Essential Commands

### Starting Services

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Start specific services
docker compose up web db

# Build and start
docker compose up --build

# Force recreate containers
docker compose up --force-recreate
```

### Stopping Services

```bash
# Stop services (keeps containers)
docker compose stop

# Stop and remove containers
docker compose down

# Also remove volumes
docker compose down -v

# Also remove images
docker compose down --rmi all
```

### Viewing Status

```bash
# List running services
docker compose ps

# List all services (including stopped)
docker compose ps -a

# View logs
docker compose logs

# Follow logs
docker compose logs -f

# Logs for specific service
docker compose logs web

# Last 100 lines
docker compose logs --tail 100
```

### Managing Services

```bash
# Restart services
docker compose restart

# Restart specific service
docker compose restart web

# Scale a service
docker compose up -d --scale web=3

# Execute command in service
docker compose exec web sh

# Run one-off command
docker compose run --rm web npm test
```

---

## Practical Example

### Full-Stack Application

Create a directory structure:

```
myapp/
├── compose.yaml
├── frontend/
│   ├── Dockerfile
│   └── src/
├── backend/
│   ├── Dockerfile
│   └── src/
└── .env
```

`compose.yaml`:

```yaml
name: myapp

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-appuser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?Database password required}
      POSTGRES_DB: ${DB_NAME:-myapp}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-appuser}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  # Redis Cache
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
    networks:
      - backend

  # Backend API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgres://${DB_USER:-appuser}:${DB_PASSWORD}@db:5432/${DB_NAME:-myapp}
      REDIS_URL: redis://redis:6379
      NODE_ENV: ${NODE_ENV:-development}
    ports:
      - "${API_PORT:-3000}:3000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - frontend
      - backend
    volumes:
      - ./backend/src:/app/src:ro  # Dev: mount source code

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      REACT_APP_API_URL: ${API_URL:-http://localhost:3000}
    ports:
      - "${FRONTEND_PORT:-80}:80"
    depends_on:
      - api
    networks:
      - frontend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

volumes:
  postgres_data:
  redis_data:
```

`.env`:

```bash
# Database
DB_USER=appuser
DB_PASSWORD=secretpassword
DB_NAME=myapp

# Ports
API_PORT=3000
FRONTEND_PORT=80

# Environment
NODE_ENV=development
```

### Running the Application

```bash
# Start everything
docker compose up -d

# View status
docker compose ps

# View logs
docker compose logs -f

# Scale backend
docker compose up -d --scale api=3

# Stop everything
docker compose down
```

---

## Variable Substitution

### Environment Variables

```yaml
services:
  web:
    image: nginx:${NGINX_VERSION:-latest}
    environment:
      # From shell environment
      - API_KEY=${API_KEY}
      # With default value
      - DEBUG=${DEBUG:-false}
      # Required (error if not set)
      - SECRET=${SECRET:?Secret is required}
```

### .env File

```bash
# .env (automatically loaded)
NGINX_VERSION=1.25
API_KEY=abc123
DEBUG=true
SECRET=mysecret
```

---

## Docker Compose vs Podman Compose

### Using podman-compose

```bash
# Install
pip install podman-compose

# Use same commands
podman-compose up -d
podman-compose down
```

### Using podman compose

```bash
# Podman 4.1+ with compose plugin
podman compose up -d
podman compose down
```

### Key Differences

| Feature | docker compose | podman-compose |
|---------|---------------|----------------|
| Daemon | Requires dockerd | Daemonless |
| Rootless | Requires setup | Default |
| Pod support | No | Yes (can create pod) |
| Command | `docker compose` | `podman-compose` or `podman compose` |

---

## Key Takeaways

1. **Compose simplifies multi-container apps** - one file, one command
2. **Services, networks, and volumes** are the core concepts
3. **Environment variables** make compose files flexible
4. **depends_on with health checks** ensures proper startup order
5. **Use -d for background** and logs to debug
6. **Works with both Docker and Podman**

---

## What's Next

Learn about advanced Compose features including profiles, extensions, and production configurations.

Continue to: [02-compose-advanced.md](02-compose-advanced.md)

---

## Quick Quiz

1. What is the modern preferred filename for Compose files?
   - [ ] docker-compose.yml
   - [x] compose.yaml
   - [ ] services.yaml
   - [ ] stack.yaml

2. How do you start services in the background?
   - [ ] `docker compose start`
   - [ ] `docker compose up --background`
   - [x] `docker compose up -d`
   - [ ] `docker compose run -d`

3. What does `depends_on` do?
   - [ ] Copies files between services
   - [x] Controls startup order
   - [ ] Creates network links
   - [ ] Shares volumes

4. How do you view logs for a specific service?
   - [ ] `docker compose log web`
   - [x] `docker compose logs web`
   - [ ] `docker compose show logs web`
   - [ ] `docker compose web logs`
