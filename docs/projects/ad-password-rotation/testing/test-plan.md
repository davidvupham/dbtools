# Test Plan: AD Password Rotation

## 1. Overview

This document defines the test strategy and test cases for validating the AD Password Rotation system before production deployment.

## 2. Test Objectives

- Verify Vault AD Secrets Engine correctly rotates passwords in Active Directory
- Confirm Vault Agent retrieves and renders credentials on target servers
- Validate service restart/reload procedures work without data loss
- Test error handling and alerting for failure scenarios
- Ensure rollback procedures function correctly

## 3. Test Environment

| Environment | Purpose | AD Domain | Vault Cluster |
|-------------|---------|-----------|---------------|
| **Dev** | Unit testing, initial integration | dev.example.com | vault-dev |
| **Non-Prod** | Full integration, pilot testing | nonprod.example.com | vault-nonprod |
| **Prod** | Production validation (limited) | example.com | vault-prod |

## 4. Test Cases

### 4.1 Vault Configuration Tests

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-001 | AD Engine Enable | `vault secrets enable ad` | Engine enabled at path `ad/` | ⬜ |
| TC-002 | AD Config Valid | Write config with valid LDAPS URL | Config accepted, no errors | ⬜ |
| TC-003 | AD Config Invalid Cert | Write config with bad certificate | Error: certificate validation failed | ⬜ |
| TC-004 | AD Config No Connectivity | Write config with unreachable DC | Error: LDAP connection timeout | ⬜ |
| TC-005 | Role Creation | Create role with valid sAMAccountName | Role created successfully | ⬜ |
| TC-006 | Role Invalid Account | Create role with non-existent account | Error: account not found | ⬜ |

### 4.2 Password Rotation Tests

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-010 | Manual Rotation | `vault write -f ad/rotate-role/<role>` | Password rotated, new value returned | ⬜ |
| TC-011 | Lazy Rotation (TTL) | Wait for TTL, then request creds | Password rotated on request | ⬜ |
| TC-012 | Credential Retrieval | `vault read ad/creds/<role>` | Returns username + current_password | ⬜ |
| TC-013 | Rotation Audit Log | Trigger rotation, check audit | Rotation event logged with timestamp | ⬜ |
| TC-014 | AD Password Changed | After rotation, verify in AD | AD shows new pwdLastSet timestamp | ⬜ |

### 4.3 Vault Agent Tests

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-020 | Agent Auth (AppRole) | Start agent with role_id/secret_id | Token acquired, auto-renewed | ⬜ |
| TC-021 | Template Rendering | Agent renders creds.json | File contains valid JSON with password | ⬜ |
| TC-022 | Command Execution | Template change triggers command | Restart script executes | ⬜ |
| TC-023 | Agent Token Renewal | Wait for token TTL | Token auto-renewed without interruption | ⬜ |
| TC-024 | Agent Recovery | Kill and restart agent | Agent re-authenticates and syncs | ⬜ |

### 4.4 Platform-Specific Tests

#### MSSQL (Windows)

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-030 | Service Password Update | Rotate, agent updates service | `sc qc MSSQLSERVER` shows new account | ⬜ |
| TC-031 | Service Restart | Agent restarts MSSQL | Service running, connections work | ⬜ |
| TC-032 | Downtime Measurement | Time from rotation to service up | Downtime < 60 seconds | ⬜ |

#### PostgreSQL (Linux)

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-040 | Keytab Regeneration | Rotate, script regenerates keytab | `klist -k` shows new keytab | ⬜ |
| TC-041 | PostgreSQL Reload | Agent sends SIGHUP | PostgreSQL reloads without restart | ⬜ |
| TC-042 | Kerberos Auth | Client authenticates with new keytab | Authentication succeeds | ⬜ |

### 4.5 Error Handling Tests

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-050 | AD Unreachable | Block LDAPS during rotation | Retry 3x, then alert | ⬜ |
| TC-051 | Permission Denied | Remove Reset Password right | Error logged, alert sent | ⬜ |
| TC-052 | Service Restart Fail | Corrupt restart script | Error logged, alert sent | ⬜ |
| TC-053 | Vault Sealed | Seal Vault, agent requests | 503 error, agent retries | ⬜ |
| TC-054 | Account Lockout | Use old password 5x | AD locks account, alert triggered | ⬜ |

### 4.6 Rollback Tests

| ID | Test Case | Steps | Expected Result | Pass/Fail |
|----|-----------|-------|-----------------|-----------|
| TC-060 | Manual Rollback | Rotation fails, manually retrieve creds | Password retrievable, service updated | ⬜ |
| TC-061 | Emergency AD Reset | Vault unavailable, reset in AD | Service functional with new password | ⬜ |

## 5. Test Execution Schedule

| Phase | Tests | Environment | Duration | Owner |
|-------|-------|-------------|----------|-------|
| Unit | TC-001 to TC-006 | Dev | 2 hours | Vault Admin |
| Integration | TC-010 to TC-024 | Non-Prod | 4 hours | Vault Admin + DBA |
| Platform | TC-030 to TC-042 | Non-Prod | 8 hours | DBA |
| Failure | TC-050 to TC-061 | Non-Prod | 4 hours | Vault Admin + DBA |
| **Total** | 30 test cases | | **~18 hours** | |

## 6. Entry/Exit Criteria

### Entry Criteria
- [ ] Vault cluster deployed and unsealed
- [ ] AD service account created with delegated permissions
- [ ] Network connectivity verified (LDAPS 636, HTTPS 8200)
- [ ] Test service accounts created in AD

### Exit Criteria
- [ ] All critical test cases (TC-001 to TC-042) pass
- [ ] No high-severity defects open
- [ ] Error handling tests demonstrate proper alerting
- [ ] Rollback procedures validated

## 7. Defect Management

| Severity | Definition | Resolution SLA |
|----------|------------|----------------|
| **Critical** | Rotation fails, passwords not updated | Block pilot, fix immediately |
| **High** | Agent fails to sync, manual intervention needed | Fix before production |
| **Medium** | Logging incomplete, minor script issues | Fix within 1 week |
| **Low** | Documentation gaps, cosmetic issues | Fix when convenient |
