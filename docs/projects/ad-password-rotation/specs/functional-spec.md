# Functional Specification: AD Password Rotation

## 1. Overview

This document defines the functional requirements for automating Active Directory (AD) service account password rotation using HashiCorp Vault.

## 2. Scope

### 2.1 In Scope

- Rotation of AD service account passwords for database platforms:
  - Microsoft SQL Server (Windows and Linux)
  - PostgreSQL
  - MongoDB
  - Snowflake connectors
- Integration with HashiCorp Vault AD Secrets Engine
- Automated credential retrieval via Vault Agent
- Service restart orchestration post-rotation

### 2.2 Out of Scope

- End-user password rotation (workstation logins)
- Non-AD authentication mechanisms (local accounts)
- Legacy applications without Vault integration capability

## 3. User Stories

### US-001: Automated Password Rotation

> **As a** Security Engineer,
> **I want** service account passwords to rotate automatically,
> **So that** I meet compliance requirements for credential hygiene.

**Acceptance Criteria:**

- [ ] Passwords rotate based on configurable TTL (default: 24 hours)
- [ ] Manual rotation can be triggered via Vault API/CLI
- [ ] Rotation events are logged in Vault audit log

### US-002: Zero-Downtime Rotation (Where Possible)

> **As a** DBA,
> **I want** password rotation to cause minimal or no downtime,
> **So that** production services remain available.

**Acceptance Criteria:**

- [ ] Services using Keytab authentication experience zero downtime
- [ ] Services requiring restart have downtime < 60 seconds
- [ ] Clustered databases use rolling restart pattern

### US-003: Emergency Credential Access

> **As an** On-Call Engineer,
> **I want** to retrieve the current password for a service account,
> **So that** I can troubleshoot authentication issues.

**Acceptance Criteria:**

- [ ] Authorized users can read current credentials via `vault read ad/creds/<role>`
- [ ] Access is logged and attributed to the requesting user
- [ ] Break-glass procedure documented for Vault unavailability

### US-004: Audit and Compliance

> **As a** Compliance Officer,
> **I want** full audit trail of password rotations,
> **So that** I can demonstrate compliance during audits.

**Acceptance Criteria:**

- [ ] Every rotation event includes: timestamp, role, initiator (TTL/manual)
- [ ] Audit logs retained for 1 year minimum
- [ ] Reports can be generated showing rotation frequency per account

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Rotation Latency | Password updated in AD within 5 seconds of trigger |
| NFR-002 | Agent Sync Latency | Vault Agent retrieves new password within 30 seconds |
| NFR-003 | Availability | Vault cluster: 99.9% uptime (HA configuration) |
| NFR-004 | Recovery Time Objective (RTO) | Service recovery < 5 minutes post-failure |
| NFR-005 | Recovery Point Objective (RPO) | Zero data loss (passwords stored in AD, not Vault) |

## 5. Security Requirements

| ID | Requirement |
|----|-------------|
| SEC-001 | All communication over TLS 1.2+ |
| SEC-002 | Vault bind account has minimal AD permissions (Reset Password only) |
| SEC-003 | AppRole credentials rotated every 30 days |
| SEC-004 | No plaintext passwords in logs or config files |

## 6. Constraints

1. **Active Directory**: Must be Windows Server 2008 R2 functional level or higher.
2. **Network**: Vault must have LDAPS (port 636) access to Domain Controllers.
3. **Vault Version**: Requires Vault 1.7+ for AD Secrets Engine features.

## 7. Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Vault Cluster (HA) | Platform Team | ✅ Available |
| AD Service Account for Vault | AD Team | 🟡 Pending |
| Network ACL (Vault → DC) | Network Team | 🟡 Pending |
| Vault Agent on DB Servers | DBA Team | ⬜ Not Started |
