# Command reference: dbtool-cli

**🔗 [← Back to Project Index](../README.md)**

> **Document Version:** 1.1
> **Last Updated:** January 26, 2026
> **Maintainers:** GDS Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Reference-blue)

This document lists all approved commands, subcommands, and arguments for the `dbtool` CLI.

## Table of contents

- [Global arguments](#global-arguments)
- [Environment variables](#environment-variables)
- [Triage & health](#1-triage--health-check)
- [Alerts](#2-alerts-alert)
- [Query & SQL](#3-query--sql-sql)
- [Access](#4-access-shell)
- [Operations & maintenance](#5-operations--maintenance-maint)
- [Liquibase](#6-liquibase-lb)
- [Configuration](#7-configuration-config)
- [System](#8-system-sys)
- [Vault](#9-vault-wrapper-vault)
- [Inventory](#10-inventory-inventory)

## Global arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--help` | `-h` | Show help message and exit. |
| `--version` | `-V` | Print version information and exit. |
| `--debug` | | Enable verbose logging to `stderr`. |
| `--quiet` | `-q` | Suppress non-essential output (errors only). |
| `--no-color` | | Disable colored output. Also respects `NO_COLOR` env var. |
| `--profile <name>` | `-p` | Use a specific configuration profile (overrides default). |
| `--dry-run` | `-n` | Preview changes without executing (destructive commands only). |

## Environment variables

Environment variables override configuration file values but are overridden by CLI flags.

| Variable | Description | Example |
|----------|-------------|---------|
| `DBTOOL_PROFILE` | Override the default profile. | `export DBTOOL_PROFILE=prod` |
| `DBTOOL_VAULT_URL` | Override the Vault server URL. | `export DBTOOL_VAULT_URL=https://vault.example.com` |
| `DBTOOL_VAULT_NAMESPACE` | Override the Vault namespace. | `export DBTOOL_VAULT_NAMESPACE=db-ops-prod` |
| `DBTOOL_DEBUG` | Enable debug output (`1`, `true`, or `yes`). | `export DBTOOL_DEBUG=1` |
| `DBTOOL_NO_COLOR` | Disable colored output (`1`, `true`, or `yes`). | `export DBTOOL_NO_COLOR=1` |
| `NO_COLOR` | Standard variable to disable color (any value). | `export NO_COLOR=1` |

> [!TIP]
> Use environment variables in CI/CD pipelines and automation scripts to avoid hardcoding credentials or configuration.

[↑ Back to Table of Contents](#table-of-contents)

## 1. Triage & health (`check`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `health check` | `<target>` | Runs default health checks (Ping, Auth, Service Status) | `ck` |
| `health check` | `<target> --deep` | Runs extended diagnostics (Resource usage, Logs) | `ck` |
| `health check` | `ad <user> --status` | Checks if AD account is Disabled/Locked | `ck ad` |
| `health check` | `ad <user> --verify-password` | Validates password (safe auth test) | `ck ad` |

[↑ Back to Table of Contents](#table-of-contents)

## 2. Alerts (`alert`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `alert triage` | `[id]` | Triages an alert by its ID (Auto-detects type) | - |
| `alert triage` | `... --target <tgt> --type <type>` | Manually triage specific alert type | - |

**Supported Alert Types**:

- `long-query`: Show currently running queries > 5m.
- `blocking`: Show blocking chains and head blocker.
- `anonymous-login`: Analyze security logs for Service Principal Name (SPN) issues.
- `ad-disabled`: Analyze failed logins for account status.

[↑ Back to Table of Contents](#table-of-contents)

## 3. Query & SQL (`sql`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `sql` | `exec <target> "<query>"` | Execute ad-hoc SQL string | - |
| `sql` | `exec <target> -f <file.sql>` | Execute SQL script file | - |
| `sql` | `exec ... --format <fmt>` | Output format: `table` (def), `json`, `csv`, `yaml` | - |

[↑ Back to Table of Contents](#table-of-contents)

## 4. Access (`shell`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `shell` | `<target>` | Opens interactive native shell (psql/sqlcmd) | `sh` |
| `login` | - | Authenticates user to Vault (Windows only) | - |

[↑ Back to Table of Contents](#table-of-contents)

## 5. Operations & maintenance (`maint`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `maint start` | `<task> <target>` | Triggers maintenance task (Vacuum, Reindex) | - |
| `maint status` | `<id>` | Checks status of long-running task | - |
| `playbook run` | `<name> <target>` | Runs Ansible Playbook | `pb run` |
| `playbook list` | - | Lists available playbooks | `pb list` |
| `tf plan` | `<proj> <env>` | Runs Terraform Plan (preview only) | - |
| `tf apply` | `<proj> <env>` | Runs Terraform Apply (**supports `--dry-run`**) | - |

> [!WARNING]
> **Destructive operation**: `tf apply` modifies infrastructure. Use `--dry-run` to preview changes before applying.
>
> ```bash
> # Preview changes without applying
> dbtool tf apply myproject prod --dry-run
>
> # Apply changes (requires confirmation)
> dbtool tf apply myproject prod
> ```

[↑ Back to Table of Contents](#table-of-contents)

## 6. Liquibase (`lb`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `lb update` | `<proj> <env>` | Runs Liquibase update (Docker) (**supports `--dry-run`**) | - |
| `lb rollback` | `<proj> <env>` | Runs Liquibase rollback (**supports `--dry-run`**) | - |
| `lb status` | `<proj> <env>` | Shows pending changesets | - |

> [!WARNING]
> **Destructive operations**: `lb update` and `lb rollback` modify database schema. Use `--dry-run` to preview SQL without executing.
>
> ```bash
> # Preview update SQL without executing
> dbtool lb update myproject prod --dry-run
>
> # Preview rollback SQL without executing
> dbtool lb rollback myproject prod --dry-run
> ```

[↑ Back to Table of Contents](#table-of-contents)

## 7. Configuration (`config`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `config list` | - | Lists all configuration values | `cfg list` |
| `config get` | `<key>` | Gets specific value (e.g. `auth.vault_url`) | `cfg get` |
| `config set` | `<key> <value>` | Sets a configuration value | `cfg set` |
| `config profiles` | - | Lists available profiles | - |
| `config use` | `<profile>` | Switches the default active profile | - |

[↑ Back to Table of Contents](#table-of-contents)

## 8. System (`sys`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `upgrade` | - | Self-updates the CLI to the latest version | - |
| `version` | - | Prints version info | - |

[↑ Back to Table of Contents](#table-of-contents)

## 9. Vault Wrapper (`vault`)

A safe, simplified wrapper around the native Vault CLI.

**Common Arguments**:
- `--hard`: Perform permanent deletion (if backend supports it).
- `--force`: Skip interactive confirmation prompts.
- `--dry-run`: Preview the operation without executing (for `put` and `delete`).

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `vault list` | `[path]` | List keys at path or alias (Default: base_path) | `vt ls` |
| `vault get` | `<path> [key]` | Read secret (JSON default, or raw string if key provided) | `vt get` |
| `vault put` | `<path> <k=v>...` | Write data to secret (**supports `--dry-run`**) | `vt put` |
| `vault delete` | `<path>` | **Interactive** deletion of secret (**supports `--dry-run`**) | `vt rm` |

> [!CAUTION]
> **Irreversible operation**: `vault delete --hard` permanently destroys secret data. Always use `--dry-run` first to verify the target path.
>
> ```bash
> # Preview what will be deleted
> dbtool vault delete logins --dry-run
>
> # Delete with confirmation prompt
> dbtool vault delete logins
>
> # Permanent deletion (use with extreme caution)
> dbtool vault delete logins --hard
> ```

[↑ Back to Table of Contents](#table-of-contents)

## 10. Inventory (`inventory`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `inventory list` | `[--type <type>]` | Lists all known database targets | `inv ls` |
| `inventory show` | `<target>` | Shows details for a specific target | `inv show` |

[↑ Back to Table of Contents](#table-of-contents)
