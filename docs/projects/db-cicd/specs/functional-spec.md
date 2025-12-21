# Functional Specification: db-cicd

## 1. Introduction

The db-cicd platform extends Liquibase Community Edition with enterprise features: policy checks, drift detection, structured logging, approval workflows, and GitHub Actions integration.

### 1.1 Purpose

Define functional and non-functional requirements for the db-cicd platform.

### 1.2 Audience

- Platform Engineers
- DBAs
- DevOps Engineers

## 2. Scope

### 2.1 In Scope

- Policy check engine with configurable rules
- Automated drift detection with alerting
- Secrets management integration (Vault, AWS)
- Structured JSON logging
- GitHub Actions reusable workflows
- Approval gates via GitHub Environments
- Audit trail tracking
- HTML operation reports

### 2.2 Out of Scope

- REST API
- Web dashboard
- Mobile applications

## 3. Functional Requirements

### 3.1 Policy Checks

- **FR-001:** System SHALL parse changelogs (YAML, XML, JSON, SQL)
- **FR-002:** System SHALL evaluate rules against parsed changesets
- **FR-003:** System SHALL block deployments when rules fail (configurable severity)
- **FR-004:** System SHALL generate policy check reports

### 3.2 Drift Detection

- **FR-010:** System SHALL compare database state against changelog
- **FR-011:** System SHALL generate drift reports (JSON, HTML)
- **FR-012:** System SHALL send alerts when drift detected
- **FR-013:** System SHALL run on schedule (configurable frequency)

### 3.3 Secrets Management

- **FR-020:** System SHALL fetch credentials from HashiCorp Vault at runtime
- **FR-021:** System SHALL fetch credentials from AWS Secrets Manager at runtime
- **FR-022:** System SHALL inject credentials as environment variables

### 3.4 Structured Logging

- **FR-030:** System SHALL transform Liquibase logs to JSON format
- **FR-031:** System SHALL include MDC fields (changeset, operation, timestamp)
- **FR-032:** System SHALL output to stdout/file for SIEM ingestion

### 3.5 Approval Workflows

- **FR-040:** System SHALL require approval for production deployments
- **FR-041:** System SHALL use GitHub Environment protection rules
- **FR-042:** System SHALL record approver in audit trail

### 3.6 Audit Trails

- **FR-050:** System SHALL log all deployments with actor, timestamp, outcome
- **FR-051:** System SHALL store audit records in database table
- **FR-052:** System SHALL support export to CSV/JSON

## 4. User Stories

### US-001: Run Policy Checks in CI

> **As a** developer,
> **I want** policy checks to run automatically on my PR,
> **So that** I catch issues before merging.

**Acceptance Criteria:**

- [ ] GitHub Action runs on PR
- [ ] Check results appear in PR comments
- [ ] PR blocked if critical rules fail

### US-002: Detect Drift Daily

> **As a** DBA,
> **I want** daily drift detection on production databases,
> **So that** I know if unauthorized changes were made.

**Acceptance Criteria:**

- [ ] Scheduled GitHub Action runs daily
- [ ] Report generated and stored as artifact
- [ ] Alert sent to Slack/PagerDuty if drift found

### US-003: Approve Production Deployments

> **As a** tech lead,
> **I want** to approve production deployments,
> **So that** changes are reviewed before going live.

**Acceptance Criteria:**

- [ ] Workflow pauses at production environment
- [ ] Approver notified via GitHub
- [ ] Deployment proceeds only after approval

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Policy check time | < 30 seconds for typical changelog |
| NFR-002 | Drift detection time | < 5 minutes per database |
| NFR-003 | Log format | JSON compatible with ELK/Splunk |
| NFR-004 | Platforms supported | PostgreSQL, SQL Server, Snowflake, MongoDB |

## 6. Dependencies

| Dependency | Status |
|------------|--------|
| Liquibase 5.0+ | ✅ Available |
| GitHub Actions | ✅ Available |
| HashiCorp Vault | ⬜ TBD |
| Python 3.11+ | ✅ Available |
