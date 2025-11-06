# Chapter 15: Docker‑Driven Dev Workflow

- Local stacks with Compose (DBs, caches, services)
- Live reload with bind mounts and app watchers
- Reproducible environments for onboarding

Check `examples/networking` and tailor for your services.

---

## Live reload patterns

Node.js example:

```yaml
# compose.yaml
services:
  api:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - ./:/app
    command: sh -c "npm ci && npx nodemon server.js"
    ports:
      - "3000:3000"
```

Python (Flask) example:

```yaml
services:
  api:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - ./:/app
    environment:
      FLASK_APP: app.py
      FLASK_RUN_HOST: 0.0.0.0
    command: sh -c "pip install -r requirements.txt && flask run"
    ports:
      - "5000:5000"
```

## Local stack for development

```yaml
services:
  app:
    build: ./app
    ports: ["8080:8080"]
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/app
    depends_on: [db, redis]

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - appdb:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  appdb:
```

## Dev containers (optional)

Develop “inside” a container for consistent toolchains (VS Code Dev Containers / GitHub Codespaces). Define a `.devcontainer/devcontainer.json` to preinstall SDKs and extensions.
