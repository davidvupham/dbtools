# Technical Architecture: db-cicd

## Overview

The db-cicd platform is a CLI-based toolset orchestrated by GitHub Actions, extending Liquibase Community with enterprise capabilities.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Changelogs  │  │ Flowfiles   │  │ Policy Rules (YAML)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflows                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Validate │→ │ Policy   │→ │ Approval │→ │ Deploy           │ │
│  │          │  │ Checks   │  │ Gate     │  │ (per-env)        │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      db-cicd Components                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Policy      │  │ Drift       │  │ Report Generator        │ │
│  │ Engine      │  │ Detector    │  │ (HTML/JSON)             │ │
│  │ (Python)    │  │ (Python)    │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Secrets     │  │ Log         │  │ Audit Service           │ │
│  │ Wrapper     │  │ Transformer │  │                         │ │
│  │ (Bash)      │  │ (Python)    │  │ (Python)                │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Liquibase Community                         │
│        (Core changelog execution, diff, snapshot)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Database Platforms                                  │
│  PostgreSQL │ SQL Server │ Snowflake │ MongoDB                  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Overview

| Component | Language | Purpose |
|-----------|----------|---------|
| Policy Engine | Python | Parse changelogs, evaluate rules |
| Drift Detector | Python | Compare DB state vs changelog |
| Report Generator | Python | Generate HTML/JSON reports |
| Secrets Wrapper | Bash | Fetch from Vault/AWS, inject env vars |
| Log Transformer | Python | Convert Liquibase logs to JSON |
| Audit Service | Python | Record deployments to DB |

## Data Flow

1. Developer pushes changelog changes
2. GitHub Action triggers validation workflow
3. Policy engine parses and validates changelog
4. If valid, approval gate activates for target environment
5. After approval, secrets wrapper fetches credentials
6. Liquibase executes changes with log transformer
7. Audit service records outcome
8. Report generator creates summary

## Integration Points

- **GitHub Actions:** Primary orchestration layer
- **HashiCorp Vault / AWS Secrets Manager:** Credential storage
- **Slack / PagerDuty:** Alerting via `gds_notification`
- **Elasticsearch / Splunk:** Log ingestion
