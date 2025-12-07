# Chapter 15: Docker-Driven Dev Workflow

Docker transforms development by ensuring everyone on your team has the exact same environment. This chapter covers patterns for productive local development.

## The Goal: "Works on My Machine" → "Works Everywhere"

```bash
# Traditional setup
# 1. Install Python 3.11
# 2. Install PostgreSQL
# 3. Install Redis
# 4. Configure environment variables
# 5. Hope versions match production...

# Docker setup
git clone project
docker compose up
# Done!
```

---

## Pattern 1: Live Code Reload with Bind Mounts

Mount your source code into the container so changes reflect immediately.

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app           # Mount source code
      - /app/node_modules # Exclude node_modules (use container's version)
    environment:
      - NODE_ENV=development
    command: npm run dev  # Use a dev server with hot reload
```

### Why Exclude `node_modules`?

```yaml
volumes:
  - .:/app              # Mounts everything
  - /app/node_modules   # Anonymous volume prevents host node_modules from overwriting
```

This prevents conflicts between host and container dependencies.

---

## Pattern 2: Development vs Production Compose Files

Use override files for environment-specific settings.

```
project/
├── docker-compose.yml          # Base (production-like)
├── docker-compose.override.yml # Auto-loaded for dev
└── docker-compose.prod.yml     # Explicit production config
```

### Base (`docker-compose.yml`)

```yaml
services:
  web:
    image: myapp:latest
    ports:
      - "8080:80"
```

### Dev Override (`docker-compose.override.yml`)

```yaml
services:
  web:
    build: .
    volumes:
      - .:/app
    environment:
      - DEBUG=true
    command: npm run dev
```

### Usage

```bash
# Development (auto-loads override.yml)
docker compose up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Pattern 3: One-Off Commands

Run commands inside your dev environment without installing tools locally.

```bash
# Run tests
docker compose run --rm web npm test

# Run migrations
docker compose run --rm web python manage.py migrate

# Install new dependency
docker compose run --rm web npm install lodash

# Open a shell
docker compose run --rm web sh
```

The `--rm` flag removes the container after the command finishes.

---

## Pattern 4: Database with Persistent Data

Keep database data across `docker compose down` cycles.

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: devpassword
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # Expose for local tools (pgAdmin, etc.)

volumes:
  db-data:
```

### Reset Database

```bash
docker compose down -v  # -v removes volumes
docker compose up
```

---

## Pattern 5: Dev Containers (VS Code Integration)

VS Code's "Dev Containers" extension lets you develop *inside* a container.

### Setup

1. Install "Dev Containers" extension in VS Code
2. Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "My Project",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "web",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

3. Open Command Palette → "Dev Containers: Reopen in Container"

**Benefits:**

- Extensions run inside the container
- Terminal is inside the container
- Debugging works seamlessly

---

## Pattern 6: Debugging in Containers

### Node.js

```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
      - "9229:9229"  # Debugger port
    command: node --inspect=0.0.0.0:9229 server.js
```

### Python

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
      - "5678:5678"  # debugpy port
    command: python -m debugpy --listen 0.0.0.0:5678 -m flask run --host=0.0.0.0
```

Then attach your IDE's debugger to `localhost:9229` (Node) or `localhost:5678` (Python).

---

## Productivity Tips

### 1. Use `docker compose watch` (Docker Compose 2.22+)

Automatically rebuild and sync files:

```yaml
services:
  web:
    build: .
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: package.json
```

```bash
docker compose watch
```

### 2. Create Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias dc='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'
alias dcrun='docker compose run --rm'
```

### 3. Use `.env` for Local Overrides

```bash
# .env (gitignored)
POSTGRES_PASSWORD=localdev
DEBUG=true
```

---

## Summary

| Pattern | Use Case |
| :--- | :--- |
| Bind mounts | Live code reload |
| Override files | Dev vs prod config |
| `run --rm` | One-off commands |
| Named volumes | Persistent database |
| Dev Containers | Full IDE integration |
| `compose watch` | Auto-rebuild on changes |

**Next Chapter:** Automate builds and deployments in **Chapter 16: CI/CD for Containers**.
