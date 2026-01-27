# gds-dbtool

Unified Database CLI tool.

## Overview

`dbtool` is a command-line tool that simplifies database troubleshooting, maintenance, and operations across Snowflake, SQL Server, MongoDB, and PostgreSQL. It abstracts authentication (Vault/Kerberos) and platform differences (Windows/Linux).

## Installation

```bash
# Install with uv
uv pip install -e .

# Or install with pip
pip install -e .
```

## Quick Start

```bash
# Show help
dbtool --help

# Show version
dbtool --version

# Authenticate with Vault
dbtool vault login --method ldap

# List secrets
dbtool vault list logins

# Get a secret value
dbtool vault get logins db_password

# Use profiles
dbtool --profile prod vault list
```

## Features

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-V` | Print version |
| `--debug` | | Enable verbose logging |
| `--quiet` | `-q` | Suppress non-essential output |
| `--no-color` | | Disable colored output |
| `--profile` | `-p` | Use specific config profile |
| `--dry-run` | `-n` | Preview changes without executing |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DBTOOL_PROFILE` | Override default profile |
| `DBTOOL_VAULT_URL` | Override Vault server URL |
| `DBTOOL_VAULT_NAMESPACE` | Override Vault namespace |
| `DBTOOL_DEBUG` | Enable debug output |
| `DBTOOL_NO_COLOR` | Disable colored output |
| `NO_COLOR` | Standard color disable |

### Command Groups

| Command | Alias | Description |
|---------|-------|-------------|
| `vault` | `vt` | Vault secret management |
| `config` | `cfg` | Configuration management |
| `health` | `ck` | Health checks and diagnostics |
| `alert` | | Alert triage and analysis |
| `sql` | | Execute SQL queries |
| `shell` | `sh` | Interactive database shells |
| `maint` | | Maintenance operations |
| `playbook` | `pb` | Ansible playbook execution |
| `tf` | | Terraform operations |
| `lb` | | Liquibase migrations |
| `inventory` | `inv` | Database target inventory |

## Vault Commands

```bash
# Login to Vault
dbtool vault login                    # LDAP (default)
dbtool vault login --method saml      # SAML

# List secrets
dbtool vault list                     # List at base path
dbtool vault list logins              # List using alias

# Read secrets
dbtool vault get logins               # Get all keys as JSON
dbtool vault get logins db_password   # Get specific key (raw value)

# Write secrets (with dry-run support)
dbtool vault put logins key=value
dbtool --dry-run vault put logins key=value

# Delete secrets (with confirmation and dry-run)
dbtool vault delete logins
dbtool vault delete logins --hard     # Permanent deletion
dbtool --dry-run vault delete logins

# Logout
dbtool vault logout
```

## Configuration

Configuration file location:
- **Windows**: `%APPDATA%\dbtool\config.toml`
- **Linux/Mac**: `~/.config/dbtool/config.toml`

Example configuration:

```toml
[auth]
ad_domain = "CONTOSO"
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[defaults]
output_format = "table"

[profile.default]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops"

[profile.prod]
vault_url = "https://vault.example.com"
vault_namespace = "db-ops-prod"

[vault.aliases]
logins = "secret/data/teams/gds/common/logins"
certs = "secret/data/teams/gds/common/certs"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | Connection error |
| 4 | Permission denied |
| 5 | Invalid input |
| 6 | Resource not found |

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=gds_dbtool --cov-report=html

# Run linting
ruff check src tests
ruff format src tests
```

## Documentation

See the full specification at:
- [Functional Specification](../../docs/projects/dbtool-cli/specs/functional-spec.md)
- [Command Reference](../../docs/projects/dbtool-cli/specs/command-reference.md)
- [Technical Architecture](../../docs/projects/dbtool-cli/architecture/technical-architecture.md)
