# Technical Architecture: db-cicd

**Version:** 1.1
**Last Updated:** 2026-01-17
**Status:** Draft

## Overview

The db-cicd platform is a CLI-based toolset orchestrated by GitHub Actions, extending Liquibase Community with enterprise capabilities. It supports four database platforms (SQL Server, PostgreSQL, Snowflake, MongoDB) with platform-specific changelogs and unified CI/CD workflows.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GitHub Repository                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        database/                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │ │
│  │  │ platforms/  │  │ shared/     │  │ policies/   │  │ snapshots/    │  │ │
│  │  │ mssql/      │  │ data/       │  │ rules.yaml  │  │ *.json        │  │ │
│  │  │ postgres/   │  │ modules/    │  │             │  │               │  │ │
│  │  │ snowflake/  │  │             │  │             │  │               │  │ │
│  │  │ mongodb/    │  │             │  │             │  │               │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  .github/                                                               │ │
│  │  ├── workflows/deploy-pipeline.yml                                      │ │
│  │  ├── workflows/drift-detection.yml                                      │ │
│  │  └── CODEOWNERS                                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflows                              │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      On PR / Push to main                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │ Validate │→ │ Policy   │→ │ Deploy   │→ │ Deploy   │→ │ Deploy │  │   │
│  │  │ Changelog│  │ Check    │  │ Dev      │  │ Stg      │  │ Prd    │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Scheduled (Daily)                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐    │   │
│  │  │ Drift        │→ │ Generate     │→ │ Alert if drift detected  │    │   │
│  │  │ Detection    │  │ Report       │  │ (Slack/PagerDuty)        │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         db-cicd Components                                   │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Policy Engine   │  │ Drift Detector  │  │ Report Generator            │  │
│  │ (Python)        │  │ (Python)        │  │ (Python/Jinja2)             │  │
│  │                 │  │                 │  │                             │  │
│  │ • Parse SQL/XML │  │ • Compare snap- │  │ • HTML reports              │  │
│  │ • Evaluate rules│  │   shots to live │  │ • JSON artifacts            │  │
│  │ • Block/warn    │  │ • Generate diff │  │ • PR comments               │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Secrets Wrapper │  │ Log Transformer │  │ Audit Service               │  │
│  │ (Bash/Python)   │  │ (Python)        │  │ (Python)                    │  │
│  │                 │  │                 │  │                             │  │
│  │ • Vault client  │  │ • JSON output   │  │ • Record deployments        │  │
│  │ • AWS SM client │  │ • MDC context   │  │ • Query history             │  │
│  │ • Env injection │  │ • SIEM format   │  │ • Export reports            │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Liquibase Runtime                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Liquibase Community 5.x                           │    │
│  │  • Changelog execution (update, rollback)                            │    │
│  │  • Diff and snapshot generation                                      │    │
│  │  • Tracking tables (DATABASECHANGELOG, DATABASECHANGELOGLOCK)        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Platform Drivers (LPM-managed)                    │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────────┐   │    │
│  │  │ mssql-jdbc│  │ postgresql│  │ snowflake │  │ mongodb (ext)   │   │    │
│  │  │ 12.8.x    │  │ 42.7.x    │  │ 3.18.x    │  │ liquibase-mongo │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └─────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Database Platforms                                   │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ SQL Server      │  │ PostgreSQL      │  │ Snowflake                   │  │
│  │                 │  │                 │  │                             │  │
│  │ • Azure SQL     │  │ • RDS/Aurora    │  │ • Data warehouse            │  │
│  │ • On-prem 2019+ │  │ • Cloud SQL     │  │ • Schema-per-env            │  │
│  │ • Managed Inst. │  │ • On-prem 14+   │  │ • Role-based access         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ MongoDB                                                              │    │
│  │                                                                      │    │
│  │ • Atlas / On-prem 6.0+                                               │    │
│  │ • Document collections, indexes                                      │    │
│  │ • YAML changelog format (ext: change types)                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Multi-Platform Project Structure

```
database/
├── changelog-master.xml              # Global root (optional, for cross-platform)
│
├── platforms/
│   ├── mssql/
│   │   ├── changelog.xml             # SQL Server master
│   │   ├── baseline/
│   │   │   └── V0000__baseline.mssql.sql
│   │   ├── changes/
│   │   │   ├── V0001__create_users.mssql.sql
│   │   │   └── V0002__add_index.mssql.sql
│   │   └── env/
│   │       ├── liquibase.dev.properties
│   │       ├── liquibase.stg.properties
│   │       └── liquibase.prd.properties
│   │
│   ├── postgres/
│   │   ├── changelog.xml             # PostgreSQL master
│   │   ├── baseline/
│   │   ├── changes/
│   │   └── env/
│   │
│   ├── snowflake/
│   │   ├── changelog.xml             # Snowflake master
│   │   ├── baseline/
│   │   ├── changes/
│   │   └── env/
│   │
│   └── mongodb/
│       ├── changelog.yaml            # MongoDB master (YAML format)
│       ├── baseline/
│       ├── changes/
│       └── env/
│
├── shared/
│   ├── data/
│   │   └── reference/                # CSV files for loadData
│   └── modules/
│       └── audit/                    # Reusable audit table patterns
│
├── policies/
│   └── rules.yaml                    # Policy check rules
│
└── snapshots/
    ├── mssql/
    ├── postgres/
    ├── snowflake/
    └── mongodb/
```

## Component Details

| Component | Language | Purpose | Input | Output |
|-----------|----------|---------|-------|--------|
| Policy Engine | Python | Parse changelogs, evaluate rules | Changelog files, rules.yaml | Pass/fail, violations report |
| Drift Detector | Python | Compare DB state vs snapshot | Live DB, snapshot JSON | Drift report (JSON/HTML) |
| Report Generator | Python/Jinja2 | Generate human-readable reports | JSON artifacts | HTML reports, PR comments |
| Secrets Wrapper | Bash/Python | Fetch credentials at runtime | Vault/AWS path | Environment variables |
| Log Transformer | Python | Convert Liquibase logs to JSON | Liquibase stdout | Structured JSON logs |
| Audit Service | Python | Record deployment history | Deployment events | Audit table entries |

## Platform-Specific Considerations

| Platform | Changelog Format | Driver | Special Considerations |
|----------|------------------|--------|------------------------|
| SQL Server | Formatted SQL | mssql-jdbc | Use `GO` as delimiter; `IF EXISTS` patterns |
| PostgreSQL | Formatted SQL | postgresql | `CREATE OR REPLACE`; transactional DDL |
| Snowflake | Formatted SQL | snowflake-jdbc | Warehouse/role context; schema prefixes |
| MongoDB | YAML | liquibase-mongodb | `ext:` change types; no SQL support |

## Environment Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PR Created                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CI Checks (Required)                                                    │
│  ├── liquibase validate (syntax check)                                   │
│  ├── policy-check (custom rules)                                         │
│  └── CODEOWNERS approval                                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ PR Merged
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Deploy Pipeline                                                         │
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐             │
│  │ Development  │────▶│   Staging    │────▶│  Production  │             │
│  │              │     │              │     │              │             │
│  │ • Auto       │     │ • Auto       │     │ • Auto       │             │
│  │ • All        │     │ • All        │     │ • All        │             │
│  │   platforms  │     │   platforms  │     │   platforms  │             │
│  └──────────────┘     └──────────────┘     └──────────────┘             │
│         │                    │                    │                      │
│         ▼                    ▼                    ▼                      │
│    [Snapshot]           [Snapshot]           [Snapshot]                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## CI/CD Workflow Matrix

| Workflow | Trigger | Platforms | Actions |
|----------|---------|-----------|---------|
| `validate-pr.yml` | PR opened/updated | All changed | validate, policy-check |
| `deploy-pipeline.yml` | Push to main | All changed | deploy dev → stg → prd |
| `drift-detection.yml` | Schedule (daily) | All | diff vs snapshot, alert |
| `baseline-generator.yml` | Manual dispatch | Selected | generateChangeLog |
| `rollback.yml` | Manual dispatch | Selected | rollback to tag |

## Secrets Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Secrets Sources                                   │
│                                                                          │
│  ┌─────────────────────┐          ┌─────────────────────────────────┐   │
│  │ GitHub Secrets      │          │ HashiCorp Vault / AWS SM        │   │
│  │ (for GitHub Actions)│          │ (for production credentials)    │   │
│  │                     │          │                                 │   │
│  │ • VAULT_ADDR        │          │ • secret/db-cicd/mssql/dev     │   │
│  │ • VAULT_TOKEN       │          │ • secret/db-cicd/mssql/stg     │   │
│  │ • AWS_ROLE_ARN      │          │ • secret/db-cicd/mssql/prd     │   │
│  └─────────────────────┘          │ • (same for postgres, etc.)     │   │
│           │                       └─────────────────────────────────┘   │
│           │                                      │                      │
│           ▼                                      ▼                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Secrets Wrapper                               │   │
│  │                                                                  │   │
│  │  vault kv get -field=password secret/db-cicd/mssql/prd          │   │
│  │           OR                                                     │   │
│  │  aws secretsmanager get-secret-value --secret-id db-cicd/mssql  │   │
│  │                                                                  │   │
│  │  → Exports: LIQUIBASE_COMMAND_PASSWORD                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Integration Points

| System | Purpose | Protocol |
|--------|---------|----------|
| GitHub Actions | CI/CD orchestration | GitHub API |
| HashiCorp Vault | Production secrets | HTTPS/API |
| AWS Secrets Manager | Alternative secrets | AWS SDK |
| Slack | Deployment notifications | Webhook |
| PagerDuty | Drift/failure alerts | Events API |
| Elasticsearch/Splunk | Log ingestion | JSON over HTTPS |

## Baseline Strategy for Existing Databases

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 1: Generate Baseline from Production                              │
│                                                                          │
│  liquibase --url=<prod> generateChangeLog \                             │
│    --changelog-file=platforms/mssql/baseline/V0000__baseline.mssql.sql  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 2: Review & Clean Baseline                                         │
│                                                                          │
│  • Remove system objects                                                 │
│  • Remove temporary/test objects                                         │
│  • Add rollback statements                                               │
│  • Verify formatting                                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 3: Sync to All Environments                                        │
│                                                                          │
│  for env in dev stg prd; do                                             │
│    liquibase --url=<$env> changelogSync                                 │
│    liquibase --url=<$env> tag baseline                                  │
│  done                                                                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 4: Capture Baseline Snapshot                                       │
│                                                                          │
│  liquibase snapshot --output-file=snapshots/mssql/baseline.json         │
│                                                                          │
│  → Enables drift detection from this point forward                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Security Considerations

| Area | Requirement | Implementation |
|------|-------------|----------------|
| Credentials | Never in source control | Vault/AWS SM + env vars |
| DB Users | Least privilege | Dedicated `liquibase_svc` account |
| Network | Runner → DB access | Self-hosted runners or VPN |
| Audit | All deployments logged | Audit service + GitHub logs |
| Rollback | Available for all changes | Mandatory rollback statements |

## Future Considerations

- **Web Dashboard:** Read-only view of deployment history and drift status
- **Slack Bot:** Interactive approvals and status queries
- **Multi-Region:** Support for geo-distributed deployments
- **Canary Deployments:** Partial rollout to subset of replicas
