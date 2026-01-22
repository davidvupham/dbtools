# Technical Architecture: dbtool-cli

## 1. Overview

`dbtool` is a Python-based CLI application built on the **Typer** framework. It acts as an operational bridge and **Wrapper** ("The One Tool to Rule Them All"), strictly separating the User from the complexity of underlying tools (Vault, Ansible, Airflow, Liquibase, Database Drivers).

## 2. Authentication Flow (Critical Path)

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

## 3. Component Design

```mermaid
graph TD
    User[Engineer / DBRE] --> CLI[dbtool CLI (Typer)]

    subgraph "Authentication Layer"
        CLI --> VaultHelper[Vault Handler]
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

## 4. Technology Stack

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

## 5. Cross-Platform Strategy

| Component | Windows Strategy | Linux Strategy |
|-----------|------------------|----------------|
| **Paths** | `pathlib` (No hardcoded backslashes) | `pathlib` |
| **Auth** | LDAP / Userpass (Prompt) | Kerberos / GSSAPI (Auto) |
| **Drivers** | ODBC Driver Manager often present | UnixODBC may be required |
| **Config** | `%APPDATA%\dbtool\config.toml` | `~/.config/dbtool/config.toml` |

## 6. Configuration Schema

The tool manages defaults via a TOML file.

```toml
[auth]
ad_domain = "CONTOSO"       # Default Active Directory Domain
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[defaults]
output_format = "table"     # table, json, csv
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
