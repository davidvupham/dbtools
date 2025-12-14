# Runbook: Business Continuity (DR Readiness & Failover Management)

This runbook covers day-2 operations, incident response, and emergency procedures for the Business Continuity service.

## 1. System Overview

The service provides:

- DR readiness monitoring (freshness, indicators, status rules)
- Approval-gated failover/switchover/failback workflows
- Notifications via `gds_notification`
- Audit evidence exports for drills and incidents

## 2. Contacts

| Role | Name | Contact |
|------|------|---------|
| Primary On-Call (Ops) | TBD | TBD |
| DBA On-Call | TBD | TBD |
| Security/IAM | TBD | TBD |
| Business/App Owner Approver | TBD | TBD |

## 3. Common Procedures

### 3.1 Respond to “RPO Indicator Breach” Alert

**When to use:** Tier-based alert indicates replication indicators exceeded threshold or freshness degraded.

**Steps:**

1. Identify impacted resource/group and tier.
2. Check freshness timestamp and last known indicators.
3. Validate whether this is:
   - transient lag (recovering)
   - sustained lag (likely incident)
   - loss of visibility (network/credentials)
4. Notify appropriate stakeholders.
5. If Tier 1 and sustained, prepare a switchover/failover request (do not execute until approvals obtained).

**Verification:**

- [ ] Current status/reason codes reviewed.
- [ ] Audit trail exists for any configuration or execution request.

### 3.2 Monitoring Shows “Loss of Visibility”

**When to use:** Targets unreachable; monitoring cannot refresh.

**Steps:**

1. Confirm service health (API/worker up).
2. Validate network path to target site(s) (primary and DR).
3. Validate secrets/credentials are still valid (no rotation drift).
4. If primary is down, confirm whether DR is reachable and gather DR-side indicators.
5. Update incident notes: last known good timestamp and what is unknown.

### 3.3 Execute a Planned Switchover/Drill

Follow `procedures.md` section “Run a Planned Switchover (Non-Prod Drill)”.

## 4. Troubleshooting

### Issue: Alerts not firing

**Symptoms:**

- Breach visible in UI but no notifications received

**Possible Causes:**

1. `gds_notification` routing misconfigured
2. Worker job not running
3. Rule engine threshold misconfiguration

**Resolution:**

1. Validate worker job health and last run times.
2. Validate notification config in non-prod (ensure not paging prod).
3. Validate rule thresholds on the resource/group.

### Issue: Execution stuck “Running”

**Symptoms:**

- Request remains Running with no progress updates

**Possible Causes:**

1. Worker crashed mid-execution
2. Connector step blocked or timed out
3. Target platform operation is long-running

**Resolution:**

1. Check worker logs and queue depth.
2. Check connector logs and last successful step.
3. If safe and supported, use resume/retry policy; otherwise create a new request with fresh approvals.

## 5. Emergency Procedures

### 5.1 Break-glass (Emergency Access)

**When to use:** Tier 1 incident and required approvers are unavailable; delay causes unacceptable impact.

> [!CAUTION]
> Break-glass is a controlled exception. It must be time-bound, fully audited, and reviewed post-incident.

**Steps:**

1. Confirm incident is declared and has an incident/ticket reference.
2. Notify Security/IAM and incident stakeholders that break-glass is requested.
3. Obtain time-bound elevation through the documented IAM process.
4. Create the execution request referencing the incident and mark as break-glass.
5. Execute with maximum feasible prechecks; document any limitations.
6. After stabilization, revoke elevated access and complete post-incident review.

**Verification:**

- [ ] Audit log includes break-glass marker and actor identity.
- [ ] Notifications sent to security/compliance distribution.

## 6. Monitoring & Alerts (starter table)

| Alert | Threshold | Action |
|-------|-----------|--------|
| RPO-indicator breach (Tier 1) | Configured threshold exceeded | Investigate immediately; prep controlled switchover/failover request |
| Loss of visibility (Tier 1) | Freshness beyond threshold | Validate network/credentials; treat as incident if sustained |
| Execution failed | Any failure | Review audit + logs; notify stakeholders; determine rollback/next request |
