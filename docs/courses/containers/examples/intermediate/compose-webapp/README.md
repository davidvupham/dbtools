# Compose Web Application Example

> **Level:** Intermediate | **Time:** 30 minutes

## Overview

This example demonstrates a complete web application stack using Docker Compose:

- **Frontend**: Nginx serving static files
- **Backend**: Python Flask API
- **Database**: PostgreSQL
- **Cache**: Redis
- **Admin Tool**: Adminer (optional)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend Network                  │
│                                                      │
│  ┌──────────────┐        ┌──────────────┐          │
│  │   Frontend   │───────►│     API      │          │
│  │   (nginx)    │        │   (Flask)    │          │
│  │    :80       │        │    :5000     │          │
│  └──────────────┘        └──────┬───────┘          │
│                                 │                   │
└─────────────────────────────────┼───────────────────┘
                                  │
┌─────────────────────────────────┼───────────────────┐
│              Backend Network    │    (internal)     │
│                                 │                   │
│  ┌──────────────┐        ┌──────▼───────┐          │
│  │    Redis     │◄───────│     API      │          │
│  │    :6379     │        │              │          │
│  └──────────────┘        └──────┬───────┘          │
│                                 │                   │
│                          ┌──────▼───────┐          │
│                          │  PostgreSQL  │          │
│                          │    :5432     │          │
│                          └──────────────┘          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
compose-webapp/
├── compose.yaml
├── .env.example
├── init-db.sql
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── __init__.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── public/
        └── index.html
```

## Quick Start

### 1. Set Up Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional)
```

### 2. Start Services

```bash
# Start all services
docker compose up -d

# View status
docker compose ps

# View logs
docker compose logs -f
```

### 3. Access Application

- **Frontend**: http://localhost
- **API**: http://localhost:5000
- **API Health**: http://localhost:5000/health
- **Adminer** (optional): http://localhost:8080

### 4. Start with Adminer

```bash
# Include debug profile
docker compose --profile debug up -d
```

## Services

### Database (PostgreSQL)

- **Image**: postgres:15-alpine
- **Port**: 5432 (internal only)
- **Credentials**: appuser / secretpassword
- **Database**: webapp

```bash
# Connect to database
docker compose exec db psql -U appuser -d webapp

# Run SQL query
docker compose exec db psql -U appuser -d webapp -c "SELECT * FROM users;"
```

### Cache (Redis)

- **Image**: redis:7-alpine
- **Port**: 6379 (internal only)

```bash
# Access Redis CLI
docker compose exec redis redis-cli

# Test connection
docker compose exec redis redis-cli ping
```

### API (Flask)

- **Build**: ./api
- **Port**: 5000
- **Endpoints**:
  - `GET /` - Welcome message
  - `GET /health` - Health check
  - `GET /api/users` - List users
  - `POST /api/users` - Create user

```bash
# Test API
curl http://localhost:5000/health
curl http://localhost:5000/api/users
```

### Frontend (Nginx)

- **Build**: ./frontend
- **Port**: 80
- **Proxies** `/api/*` to backend

## Development

### Watch Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build api
```

### Access Container Shell

```bash
# API container
docker compose exec api sh

# Database container
docker compose exec db bash
```

## Cleanup

```bash
# Stop services
docker compose down

# Stop and remove volumes (deletes data!)
docker compose down -v

# Remove everything including images
docker compose down -v --rmi all
```

## Key Concepts Demonstrated

1. **Multi-container application** with compose
2. **Network isolation** (frontend/backend)
3. **Health checks** for dependencies
4. **Volume persistence** for data
5. **Environment variables** for configuration
6. **Profiles** for optional services
7. **Build context** for custom images

## Troubleshooting

### Database not ready

```bash
# Check database logs
docker compose logs db

# Verify health
docker compose exec db pg_isready -U appuser
```

### API can't connect

```bash
# Check network
docker compose exec api ping db

# Check environment
docker compose exec api env | grep DATABASE
```

### Port already in use

```bash
# Change port in compose.yaml or use different host port
ports:
  - "8081:80"  # Use 8081 instead of 80
```

## Next Steps

- Add authentication
- Implement CI/CD pipeline
- Add monitoring (Prometheus/Grafana)
- Deploy to production
