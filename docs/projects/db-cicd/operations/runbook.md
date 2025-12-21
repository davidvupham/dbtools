# Runbook: db-cicd

## Incident Response

### Policy Check Failures

**Symptoms:** PR blocked, policy check failed

**Steps:**

1. Review error message in PR comments
2. Identify failing rule
3. Either fix the changelog or request rule exception

### Drift Detection Alerts

**Symptoms:** Slack/PagerDuty alert about drift

**Steps:**

1. Identify affected database from alert
2. Run manual diff: `liquibase diff`
3. Determine if change is authorized
4. If unauthorized: revert change and investigate
5. If authorized hotfix: add to changelog and sync

### Failed Deployments

**Symptoms:** GitHub Action deployment failed

**Steps:**

1. Check workflow logs for error
2. If SQL error: review changeset and fix
3. If connection error: verify secrets and network
4. If lock error: run `liquibase releaseLocks`
5. Re-run workflow after fix

### Vault/Secrets Errors

**Symptoms:** "Secrets not found" or auth errors

**Steps:**

1. Verify Vault token is valid
2. Check secret path is correct
3. Verify GitHub Actions has Vault access
4. Check OIDC configuration if using JWT auth

## Escalation

| Severity | Response Time | Escalation Path |
|----------|---------------|-----------------|
| Critical | 15 min | Tech Lead → Manager |
| High | 1 hour | Tech Lead |
| Medium | 4 hours | Team |
| Low | Next business day | Team |
