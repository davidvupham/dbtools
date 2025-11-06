# Chapter 11: Introduction to Docker Compose

Compose defines multi‑container apps declaratively.

```yaml
services:
  web:
    image: nginx:alpine
    ports: ["8080:80"]
  redis:
    image: redis:7-alpine
```

```bash
docker compose up -d
docker compose logs -f
docker compose down
```

---

## A slightly larger example

```yaml
# compose.yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./site:/usr/share/nginx/html:ro
    depends_on:
      - api
    networks: [app]

  api:
    image: hashicorp/http-echo
    command: ["-listen=:5000", "-text=hello from api"]
    ports:
      - "5000:5000"
    networks: [app]

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks: [app]

volumes:
  pgdata:

networks:
  app:
```

Lifecycle and common commands:

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
docker compose exec db psql -U postgres -c 'select now()'
docker compose restart web
docker compose down             # remove containers, keep volumes
docker compose down -v          # remove volumes too
```

Best practices:
- Keep secrets out of compose files; use env vars or external secrets providers.
- Use named volumes for databases; avoid bind mounts for prod data.
- Use user‑defined networks for service discovery; refer to services by name.
- Split dev/prod with profiles and override files (see Chapter 12).

Troubleshooting:
- `docker compose config` to see the fully-resolved configuration.
- `docker compose logs -f` to stream logs; add `--since 5m` for recent issues.
- `docker compose exec <svc> sh` to debug inside a container.

Next steps: See [Chapter 12: Advanced Compose](./chapter12_compose_advanced.md) for profiles, overrides, scaling, and production patterns.
