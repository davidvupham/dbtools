# Compose volumes and storage

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Configure named volumes in Compose
- Use bind mounts for development
- Manage volume lifecycle
- Implement backup strategies

---

## Volume types in Compose

### Named volumes

```yaml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:  # Named volume - managed by Docker/Podman
```

### Bind mounts

```yaml
services:
  web:
    image: nginx
    volumes:
      - ./html:/usr/share/nginx/html:ro  # Host path:container path
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

### tmpfs mounts

```yaml
services:
  api:
    image: myapi
    tmpfs:
      - /tmp
      - /run
```

---

## Volume syntax

### Short syntax

```yaml
volumes:
  # Named volume
  - data:/app/data

  # Bind mount (absolute)
  - /host/path:/container/path

  # Bind mount (relative)
  - ./local:/container/path

  # Read-only
  - ./config:/app/config:ro

  # Named volume read-only
  - data:/app/data:ro
```

### Long syntax

```yaml
services:
  api:
    volumes:
      - type: volume
        source: api_data
        target: /app/data
        read_only: false

      - type: bind
        source: ./src
        target: /app/src
        read_only: true

      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 100000000  # 100MB

volumes:
  api_data:
```

---

## Volume configuration

### Named volume options

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/data/postgres
      o: bind
```

### External volumes

```yaml
volumes:
  shared_data:
    external: true  # Must exist before compose up
    name: my-existing-volume
```

```bash
# Create volume first
docker volume create my-existing-volume

# Then run compose
docker compose up -d
```

### Labels

```yaml
volumes:
  app_data:
    labels:
      - "com.example.project=myapp"
      - "com.example.environment=production"
```

---

## Development patterns

### Hot reload with bind mounts

```yaml
services:
  frontend:
    build: ./frontend
    volumes:
      - ./frontend/src:/app/src        # Source code
      - ./frontend/public:/app/public  # Static files
      - /app/node_modules              # Anonymous volume (preserve)
    environment:
      - CHOKIDAR_USEPOLLING=true       # For file watching
```

### Development vs production

```yaml
# compose.yaml (production)
services:
  api:
    image: myapi:latest
    volumes:
      - api_logs:/app/logs

volumes:
  api_logs:
```

```yaml
# compose.override.yaml (development - auto-loaded)
services:
  api:
    build: ./api
    volumes:
      - ./api/src:/app/src:ro
      - api_logs:/app/logs
```

```bash
# Development (loads both files)
docker compose up -d

# Production (explicit file)
docker compose -f compose.yaml up -d
```

---

## Database persistence

### PostgreSQL

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### MongoDB

```yaml
services:
  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
      - mongo_config:/data/configdb

volumes:
  mongo_data:
  mongo_config:
```

### Redis

```yaml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

---

## Shared volumes

### Between services

```yaml
services:
  writer:
    image: writer-app
    volumes:
      - shared_data:/data

  reader:
    image: reader-app
    volumes:
      - shared_data:/data:ro

volumes:
  shared_data:
```

### Between projects

```yaml
# Project A
volumes:
  shared:
    name: cross-project-data

# Project B
volumes:
  shared:
    external: true
    name: cross-project-data
```

---

## Volume management

### Lifecycle commands

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect myapp_postgres_data

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm myapp_postgres_data

# Remove all project volumes
docker compose down -v
```

### Backup volumes

```bash
# Backup a volume to tar file
docker run --rm \
  -v myapp_postgres_data:/data:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore from tar file
docker run --rm \
  -v myapp_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

### Backup script example

```bash
#!/bin/bash
# backup-volumes.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Stop services for consistent backup
docker compose stop

# Backup each volume
for volume in $(docker volume ls -q | grep myapp); do
    echo "Backing up $volume..."
    docker run --rm \
        -v "$volume":/data:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/${volume}.tar.gz" -C /data .
done

# Restart services
docker compose start

echo "Backup complete: $BACKUP_DIR"
```

---

## Practical example: Full application

```yaml
name: webapp

services:
  # Frontend with development bind mount
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend/src:/app/src:ro      # Dev: hot reload
      - ./frontend/public:/app/public:ro
      - frontend_build:/app/build       # Build output
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=${NODE_ENV:-development}

  # API with logs volume
  api:
    build: ./api
    volumes:
      - ./api/src:/app/src:ro           # Dev: hot reload
      - api_logs:/app/logs
      - upload_data:/app/uploads
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  # Database with persistent data
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis with AOF persistence
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # Scheduled backup service
  backup:
    image: alpine
    volumes:
      - postgres_data:/postgres:ro
      - redis_data:/redis:ro
      - ./backups:/backups
    command: |
      sh -c 'while true; do
        tar czf /backups/postgres_$(date +%Y%m%d_%H%M).tar.gz -C /postgres .
        tar czf /backups/redis_$(date +%Y%m%d_%H%M).tar.gz -C /redis .
        find /backups -mtime +7 -delete
        sleep 86400
      done'
    profiles:
      - backup

volumes:
  postgres_data:
    labels:
      - "com.example.backup=daily"
  redis_data:
  api_logs:
  upload_data:
  frontend_build:
```

---

## Key takeaways

1. **Named volumes** for persistent data (databases, uploads)
2. **Bind mounts** for development (source code, configs)
3. **Anonymous volumes** to preserve container-managed data
4. **External volumes** for cross-project sharing
5. **Regular backups** are essential for production

---

## What's next

Learn about building custom images in Compose.

Continue to: [05-building-images.md](05-building-images.md)
