# Building images with Compose

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Configure build contexts in Compose
- Use build arguments and targets
- Implement multi-stage builds
- Optimize build caching

---

## Build configuration basics

### Simple build

```yaml
services:
  api:
    build: ./api  # Context directory with Dockerfile
```

### Full build syntax

```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      args:
        - BUILD_VERSION=1.0.0
        - NODE_ENV=production
      target: production
      cache_from:
        - myregistry/api:cache
      labels:
        - "com.example.version=1.0.0"
      platforms:
        - linux/amd64
        - linux/arm64
```

---

## Build arguments

### Defining build args

```dockerfile
# api/Dockerfile
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine

ARG BUILD_VERSION=unknown
ENV APP_VERSION=${BUILD_VERSION}

COPY . .
RUN npm install
```

```yaml
# compose.yaml
services:
  api:
    build:
      context: ./api
      args:
        NODE_VERSION: "20"
        BUILD_VERSION: "2.1.0"
```

### Args from environment

```yaml
services:
  api:
    build:
      context: ./api
      args:
        - BUILD_VERSION  # Takes value from host environment
        - GIT_COMMIT=${GIT_COMMIT:-unknown}
```

```bash
# Pass at build time
BUILD_VERSION=1.2.3 docker compose build
```

---

## Multi-stage builds

### Dockerfile with stages

```dockerfile
# api/Dockerfile

# Stage 1: Build dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build application
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Development
FROM node:20-alpine AS development
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
CMD ["npm", "run", "dev"]

# Stage 4: Production
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

# Only copy built artifacts
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
COPY package*.json ./

USER node
CMD ["node", "dist/index.js"]
```

### Targeting stages in Compose

```yaml
services:
  api-dev:
    build:
      context: ./api
      target: development
    volumes:
      - ./api:/app
      - /app/node_modules

  api-prod:
    build:
      context: ./api
      target: production
    profiles:
      - production
```

---

## Development vs production builds

### Compose override pattern

```yaml
# compose.yaml (base)
services:
  api:
    build:
      context: ./api
      target: production
    environment:
      - NODE_ENV=production
```

```yaml
# compose.override.yaml (auto-loaded for development)
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
```

```bash
# Development (loads both files automatically)
docker compose up -d

# Production (explicit file, ignores override)
docker compose -f compose.yaml up -d
```

---

## Build caching

### Layer caching

Order Dockerfile instructions from least to most frequently changed:

```dockerfile
# Good: Dependencies cached separately
FROM node:20-alpine
WORKDIR /app

# Rarely changes - cached
COPY package*.json ./
RUN npm ci

# Frequently changes - not cached
COPY . .
RUN npm run build
```

### Cache from registry

```yaml
services:
  api:
    build:
      context: ./api
      cache_from:
        - myregistry/api:cache
        - myregistry/api:latest
    image: myregistry/api:latest
```

### BuildKit cache mounts

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine
WORKDIR /app

COPY package*.json ./

# Cache npm packages across builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY . .
RUN npm run build
```

---

## Build secrets

### Using build secrets

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine
WORKDIR /app

# Secret available only during build
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
```

```yaml
services:
  api:
    build:
      context: ./api
      secrets:
        - npmrc

secrets:
  npmrc:
    file: ./.npmrc
```

---

## Platform-specific builds

### Multi-platform builds

```yaml
services:
  api:
    build:
      context: ./api
      platforms:
        - linux/amd64
        - linux/arm64
    image: myregistry/api:latest
```

```bash
# Build for multiple platforms
docker compose build

# Push multi-arch image
docker compose push
```

---

## Build commands

```bash
# Build all services
docker compose build

# Build specific service
docker compose build api

# Build with no cache
docker compose build --no-cache

# Build and start
docker compose up -d --build

# Build with progress output
docker compose build --progress=plain

# Pull base images before build
docker compose build --pull
```

---

## Practical example: Full stack build

```yaml
name: fullstack

services:
  # React frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-development}
      args:
        - REACT_APP_API_URL=${API_URL:-http://localhost:5000}
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src:ro
    depends_on:
      - api

  # Node.js API
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      target: ${BUILD_TARGET:-development}
      args:
        - BUILD_VERSION=${VERSION:-dev}
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    volumes:
      - ./api/src:/app/src:ro
    depends_on:
      db:
        condition: service_healthy

  # PostgreSQL (no build needed)
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS development
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

FROM node:20-alpine AS builder
WORKDIR /app
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### API Dockerfile

```dockerfile
# api/Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS dev-deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS development
WORKDIR /app
COPY --from=dev-deps /app/node_modules ./node_modules
COPY . .
EXPOSE 5000
CMD ["npm", "run", "dev"]

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=dev-deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS production
WORKDIR /app
ARG BUILD_VERSION=unknown
ENV APP_VERSION=${BUILD_VERSION}
ENV NODE_ENV=production

COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package*.json ./

USER node
EXPOSE 5000
CMD ["node", "dist/index.js"]
```

---

## Key takeaways

1. **Build args** parameterize images at build time
2. **Multi-stage builds** create smaller production images
3. **Target selection** allows different builds from one Dockerfile
4. **Layer ordering** affects cache efficiency
5. **Override files** separate dev and prod configurations

---

## What's next

Learn about managing secrets and configuration.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Compose Volumes](04-compose-volumes.md) | [Part 2 Overview](../../course_overview.md#part-2-intermediate) | [Secrets and Config](06-secrets-config.md) |
