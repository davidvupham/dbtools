# Command reference: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** GDS Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Reference-blue)

This document lists all approved commands, subcommands, and arguments for the `dbtool` CLI.

## Global arguments

| Argument | Description |
|----------|-------------|
| `--debug` | Enable verbose logging to `stderr`. |
| `--profile <name>` | Use a specific configuration profile (overrides default). |
| `--help` | Show help message and exit. |

## Table of contents

- [Triage & health](#1-triage--health-check)
- [Alerts](#2-alerts-alert)
- [Query & SQL](#3-query--sql-sql)
- [Access](#4-access-shell)
- [Operations & maintenance](#5-operations--maintenance-maint)
- [Liquibase](#6-liquibase-lb)
- [Configuration](#7-configuration-config)
- [System](#8-system-sys)

## 1. Triage & health (`check`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `check` | `<target>` | Runs default health checks (Ping, Auth, Service Status) | `ck` |
| `check` | `<target> --deep` | Runs extended diagnostics (Resource usage, Logs) | `ck` |
| `ck ad` | `<user> --status` | Checks if AD account is Disabled/Locked | - |
| `ck ad` | `<user> --verify-password` | Validates password (safe auth test) | - |

[↑ Back to Table of Contents](#table-of-contents)

## 2. Alerts (`alert`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `alert` | `<id>` | Triages an alert by its ID (Auto-detects type) | - |
| `alert` | `<target> --type <type>` | Manually triage specific alert type | - |

**Supported Alert Types**:

- `long-query`: Show currently running queries > 5m.
- `blocking`: Show blocking chains and head blocker.
- `anonymous-login`: Analyze security logs for SPN issues.
- `ad-disabled`: Analyze failed logins for account status.

[↑ Back to Table of Contents](#table-of-contents)

## 3. Query & SQL (`sql`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `sql` | `<target> "<query>"` | Execute ad-hoc SQL string | - |
| `sql` | `<target> -f <file.sql>` | Execute SQL script file | - |
| `sql` | `... --format <fmt>` | Output format: `table` (def), `json`, `csv` | - |

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
| `tf plan` | `<proj> <env>` | Runs Terraform Plan | - |
| `tf apply` | `<proj> <env>` | Runs Terraform Apply | - |

[↑ Back to Table of Contents](#table-of-contents)

## 6. Liquibase (`lb`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `lb update` | `<proj> <env>` | Runs Liquibase update (Docker) | - |
| `lb rollback` | `<proj> <env>` | Runs Liquibase rollback | - |
| `lb status` | `<proj> <env>` | Shows pending changesets | - |

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
