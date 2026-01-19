# Secrets and configuration management

> **Module:** Part 2 - Intermediate | **Level:** Intermediate | **Time:** 25 minutes

## Learning objectives

By the end of this section, you will be able to:

- Manage secrets securely in Compose
- Use config objects for non-sensitive data
- Implement environment variable patterns
- Follow security best practices

---

## Environment variables

### Inline environment

```yaml
services:
  api:
    image: myapi
    environment:
      - DATABASE_HOST=db
      - DATABASE_PORT=5432
      - DEBUG=false
```

### Environment file

```yaml
services:
  api:
    image: myapi
    env_file:
      - .env                 # Default
      - .env.local           # Overrides
```

```bash
# .env
DATABASE_HOST=db
DATABASE_PORT=5432
LOG_LEVEL=info

# .env.local
LOG_LEVEL=debug
```

### Shell environment interpolation

```yaml
services:
  api:
    image: myapi
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY:?Secret key is required}
      - LOG_LEVEL=${LOG_LEVEL:-info}
```

| Syntax | Description |
|--------|-------------|
| `${VAR}` | Variable value |
| `${VAR:-default}` | Default if unset or empty |
| `${VAR-default}` | Default if unset |
| `${VAR:?message}` | Error if unset or empty |
| `${VAR:+value}` | Value if VAR is set |

---

## Secrets in Compose

### File-based secrets

```yaml
services:
  api:
    image: myapi
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

Secrets are mounted at `/run/secrets/<secret_name>`:

```bash
# Inside container
cat /run/secrets/db_password
```

### Reading secrets in application

```python
# Python example
def get_secret(name):
    try:
        with open(f'/run/secrets/{name}') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fall back to environment variable
        return os.environ.get(name.upper())

db_password = get_secret('db_password')
```

```javascript
// Node.js example
const fs = require('fs');

function getSecret(name) {
    try {
        return fs.readFileSync(`/run/secrets/${name}`, 'utf8').trim();
    } catch {
        return process.env[name.toUpperCase()];
    }
}

const dbPassword = getSecret('db_password');
```

### External secrets

```yaml
secrets:
  db_password:
    external: true  # Must exist before compose up
    name: prod_db_password
```

```bash
# Create secret first (Swarm mode)
echo "mypassword" | docker secret create prod_db_password -

# Or use file
docker secret create prod_db_password ./password.txt
```

---

## Config objects

For non-sensitive configuration files:

```yaml
services:
  nginx:
    image: nginx
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
        mode: 0440

configs:
  nginx_config:
    file: ./nginx.conf
```

### Multiple configs

```yaml
services:
  api:
    image: myapi
    configs:
      - source: app_config
        target: /app/config.json
      - source: logging_config
        target: /app/logging.yaml

configs:
  app_config:
    file: ./config/app.json
  logging_config:
    file: ./config/logging.yaml
```

---

## Patterns for different environments

### Environment-specific files

```
project/
├── compose.yaml           # Base configuration
├── compose.override.yaml  # Development (auto-loaded)
├── compose.prod.yaml      # Production
├── .env                   # Default environment
├── .env.development       # Development environment
├── .env.production        # Production environment
└── secrets/
    ├── .gitignore         # Ignore actual secrets
    ├── db_password.txt    # Development secret
    └── README.md          # Instructions
```

```yaml
# compose.yaml (base)
services:
  api:
    image: myapi:${IMAGE_TAG:-latest}
    env_file:
      - .env
```

```yaml
# compose.override.yaml (development)
services:
  api:
    build: ./api
    env_file:
      - .env
      - .env.development
    volumes:
      - ./api:/app
```

```yaml
# compose.prod.yaml (production)
services:
  api:
    env_file:
      - .env
      - .env.production
    secrets:
      - db_password
      - api_secret_key

secrets:
  db_password:
    external: true
  api_secret_key:
    external: true
```

```bash
# Development
docker compose up -d

# Production
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

---

## Security best practices

### Never commit secrets

```bash
# .gitignore
.env.local
.env.*.local
secrets/
*.pem
*.key
```

### Use .env.example

```bash
# .env.example (committed to repo)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=appuser
DATABASE_PASSWORD=<your-password-here>
SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

### Validate required variables

```yaml
services:
  api:
    image: myapi
    environment:
      # Fail if not set
      - DATABASE_URL=${DATABASE_URL:?DATABASE_URL is required}
      - SECRET_KEY=${SECRET_KEY:?SECRET_KEY is required}
      # Optional with defaults
      - LOG_LEVEL=${LOG_LEVEL:-info}
```

### Restrict secret permissions

```yaml
services:
  api:
    secrets:
      - source: db_password
        target: /run/secrets/db_password
        uid: '1000'
        gid: '1000'
        mode: 0400  # Owner read only
```

---

## Practical example: Secure application

```yaml
name: secure-app

services:
  api:
    build:
      context: ./api
      secrets:
        - npmrc  # Build-time secret
    environment:
      - DATABASE_HOST=db
      - DATABASE_PORT=5432
      - DATABASE_NAME=appdb
      - DATABASE_USER=appuser
      # Password via secret file
      - DATABASE_PASSWORD_FILE=/run/secrets/db_password
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - LOG_LEVEL=${LOG_LEVEL:-info}
    secrets:
      - db_password
      - secret_key
    configs:
      - source: app_config
        target: /app/config.yaml
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
  npmrc:
    file: ~/.npmrc

configs:
  app_config:
    file: ./config/app.yaml

volumes:
  postgres_data:
```

### Application code to read secrets

```python
# api/app/config.py
import os

def read_secret_file(env_var):
    """Read secret from file path specified in environment variable."""
    file_path = os.environ.get(env_var)
    if file_path and os.path.exists(file_path):
        with open(file_path) as f:
            return f.read().strip()
    # Fall back to direct environment variable
    base_var = env_var.replace('_FILE', '')
    return os.environ.get(base_var)

class Config:
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DATABASE_PORT = int(os.environ.get('DATABASE_PORT', 5432))
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'app')
    DATABASE_USER = os.environ.get('DATABASE_USER', 'app')
    DATABASE_PASSWORD = read_secret_file('DATABASE_PASSWORD_FILE')
    SECRET_KEY = read_secret_file('SECRET_KEY_FILE')

    @property
    def database_url(self):
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
```

---

## Key takeaways

1. **Never hardcode secrets** in compose files or images
2. **Use secrets objects** for sensitive data like passwords
3. **Use configs** for non-sensitive configuration files
4. **Environment files** help separate environments
5. **Validate required variables** to fail fast
6. **Follow the _FILE convention** for secret file paths

---

## What's next

Learn about container registries and image distribution.

---

## Navigation

| Previous | Up | Next |
|----------|-----|------|
| [Building Images](05-building-images.md) | [Part 2 Overview](../../course_overview.md#part-2-intermediate) | [Registries](07-registries.md) |
