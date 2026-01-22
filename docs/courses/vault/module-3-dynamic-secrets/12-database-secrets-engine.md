# Database Secrets Engine

**[← Back to Module 3](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Maintainers:** Global Data Services Team
> **Status:** Production

![Status](https://img.shields.io/badge/Status-Production-green)
![Module](https://img.shields.io/badge/Module-3_Dynamic_Secrets-blue)
![Lesson](https://img.shields.io/badge/Lesson-12-purple)

## Learning objectives

By the end of this lesson, you will be able to:

- Configure the database secrets engine for PostgreSQL
- Create roles with custom SQL statements
- Generate dynamic database credentials
- Manage credential lifecycle

## Table of contents

- [Overview](#overview)
- [Supported databases](#supported-databases)
- [Configuration](#configuration)
- [Creating roles](#creating-roles)
- [Generating credentials](#generating-credentials)
- [Hands-on lab](#hands-on-lab)
- [Key takeaways](#key-takeaways)

---

## Overview

The database secrets engine generates database credentials dynamically. When an application needs database access, it requests credentials from Vault, which creates a temporary database user.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   DATABASE SECRETS FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   1. App requests credentials                                           │
│   ┌─────────┐     vault read database/creds/app                        │
│   │   App   │ ─────────────────────────────────────▶ ┌─────────┐       │
│   └─────────┘                                        │  Vault  │       │
│                                                      └────┬────┘       │
│   2. Vault creates DB user                                │            │
│                                                           │            │
│   ┌─────────┐     CREATE ROLE "v-app-xyz"...             │            │
│   │   DB    │ ◀──────────────────────────────────────────┘            │
│   └─────────┘                                                          │
│                                                                          │
│   3. Vault returns credentials                                         │
│   ┌─────────┐     username: v-app-xyz                                  │
│   │   App   │ ◀── password: random-abc123                              │
│   └─────────┘     lease_id: database/creds/app/xyz                     │
│                                                                          │
│   4. App connects to database                                          │
│   ┌─────────┐ ─────────────────────────────────────▶ ┌─────────┐       │
│   │   App   │     (using dynamic credentials)        │   DB    │       │
│   └─────────┘                                        └─────────┘       │
│                                                                          │
│   5. Lease expires → Vault drops DB user                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Supported databases

| Database | Plugin |
|----------|--------|
| PostgreSQL | `postgresql-database-plugin` |
| MySQL/MariaDB | `mysql-database-plugin` |
| MongoDB | `mongodb-database-plugin` |
| MSSQL | `mssql-database-plugin` |
| Oracle | `oracle-database-plugin` |

---

## Configuration

### Enable the engine

```bash
vault secrets enable database
```

### Configure PostgreSQL connection

```bash
vault write database/config/mydb \
    plugin_name=postgresql-database-plugin \
    allowed_roles="readonly,readwrite" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb?sslmode=disable" \
    username="vault" \
    password="vault-initial-password"
```

### Rotate root credentials

```bash
# Vault takes over the root password (recommended)
vault write -f database/rotate-root/mydb
```

---

## Creating roles

### Read-only role

```bash
vault write database/roles/readonly \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

### Read-write role

```bash
vault write database/roles/readwrite \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="4h"
```

---

## Generating credentials

```bash
# Generate credentials
$ vault read database/creds/readonly

Key                Value
---                -----
lease_id           database/creds/readonly/abc123
lease_duration     1h
lease_renewable    true
password           A1B2-randomized-C3D4
username           v-token-readonly-xyz123

# Use in application
psql -h localhost -U v-token-readonly-xyz123 -d mydb
```

---

## Hands-on lab

### Setup

Start PostgreSQL:
```bash
docker run -d --name postgres \
    -e POSTGRES_PASSWORD=rootpassword \
    -e POSTGRES_USER=vault \
    -e POSTGRES_DB=mydb \
    -p 5432:5432 \
    postgres:15
```

### Configure Vault

```bash
# Enable database engine
vault secrets enable database

# Configure connection
vault write database/config/mydb \
    plugin_name=postgresql-database-plugin \
    allowed_roles="*" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb?sslmode=disable" \
    username="vault" \
    password="rootpassword"

# Create role
vault write database/roles/app \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="5m" \
    max_ttl="1h"
```

### Test

```bash
# Get credentials
vault read database/creds/app

# Test connection
psql "postgresql://v-token-app-xyz:password@localhost:5432/mydb"
```

---

## Key takeaways

1. **Database engine generates dynamic DB users**
2. **Credentials expire automatically** - No manual cleanup
3. **Each request gets unique credentials** - Improved audit trail
4. **Rotate root credentials** - Vault manages the admin password
5. **Custom SQL for any permission model**

---

[← Previous: Dynamic Concepts](./11-dynamic-secrets-concepts.md) | [Back to Module 3](./README.md) | [Next: AWS Secrets →](./13-aws-secrets-engine.md)
