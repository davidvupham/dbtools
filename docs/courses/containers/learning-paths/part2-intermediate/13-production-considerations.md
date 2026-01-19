# Production deployment considerations

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Prepare containers for production
- Implement security hardening
- Configure high availability
- Plan deployment strategies

---

## Production readiness checklist

### Essential requirements

- [ ] Non-root user
- [ ] Read-only filesystem where possible
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Proper logging
- [ ] Secrets management
- [ ] Image scanning completed
- [ ] Restart policies configured

---

## Security hardening

### Run as non-root

```dockerfile
FROM node:20-alpine

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app
COPY --chown=appuser:appgroup . .

USER appuser
CMD ["node", "index.js"]
```

### Read-only containers

```yaml
services:
  api:
    image: myapi:latest
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    volumes:
      - logs:/app/logs  # Writable volume for logs
```

### Security options

```yaml
services:
  api:
    image: myapi:latest
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if needed
```

### No privileged containers

```yaml
# Never do this in production
services:
  dangerous:
    image: myimage
    privileged: true  # AVOID
```

---

## Image security

### Use specific tags

```yaml
# Bad
services:
  api:
    image: node:latest  # Unpredictable

# Good
services:
  api:
    image: node:20.10.0-alpine3.18  # Specific version
```

### Image scanning

```bash
# Scan with Docker Scout
docker scout cves myimage:latest

# Scan with Trivy
trivy image myimage:latest

# Scan with Grype
grype myimage:latest
```

### Minimal base images

```dockerfile
# Production: minimal base
FROM node:20-alpine AS production

# Or distroless for compiled apps
FROM gcr.io/distroless/nodejs20
```

---

## High availability

### Restart policies

```yaml
services:
  api:
    image: myapi:latest
    restart: unless-stopped
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

### Multiple replicas

```yaml
services:
  api:
    image: myapi:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
```

### Load balancing

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api

  api:
    image: myapi:latest
    deploy:
      replicas: 3
    expose:
      - "5000"
```

```nginx
# nginx.conf
upstream api {
    server api:5000;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Resource management

### Set limits

```yaml
services:
  api:
    image: myapi:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Memory for JVM/Node.js

```yaml
services:
  java-api:
    image: myjavaapi:latest
    environment:
      - JAVA_OPTS=-Xmx384m -Xms384m
    deploy:
      resources:
        limits:
          memory: 512M

  node-api:
    image: mynodeapi:latest
    environment:
      - NODE_OPTIONS=--max-old-space-size=384
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## Graceful shutdown

### Handle signals

```javascript
// Node.js graceful shutdown
const server = app.listen(port);

process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received');
    server.close(() => process.exit(0));
});
```

### Configure stop timeout

```yaml
services:
  api:
    image: myapi:latest
    stop_grace_period: 30s  # Time before SIGKILL
```

### Use init system

```dockerfile
FROM node:20-alpine

# Add dumb-init for signal handling
RUN apk add --no-cache dumb-init

USER node
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "index.js"]
```

---

## Logging for production

### Structured logging

```yaml
services:
  api:
    image: myapi:latest
    environment:
      - LOG_FORMAT=json
      - LOG_LEVEL=info
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
```

### Centralized logging

```yaml
services:
  api:
    image: myapi:latest
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: api.{{.Name}}
```

---

## Health checks

```yaml
services:
  api:
    image: myapi:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Health endpoint best practices

```python
# Python Flask health endpoint
@app.route('/health')
def health():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space()
    }

    status = 'healthy' if all(checks.values()) else 'unhealthy'
    code = 200 if status == 'healthy' else 503

    return jsonify({
        'status': status,
        'checks': checks,
        'version': app.config['VERSION']
    }), code
```

---

## Deployment strategies

### Blue-green deployment

```bash
# Deploy new version
docker compose -f compose.yaml -p myapp-green up -d

# Test new version
curl http://localhost:8081/health

# Switch traffic (update load balancer)
# ...

# Remove old version
docker compose -f compose.yaml -p myapp-blue down
```

### Rolling update

```yaml
services:
  api:
    image: myapi:${VERSION}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1       # Update one at a time
        delay: 30s           # Wait between updates
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.1
```

### Canary deployment

```yaml
services:
  api-stable:
    image: myapi:v1.0.0
    deploy:
      replicas: 9

  api-canary:
    image: myapi:v1.1.0
    deploy:
      replicas: 1  # 10% of traffic
```

---

## Production compose example

```yaml
name: myapp-production

services:
  api:
    image: myregistry/api:${VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      update_config:
        parallelism: 1
        delay: 30s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    environment:
      - NODE_ENV=production
      - DATABASE_URL_FILE=/run/secrets/database_url
    secrets:
      - database_url
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
    networks:
      - frontend
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    deploy:
      replicas: 2
    depends_on:
      - api
    networks:
      - frontend

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    deploy:
      resources:
        limits:
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

secrets:
  database_url:
    external: true
  db_password:
    external: true

networks:
  frontend:
  backend:
    internal: true

volumes:
  postgres_data:
```

---

## Key takeaways

1. **Run as non-root** with minimal capabilities
2. **Set resource limits** to prevent runaway containers
3. **Use health checks** for automatic recovery
4. **Implement graceful shutdown** for zero-downtime deploys
5. **Use secrets** for sensitive configuration
6. **Plan deployment strategy** (rolling, blue-green, canary)

---

## What's next

Complete the intermediate exercises and quiz.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Development Workflows](12-development-workflows.md) | [Part 2 Overview](../../course_overview.md#part-2-intermediate) | [Part 2 Quiz](quiz.md) |
