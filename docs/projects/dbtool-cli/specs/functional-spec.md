# Functional specification: dbtool-cli

**[← Back to Project Index](../README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 22, 2026
> **Maintainers:** DBRE Team
> **Status:** Draft

![Status](https://img.shields.io/badge/Status-Draft-yellow)
![Type](https://img.shields.io/badge/Type-Specification-blue)

## Table of contents

- [Overview](#1-overview)
- [User stories](#2-user-stories)
- [Interfaces & commands](#3-interfaces--commands)
- [Non-functional requirements](#4-non-functional-requirements-nfrs)
- [Security & access control](#5-security--access-control)

## 1. Overview

`dbtool` is a unified command-line tool for the DBRE team. It simplifies database troubleshooting, maintenance execution, and ad-hoc querying by abstracting authentication (Vault/Kerberos) and platform differences (Windows/Linux) across Snowflake, SQL Server, MongoDB, and PostgreSQL.

[↑ Back to Table of Contents](#table-of-contents)

## 2. User stories

### Core: Troubleshooting & alerts

**US-101: Auto-triage alerts**
> As a DBRE Engineer,
> I want to run `dbtool troubleshoot --alert-id <ID>` or `dbtool troubleshoot --target <hostname>`,
> So that I can immediately see top blocking queries, resource usage, and replication lag without manually running SQL.

**US-102: Analyze long-running queries**
> As a DBRE Engineer receiving a "Long Running Query" alert,
> I want the tool to output a table showing `User`, `Duration`, `Wait Type` (CPU vs Lock), and the `SQL Text`.
> Scope: Postgres (`pg_stat_activity`), MSSQL (`sys.dm_exec_requests`), Mongo (`currentOp`), Snowflake (`QUERY_HISTORY`).

**US-103: Analyze blocking chains**
> As a DBRE Engineer receiving a "Blocking Detected" alert,
> I want the tool to visualize the "Head Blocker" (the root cause session) and all stuck children.
> **Critical**: Distinguish between "Active Blocker" (running SQL) and "Sleeping Blocker" (transaction left open).

**US-104: Investigate anonymous logins (security)**
> As a DBRE Engineer receiving a "SQL Server Anonymous Login" alert,
> I want the tool to query the Audit Logs or Ring Buffer (`sys.dm_os_ring_buffers`) to find the source IP and application name of the `NT AUTHORITY\ANONYMOUS LOGON` attempt to determine if it's a Kerberos/SPN configuration issue.

**US-105: Analyze disabled AD logins**
> As a DBRE Engineer receiving a "Login Failed (Account Disabled)" alert,
> I want the tool to check the status of the Active Directory account associated with the login attempt.
> **Scope**: Query AD (via LDAP) to check `userAccountControl` flags for "Disabled" or "Locked Out" status.
> **Note**: This distinguishes between "User typed wrong password" (Lockout) vs "Account was intentionally disabled" (Terminated/Expired).

**US-106: Direct AD account checks**
> As a DBRE Engineer,
> I want to run `dbtool ck ad <user> --status` or `dbtool ck ad <user> --verify-password`,
> So that I can instantly validate if an account is Disabled/Locked or if a password is valid, independent of any database alert.
> **Alias**: `ck` for `check`.

**US-203: Execute Ansible playbooks**
> As a DBRE Engineer,
> I want to run `dbtool playbook run <name> --target <host> --extra-vars "patch_level=1.2"`,
> So that I can trigger complex infrastructure changes (OS Patching, Config Updates) using standard playbooks without remembering `ansible-playbook` flag syntax or inventory paths.
> **Requirement**: Must stream standard output to the console.

**US-204: Execute Terraform plans**
> As a DBRE Engineer,
> I want to run `dbtool tf plan <project> --target <env>` or `dbtool tf apply <project> --target <env>`,
> So that I can manage database infrastructure (EC2, RDS, IAM) using standard Terraform workflows wrapped with Vault authentication injection.
> **Alias**: `tf`.

**US-205: Execute Liquibase migrations**
> As a DBRE Engineer,
> I want to run `dbtool lb update <project> --target <env>`,
> So that I can deploy database schema changes using a standardized Liquibase Docker container, with `dbtool` handling the volume mounts and credential injection.
> **Alias**: `lb`.

### Core: Maintenance

**US-201: Execute ad-hoc queries**
> As a DBRE Engineer,
> I want to run `dbtool query execute --target <db> --query "SELECT..." --format [table|json|csv]`,
> So that I can choose between reading the output instantly (Table) or piping it to another tool/file (JSON/CSV).
> **Default**: Human-readable Table.

**US-202: Execute SQL scripts**
> As a DBRE Engineer,
> I want to run `dbtool query execute --target <db> --file <script.sql>`,
> So that I can safely run diagnostic or fix scripts across environments with automatic Vault authentication.

### Core: Access

**US-301: Connect shell**
> As a DBRE Engineer,
> I want to run `dbtool connect --target <db>`,
> So that I am dropped into a native shell (`psql`, `sqlcmd`) with temporary credentials already injected.

[↑ Back to Table of Contents](#table-of-contents)

## 3. Interfaces & commands

```bash
# Check (General Health & Status) - Alias: ck
dbtool ck <target>                            # Runs default checks (Was: check)
dbtool ck ad <username> --status              # Returns: Active, Disabled, or Locked
dbtool ck ad <username> --verify-password     # Prompts for password to test validity (Safe test)

# Alerts (Specific Investigations)
dbtool alert <id>                             # Auto-detects alert type from ID
dbtool alert <target> --type blocking         # Specific check type

# Query (Ad-Hoc)
dbtool sql <target> "SELECT 1"                # Shorter alias for 'query execute'
dbtool sql <target> -f script.sql             # -f flag for file
dbtool shell <target>                         # Drops into psql/sqlcmd (was 'connect')

# Ops (Maintenance & Infrastructure)
dbtool maint start <task> <target>            # 'maint' alias for 'maintenance'
dbtool maint status <id>
dbtool playbook run <name> <target>           # Wrapper for ansible-playbook (e.g., dbtool playbook run os-patch mssql-01)
dbtool playbook list                          # Lists available approved playbooks
dbtool tf plan <project> <target>             # Wrapper for terraform plan (e.g., dbtool tf plan mssql-cluster dev)
dbtool tf apply <project> <target>            # Wrapper for terraform apply
dbtool lb update <project> <target>           # Wrapper for liquibase update (Docker)
dbtool lb rollback <project> <target>         # Wrapper for liquibase rollback
```

[↑ Back to Table of Contents](#table-of-contents)

## 4. Non-functional requirements

- **NFR-01 (Security)**: Secrets MUST never be displayed in stdout/logs.
- **NFR-02 (Platform)**: ALL commands must work identically on Windows (PowerShell) and Linux (Bash).
- **NFR-03 (Audit)**: All `dbtool query` executions must accept a `--reason` flag or Ticket ID for audit logging.
- **NFR-04 (Output)**: All generic commands MUST support `--format json` to enable automation (Airflow/Ansible integration).

[↑ Back to Table of Contents](#table-of-contents)

## 5. Security & access control

- **Authentication**:
  - **Windows**: LDAP/AD integration via Vault.
  - **Linux**: Zero-touch Kerberos authentication (`requests-kerberos`).
- **Authorization**:
  - The CLI forwards the authenticated identity to Vault.
  - Vault policies determine if the user can `read` vs `write` to a specific database path.

[↑ Back to Table of Contents](#table-of-contents)
