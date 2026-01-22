# Project Plan: dbtool-cli

## 1. Executive Summary

The `dbtool-cli` project delivers the `dbtool` binary, a unified operational tool designed to streamline the troubleshooting...

## 2. Objectives

- **Primary**: Reduce Mean Time To Resolution (MTTR) for database alerts by automating initial diagnostic steps.
- **Secondary**: Standardize authentication patterns (Vault + Kerberos/AD) across Windows and Linux.
- **Success Metrics**:
  - Tool successfully authenticates on both Windows and Linux without manual secret entry.
  - "Troubleshoot" command provides actionable metrics for 3 common alert types within < 10 seconds.

## 3. Scope

### In Scope

- Python-based CLI using `Typer` (or `Click`).
- **Authentication**:
  - Vault integration with Active Directory backend.
  - Linux: Automatic Kerberos ticket usage (`requests-kerberos` / `gssapi`).
  - Windows: AD/LDAP integration or standard Windows Auth patterns.
- **Modules**:
  - `troubleshoot`: Diagnostics for Connectivity, Locks, and Resource Usage.
  - Support for: SQL Server, PostgreSQL, MongoDB, Snowflake.
- **Platform**: Windows 10/11, RHEL/Ubuntu Linux.

### Out of Scope (MVP)

- Automated remediation (Auto-fixing issues).
- GUI interface.
- Integration with ticketing systems (Jira/ServiceNow) - *Phase 2*.

## 4. Phases and Timeline

### Phase 1: Foundation & Authentication (Sprint 1)

**Effort**: 5 Days

- [ ] Scaffold Python project structure (`src/dbtool`).
- [ ] Implement `VaultAuth` class.
  - [ ] Linux Strategy: `hvac` + Kerberos support.
  - [ ] Windows Strategy: `hvac` + AD/LDAP Support.
- [ ] Verify connectivity from WSL, Linux Server, and Windows PowerShell.

### Phase 2: Core Troubleshooting Framework (Sprint 2)

**Effort**: 5 Days

- [ ] Implement basic `dbtool troubleshoot <target>` command structure.
- [ ] Create abstract `DatabaseProvider` interface.
- [ ] Implement `PostgresProvider` (using `psycopg`).
- [ ] Implement `MSSQLProvider` (using `pymssql` or `pyodbc`).

### Phase 3: "Doctor" Logic & Alert Handling (Sprint 3)

**Effort**: 5 Days

- [ ] Define "Health Checks" per engine (e.g., Check Blocking Leaders for MSSQL).
- [ ] Output formatting (Rich tables/JSON).
- [ ] Test against mock alerts.

### Phase 4: Packaging & Distribution (Sprint 4)

- [ ] Configure `pyproject.toml` for entry points.
- [ ] Build mechanisms (shiv/pex/pip) for distribution to Jump Hosts.

## 5. Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Auth Complexity** | High | Prototype `hvac` + Kerberos immediately (Day 1). |
| **Driver Hell** | Medium | Use standardized container for Dev; Document ODBC reqs for Windows. |
| **OS Differences** | Medium | Use `pathlib` for all file ops; Abstract OS-specific calls. |

## 6. Resources Required

- **Service Account**: Read-only service account for Vault testing.
- **Test Databases**: Non-prod instances of MSSQL and Postgres.
