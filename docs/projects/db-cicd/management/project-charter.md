# Project Charter: db-cicd

**Version:** 1.1
**Last Updated:** 2026-01-17
**Status:** Active

## Project Name

Database Change Management CI/CD Platform (db-cicd)

## Purpose

Implement Liquibase Secure/Pro features without licensing, providing enterprise-grade database change management with full GitHub Actions integration. Enable both developers and DBAs to collaborate on database schema changes with appropriate governance.

## Scope

### In Scope

- Secrets management wrapper (HashiCorp Vault, AWS Secrets Manager)
- Structured JSON logging with SIEM integration
- Automated drift detection with alerting
- Policy check engine (Python-based)
- Audit trail tracking
- HTML operation reports
- Stored logic extraction scripts
- Targeted rollback wrapper
- GitHub Actions reusable workflows
- Approval workflows via GitHub Environments
- Multi-platform support (SQL Server, PostgreSQL, Snowflake, MongoDB)
- Baseline generation for existing databases
- New database provisioning workflows

### Out of Scope

- Web dashboard UI
- REST API
- ServiceNow/Jira integration
- Mobile applications

## Database Platforms

| Platform | Version | Use Cases | Driver |
|----------|---------|-----------|--------|
| SQL Server | 2019+ / Azure SQL | Transactional apps, reporting | mssql-jdbc |
| PostgreSQL | 14+ / Aurora | Microservices, analytics | postgresql |
| Snowflake | Current | Data warehouse, analytics | snowflake-jdbc |
| MongoDB | 6.0+ | Document store, NoSQL apps | mongodb (ext) |

## Database State

| Scenario | Approach | Environments |
|----------|----------|--------------|
| Existing databases | Generate baseline, `changelogSync` | Production, Legacy |
| New databases | Start with empty changelog | New projects |

## Stakeholders

| Role | Name/Team | Responsibilities |
|------|-----------|------------------|
| Project Sponsor | TBD | Approve scope, budget, resources |
| Product Owner | TBD | Define requirements, prioritize backlog |
| Tech Lead | TBD | Architecture decisions, code review |
| Platform Engineers | TBD | Implementation, CI/CD workflows |
| DBA Team | TBD | Policy review, production approvals, drift remediation |
| Development Teams | TBD | Changelog authoring, local testing |

## RACI Matrix

| Activity | Authors | CODEOWNERS | Tech Lead | Platform Eng |
|----------|---------|------------|-----------|--------------|
| Author changesets | **R** | I | I | I |
| Review changesets (PR) | C | **R** | I | I |
| Approve PR (CODEOWNERS) | I | **R** | A | I |
| Deploy (all envs) | I | I | I | **R** (CI) |
| Define policy rules | C | C | A | **R** |
| Remediate drift | C | **R** | I | C |
| Maintain CI/CD workflows | I | C | A | **R** |
| Baseline existing DBs | C | **R** | A | C |
| Rollback decisions | C | **R** | A | C |
| Maintain CODEOWNERS | I | **R** | A | C |

**Legend:** R=Responsible, A=Accountable, C=Consulted, I=Informed

**Note:** "Authors" = anyone with repository write access. "CODEOWNERS" = platform-specific owners defined in `.github/CODEOWNERS`.

## Workflow Summary

```
Author                     CODEOWNER                  CI/CD
   │                           │                        │
   ├─── Author changeset ──────┤                        │
   │                           │                        │
   ├─── Push to feature ───────┤                        │
   │    branch                 │                        │
   │                           │                        │
   │    ◄── Policy check ──────┼──── CI validates ──────┤
   │        (auto)             │                        │
   │                           │                        │
   ├─── Create PR ─────────────┤                        │
   │                           │                        │
   │                           ├─── Review & approve ───┤
   │                           │    (CODEOWNERS)        │
   │                           │                        │
   │    ◄── PR merged ─────────┤                        │
   │                           │                        │
   │    ◄── Deploy Dev ────────┼──── Auto deploy ───────┤
   │    ◄── Deploy Stg ────────┼──── Auto deploy ───────┤
   │    ◄── Deploy Prd ────────┼──── Auto deploy ───────┤
   │        (all auto)         │                        │
```

## Success Criteria

1. All P1 features implemented and tested
2. GitHub Actions workflows deployed to production repos
3. Documentation complete and reviewed
4. No increase in deployment incidents
5. Developer changeset-to-production time reduced by 50%
6. 100% of production deployments have approval audit trail
7. Drift detection running daily on all production databases

## Constraints

- No Liquibase Pro license
- Must integrate with existing GitHub Actions infrastructure
- Must support PostgreSQL, SQL Server, Snowflake, MongoDB
- CODEOWNERS-based approval (no separate environment gates)
- Anyone with repo permissions can author changes

## Assumptions

- GitHub Enterprise or GitHub.com available for all teams
- HashiCorp Vault or AWS Secrets Manager available for credentials
- Teams have basic Git/GitHub experience
- Network connectivity exists between CI runners and databases

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MongoDB changelog support limited | Medium | Medium | Use YAML/JSON format, test early |
| Snowflake driver compatibility | Low | High | Pin driver versions, test in CI |
| Developer adoption resistance | Medium | High | Training, clear docs, quick wins |
| Drift in production databases | High | High | Daily drift detection + alerts |
