# Chapter 12: Advanced Compose

- Profiles for dev/prod variants
- Overrides and environment files
- Scaling services

```yaml
services:
  web:
    image: myorg/web:1.0
    profiles: ["dev"]
```

```bash
docker compose --profile dev up -d
```

---

## Profiles and overrides

Use profiles to include or exclude services by environment.

```yaml
# compose.yaml
services:
  web:
    build: ./web
    ports: ["8080:80"]
  redis:
    image: redis:7-alpine
    profiles: ["dev"]
```

```bash
# Start only default services
docker compose up -d

# Include dev-only services
docker compose --profile dev up -d
```

Override files apply on top of base configuration.

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

## Environment files and secrets

```yaml
services:
  app:
    image: myorg/app:1.0
    env_file: [.env]
    environment:
      LOG_LEVEL: info
    secrets: [app_token]

secrets:
  app_token:
    file: ./secrets/app_token
```

Keep secrets out of VCS; mount as files and read at runtime.

## Scaling and dependencies

```bash
docker compose up -d --scale web=3
docker compose ps
```

Service dependencies control startup order but not readiness; add healthchecks.

```yaml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
  app:
    build: ./app
    depends_on:
      db:
        condition: service_healthy
```

## Production-friendly patterns

- Use explicit image tags, not `latest`.
- Use named volumes for data.
- Keep per-env differences in small override files.
- Externalize secrets and sensitive configs.
