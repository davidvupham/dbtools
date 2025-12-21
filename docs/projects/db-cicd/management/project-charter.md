# Project Charter: db-cicd

## Project Name

Database Change Management CI/CD Platform (db-cicd)

## Purpose

Implement Liquibase Secure/Pro features without licensing, providing enterprise-grade database change management with full GitHub Actions integration.

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

### Out of Scope

- Web dashboard UI
- REST API
- ServiceNow/Jira integration
- Mobile applications

## Stakeholders

| Role | Responsibilities |
|------|------------------|
| Project Sponsor | Approve scope, budget, resources |
| Product Owner | Define requirements, prioritize backlog |
| Tech Lead | Architecture decisions, code review |
| Developer | Implementation |
| DBA Team | Testing, validation, feedback |

## Success Criteria

1. All P1 features implemented and tested
2. GitHub Actions workflows deployed to production repos
3. Documentation complete and reviewed
4. No increase in deployment incidents

## Constraints

- No Liquibase Pro license
- Must integrate with existing GitHub Actions infrastructure
- Must support PostgreSQL, SQL Server, Snowflake, MongoDB
