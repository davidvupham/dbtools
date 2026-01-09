# Liquibase Course Design

## Overview

This document defines requirements and design for the Liquibase course refactoring in `docs/courses/liquibase`.

---

## Requirements

### Platform & Infrastructure

| # | Requirement | Details |
|---|-------------|---------|
| 1 | **Ubuntu + RHEL support** | Tutorial runs on both Ubuntu and Red Hat Linux |
| 2 | **Separate SQL containers** | `mssql_dev`, `mssql_stg`, `mssql_prd` (not one container with 3 DBs) |
| 3 | **Custom Dockerfiles** | Liquibase: existing UBI-based; SQL Server: Microsoft official image |
| 4 | **Database drivers** | MSSQL, PostgreSQL, Snowflake, MongoDB |
| 5 | **Data persistence** | All data in `/data/$USER/liquibase_tutorial/` |
| 6 | **Working directory** | Use `/data` inside Liquibase container |
| 7 | **Multi-platform** | MSSQL (current); PostgreSQL, Snowflake, MongoDB (future) |

### Naming & Standards

| # | Requirement | Details |
|---|-------------|---------|
| 8 | **Database name** | `orderdb` (reflects orders/customers domain) |
| 9 | **Formatted SQL** | Liquibase Formatted SQL with `.mssql.sql` extension (Liquibase requires `*.databaseType.sql`) |
| 10 | **Network** | Docker: bridge/host network; Podman: slirp4netns for rootless compatibility |
| 11 | **Naming convention** | Use underscores (`_`) everywhere |
| 14 | **Volume mounts** | Use `:Z,U` for SELinux/rootless Podman; omit for Docker |

### Scripting & Validation

| # | Requirement | Details |
|---|-------------|---------|
| 12 | **Script each step** | Minimize copy/paste; show success/fail |
| 13 | **Validation scripts** | Each step has validation with expected output |
| 20 | **Cleanup script** | Remove all tutorial artifacts |
| 21 | **Health checks** | Verify health before next step |
| 22 | **Error guidance** | Common failures documented |

### Schema Management

| # | Requirement | Details |
|---|-------------|---------|
| 15 | **Scenarios** | Current + future documented |

**Current:** Baseline, create table/view/index, constraints, deploy, rollback, drift, tagging

**Future:** Alter table, stored procedures, triggers, data migration, schema refactoring, drop objects, preconditions, parameter substitution

### Documentation

| # | Requirement | Details |
|---|-------------|---------|
| 16 | **Course Overview** | Learning objectives, prerequisites |
| 17 | **Architecture Diagram** | Container relationships |
| 18 | **Quick Reference** | Common commands |
| 19 | **Glossary** | Terminology definitions |
| 23 | **Naming conventions** | Documented standards |
| 24 | **Rollback testing** | Standard practice |
| 25 | **Changelog folder structure** | Simple structure: `database/changelog/` with `baseline/` and `changes/` subdirs |
| 26 | **Docker Compose build** | Reference Dockerfiles via `build.context`; no pre-build required |

---

## Architecture

```text
/data/$USER/liquibase_tutorial/
├── mssql_dev/              # Dev SQL Server data
├── mssql_stg/              # Staging SQL Server data
├── mssql_prd/              # Production SQL Server data
├── database/
│   └── changelog/
│       ├── changelog.xml
│       ├── baseline/
│       │   └── V0000__baseline.mssql.sql
│       └── changes/
│           └── V0001__add_orders_table.sql
└── env/
    ├── liquibase.dev.properties
    ├── liquibase.stg.properties
    └── liquibase.prd.properties
```

**Network:** `liquibase_tutorial_network`

**Containers:**
| Container | Port | Database |
|-----------|------|----------|
| `mssql_dev` | 14331 | `orderdb` |
| `mssql_stg` | 14332 | `orderdb` |
| `mssql_prd` | 14333 | `orderdb` |

---

## Issues Fixed

- [x] Path references: `docs/tutorials/` → `docs/courses/`
- [x] File references: Updated to `.mssql.sql` extension (Liquibase requirement for Formatted SQL)
- [x] Network mode: Docker uses host/bridge; Podman uses slirp4netns
- [x] Multi-platform: Clarified as MSSQL current, others future
- [x] Verification checklist: Expanded with additional items
- [x] Scripts: Auto-detect container runtime (Docker vs Podman)
- [ ] YAML syntax: `runs-on` with labels (Part 3 CI/CD)
- [ ] Broken link: best-practices file reference (Part 3 CI/CD)

---

## Verification

### Platform Testing

- [x] Test with Docker
- [ ] Test on Ubuntu
- [ ] Test with rootless Podman
- [ ] Test on RHEL
- [ ] Test with Docker
- [ ] Test with rootless Podman

### Functionality

- [ ] All scripts show pass/fail
- [ ] Cleanup removes all artifacts
- [ ] Multi-user (shared host) tested
- [ ] CI/CD workflow runs successfully

### Documentation Checklist

- [ ] All file paths consistent
- [ ] All environment variables documented
- [ ] Documentation links valid
- [ ] Troubleshooting guide complete
