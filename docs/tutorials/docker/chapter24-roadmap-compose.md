# Docker Compose Basics

## Introduction
Docker Compose simplifies running multi-container applications.

## `docker-compose.yml` Structure
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  redis:
    image: "redis:alpine"
```

## Commands
- `docker-compose up -d`: Start services in background.
- `docker-compose down`: Stop and remove containers.
- `docker-compose logs -f`: Follow logs.
