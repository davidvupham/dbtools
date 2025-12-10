# Project Plan: Active Directory Password Rotation with HashiCorp Vault

## 1. Executive Summary

This project aims to automate the rotation of Active Directory (AD) service account passwords using HashiCorp Vault. This will eliminate manual password management, reduce the risk of credential theft, and ensure compliance with security policies. The project covers infrastructure configuration, policy updates, and the migration of database service accounts (MSSQL, PostgreSQL, MongoDB, Snowflake).

## 2. Objectives

- **Security**: Eliminate static, long-lived passwords for critical service accounts.
- **Compliance**: Meet audit requirements for regular credential rotation (e.g., every 30 days).
- **Reliability**: Ensure zero-downtime rotation for supported applications.
- **Automation**: Reduce operational overhead by 90%.

## 3. Scope

- **In Scope**:
  - HashiCorp Vault AD Secrets Engine configuration.
  - Integration with Active Directory (Prod and Non-Prod).
  - Database platforms: MSSQL (Windows/Linux), PostgreSQL, MongoDB, Snowflake.
  - Application sidecar/agent configuration for 5 pilot applications.
- **Out of Scope**:
  - User password rotation (workstation logins).
  - Legacy applications that cannot support dynamic retrieval (will be flagged for remediation).

## 4. Phases and Timeline

### Phase 1: Discovery & Design

**Effort: 3 Days**

- **Tasks**:
  - [ ] Audit existing service accounts.
  - [ ] Identify dependencies (Service Dependencies, Hardcoded scripts).
  - [ ] Define Vault Roles and Policies.
  - [ ] Draft Technical Architecture.
- **Deliverables**: Audit Report, Architecture Diagram.

### Phase 2: Infrastructure Configuration

**Effort: 2 Days**

- **Tasks**:
  - [ ] Create Vault Service Account in AD (Permissions: Reset Password).
  - [ ] Enable/Configure Vault AD Secrets Engine.
  - [ ] Configure Vault Policies and AppRoles.
- **Deliverables**: Configured Vault Instance, Terraform Scripts.

### Phase 3: Pilot Implementation (Non-Prod)

**Effort: 5 Days**

- **Tasks**:
  - [ ] Select 1 MSSQL, 1 Postgres instance.
  - [ ] Implement Vault Agent/Sidecar.
  - [ ] Test Rotation (TTL: 1 hour) and verify application recovery.
  - [ ] Test "Emergency Rollback" procedure.
- **Deliverables**: Validated Pilot, Runbooks Update.

### Phase 4: Production Rollout

**Effort: 5-10 Days (depending on scale)**

- **Tasks**:
  - [ ] Schedule maintenance windows (if required).
  - [ ] Batch migration of service accounts (e.g., 5-10 per batch).
  - [ ] Monitoring for auth failures.
- **Deliverables**: 100% Rotated Accounts.

### Phase 5: Handover & Closure

**Effort: 1 Day**

- **Tasks**:
  - [ ] Finalize Documentation.
  - [ ] Train Operations Team.
- **Deliverables**: Signed-off Project.

## 5. Effort Estimation

| Role | Phase | Est. Hours |
|------|-------|------------|
| Security Engineer | Discovery/Design | 24 |
| Vault Admin | Infra Config | 16 |
| DBA (MSSQL/Postgres) | Pilot/Rollout | 40 |
| Application Owner | Pilot | 16 |
| **Total** | | **~96 Hours** |

## 6. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Account Lockout** | Medium | High | Use "Grace Period" if possible; Monitor event logs closely during rollout. |
| **Service Downtime** | Low | High | Pilot in Non-Prod; Ensure `Restart-Service` logic is robust. |
| **Legacy Incompatibility**| Medium | Medium | Maintain "Static" roles for legacy apps until refactored. |

## 7. Resources Required

- **Active Directory**: Admin access to create the Vault Service Account.
- **Vault**: Token with `sudo` or `root` equivalent for configuration.
- **Compute**: Access to install Vault Agent on DB servers/App servers.
