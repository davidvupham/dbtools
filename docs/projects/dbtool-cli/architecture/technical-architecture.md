# Technical architecture: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** GDS Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Architecture-blue)

## Table of contents

- [Overview](#1-overview)
- [Authentication flow](#2-authentication-flow-critical-path)
- [Component design](#3-component-design)
- [Technology stack](#4-technology-stack)
- [Cross-platform strategy](#5-cross-platform-strategy)
- [Configuration schema](#6-configuration-schema)
- [Configuration schema](#6-configuration-schema)
- [Telemetry & debugging](#7-telemetry--debugging)
- [Error handling](#8-error-handling)

## 1. Overview

`dbtool` is a Python-based CLI application built on the **Typer** framework. The tool acts as an operational bridge and **Wrapper** ("The One Tool to Rule Them All"), strictly separating the user from the complexity of underlying tools (Vault, Ansible, Airflow, Liquibase, Database Drivers).

[↑ Back to Table of Contents](#table-of-contents)

## 2. Authentication flow (critical path)

The tool acts as a **Vault Client**. It does not persist long-lived credentials.

### Linux (Kerberos / keytab)

1. **Pre-requisite**: User has valid Kerberos ticket (`klist` shows ticket).
2. `dbtool` starts.
3. Detects Linux OS.
4. Uses `requests-kerberos` to negotiate with Vault (Auth Method: `kerberos` or `ldap`).
5. Vault returns `client_token`.
6. `dbtool` uses `client_token` to fetch dynamic database credentials (TTL: 15m).

### Windows (Active Directory)

1. User runs `dbtool login`.
2. Tool prompts for AD Username/Password (or uses Windows SSPI if supported/configured).
3. Authenticates against Vault `ldap` or `userpass` backend.
4. Vault returns `client_token`.
5. Token is cached in secure memory (or OS Keyring) for session duration.

[↑ Back to Table of Contents](#table-of-contents)

## 3. Component design

<!-- Component diagram: User connects to dbtool CLI, which authenticates via Vault Handler
using Kerberos (Linux) or AD/LDAP (Windows). The CLI uses a Provider Factory to route
requests to database-specific providers (Postgres, MSSQL) that leverage gds_* packages
for actual database connectivity. -->

```mermaid
graph TD
    User[Engineer / DBRE] --> CLI[dbtool CLI (Typer)]
    CLI --> VaultCmd[Vault Wrapper]

    subgraph "Authentication Layer"
        CLI --> VaultHelper[Vault Handler]
        VaultCmd --> VaultHelper
        VaultHelper -->|Kerberos/AD| Vault[HashiCorp Vault]
        Vault -->|Lease Credentials| VaultHelper
    end

    subgraph "Provider Layer"
        CLI --> Factory[Provider Factory]
        Factory --> PG[Postgres Provider]
        Factory --> MS[MSSQL Provider]

        MS -.->|Import| GDS_MS[gds_mssql Package]
        PG -.->|Import| GDS_PG[gds_postgres Package]

        GDS_MS --> MSSQLDB
        GDS_PG --> PostgresDB
    end

    subgraph "Infrastructure"
        VaultHelper -.-> PG
        VaultHelper -.-> MS
    end

    PG --> PostgresDB[(PostgreSQL)]
    MS --> MSSQLDB[(SQL Server)]
```

[↑ Back to Table of Contents](#table-of-contents)

## 4. Technology stack

- **Language**: Python 3.12+
- **CLI Framework**: `Typer` (Modern, typed, intuitive).
- **Terminal UI**: `Rich` (Tables, Spinners, Colors).
- **Packaging**: `uv` (Dependency management), `hatch` or `setuptools` (Build).
- **Vault SDK**: `hvac`.
- **Database Drivers**:
  - Postgres: `psycopg` (v3)
  - MSSQL: `pymssql` (simpler for Linux) or `pyodbc` (standard for Windows).
  - Mongo: `pymongo`.
  - Snowflake: `snowflake-connector-python`.

[↑ Back to Table of Contents](#table-of-contents)

## 5. Cross-platform strategy

| Component | Windows Strategy | Linux Strategy |
|-----------|------------------|----------------|
| **Paths** | `pathlib` (No hardcoded backslashes) | `pathlib` |
| **Auth** | LDAP / Userpass (Prompt) | Kerberos / GSSAPI (Auto) |
| **Drivers** | ODBC Driver Manager often present | UnixODBC may be required |
| **Config** | `%APPDATA%\dbtool\config.toml` | `~/.config/dbtool/config.toml` |
| **Distribution** | Standalone EXE via PyInstaller | PEX/Shiv or PyInstaller binary |

> **Note on Distribution**: To avoid Python dependency conflicts on user workstations, `dbtool` is distributed as a self-contained binary. This ensures that the tool runs identically regardless of the user's local Python environment.

[↑ Back to Table of Contents](#table-of-contents)

## 6. Configuration schema

The tool manages defaults via a TOML file.

```toml
[auth]
ad_domain = "CONTOSO"       # Default Active Directory Domain
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[defaults]
output_format = "table"     # table, json, csv

[profile.default]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[profile.prod]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops-prod"

[vault.aliases]
# Format: alias = "full/path/to/secret"
logins = "secret/data/teams/gds/common/logins"
certs  = "secret/data/teams/gds/common/certs"
```

The troubleshooting module uses a **Strategy Pattern**.

`dbtool troubleshoot --target prod-reporting-db`

1. **Resolve**: Look up `prod-reporting-db` in inventory (YAML/API).
2. **Identify**: Type is `Postgres`.
3. **Instantiate**: `PostgresProvider`.
4. **Execute Plans**:
    - *Connectivity*: TCP Ping port 5432.
    - *Auth*: Test Vault credential validity.
    - *Queries*: Run `SELECT * FROM pg_stat_activity WHERE state = 'active'`.
5. **Report**: Render `Rich` table with findings.

[↑ Back to Table of Contents](#table-of-contents)

[↑ Back to Table of Contents](#table-of-contents)

## 7. Telemetry & debugging

To support operational troubleshooting of the tool itself, `dbtool` implements a robust logging strategy.

- **Standard Operation**: Output goes to `stdout`. Errors go to `stderr`.
- **Debug Mode**: When run with `--debug`, verbose logs (HTTP requests, Vault interactions, SQL driver traces) are emitted to `stderr`.
- **Log Files**: A rotating log file is maintained at `%APPDATA%\dbtool\logs\dbtool.log` (Windows) or `~/.local/state/dbtool/logs/dbtool.log` (Linux) for post-mortem analysis.

[↑ Back to Table of Contents](#table-of-contents)

## 8. Error handling

The CLI uses consistent error codes and messages across all commands.

### Exit codes

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Command completed successfully |
| `1` | General error | Unspecified failure |
| `2` | Authentication error | Vault token expired, Kerberos ticket invalid |
| `3` | Connection error | Database unreachable, network timeout |
| `4` | Permission denied | Insufficient Vault policy permissions |
| `5` | Invalid input | Malformed target name, missing required argument |
| `6` | Resource not found | Target database not in inventory |

### Common error messages

| Error | Cause | Resolution |
|-------|-------|------------|
| `VAULT_AUTH_FAILED` | Kerberos ticket expired or AD credentials invalid | Run `kinit` (Linux) or `dbtool login` (Windows) |
| `TARGET_NOT_FOUND` | Target name not in inventory | Check spelling, run `dbtool inventory list` |
| `CONNECTION_TIMEOUT` | Database host unreachable | Verify network connectivity, check firewall rules |
| `PERMISSION_DENIED` | Vault policy restricts access | Contact security team for policy update |
| `DRIVER_NOT_FOUND` | Required database driver not installed | Install missing driver (see Technology Stack) |

[↑ Back to Table of Contents](#table-of-contents)
