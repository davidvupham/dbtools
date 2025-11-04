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
