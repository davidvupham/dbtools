# Command Inventory & Reference - dbtool

This document lists all approved commands, subcommands, and arguments for the `dbtool` CLI.

## 1. Triage & Health (`check`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `check` | `<target>` | Runs default health checks (Ping, Auth, Service Status) | `ck` |
| `check` | `<target> --deep` | Runs extended diagnostics (Resource usage, Logs) | `ck` |
| `ck ad` | `<user> --status` | Checks if AD account is Disabled/Locked | - |
| `ck ad` | `<user> --verify-password` | Validates password (safe auth test) | - |

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

## 3. Query & SQL (`sql`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `sql` | `<target> "<query>"` | Execute ad-hoc SQL string | - |
| `sql` | `<target> -f <file.sql>` | Execute SQL script file | - |
| `sql` | `... --format <fmt>` | Output format: `table` (def), `json`, `csv` | - |

## 4. Access (`shell`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `shell` | `<target>` | Opens interactive native shell (psql/sqlcmd) | `sh` |
| `login` | - | Authenticates User to Vault (Windows Only) | - |

## 5. Operations & Maintenance (`maint`)

| Command | Arguments | Description | Alias |
|---------|-----------|-------------|-------|
| `maint start` | `<task> <target>` | Triggers maintenance task (Vacuum, Reindex) | - |
| `maint status` | `<id>` | Checks status of long-running task | - |
| `playbook run` | `<name> <target>` | Runs Ansible Playbook | `pb run` |
| `playbook list` | - | Lists available playbooks | `pb list` |
| `tf plan` | `<proj> <env>` | Runs Terraform Plan | - |
| `tf apply` | `<proj> <env>` | Runs Terraform Apply | - |
