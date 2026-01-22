# Vault Dev Environment

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-1_Foundations-blue)
![Lesson](https://img.shields.io/badge/Lesson-03-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Set up a Vault development server using Docker
- Configure the Vault CLI and environment variables
- Execute basic Vault commands
- Interact with Vault using both CLI and HTTP API

## Table of contents

- [Prerequisites](#prerequisites)
- [Docker setup](#docker-setup)
- [Vault CLI configuration](#vault-cli-configuration)
- [Basic commands](#basic-commands)
- [HTTP API basics](#http-api-basics)
- [Development vs production](#development-vs-production)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Prerequisites

Before starting, ensure you have:

```bash
# Docker (or Podman)
docker --version
# Docker version 24.0.0 or later

# curl (for API testing)
curl --version

# jq (optional, for JSON formatting)
jq --version
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Docker setup

### Option 1: Quick start with Docker run

The fastest way to get a dev server running:

```bash
# Start Vault dev server
docker run -d \
  --name vault-dev \
  --cap-add=IPC_LOCK \
  -p 8200:8200 \
  -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
  -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
  hashicorp/vault:1.15

# Verify it's running
docker ps | grep vault-dev

# View logs
docker logs vault-dev
```

### Option 2: Docker Compose (recommended)

Create a `docker-compose.dev.yml` file:

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  vault:
    image: hashicorp/vault:1.15
    container_name: vault-dev
    cap_add:
      - IPC_LOCK
    ports:
      - "8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: root
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
      VAULT_ADDR: http://127.0.0.1:8200
    healthcheck:
      test: ["CMD", "vault", "status"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - vault-network

networks:
  vault-network:
    driver: bridge
```

Start with Docker Compose:

```bash
# Start
docker compose -f docker-compose.dev.yml up -d

# Check status
docker compose -f docker-compose.dev.yml ps

# View logs
docker compose -f docker-compose.dev.yml logs vault

# Stop
docker compose -f docker-compose.dev.yml down
```

### Verify Vault is running

```bash
# Health check endpoint
curl -s http://localhost:8200/v1/sys/health | jq

# Expected output:
{
  "initialized": true,
  "sealed": false,
  "standby": false,
  "performance_standby": false,
  "replication_performance_mode": "disabled",
  "replication_dr_mode": "disabled",
  "server_time_utc": 1705851600,
  "version": "1.15.0",
  "cluster_name": "vault-cluster-abc123",
  "cluster_id": "abc123-def456-ghi789"
}
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Vault CLI configuration

### Install Vault CLI (optional but recommended)

While you can use `docker exec`, installing the CLI locally is more convenient.

**macOS:**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/vault
```

**Linux (Ubuntu/Debian):**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault
```

**Windows:**
```powershell
choco install vault
```

### Configure environment variables

```bash
# Set Vault address
export VAULT_ADDR='http://127.0.0.1:8200'

# Set token (dev server uses 'root' by default)
export VAULT_TOKEN='root'

# (Optional) Enable JSON output
export VAULT_FORMAT='json'

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export VAULT_ADDR="http://127.0.0.1:8200"' >> ~/.bashrc
```

### Using Docker exec (alternative)

If you don't install the CLI locally:

```bash
# Create an alias
alias vault='docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=root vault-dev vault'

# Now use normally
vault status
```

### Verify CLI connection

```bash
# Check status
$ vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.15.0
Build Date      2023-09-22T16:57:08Z
Storage Type    inmem
Cluster Name    vault-cluster-abc123
Cluster ID      abc123-def456
HA Enabled      false
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Basic commands

### Server status

```bash
# Full status
vault status

# Check if sealed
vault status -format=json | jq '.sealed'
```

### Authentication

```bash
# Login with token
vault login root

# Login with token from stdin
echo "root" | vault login -

# Check current token
vault token lookup
```

### Working with secrets (preview)

```bash
# Write a secret
vault kv put secret/hello foo=bar

# Read a secret
vault kv get secret/hello

# Read specific field
vault kv get -field=foo secret/hello

# Delete a secret
vault kv delete secret/hello
```

### Help and documentation

```bash
# General help
vault --help

# Command-specific help
vault kv --help
vault kv put --help

# List available paths
vault path-help secret/
```

[↑ Back to Table of Contents](#table-of-contents)

---

## HTTP API basics

Every CLI command translates to an HTTP API call. Understanding the API helps with debugging and integration.

### API structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VAULT API STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Base URL: http://localhost:8200/v1                                    │
│                                                                          │
│   Authentication Header:                                                 │
│   X-Vault-Token: <token>                                                │
│                                                                          │
│   Common Endpoints:                                                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ /v1/sys/health          Health check                            │   │
│   │ /v1/sys/seal-status     Seal status                             │   │
│   │ /v1/auth/token/lookup   Current token info                      │   │
│   │ /v1/secret/data/<path>  KV v2 secrets                           │   │
│   │ /v1/secret/metadata/<p> KV v2 metadata                          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Common API calls with curl

**Health check (no auth required):**
```bash
curl -s http://localhost:8200/v1/sys/health | jq
```

**Read a secret:**
```bash
curl -s \
  -H "X-Vault-Token: root" \
  http://localhost:8200/v1/secret/data/hello | jq
```

**Write a secret:**
```bash
curl -s \
  -H "X-Vault-Token: root" \
  -X POST \
  -d '{"data": {"username": "admin", "password": "secret123"}}' \
  http://localhost:8200/v1/secret/data/myapp | jq
```

**List secrets:**
```bash
curl -s \
  -H "X-Vault-Token: root" \
  -X LIST \
  http://localhost:8200/v1/secret/metadata/ | jq
```

**Delete a secret:**
```bash
curl -s \
  -H "X-Vault-Token: root" \
  -X DELETE \
  http://localhost:8200/v1/secret/data/myapp
```

### CLI to API mapping

| CLI Command | HTTP Method | API Path |
|-------------|-------------|----------|
| `vault status` | GET | `/v1/sys/seal-status` |
| `vault kv get secret/foo` | GET | `/v1/secret/data/foo` |
| `vault kv put secret/foo k=v` | POST | `/v1/secret/data/foo` |
| `vault kv delete secret/foo` | DELETE | `/v1/secret/data/foo` |
| `vault kv list secret/` | LIST | `/v1/secret/metadata/` |
| `vault token lookup` | GET | `/v1/auth/token/lookup-self` |

[↑ Back to Table of Contents](#table-of-contents)

---

## Development vs production

### Dev mode characteristics

| Aspect | Dev Mode | Production |
|--------|----------|------------|
| **Storage** | In-memory (lost on restart) | Persistent (Raft, Consul) |
| **Seal** | Auto-unsealed | Manual or auto-unseal with KMS |
| **TLS** | Disabled | Required |
| **Root token** | Pre-configured | Generated once, then revoked |
| **Listener** | localhost:8200 | Custom address |
| **Audit** | Disabled | Required for compliance |

### Dev mode warnings

> [!WARNING]
> Dev mode is for learning and development only. Never use it in production!

**Problems with dev mode in production:**
1. Data is lost when the container restarts
2. No TLS means secrets transmitted in cleartext
3. Root token is well-known
4. No audit logging
5. No access control enforcement

### Preparing for production

The journey from dev to production:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEV TO PRODUCTION JOURNEY                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DEV MODE (This lesson)                                                │
│   ─────────────────────                                                  │
│   • In-memory storage                                                   │
│   • Auto-unseal                                                         │
│   • No TLS                                                              │
│   • Root token: "root"                                                  │
│                                                                          │
│        │                                                                 │
│        ▼                                                                 │
│                                                                          │
│   MODULE 2-3 (Coming up)                                                │
│   ─────────────────────                                                  │
│   • Auth methods (AppRole, etc.)                                        │
│   • Policies and access control                                         │
│   • Dynamic secrets                                                     │
│                                                                          │
│        │                                                                 │
│        ▼                                                                 │
│                                                                          │
│   MODULE 4 (Production)                                                 │
│   ────────────────────                                                   │
│   • Persistent storage (Raft)                                           │
│   • TLS certificates                                                    │
│   • High availability                                                   │
│   • Audit logging                                                       │
│   • Auto-unseal with KMS                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

[↑ Back to Table of Contents](#table-of-contents)

---

## Hands-on lab

### Lab setup

1. Start the dev environment:
   ```bash
   docker run -d \
     --name vault-dev \
     --cap-add=IPC_LOCK \
     -p 8200:8200 \
     -e 'VAULT_DEV_ROOT_TOKEN_ID=root' \
     -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
     hashicorp/vault:1.15
   ```

2. Configure your shell:
   ```bash
   export VAULT_ADDR='http://127.0.0.1:8200'
   export VAULT_TOKEN='root'
   ```

### Exercise 1: Explore the CLI

1. Check the server status:
   ```bash
   vault status
   ```

2. Look up the current token:
   ```bash
   vault token lookup
   ```
   Note the `policies` and `ttl` fields.

3. List enabled secrets engines:
   ```bash
   vault secrets list
   ```

4. List enabled auth methods:
   ```bash
   vault auth list
   ```

### Exercise 2: Your first secrets

1. Create a secret:
   ```bash
   vault kv put secret/myapp/database \
       username="dbadmin" \
       password="SuperSecret123" \
       host="db.example.com"
   ```

2. Read the secret:
   ```bash
   vault kv get secret/myapp/database
   ```

3. Read a specific field:
   ```bash
   vault kv get -field=password secret/myapp/database
   ```

4. Update the secret:
   ```bash
   vault kv put secret/myapp/database \
       username="dbadmin" \
       password="NewPassword456" \
       host="db.example.com"
   ```

5. List secrets at a path:
   ```bash
   vault kv list secret/myapp/
   ```

### Exercise 3: Use the HTTP API

1. Read the secret via API:
   ```bash
   curl -s \
     -H "X-Vault-Token: $VAULT_TOKEN" \
     "$VAULT_ADDR/v1/secret/data/myapp/database" | jq
   ```

2. Write a new secret via API:
   ```bash
   curl -s \
     -H "X-Vault-Token: $VAULT_TOKEN" \
     -X POST \
     -d '{"data": {"api_key": "sk-test-123", "api_secret": "abc123"}}' \
     "$VAULT_ADDR/v1/secret/data/myapp/api" | jq
   ```

3. Verify with CLI:
   ```bash
   vault kv get secret/myapp/api
   ```

### Exercise 4: JSON output

1. Enable JSON output:
   ```bash
   export VAULT_FORMAT=json
   ```

2. Get secret as JSON:
   ```bash
   vault kv get secret/myapp/database | jq '.data.data'
   ```

3. Extract just the password:
   ```bash
   vault kv get secret/myapp/database | jq -r '.data.data.password'
   ```

### Cleanup

```bash
# Stop and remove container
docker stop vault-dev && docker rm vault-dev
```

---

## Key takeaways

1. **Docker makes dev setup easy** - One command to get a working Vault server

2. **Environment variables are essential**:
   - `VAULT_ADDR` - Where to connect
   - `VAULT_TOKEN` - How to authenticate
   - `VAULT_FORMAT` - Output format

3. **CLI and API are interchangeable** - Every CLI command has an API equivalent

4. **Dev mode is for development only**:
   - In-memory storage
   - No TLS
   - Auto-unsealed
   - Not secure for production

5. **The workflow is: authenticate → request → receive** - Token-based access control

---

## Next steps

In the next lesson, you'll dive deeper into secrets engines, learning about KV v1 vs v2, versioning, and metadata.

---

[← Previous: Vault Architecture](./02-vault-architecture.md) | [Back to Module 1](./README.md) | [Next: Secrets Engines →](./04-secrets-engines-basics.md)
