# Development workflows with containers

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Set up efficient development environments
- Use bind mounts for hot reloading
- Configure development vs production builds
- Debug applications in containers

---

## Development environment goals

| Goal | Solution |
|------|----------|
| Fast iteration | Bind mounts + hot reload |
| Consistent environment | Same Dockerfile for dev/prod |
| Easy debugging | Debug tools + source maps |
| Quick startup | Prebuilt dependencies |

---

## Bind mounts for development

### Basic setup

```yaml
# compose.yaml
services:
  api:
    build: ./api
    volumes:
      - ./api/src:/app/src        # Mount source code
      - /app/node_modules         # Anonymous volume for deps
    environment:
      - NODE_ENV=development
```

### Hot reload patterns

**Node.js with nodemon:**

```yaml
services:
  api:
    build: ./api
    volumes:
      - ./api:/app
      - /app/node_modules
    command: npm run dev
    environment:
      - NODE_ENV=development
```

```json
// package.json
{
  "scripts": {
    "dev": "nodemon --watch src src/index.js",
    "start": "node src/index.js"
  }
}
```

**Python with Flask:**

```yaml
services:
  api:
    build: ./api
    volumes:
      - ./api:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
```

**React/Vue/Angular:**

```yaml
services:
  frontend:
    build: ./frontend
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true  # For Docker on Windows/Mac
```

---

## Compose override pattern

### Base configuration

```yaml
# compose.yaml (production-ready base)
services:
  api:
    build:
      context: ./api
      target: production
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production

  frontend:
    build:
      context: ./frontend
      target: production
    ports:
      - "80:80"

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Development override

```yaml
# compose.override.yaml (auto-loaded in development)
services:
  api:
    build:
      target: development
    volumes:
      - ./api:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DEBUG=true

  frontend:
    build:
      target: development
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules
    environment:
      - NODE_ENV=development

  db:
    ports:
      - "5432:5432"  # Expose for local tools
```

### Usage

```bash
# Development (auto-loads override)
docker compose up -d

# Production (explicit file)
docker compose -f compose.yaml up -d

# Preview merged config
docker compose config
```

---

## Multi-stage Dockerfile for dev/prod

```dockerfile
# Base stage
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

# Development stage
FROM base AS development
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

---

## Development tools integration

### VS Code Dev Containers

```json
// .devcontainer/devcontainer.json
{
  "name": "My Project",
  "dockerComposeFile": ["../compose.yaml", "compose.devcontainer.yaml"],
  "service": "api",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "esbenp.prettier-vscode"
      ]
    }
  },
  "forwardPorts": [5000, 3000, 5432],
  "postCreateCommand": "npm install"
}
```

### Debug configuration

```yaml
# compose.debug.yaml
services:
  api:
    build:
      target: development
    ports:
      - "5000:5000"
      - "9229:9229"  # Node.js debugger
    command: node --inspect=0.0.0.0:9229 src/index.js
    volumes:
      - ./api:/app
      - /app/node_modules
```

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Docker: Attach to Node",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "address": "localhost",
      "localRoot": "${workspaceFolder}/api",
      "remoteRoot": "/app",
      "restart": true
    }
  ]
}
```

---

## Database development

### Local database with seed data

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: developer
      POSTGRES_PASSWORD: devpassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

```sql
-- init-db/01-schema.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- init-db/02-seed.sql
INSERT INTO users (email) VALUES
    ('test@example.com'),
    ('dev@example.com');
```

### Reset database

```bash
# Reset database (removes volume)
docker compose down -v
docker compose up -d

# Or recreate just the database
docker compose rm -sf db
docker volume rm myapp_postgres_data
docker compose up -d db
```

---

## Testing in containers

### Run tests in container

```yaml
# compose.test.yaml
services:
  test:
    build:
      context: ./api
      target: development
    command: npm test
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgres://test:test@db:5432/testdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test -d testdb"]
      interval: 5s
      timeout: 5s
      retries: 5
```

```bash
# Run tests
docker compose -f compose.test.yaml run --rm test

# With coverage
docker compose -f compose.test.yaml run --rm test npm run test:coverage
```

### Watch mode for TDD

```yaml
services:
  test-watch:
    build:
      context: ./api
      target: development
    command: npm run test:watch
    volumes:
      - ./api/src:/app/src
      - ./api/tests:/app/tests
      - /app/node_modules
```

---

## Performance tips

### Optimize file watching

```yaml
services:
  frontend:
    environment:
      # For webpack/React on Docker Desktop
      - CHOKIDAR_USEPOLLING=true
      - WATCHPACK_POLLING=true
```

### Cache dependencies

```dockerfile
# Good: Cache dependencies separately
FROM node:20-alpine
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
```

### Use named volumes for deps

```yaml
services:
  api:
    volumes:
      - ./api:/app
      - api_node_modules:/app/node_modules  # Named volume

volumes:
  api_node_modules:
```

---

## Practical example: Full stack development

```yaml
# compose.yaml
name: fullstack-dev

services:
  frontend:
    build:
      context: ./frontend
      target: development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:5000
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - api

  api:
    build:
      context: ./api
      target: development
    ports:
      - "5000:5000"
      - "9229:9229"
    volumes:
      - ./api/src:/app/src
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://dev:devpass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: devpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Database admin (optional)
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    profiles:
      - tools

volumes:
  postgres_data:
```

---

## Key takeaways

1. **Use compose.override.yaml** for development-specific config
2. **Bind mount source code** for hot reloading
3. **Multi-stage builds** share base with different targets
4. **Named volumes** for dependencies improve performance
5. **Expose database ports** for local tool access

---

## What's next

Learn about production deployment considerations.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Resource Management](11-resource-management.md) | [Part 2 Overview](../../course_overview.md#part-2-intermediate) | [Production Considerations](13-production-considerations.md) |
